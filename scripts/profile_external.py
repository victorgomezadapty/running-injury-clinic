"""Profile the separately namespaced BMC–RIC metadata offline. No waveforms."""
from pathlib import Path
import json
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.acquire_external import COMMIT, FILES, git_blob_sha
from src.analysis.metadata_summary import markdown_table


def load_external(root=ROOT):
    directory = Path(root) / "data/external/bmc_ric"
    for relative, expected in FILES.items():
        path = directory / relative
        if git_blob_sha(path.read_bytes()) != expected:
            raise ValueError(f"External source integrity mismatch: {relative}")
    data = pd.read_csv(directory / "data/metadata.txt", sep="\t", index_col=0,
                       dtype={"Group": "string", "Subject": "string", "Trial": "string", "Filename": "string"})
    expected_columns = ["Group", "Subject", "Trial", "Filename", "Speed", "Age", "Height", "Mass"]
    if list(data.columns) != expected_columns:
        raise ValueError("Unexpected external source schema")
    data["source_id"] = "bmc_ric_" + COMMIT[:8]
    data["external_participant_id"] = data.Group + ":" + data.Subject
    return data


def main():
    data = load_external()
    output = ROOT / "reports/tables"
    output.mkdir(parents=True, exist_ok=True)
    groups = data.groupby("Group").agg(source_rows=("Subject", "size"), participants=("external_participant_id", "nunique"), speed_min=("Speed", "min"), speed_max=("Speed", "max"), row_weighted_speed_mean=("Speed", "mean")).reset_index()
    persons = data.groupby(["Group", "external_participant_id"], sort=True).agg(source_rows=("Trial", "size"), age=("Age", "first"), height_cm=("Height", "first"), mass_kg=("Mass", "first"), median_speed_m_s=("Speed", "median")).reset_index()
    consistency = data.groupby("external_participant_id")[["Age", "Height", "Mass"]].nunique(dropna=False)
    consistency["demographics_vary_within_id"] = consistency.gt(1).any(axis=1)
    groups.to_csv(output / "external_group_summary.csv", index=False)
    persons.to_csv(output / "external_participant_summary.csv", index=False)
    consistency.reset_index().to_csv(output / "external_demographic_consistency.csv", index=False)
    statistics = persons.groupby("Group")[["age", "height_cm", "mass_kg", "median_speed_m_s"]].agg(["count", "mean", "std", "min", "median", "max"])
    statistics.to_csv(output / "external_participant_numeric.csv")
    profile = {
        "source": "regifukuchi/BMC-RIC-running-biomechanics", "commit": COMMIT, "license": "CC BY 4.0",
        "source_rows": len(data), "source_columns": ["Group", "Subject", "Trial", "Filename", "Speed", "Age", "Height", "Mass"],
        "source_missing_cells": int(data.iloc[:, :8].isna().sum().sum()),
        "unique_composite_participants": int(data.external_participant_id.nunique()),
        "unique_unqualified_subject_numbers": int(data.Subject.nunique()),
        "groups": groups.to_dict("records"),
        "duplicate_group_subject_trial_rows": int(data.duplicated(["Group", "Subject", "Trial"]).sum()),
        "participants_with_varying_demographics": int(consistency.demographics_vary_within_id.sum()),
        "trial_unit": "source records labelled Trial, corresponding to normalized waveform records in upstream notebook; not independent people or established clinical sessions",
        "primary_dataset_crosswalk": None, "possible_ric_overlap": "unresolved", "waveforms_acquired": False,
        "upstream_notebook_executed": False, "pooled_with_primary": False,
    }
    (output / "external_metadata_profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
    text = f"""# External metadata profile: BMC–RIC

Generated offline by `python scripts/profile_external.py`. Source files are checked against the pinned Git blob hashes before analysis. Commit: `{COMMIT}`. This analysis uses metadata only.

{markdown_table(groups)}

There are {profile['unique_composite_participants']} composite participant identifiers and only {profile['unique_unqualified_subject_numbers']} unqualified Subject numbers. Using Subject alone would merge different people. The source metadata have {profile['source_missing_cells']} missing cells and {profile['duplicate_group_subject_trial_rows']} duplicate Group–Subject–Trial rows. Demographic consistency warnings occur in {profile['participants_with_varying_demographics']} participants.

Rows labelled Trial are normalized waveform records in the upstream notebook, which loads 101 × 9 arrays and takes a median over records per Group–Subject. They are not evidence of separate clinical sessions. The source notebook was inspected but not executed, and waveforms were not downloaded. No injury or gender field and no crosswalk to Calgary sub_id are available.

The participant summary uses one row per Group–Subject, first recorded age/height/mass after checking within-person consistency, and median speed across source records. Thus participants with more records do not acquire more weight in the participant numeric summary. The group table explicitly labels its separate row-weighted speed mean. Units are based on the companion study; metadata labels alone do not establish harmonized biomechanics.

No primary/external rows are merged. Possible overlap of the RIC subset with the main dataset remains unresolved. See `../docs/external_compatibility.md` before reuse.
"""
    (ROOT / "reports/external_metadata_summary.md").write_text(text, encoding="utf-8")
    print(json.dumps(profile, indent=2))


if __name__ == "__main__":
    main()
