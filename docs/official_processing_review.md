# Official processing review for the technical pilot

Source: Figshare 24255795, version 1, Supplemental_materials.zip. The unchanged official MATLAB code, tutorials 1–2 and small event-model files are stored in `data/raw/official_code/`. The original licence is retained. Tutorials were inspected through their `matlab/document.xml`; they were not executed in MATLAB. `scripts/run_pilot.py` records their SHA-256 and recreates the readable text in `data/interim/official_tutorials/`.

## Verified conventions

- Tutorial 1 demonstrates reading discrete values directly from `dv_r.left/right` and distinguishes running/walking with source metadata. Its temporary names ending in `_hz` do not define the unit: plots label STRIDE_RATE as strides/min, agreeing with the `60*hz/diff(TD)` implementation.
- Tutorial 2 describes the official `gait_kinematics` → `gait_steps` sequence. JSON static vectors are transposed for MATLAB; existing Python source values are not reoriented. The example's matching/age/exclusion rules are instructional and are not adopted as the primary injury cohort definition.
- `gait_kinematics.m`, lines 596–604, converts angular outputs from radians to degrees. The pilot preserves stored degree values; it does not reapply this conversion.
- `gait_steps.m`, lines 671 onward, normalizes touchdown-to-toe-off into 101 samples, so these are stance waveforms. Swing and stride intervals have separate definitions.
- Source matrix row 23 uses the first 70 stance samples for knee flexion; row 43 uses the first 60 for hip adduction. The exact indexed windows are recorded rather than replacing them with global cycle peaks.
- Left/right formulas are not universally identical. In particular, peak knee flexion includes a negative sign and rotation-plane interpretation depends on source conventions. No absolute value, generic side sign-flip or injured-limb remapping is applied.

## Placeholder and version handling

`DISCRETE_VARIABLES` starts as a zero matrix. Some labelled rows are never assigned in the reviewed code. The registry builder identifies those rows from active assignments and excludes their names. This supports identifying reserved output slots; it does not imply that every zero in an implemented field is invalid, or that the supplied code version exactly matches all historical JSON processing versions. Exactly-zero selected angles are preserved as source values and held for review. Unassigned current-code fields with nonzero stored values, if observed, are explicitly counted as a version/semantics discrepancy.

The whitelist contains 13 types of features per side: nine joint-angle peaks and stride rate, stride length, swing time and stance time. Every entry records its matrix row, exact source lines/expressions, unit, time window and source SHA-256. Step width, timing placeholders, excursions and angular velocities are not added to this first selection. This is a deliberate scope limit, not a statement that all omitted fields lack scientific value.

## Quality and reconstruction boundaries

The JSONs expose marker arrays and aggregate descriptive values. They do not provide the independently validated touchdown/toe-off arrays, event-method flags, rejected/retained cycles and version provenance needed to validate event detection from the stored aggregates alone. The official function returns those outputs during execution. They must not be inferred as observed valid cycle counts from stride rate multiplied by recording duration.

This pilot checks source integrity, structural completeness, static/cluster geometry and internal temporal consistency. A 5% relative-MAD or temporal-residual threshold is an engineering review trigger, not a validated clinical limit. Source values remain available in the long audit table; provisional analysis values are masked while flags await review. Neither structural success nor an intact source scalar establishes independent reconstruction accuracy or clinical diagnostic validity.

Further verification should run the official workflow in a compatible MATLAB environment or compare an equivalent implementation against official reference outputs. Only then can explicit usable-cycle criteria and downstream waveform analyses be validated. No custom reconstruction, hypothesis testing, clustering or injury-status model is run during this pilot.

## Event/cycle reprocessing handoff

The supplementary `tutorial_2.mat` and `tutorial_4_cache.mat` have now been acquired and integrity-checked. They contain MATLAB tables/statistic caches, not per-trial touchdown/toe-off arrays. SciPy reports the saved MATLAB tables as opaque objects. No MATLAB or Octave executable is present in the current environment, and the official classifier is a MATLAB `gaitClass` object. A fixed-manifest MATLAB runner is available at `scripts/validate_official_events.m`; its status and expected outputs are documented in `reports/milestone_03_official_events_validation.md`. No event or cycle parity result is claimed until that runner executes successfully.
