"""Acquire the small, version-pinned official BMC/RIC companion files.

Waveforms are intentionally excluded from Milestone 1. Existing source files
are checked against Git blob hashes and are never silently overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

COMMIT = "21f5a4607c9e4f6a365caa6e6d85c96787517844"
REPOSITORY = "regifukuchi/BMC-RIC-running-biomechanics"
FILES = {
    "data/metadata.txt": "6c8359205a9ab15da1e0e349aa0720d34629a0e0",
    "README.md": "6da6c2e63b1159d2ba39af4eb9b0994da5222a30",
    "LICENSE.txt": "0fb847eb09afc05734c2f1aa34bc3ebd995a072a",
    "notebooks/BMC_RIC_dataset.ipynb": "014be591bfbc0a174590034a63d4ee343ffd2370",
}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def acquire(root: Path) -> dict:
    destination = root / "data/external/bmc_ric"
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {"repository": REPOSITORY, "commit": COMMIT,
                "license": "CC-BY-4.0", "files": []}
    for relative, expected_sha in FILES.items():
        path = destination / relative
        url = f"https://raw.githubusercontent.com/{REPOSITORY}/{COMMIT}/{relative}"
        if path.exists():
            content = path.read_bytes()
        else:
            response = requests.get(url, timeout=(15, 60))
            response.raise_for_status()
            content = response.content
        actual_sha = git_blob_sha(content)
        if actual_sha != expected_sha:
            raise ValueError(f"Source integrity mismatch: {relative}")
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as handle:
                handle.write(content)
        manifest["files"].append({"path": relative, "source_url": url,
                                 "bytes": len(content), "git_blob_sha1": actual_sha,
                                 "sha256": hashlib.sha256(content).hexdigest()})
    manifest["verified_at_utc"] = datetime.now(timezone.utc).isoformat()
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(acquire(args.root), indent=2))
