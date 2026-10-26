# Reproducible candidate running cohort

Implementation: `src/data/load_metadata.py`, `src/data/validation.py`, and `scripts/run_milestone1.py`. Every running source row receives a flag/reason in `data/processed/running_cohort_audit.csv`; selected participant rows are in `candidate_running_participants.csv`. Observed counts are generated in `reports/tables/cohort_counts.json`.

## Units and keys

- Person: exact source `sub_id`, loaded as text, never an integer feature.
- Task observation: participant + filename + running/walking task.
- JSON collection: participant + filename. Both task observations can share this key.
- Session time: parsed CSV `datestring`; if missing/NaT, recover from the exact `%Y%m%dT%H%M%S.json` filename and record `session_time_source=filename_recovery`. Original text remains unchanged. Any CSV/filename disagreement is flagged. Distinct timestamps and collection days are reported separately; neither is guaranteed to equal an independently documented clinical visit.

## Injury status

Canonical text is stripped/lowercased in appended columns. Empty, NaN, NaT, NULL, N/A and NA are missing. Raw spellings remain intact.

| Derived category | Rule |
| --- | --- |
| healthy | severity explicitly No injury; no primary or secondary injury location/diagnosis evidence |
| injured | severity explicitly training with pain, training volume/intensity affected, or two workouts missed |
| discordant | severity No injury but primary/secondary injury evidence present |
| unknown | missing or unrecognized severity, regardless of other injury evidence |

Blank locations and variants `No Injury` / `No injury,No injury` count as no recorded injury location. A diagnosis value `No injury` likewise carries no diagnosis evidence. The source README's control definition informs these rules; additionally checking secondary fields is a deliberately conservative extension. A secondary label can exclude a record from controls, but side alone cannot create an injury. InjSide sometimes says Right in records with no injury; do not interpret that as a clinically injured right limb. Positive self-reported severity is not proof of a specific clinician-confirmed diagnosis. Preserve specific-diagnosis and unspecified-pain groups separately.

## Inclusion and selection

1. The row comes from the actual running CSV, with a valid participant/filename/time identity.
2. Running speed is finite and positive. Do not impose a universal speed threshold to relabel walking/running.
3. Status is resolved as healthy or injured; discordant/unknown are excluded from the primary candidate and retained for sensitivity work.
4. Exact participant-file member appears in the pinned raw ZIP directory.
5. Select each participant's earliest eligible running row, breaking timestamp ties by filename. Do not choose their fastest trial or most severe injury.

Descriptive tables use the earliest running observation BEFORE candidate exclusions so missingness and discordance remain visible. Candidate counts therefore have a different denominator. Every excluded observation remains in the audit with semicolon-separated reasons. A participant with an excluded early row can have a later eligible row selected.

Missing demographics do not automatically exclude a person from the unadjusted metadata candidate. An optional complete-covariate flag requires plausible age/height/weight/experience and recorded female/male gender and recreational/competitive level. It is an exploratory complete-case subset, not a recommended final missing-data strategy; it excludes missing/unknown values and is unsuitable for generalizing gender categories beyond the observed data.

## QC screens and unresolved eligibility

Broad data-entry plausibility screens: age 18–100 years; height 100–230 cm; weight 30–250 kg; running experience 0–100 years and no greater than age; injury duration 0–36,500 days and no greater than recorded age × 365.25; races/year 0–365. These are predeclared engineering screens, not clinical thresholds. All source values remain unchanged. Numeric parsing failure becomes missing in appended numeric/analysis fields; flagged numeric entries are masked only in analysis fields. No imputation, winsorization or guessed unit conversion is applied. Age 255 and experience 999 are flagged as implausible; their exact upstream meaning is not assumed.

The sampled JSONs receive structural checks for task availability, hz, marker shapes, absent expected fields, non-finite values, zero trajectories and available calculated fields. A structural pass is not proof of valid joint waveforms or gait events. Only a small convenience sample is audited. **The final usable-running observation and participant counts remain unknown until all candidate raw trials satisfy an agreed biomechanical QC protocol.** Full-cohort gait-event, usable-cycle, static-calibration and per-variable criteria belong to a later reviewed stage.

## Diagnosis feasibility

Report exact source labels, then lowercase and apply only the README's named alias merges (OA variants including the documented misspelling, ITBS, PFPS). Other spelling variants stay separate for review. Primary and secondary diagnoses are counted as unique participant–diagnosis pairs across injury-positive running observations. Counts are nonadditive. Generic pain, other, form placeholders and unspecified tendonitis do not create specific-diagnosis groups. N≥30 is only a descriptive shortlist, not a sufficient-sample-size claim. Future power/precision, speed overlap and control availability must determine feasibility.
