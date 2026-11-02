"""Design-pass checks for the static site extras (no network access needed)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRAS = json.loads((ROOT / "site" / "data" / "extras.json").read_text(encoding="utf-8"))


def test_balance_matches_cohort_story():
    smd = {row["variable"]: row["smd"] for row in EXTRAS["covariate_balance"]}
    assert round(smd["speed_m_s"], 2) == -0.51
    assert round(smd["age_analysis"], 2) == 0.32
    assert all(abs(smd[k]) < 0.2 for k in ("Height_analysis", "Weight_analysis", "YrsRunning_analysis"))


def test_speed_overlap_counts():
    support = {row["status"]: row for row in EXTRAS["speed_support"]}
    assert support["healthy"]["participants"] + support["injured"]["participants"] == 1257
    assert round(support["healthy"]["inside_percent"]) == 82
    assert round(support["injured"]["inside_percent"]) == 80


def test_status_matrix_totals():
    cells = EXTRAS["status_endpoints"]
    assert sum(c["participants"] for c in cells) == 209
    changed = sum(c["participants"] for c in cells if c["first"] != c["latest"])
    assert changed == 20 == EXTRAS["repeated_summary"]["repeated_participants_with_different_earliest_latest_status"]["n"]


def test_site_has_no_long_dashes_and_no_tiny_fonts():
    html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    assert not re.search("[\u2013\u2014]", html)
    css = (ROOT / "site" / "styles.css").read_text(encoding="utf-8")
    assert not re.search(r"font(?:-size)?:(?:\d{3} )?(?:[0-9]|1[01])(?:\.\d+)?px", css)
