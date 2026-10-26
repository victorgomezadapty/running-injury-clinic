# External metadata profile: BMC–RIC

Generated offline by `python scripts/profile_external.py`. Source files are checked against the pinned Git blob hashes before analysis. Commit: `21f5a4607c9e4f6a365caa6e6d85c96787517844`. This analysis uses metadata only.

| Group | source_rows | participants | speed_min | speed_max | row_weighted_speed_mean |
| --- | --- | --- | --- | --- | --- |
| BMC | 791 | 23 | 2.50 | 2.50 | 2.50 |
| RIC | 823 | 23 | 2.43 | 2.57 | 2.49 |

There are 46 composite participant identifiers and only 23 unqualified Subject numbers. Using Subject alone would merge different people. The source metadata have 0 missing cells and 0 duplicate Group–Subject–Trial rows. Demographic consistency warnings occur in 0 participants.

Rows labelled Trial are normalized waveform records in the upstream notebook, which loads 101 × 9 arrays and takes a median over records per Group–Subject. They are not evidence of separate clinical sessions. The source notebook was inspected but not executed, and waveforms were not downloaded. No injury or gender field and no crosswalk to Calgary sub_id are available.

The participant summary uses one row per Group–Subject, first recorded age/height/mass after checking within-person consistency, and median speed across source records. Thus participants with more records do not acquire more weight in the participant numeric summary. The group table explicitly labels its separate row-weighted speed mean. Units are based on the companion study; metadata labels alone do not establish harmonized biomechanics.

No primary/external rows are merged. Possible overlap of the RIC subset with the main dataset remains unresolved. See `../docs/external_compatibility.md` before reuse.
