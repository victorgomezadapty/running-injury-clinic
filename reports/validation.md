# Milestone 1 verification

Review date: 25 October 2026 (Asia/Riyadh).

- Primary CSV and README sizes and MD5 match the pinned Figshare v1 file manifest.
- Sampled raw JSON member sizes and CRC match the pinned ZIP directory. Raw SHA-256 values are recorded in the acquisition and run provenance.
- Exact participant/task counts reconcile with 1,798 unique metadata IDs and 2,506 JSON members; every metadata participant-file key is in the archive and no indexed JSON lacks metadata.
- Shared running/walking rows agree on non-speed source metadata. Repeated observations remain grouped by participant.
- Regression checks cover conservative injury status, source-preserving plausibility flags, timestamp recovery, earliest-file selection, exact archive linkage, real JSON task/shape checks and integrity. Run `python -m unittest discover -s tests -v` for current results.
- Notebooks 01–04 execute their actual Python cells with a fresh namespace per notebook. Execution counts/results and `verification.execution_mode=in_process_python` are saved. A Jupyter kernel/UI was not verified; a kernel launch did not complete in the restricted environment, so verification uses the explicit in-process backend.
- All nine notebook files pass nbformat schema validation. Notebooks 05–09 contain no executable analysis. Notebook 04 was activated for the technical pilot after the initial Milestone 1 review.
- Source/scripts/tests compile. All five exported PNGs were visually inspected for readable labels, axes and unclipped content.

These checks verify ingestion and metadata reporting. They do not validate full-cohort gait events, motion quality, joint-angle reconstruction, clinical diagnostic utility or prospective injury risk. The external-source verification is described in its own compatibility/profile files.

## Technical pilot extension

The reviewed 30-person manifest is stored by SHA-256 during selective acquisition. The downloader checks member size/CRC and stores per-file SHA-256. The pilot export rechecks every file hash, exact metadata linkage and all expected participant–file–side–feature keys. Its 780 slots preserve source values with explicit unit/source/quality columns. The wide matrix masks any slots pending technical review rather than overwriting their source values.

Tests cover placeholder exclusion, stride-rate units, preservation of negative knee-flexion values, missing/non-finite/zero fields, absent markers, invalid frequency, temporal inconsistencies and explicit unavailable event validation. A second cached export is compared with the first to confirm deterministic feature and matrix contents. The pilot figure is visually reviewed. These are structural and source-definition checks; the official MATLAB event/reconstruction workflow has not been executed.
