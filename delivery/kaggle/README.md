# Running Injury Clinic Kinematic Technical Pilot

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
