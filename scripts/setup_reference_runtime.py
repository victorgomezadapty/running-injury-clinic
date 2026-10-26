"""Acquire a pinned portable GNU Octave locally; no system installation."""
from pathlib import Path
import hashlib
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

ROOT = Path(__file__).resolve().parents[1]
VERSION = "11.3.0"
URL = f"https://ftp.gnu.org/gnu/octave/windows/octave-{VERSION}-w64.7z"


def parallel_archive_download(partial, archive):
    """Bounded 8 MiB ranges avoid the GNU server's slow single-stream transfer."""
    response = requests.head(URL, timeout=60)
    response.raise_for_status()
    total = int(response.headers["Content-Length"])
    start = partial.stat().st_size if partial.exists() else 0
    segments = archive.parent / "segments"
    segments.mkdir(exist_ok=True)
    ranges = [(a, min(a + 8 * 1024 * 1024, total) - 1) for a in range(start, total, 8 * 1024 * 1024)]

    def fetch(bounds):
        first, last = bounds
        path = segments / f"{first}-{last}.part"
        length = last - first + 1
        if path.exists() and path.stat().st_size == length:
            return path
        with requests.get(URL + f"?chunk={first}", headers={"Range": f"bytes={first}-{last}"}, stream=True, timeout=(30, 180)) as part:
            part.raise_for_status()
            if part.status_code != 206 or part.headers.get("Content-Range", "").split("/")[0] != f"bytes {first}-{last}":
                raise RuntimeError("GNU server did not honor bounded byte range")
            with path.open("wb") as handle:
                for chunk in part.iter_content(256 * 1024):
                    handle.write(chunk)
        if path.stat().st_size != length:
            raise IOError("Incomplete archive segment")
        return path

    completed = start
    with ThreadPoolExecutor(max_workers=8) as pool:
        tasks = {pool.submit(fetch, bounds): bounds for bounds in ranges}
        for task in as_completed(tasks):
            path = task.result()
            completed += path.stat().st_size
            print(f"Octave verified transfer {completed/1e6:.1f}/{total/1e6:.1f} MB", flush=True)
    assembled = archive.with_suffix(".7z.assembled")
    with assembled.open("wb") as output:
        paths = ([partial] if start else []) + [segments / f"{a}-{b}.part" for a, b in ranges]
        for path in paths:
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    output.write(chunk)
    if assembled.stat().st_size != total:
        raise IOError("Assembled archive size mismatch")
    assembled.rename(archive)


def main():
    folder = ROOT / ".tools/reference_runtime"
    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / f"octave-{VERSION}-w64.7z"
    partial = archive.with_suffix(".7z.part")
    if not archive.exists():
        parallel_archive_download(partial, archive)
    if not archive.exists():
        # Resume only when the server confirms the requested byte range.
        start = partial.stat().st_size if partial.exists() else 0
        headers = {"Range": f"bytes={start}-"} if start else {}
        with requests.get(URL, headers=headers, stream=True, timeout=(30, 120)) as response:
            response.raise_for_status()
            if start and (response.status_code != 206 or not response.headers.get("Content-Range", "").startswith(f"bytes {start}-")):
                raise RuntimeError("Server did not honor resumable download")
            expected = int(response.headers.get("Content-Length", "0"))
            downloaded, last = 0, time.monotonic()
            with partial.open("ab" if start else "xb") as handle:
                for chunk in response.iter_content(1024 * 1024):
                    handle.write(chunk)
                    downloaded += len(chunk)
                    if time.monotonic() - last > 15:
                        print(f"Octave downloaded {(start + downloaded)/1e6:.1f} MB", flush=True)
                        last = time.monotonic()
            if expected and downloaded != expected:
                raise IOError("Incomplete GNU archive")
        partial.rename(archive)
    digest = hashlib.sha256()
    with archive.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    signature = archive.with_suffix(".7z.sig")
    if not signature.exists():
        response = requests.get(URL + ".sig", timeout=60)
        response.raise_for_status()
        signature.write_bytes(response.content)
    listing = subprocess.run(["tar", "-tf", str(archive)], capture_output=True, text=True, check=True)
    names = listing.stdout.splitlines()
    if any(Path(name).is_absolute() or ".." in Path(name).parts for name in names):
        raise ValueError("Unsafe archive path")
    executable = next((folder / name for name in names if name.endswith("/bin/octave-cli.exe")), None)
    if executable is None:
        raise ValueError("Portable archive has no octave-cli.exe")
    if not executable.exists():
        print("Extracting portable reference runtime inside project .tools/", flush=True)
        subprocess.run(["tar", "-xf", str(archive), "-C", str(folder)], check=True)
    proof = subprocess.run([str(executable), "--no-gui", "--quiet", "--eval", "disp(version); pkg list;"], capture_output=True, text=True, timeout=120)
    print(proof.stdout, flush=True)
    if proof.returncode:
        print(proof.stderr, flush=True)
        raise RuntimeError("Portable reference runtime did not start")
    manifest = {"version": VERSION, "download_url": URL, "archive_bytes": archive.stat().st_size,
                "archive_sha256": digest.hexdigest(), "executable": executable.relative_to(ROOT).as_posix(),
                "source": "official GNU distribution linked from https://octave.org/download",
                "signature_downloaded": True, "publisher_signature_verified": False,
                "runtime_probe": proof.stdout, "system_installation": False}
    (folder / "runtime_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
