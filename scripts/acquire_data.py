"""Acquire the version-pinned public metadata; never overwrite raw files.

Large archives are indexed and sampled through bounded HTTP range reads.
No full-archive fallback is allowed.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile
import struct
import zlib
import sys
import csv

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
API = "https://api.figshare.com/v2/articles/24255795/versions/1"


def acquire_pilot(article, manifest_path, raw, provenance):
    """Acquire exact reviewed members in bounded batches; record partial failures."""
    payload = manifest_path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    immutable_write(provenance / "pilot_manifests" / (digest + ".csv"), payload)
    rows = list(csv.DictReader(payload.decode("utf-8-sig").splitlines()))
    if not 1 <= len(rows) <= 40 or len({r["participant_id"] for r in rows}) != len(rows):
        raise ValueError("Pilot manifest must contain 1–40 distinct participants")
    for row in rows:
        expected = f"reformat_data/{row['participant_id']}/{row['filename']}"
        if row["archive_member"] != expected or Path(expected).is_absolute() or ".." in Path(expected).parts:
            raise ValueError("Unsafe or inconsistent pilot member")
    entry = next(f for f in article["files"] if f["name"] == "ric_data.zip")
    journal = {"manifest_sha256": digest, "source_archive_file_id": entry["id"], "records": [], "range_bytes": 0}
    reader, archive = None, None
    try:
        for row in rows:
            record = {"participant_id": row["participant_id"], "filename": row["filename"], "archive_member": row["archive_member"]}
            try:
                if archive is None or reader.transferred + int(row["compressed_bytes"]) + 1_000_000 > 145_000_000:
                    if archive is not None:
                        journal["range_bytes"] += reader.transferred
                        archive.close()
                        reader.session.close()
                    reader = RangeReader(entry["download_url"], entry["size"])
                    archive = zipfile.ZipFile(reader)
                item = archive.getinfo(row["archive_member"])
                if item.compress_size != int(row["compressed_bytes"]) or item.file_size != int(row["uncompressed_bytes"]):
                    raise ValueError("Reviewed manifest differs from remote archive directory")
                existing = raw / "sample" / item.filename
                destination = existing if existing.exists() else raw / "pilot" / item.filename
                content = destination.read_bytes() if destination.exists() else read_member(archive, reader, item)
                if len(content) != item.file_size or zlib.crc32(content) != item.CRC:
                    raise ValueError("Existing/downloaded pilot member failed ZIP integrity")
                immutable_write(destination, content)
                record.update(status="verified", path=destination.relative_to(ROOT).as_posix(),
                              bytes=len(content), sha256=hashlib.sha256(content).hexdigest(), crc32=item.CRC)
                print(f"Pilot verified {row['participant_id']} / {row['filename']}", flush=True)
            except Exception as error:
                record.update(status="failed", error=f"{type(error).__name__}: {error}")
                print(f"Pilot FAILED {row['participant_id']}: {error}", flush=True)
            journal["records"].append(record)
            (provenance / "pilot_acquisition.json").write_text(json.dumps(journal, indent=2), encoding="utf-8")
    finally:
        if archive is not None:
            journal["range_bytes"] += reader.transferred
            archive.close()
            reader.session.close()
        (provenance / "pilot_acquisition.json").write_text(json.dumps(journal, indent=2), encoding="utf-8")
    if any(r["status"] != "verified" for r in journal["records"]):
        raise RuntimeError("Pilot acquisition incomplete; inspect the acquisition journal")


def immutable_write(path: Path, payload: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"Refusing to overwrite immutable source: {path}")
    else:
        with path.open("xb") as handle:
            handle.write(payload)


class RangeReader(io.RawIOBase):
    """Seekable remote file with a strict byte budget and range validation."""

    def __init__(self, url: str, size: int, budget: int = 150_000_000):
        self.url, self.size, self.budget = url, size, budget
        self.position = self.transferred = 0
        self.session = requests.Session()

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        self.position = offset if whence == 0 else (self.position if whence == 1 else self.size) + offset
        if self.position < 0:
            raise ValueError("Negative offset")
        return self.position

    def read(self, size=-1):
        size = self.size - self.position if size < 0 else min(size, self.size - self.position)
        if size <= 0:
            return b""
        if size > 50_000_000 or self.transferred + size > self.budget:
            raise ValueError("Remote range byte budget exceeded")
        start, end = self.position, self.position + size - 1
        # Cache-busting range query prevents a CDN from reusing another byte range.
        url = f"{self.url}?range_start={start}&range_end={end}"
        with self.session.get(url, headers={"Range": f"bytes={start}-{end}", "Accept-Encoding": "identity"}, stream=True, timeout=90) as response:
            response.raise_for_status()
            if response.status_code != 206 or response.headers.get("Content-Range", "").split("/")[0] != f"bytes {start}-{end}":
                raise RuntimeError("Server did not honor exact byte range; full download refused")
            result = response.raw.read(size + 1)
        if len(result) != size:
            raise IOError(f"Expected {size} bytes, got {len(result)}")
        self.position += size
        self.transferred += size
        return result


def read_member(archive, reader, item):
    """Handle the archive's Deflate64 members and verify size and ZIP CRC."""
    if item.file_size > 150_000_000:
        raise ValueError("Uncompressed sample member exceeds byte limit")
    if item.compress_type != 9:
        content = archive.read(item)
    else:
        import inflate64
        reader.seek(item.header_offset)
        header = reader.read(30)
        if header[:4] != b"PK\x03\x04":
            raise ValueError("Invalid ZIP local file header")
        name_length, extra_length = struct.unpack_from("<HH", header, 26)
        reader.seek(name_length + extra_length, 1)
        compressed = reader.read(item.compress_size)
        content = inflate64.Inflater().inflate(compressed)
    if len(content) != item.file_size or zlib.crc32(content) != item.CRC:
        raise ValueError("ZIP member size/CRC integrity check failed")
    return content


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=int, default=0, choices=range(0, 11))
    parser.add_argument("--index-archives", action="store_true")
    parser.add_argument("--pilot-manifest", type=Path)
    parser.add_argument("--tutorials", action="store_true", help="Acquire official tutorials 1–2 and small event-model files")
    parser.add_argument("--validation-references", action="store_true", help="Acquire the small official tutorial output caches 2 and 4")
    args = parser.parse_args()
    raw = ROOT / "data/raw"
    provenance = ROOT / "data/interim/provenance"
    provenance.mkdir(parents=True, exist_ok=True)
    snapshot = provenance / "figshare_24255795_v1.json"
    if snapshot.exists():
        article = json.loads(snapshot.read_text(encoding="utf-8"))
    else:
        response = requests.get(API, timeout=60)
        response.raise_for_status()
        article = response.json()
        immutable_write(snapshot, json.dumps(article, ensure_ascii=False, indent=2).encode("utf-8"))
    manifest = []
    for entry in article["files"]:
        manifest.append({k: entry.get(k) for k in ("id", "name", "size", "download_url", "computed_md5")})
        if entry["name"] in {"README.txt", "run_data_meta.csv", "walk_data_meta.csv"}:
            path = raw / entry["name"]
            if path.exists():
                content = path.read_bytes()
            else:
                response = requests.get(entry["download_url"], timeout=90)
                response.raise_for_status()
                content = response.content
            if len(content) != entry["size"] or hashlib.md5(content).hexdigest() != entry["computed_md5"]:
                raise ValueError(f"Size/MD5 mismatch: {entry['name']}")
            immutable_write(path, content)
            print(f"Verified {entry['name']}: {len(content):,} bytes", flush=True)
    (provenance / "file_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if args.index_archives or args.sample or args.tutorials or args.validation_references:
        for entry in article["files"]:
            if not entry["name"].endswith(".zip"):
                continue
            if (args.tutorials or args.validation_references) and not args.index_archives and not args.sample and entry["name"] == "ric_data.zip":
                continue
            reader = RangeReader(entry["download_url"], entry["size"])
            with zipfile.ZipFile(reader) as archive:
                index = [{"filename": i.filename, "size": i.file_size, "compressed_size": i.compress_size, "crc32": i.CRC} for i in archive.infolist()]
                index_path = provenance / (Path(entry["name"]).stem + "_index.json")
                index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
                print(f"Indexed {entry['name']}: {len(index)} entries", flush=True)
                if entry["name"] == "Supplemental_materials.zip":
                    selected = [i for i in archive.infolist() if Path(i.filename).suffix.lower() in {".m", ".txt", ".md"} and i.file_size < 1_000_000]
                    if args.tutorials:
                        selected += [i for i in archive.infolist() if Path(i.filename).name in {"tutorial_1.mlx", "tutorial_2.mlx", "event_data_TD.mat", "event_data_TO.mat", "gaitClass.mat"}]
                    if args.validation_references:
                        selected += [i for i in archive.infolist() if Path(i.filename).name in {"tutorial_2.mat", "tutorial_4_cache.mat", "tutorial_3.mlx", "tutorial_4.mlx"}]
                else:
                    # Five ingestion examples plus up to five task/status strata.
                    selected, subjects = [], set()
                    for item in archive.infolist():
                        if item.filename.lower().endswith(".json") and not item.filename.startswith("__MACOSX/"):
                            subject = Path(item.filename).parent.name
                            if subject not in subjects and len(selected) < min(args.sample, 5):
                                selected.append(item)
                                subjects.add(subject)
                    if args.sample > 5:
                        from src.data.load_metadata import load_metadata, first_observation
                        metadata = load_metadata(raw)
                        runs = first_observation(metadata[metadata.task.eq("running")])
                        walking_ids = set(metadata.loc[metadata.task.eq("walking"), "participant_id"])
                        pools = [runs[runs.participant_id.isin(walking_ids) & runs.injury_status.eq(status)] for status in ["healthy", "injured", "unknown", "discordant"]]
                        pools.append(first_observation(metadata[metadata.task.eq("walking") & ~metadata.participant_id.isin(set(runs.participant_id))]))
                        for pool in pools:
                            if len(selected) >= args.sample:
                                break
                            for row in pool.itertuples():
                                member = f"reformat_data/{row.participant_id}/{row.filename}"
                                if row.participant_id not in subjects and member in archive.namelist():
                                    selected.append(archive.getinfo(member))
                                    subjects.add(row.participant_id)
                                    break
                for item in selected:
                    # Flatten only official code; retain participant path for raw samples.
                    relative = Path(item.filename)
                    if relative.is_absolute() or ".." in relative.parts:
                        raise ValueError("Unsafe archive path")
                    destination = raw / ("official_code" if entry["name"] == "Supplemental_materials.zip" else "sample") / relative
                    if destination.exists():
                        existing = destination.read_bytes()
                        if len(existing) != item.file_size or zlib.crc32(existing) != item.CRC:
                            raise ValueError(f"Existing immutable sample failed ZIP size/CRC: {destination}")
                    else:
                        immutable_write(destination, read_member(archive, reader, item))
                    print(f"Sampled {item.filename}", flush=True)
            print(f"Range bytes transferred: {reader.transferred:,}", flush=True)
    if args.pilot_manifest:
        acquire_pilot(article, args.pilot_manifest.resolve(), raw, provenance)
    hashes = []
    for path in sorted(raw.rglob("*")):
        if path.is_file():
            hashes.append({"path": path.relative_to(ROOT).as_posix(), "size": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (provenance / "raw_checksums.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
