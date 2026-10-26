# Limitations

- Cross-sectional clinical-episode measurements cannot establish prospective injury risk, temporal causation or treatment effects.
- Clinical/research recruitment at one clinic, treadmill familiarity, standardized footwear and self-selected speed limit population and overground generalization.
- Speed, age, self-reported gender, anthropometry, experience and activity level may confound group differences. Gender is not a validated sex variable.
- Multiple task rows and timestamped collections per person are dependent. A timestamp is not a proven separate clinical visit. Injury status can change.
- Clinical labels include nonspecific pain, Other, form placeholders, free text, spelling variants and primary/secondary injuries. Injury-positive severity is not equivalent to a verified specific diagnosis.
- Missing duration, race-history and experience fields may be selective or structurally inapplicable. Raw missingness and plausibility exclusions are different.
- Implausible values are flagged with broad engineering screens. Their true corrected values and exact sentinel semantics are unknown.
- Raw archive membership does not demonstrate available/usable running kinematics. Milestone 1 inspected ten ingestion examples; the subsequent technical pilot inspected 30 separately selected running observations. These samples do not establish full-cohort QC or usable cycle counts. Source-defined scalar extraction and structural/internal-consistency checks do not independently validate historical event detection or joint-angle reconstruction.
- Equipment, sample rate and anatomical marker availability can differ. Structural marker checks cannot replace calibration, event and waveform validation.
- Diagnosis sample-size screening is descriptive. No power/precision or causal-identification claim follows from an n30 flag.
- Contralateral limbs cannot automatically serve as healthy references. Dataset percentiles are not external clinical norms.
- External data use separate participants/protocols and may overlap the RIC source. No unverified row-level merge, filling of missing patient fields or independent-validation claim is permitted.
- Official processing source is inspected but not executed in MATLAB. Tutorial and port parity, units/sign conventions and full motion QC remain future reviewed work.
