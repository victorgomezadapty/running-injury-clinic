# Biomechanics conventions and ingestion boundaries

Authoritative sources: original README and `Supplemental_materials/Code/gait_kinematics.m`, `gait_steps.m`, `processing_code_example.m`, retrieved unchanged under the upstream MIT licence. Associated [data descriptor](https://doi.org/10.1038/s41597-024-04011-7).

## Verified JSON structure

Actual top-level fields in the ingestion sample are `hz_w`, `hz_r`, `walking`, `running`, `joints`, `neutral`, `dv_w`, `dv_r`. Tasks are identified from their explicit branches and metadata source CSV, not inferred from a speed cutoff. An absent task can be an empty list, with empty hz and dv fields. Sampling rates must be checked per task, not assumed constant across subjects.

The first sampled dynamic marker arrays are frames × 3, e.g. 4000 × 3. Static anatomical marker vectors are length 3 in the JSON representation. The official MATLAB wrapper explicitly transposes static `joints` and `neutral` fields before reconstruction. Our loader inventories native shapes and does not transpose or rotate them. `joints` contains anatomical marker locations rather than literal computed joint centres. `neutral` holds the static tracking markers. `dv_r` and `dv_w` are nested descriptive-variable structures, including left/right fields in the sample. Field presence is not confirmation of correct units, sign, reliability or valid events.

## Coordinate systems

The official kinematics code comments describe the original Bonita lab axes as X to the subject's right, Y forward and Z upward, then a switched laboratory convention with X to the right, Y upward and Z opposite walking direction. Segment axes are described as X anterior, Y upward and Z to the subject's right. These statements are provenance from the code; this milestone does not execute a transformation or assert that every raw JSON should be independently rotated again. Confirm the upstream transformation path on a stratified sample before any port. Do not silently change conventions or mix segment/laboratory axes.

Joint rotations, positive signs, left/right harmonization, reference posture, units of every descriptive variable, event detection and stance/cycle normalization must be verified against the official processing code and relevant tutorials in Phase 2. No generic ankle/hip sign convention is substituted here. Existing processed values should not be filtered, converted or re-normalized without evidence of their upstream definitions.

The technical pilot now checks the source definitions/units of 13 selected scalar fields per side; see `official_processing_review.md`. The source normalizes touchdown-to-toe-off into 101 stance samples, with feature-specific indexed windows. That source-definition review does not establish independent reconstruction or event parity for historical JSONs. No coordinate changes or sign transformations are performed during extraction.

## Quality control

The inspector inventories every marker field, frame count, shape, non-finite values and zero XYZ frames. Its expected tracking-field list reflects seven segments with four upstream marker slots; a fourth marker can be constructed in upstream processing, so an absent slot is a review flag, not automatic clinical rejection. It also records fields whose names suggest embedded warnings/errors/quality flags. No such field should be invented when absent. Gait-event warnings can be outputs of `gait_steps` rather than stored JSON fields.

Current checks do not assess marker-label swaps, calibration geometry, noise, event accuracy or sufficient valid cycles. Structural success must not be reported as complete biomechanical validity. No injured/contralateral limb reassignment is performed, and the contralateral side is not treated as a healthy control.
