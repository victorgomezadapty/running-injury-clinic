# Primary/external compatibility contract

Primary source: [Calgary RIC Figshare v1](https://doi.org/10.25452/figshare.plus.24255795.v1). Complement: official [BMC–RIC supplement](https://github.com/regifukuchi/BMC-RIC-running-biomechanics/tree/21f5a4607c9e4f6a365caa6e6d85c96787517844), CC BY 4.0. The [companion interlaboratory study](https://doi.org/10.1123/jab.2024-0007) motivates checks of laboratory/protocol effects. No harmonized waveform dataset is created in Milestone 1.

| Construct | Primary RIC | BMC–RIC complement | Current treatment |
| --- | --- | --- | --- |
| Identity | sub_id + filename + task | Group + Subject + Trial | Separate source namespace; no crosswalk |
| Participant | 1,798 overall / 1,402 with running metadata | 23 BMC + 23 RIC composite IDs | Never add external IDs to Calgary counts |
| Observation | task row linked to a timestamped JSON | source Trial row used for normalized waveforms upstream | Do not treat the two row types as equivalent sessions |
| Age | age, years | Age, years | Metadata construct comparison only; preserve source and QC |
| Height | Height, cm | Height, cm | Keep original fields; evaluate plausibility per source |
| Body mass | Weight, kg | Mass, kg | Semantic alias documented, no row-level imputation |
| Speed | speed_r, m/s, self-selected running | Speed, m/s in the companion study | Inspect source-specific distributions and protocol before adjustment |
| Injury | self-reported severity + primary/secondary diagnosis/site | no clinical fields | Cannot augment injury labels or missing history |
| Gender / experience / level | available with missingness | absent in these metadata | No inferred demographic or athletic attributes |
| Movement representation | raw marker JSON plus calculated variables | normalized waveform records in upstream code | No numerical combination before verification |
| Kinematic conventions | official RIC coordinate/event pipeline | study-specific definitions and processing | Confirm axes, signs, units, normalization and phase coverage |

## Identity and dependence

The external source reuses Subject numbers across centres. All downstream grouping must include Group and a source namespace. Repeated Trial rows are dependent observations from a participant. Its RIC cohort could also overlap the primary Calgary resource; a shared lab name or similar age/height/speed is not a crosswalk. Do not match people probabilistically from those attributes, pool rows or claim independent external validation.

## Permitted Milestone 1 operations

Acquire pinned small source files, verify their hashes, inspect the notebook as documentation, inventory actual fields/missingness, create one-row-per-participant metadata summaries, and document compatibility questions. The metadata profile checks whether age/height/mass vary within Group–Subject and reports any inconsistencies before selecting the first demographic record. Speed is summarized by participant median for the participant-level table; raw-row speed summaries are explicitly labelled.

## Later review requirements

Before waveform or feature comparisons, verify joint definitions, laboratory and segment axes, angular signs/units, static references, filtering, normalization to stance versus whole cycle, event definitions, number of valid records and speed protocol. Inspect the official notebook and source methods before building any harmonization layer. An apparent laboratory difference could reflect participants, speed or processing rather than physiology. Evaluate compatible constructs individually; sharing a feature name does not establish equivalence.

The current artefacts are a metadata/compatibility preparation, not evidence of successful pooled kinematic analysis. Future external validation requires independent participants and a predefined target, while prospective injury-risk modeling requires longitudinal outcome data absent here.
