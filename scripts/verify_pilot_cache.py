"""Confirm a warm pilot export preserves scientific tables byte for byte."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ["data/processed/pilot_features_long.csv", "data/processed/pilot_features_wide.csv"]


def checksums():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in TARGETS}


def main():
    before = checksums()
    result = subprocess.run([sys.executable, str(ROOT / "scripts/run_pilot.py")], cwd=ROOT, check=True, text=True, capture_output=True)
    after = checksums()
    summary = json.loads((ROOT / "reports/tables/pilot_summary.json").read_text())
    proof = {"tables_before": before, "tables_after": after, "scientific_tables_identical": before == after,
             "cache_hits": summary["cache_hits"], "participants": summary["participants"],
             "registry_sha256": summary["registry_sha256"]}
    (ROOT / "reports/tables/pilot_reproducibility.json").write_text(json.dumps(proof, indent=2), encoding="utf-8")
    if before != after or summary["cache_hits"] != summary["participants"]:
        raise AssertionError("Warm-cache export changed scientific tables or missed a cache entry")
    print(json.dumps(proof, indent=2))


if __name__ == "__main__":
    main()
