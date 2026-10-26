# Literature review and discussion

**Search date:** 26 October 2026. **Purpose:** focused narrative review to justify the research question and analysis safeguards; this is not a registered systematic review or an exhaustive evidence synthesis.

## Search and selection

Targeted searches were run in PubMed and publisher/journal records for running-related injury, running biomechanics, prospective cohorts, systematic reviews/meta-analyses, and running speed/kinematics. We prioritized peer-reviewed human studies that directly informed one of four design decisions: distinguish current injury status from future incidence; avoid treating a single gait variable as a universal marker; describe population and diagnosis; and account for speed. We also included the source dataset descriptor. DOI and PubMed links are supplied below. Search terms, eligibility and scope are deliberately reported so the discussion is auditable, but no formal dual-reviewer selection, protocol registration, or risk-of-bias update was performed.

## What the evidence supports

### There is no established universal running-injury gait signature

Lopes, Mascarinas and Hespanhol synthesized 82 studies involving 5,465 runners; 51 studies contributed to quantitative analyses of 11 biomechanical variables. Peak hip adduction was the only pooled variable associated with injury, and that estimate was strongly influenced by two of five contributing studies. The review judged the overall evidence minimal and emphasized heterogeneity in testing conditions and variable definitions. This supports using a predeclared source-defined feature registry and treating any later association as a hypothesis requiring replication, rather than selecting features after observing group differences.

Vannatta, Heinert and Kernozek reviewed prospective studies and identified 13 eligible reports but only five unique running samples. Their pooled evidence differed across sex and competitive level; moderate evidence for some associations was specific to female recreational runners. This cautions against assuming that an association transfers across runner populations. The current source cohort is not a substitute for those stratified, prospective designs.

### Current status and future incidence are different outcomes

The 52-week prospective cohort by Ramskov and colleagues followed 224 injury-free recreational runners and recorded medically diagnosed injuries. It reported associations for late timing of maximal rearfoot eversion and a low hip-abductor-to-adductor strength ratio. These observations are useful context, not validation of the present analysis: the population, baseline state, follow-up, clinical outcome and exposure definitions differ. The current dataset records contemporaneous self-reported injury status, so it cannot establish temporal order or future risk.

### Running speed can change the measured movement

Orendurff and colleagues experimentally compared four running speeds in recreational runners and observed speed-related changes in peak lower-limb kinematic and kinetic measures. Speed is therefore not merely a descriptive convenience. The candidate groups in this dataset have different recorded mean speeds (2.739 m/s in healthy candidates and 2.554 m/s in injured candidates; metadata summary). Any eventual biomechanical comparison should show speed distributions, inspect overlap, predefine a speed-aware analysis and avoid extrapolating outside common support. Adjustment cannot repair poor overlap or an unvalidated outcome.

### Technical and clinical phenotyping need separate validation

The source dataset descriptor documents a large archive of clinical metadata and 3D running kinematics (Ferber et al., 2024). The present pilot checks JSON structure and summarizes 13 bilateral source-provided discrete variables. These checks do not verify the timing of touchdown/toe-off, the retained normalized cycles, reconstructed joint angles or clinical measurement validity. Reprocessing against the supplied MATLAB implementation can establish computational parity only after the official workflow executes successfully; comparison to manually adjudicated events or an independent reference would still be required for event accuracy.

## Implications for this project

1. Keep the target explicit: **reported current injury status**, not incidence, prognosis or causal risk.
2. Do not widen the biomechanical cohort until the official event/cycle processing runner has been executed, its outputs inspected, and scalar discrepancies explained.
3. Report source-defined feature names, units, sign conventions, phase windows, missingness, event quality and trial-to-participant aggregation.
4. Treat the 30-person balanced pilot as engineering selection, not a representative sample. Do not report its class balance as population prevalence or use it to estimate clinical performance.
5. Report speed and covariate overlap before models. If overlap is inadequate, restrict the estimand or describe the limitation rather than relying on model adjustment alone.
6. Separate exploratory group contrasts from confirmatory inference; account for repeated trials within participant and multiple feature testing.
7. Use diagnosis-specific phenotypes only when the source labels, counts and definition support them. Self-reported current status is not equivalent to a verified clinician diagnosis.
8. Do not produce clinical cutoffs, screening claims, treatment advice or future-risk claims from these data.

## Limitations of this review

This is a focused narrative review, not a PRISMA-compliant systematic review. Searches were targeted rather than exhaustive and were not independently screened. The cited studies use different populations, case definitions, measurement systems and exposure phases. Their findings provide rationale and context; they do not establish an effect size for this dataset. The cohort speed summaries are unadjusted descriptive statistics and should not be interpreted as an injury effect.

## References

1. Ferber R, Brett K, Fukuchi R, Hettinga B, Osis S. A dataset of running biomechanics and clinical measures of runners with and without running-related injuries. *Scientific Data*. 2024. [https://doi.org/10.1038/s41597-024-04011-7](https://doi.org/10.1038/s41597-024-04011-7).
2. Ferber R, Brett K, Fukuchi R, Hettinga B, Osis S. Running Injury Clinic Kinematic Dataset, version 1. Figshare. [https://doi.org/10.25452/figshare.plus.24255795.v1](https://doi.org/10.25452/figshare.plus.24255795.v1). Dataset licence: CC BY 4.0.
3. Lopes AD, Mascarinas A, Hespanhol L. Are alterations in running biomechanics associated with running injuries? A systematic review with meta-analysis. *Brazilian Journal of Physical Therapy*. 2023;27(4):100538. [https://doi.org/10.1016/j.bjpt.2023.100538](https://doi.org/10.1016/j.bjpt.2023.100538) · [PubMed](https://pubmed.ncbi.nlm.nih.gov/37651773/).
4. Vannatta CN, Heinert BL, Kernozek TW. Biomechanical risk factors for running-related injury differ by sample population: a systematic review and meta-analysis. *Clinical Biomechanics*. 2020;75:104991. [https://doi.org/10.1016/j.clinbiomech.2020.104991](https://doi.org/10.1016/j.clinbiomech.2020.104991) · [PubMed](https://pubmed.ncbi.nlm.nih.gov/32203864/).
5. Ramskov D, et al. Associations between biomechanical and clinical/anthropometrical factors and running-related injuries among recreational runners: a 52-week prospective cohort study. *Injury Epidemiology*. 2020. [https://doi.org/10.1186/s40621-020-00237-2](https://doi.org/10.1186/s40621-020-00237-2) · [Full text](https://injepijournal.biomedcentral.com/articles/10.1186/s40621-020-00237-2).
6. Orendurff MS, Kobayashi T, Tulchin-Francis K, et al. A little bit faster: lower extremity joint kinematics and kinetics as recreational runners achieve faster speeds. *Journal of Biomechanics*. 2018;71:167–175. [https://doi.org/10.1016/j.jbiomech.2018.02.010](https://doi.org/10.1016/j.jbiomech.2018.02.010) · [PubMed](https://pubmed.ncbi.nlm.nih.gov/29472010/).
7. Wolski A, et al. Utilising inertial measurement units and force-velocity profiling to explore sprint injury risk: a feasibility study. *Sensors*. 2025;25(5):1518. [https://doi.org/10.3390/s25051518](https://doi.org/10.3390/s25051518).
