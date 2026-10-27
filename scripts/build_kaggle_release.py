"""Build the small, attributed, identifier-stripped Kaggle pilot package."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/pilot_features_wide.csv"
OUT = ROOT / "delivery/kaggle"
FEATURES = [
    "ANKLE_DF_PEAK_ANGLE", "ANKLE_EVE_PEAK_ANGLE", "ANKLE_ROT_PEAK_ANGLE",
    "HIP_ADD_PEAK_ANGLE", "HIP_EXT_PEAK_ANGLE", "HIP_ROT_PEAK_ANGLE",
    "KNEE_ADD_PEAK_ANGLE", "KNEE_FLEX_PEAK_ANGLE", "KNEE_ROT_PEAK_ANGLE",
    "STANCE_TIME", "STRIDE_LENGTH", "STRIDE_RATE", "SWING_TIME",
]
UNITS = {
    "ANKLE_DF_PEAK_ANGLE": "deg", "ANKLE_EVE_PEAK_ANGLE": "deg",
    "ANKLE_ROT_PEAK_ANGLE": "deg", "HIP_ADD_PEAK_ANGLE": "deg",
    "HIP_EXT_PEAK_ANGLE": "deg", "HIP_ROT_PEAK_ANGLE": "deg",
    "KNEE_ADD_PEAK_ANGLE": "deg", "KNEE_FLEX_PEAK_ANGLE": "deg",
    "KNEE_ROT_PEAK_ANGLE": "deg", "STANCE_TIME": "s",
    "STRIDE_LENGTH": "m", "STRIDE_RATE": "strides/min", "SWING_TIME": "s",
}


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"Missing pilot output: {SOURCE}")
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    if len(source_rows) != 30:
        raise SystemExit(f"Expected the fixed 30-person technical pilot; found {len(source_rows)} rows")

    # Canonical feature content determines only a stable, opaque project row key.
    # Source identifiers, filenames, injury location and raw trajectories are never copied.
    prepared = []
    for row in source_rows:
        status = row.get("injury_status", "").strip().lower()
        if status not in {"healthy", "injured"}:
            raise SystemExit(f"Unexpected current-status value: {status!r}")
        features = {}
        for side in ("left", "right"):
            for feature in FEATURES:
                key = f"{side}__{feature}"
                raw = row.get(key, "").strip()
                if not raw:
                    raise SystemExit(f"Missing source-provided pilot feature: {key}")
                value = float(raw)
                if not (value == value and abs(value) != float("inf")):
                    raise SystemExit(f"Non-finite value in {key}")
                features[f"{side}_{feature.lower()}"] = format(value, ".15g")
        content = json.dumps([status, row.get("gender", ""), row.get("speed_m_s", ""), features], sort_keys=True)
        prepared.append((hashlib.sha256(content.encode()).hexdigest(), row, features, status))

    prepared.sort(key=lambda item: item[0])
    OUT.mkdir(parents=True, exist_ok=True)
    fieldnames = ["pilot_case_id", "current_injury_status_source", "gender_as_reported", "running_speed_m_s"]
    fieldnames += [f"{side}_{feature.lower()}" for side in ("left", "right") for feature in FEATURES]
    with (OUT / "pilot_bilateral_features.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index, (_, row, features, status) in enumerate(prepared, start=1):
            writer.writerow({
                "pilot_case_id": f"pilot_{index:03d}",
                "current_injury_status_source": status,
                "gender_as_reported": row.get("gender", ""),
                "running_speed_m_s": format(float(row["speed_m_s"]), ".15g"),
                **features,
            })

    # A field-level dictionary is supplied for every released column.
    dictionary_rows = [
        ("pilot_case_id", "Project-generated opaque row label; not a source participant identifier", "text"),
        ("current_injury_status_source", "Current status category as defined from the source metadata; not a future outcome", "category"),
        ("gender_as_reported", "Source self-reported gender category", "category"),
        ("running_speed_m_s", "Source running speed", "m/s"),
    ]
    for side in ("left", "right"):
        for feature in FEATURES:
            dictionary_rows.append((f"{side}_{feature.lower()}", f"Source-provided {side}-side discrete summary: {feature}; see project registry for phase/sign details", UNITS[feature]))
    with (OUT / "data_dictionary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["column", "definition", "unit_or_type"])
        writer.writerows(dictionary_rows)

    metadata = {
        "title": "Running Injury Clinic Kinematic Technical Pilot",
        "id": "vctorandrsgmezlpez/running-injury-clinic-kinematic-pilot",
        "licenses": [{"name": "CC-BY-4.0"}],
    }
    (OUT / "dataset-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    # Remove a plural-name file created while checking CLI-version differences.
    (OUT / "datasets-metadata.json").unlink(missing_ok=True)
    attribution = """# Running Injury Clinic Kinematic Technical Pilot

This is a fixed **30-person technical pilot**, selected for engineering checks (15 source-labeled healthy; 15 source-labeled injured). It is not a representative cohort, validated biomechanical analysis, clinical benchmark or model-training recommendation.

## Contents

- `pilot_bilateral_features.csv`: 30 project-pseudonymized rows; source status, source-reported gender, running speed, and 13 source-provided discrete summaries for each side (780 scalars total).
- `data_dictionary.csv`: definitions and units for each released field.

Source participant identifiers, source filenames, exact injury side/joint labels and raw trajectories are omitted. The values remain linkable in principle to the public upstream data; opaque case labels are not a guarantee of anonymity.

## Validation status

All 30 pilot JSON files passed structural checks. The 780 feature values are copied from source-provided `dv_r` summaries. Independent official touchdown/toe-off and normalized-cycle reprocessing is pending execution of the supplied MATLAB workflow. No group-difference analysis or prediction result is claimed. See the project [Milestone 3 status](https://github.com/victorgomezadapty/running-injury-clinic/blob/main/reports/milestone_03_official_events_validation.md).

## Reuse and attribution

Adapted from Ferber R, Brett K, Fukuchi R, Hettinga B, Osis S, *Running Injury Clinic Kinematic Dataset*, version 1 (2024), https://doi.org/10.25452/figshare.plus.24255795.v1, licensed CC BY 4.0. Changes: fixed pilot selection, source-ID removal, opaque row IDs, selected bilateral fields, column naming and packaging. Please cite the original dataset and descriptor (https://doi.org/10.1038/s41597-024-04011-7), link CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), and follow the source consent context. The dataset descriptor article has a separate publication licence.

## Reproduce the package

From the project repository, run `python scripts/build_kaggle_release.py`. This deterministically rebuilds the table and metadata from the local processed pilot CSV. To reacquire/rebuild the pilot, follow the repository README and data provenance instructions.

Project: https://running-injury-clinic.vercel.app · Source code: https://github.com/victorgomezadapty/running-injury-clinic
"""
    (OUT / "README.md").write_text(attribution, encoding="utf-8")
    print(f"Built {OUT} with {len(prepared)} rows, {len(fieldnames) - 4} features, and no source participant IDs/filenames.")


if __name__ == "__main__":
    main()
