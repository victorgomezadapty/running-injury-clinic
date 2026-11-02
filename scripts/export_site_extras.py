"""Export small aggregate tables used by the website's design-pass sections.

Reads only committed aggregate files in reports/tables (no participant rows)
and writes site/data/extras.json. Run: python scripts/export_site_extras.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "reports" / "tables"
OUT = ROOT / "site" / "data" / "extras.json"


def rows(name: str) -> list[dict[str, str]]:
    with (TABLES / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    balance = [
        {
            "variable": r["variable"],
            "healthy_n": int(r["healthy_n"]),
            "injured_n": int(r["injured_n"]),
            "healthy_mean": round(float(r["healthy_mean"]), 3),
            "injured_mean": round(float(r["injured_mean"]), 3),
            "smd": round(float(r["standardized_mean_difference"]), 3),
        }
        for r in rows("readiness_covariate_balance.csv")
    ]
    speed = [
        {
            "status": r["injury_status"],
            "participants": int(r["participants"]),
            "inside": int(r["inside_shared_central_range"]),
            "inside_percent": round(float(r["inside_percent"]), 1),
            "lower_m_s": round(float(r["central_lower_m_s"]), 2),
            "upper_m_s": round(float(r["central_upper_m_s"]), 2),
        }
        for r in rows("readiness_speed_support.csv")
    ]
    summary = {r["measure"]: {"n": int(r["n"]), "denominator": int(r["denominator"])} for r in rows("repeated_record_audit_summary.csv")}
    endpoints = [
        {"first": r["first_status"], "latest": r["latest_status"], "participants": int(r["participants"])}
        for r in rows("repeated_record_status_endpoint_matrix.csv")
    ]
    data = {
        "source": "reports/tables (readiness_covariate_balance, readiness_speed_support, repeated_record_audit_summary, repeated_record_status_endpoint_matrix)",
        "covariate_balance": balance,
        "speed_support": speed,
        "repeated_summary": summary,
        "status_endpoints": endpoints,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
