# Running Biomechanics & Injury Phenotyping

**Exploring 3D running kinematics across healthy and clinically injured runners**

Sports Rehabilitation & Human Performance · Physiotherapy Data Science portfolio

Running-related injuries are heterogeneous. This project investigates lower-limb movement patterns associated with current injury status, using the Running Injury Clinic Kinematic Dataset and its clinical metadata. The broader research direction is interpretable biomechanical phenotyping and physiotherapist assessment support.

**Current delivery: Milestone 2 — Technical Biomechanical Feature Pilot.** Read [the pilot report](reports/milestone_02_pilot_summary.md): 30 selected participants, source-defined bilateral features and explicit structural/internal-consistency checks. The pilot preserves original scalars and signs, excludes known placeholder fields and records provenance. The fixed-manifest [official event/cycle reprocessing runner](scripts/validate_official_events.m) is prepared; its execution is pending a MATLAB environment, so event parity and valid cycle counts remain unverified. See the [Milestone 3 status](reports/milestone_03_official_events_validation.md).

The [Milestone 1 baseline](reports/milestone_01_summary.md) documents actual counts, metadata, injury distributions and the candidate cohort. Its ten-file ingestion sample remains separate from the 30-person pilot. The subsequent [readiness review](reports/milestone_01_readiness_review.md) explains the pilot selection and cohort sensitivities.

## Scientific framing

This is a cross-sectional injury-status classification / biomechanical phenotyping resource. It is not initially a future injury prediction dataset. If classification is explored later, the supported statement will be: “the model distinguishes biomechanical patterns associated with current injury status within this dataset.” Clinical diagnostic performance and future injury risk would require different evidence.

- Biomechanical difference ≠ diagnostic biomarker.
- Association ≠ causation.
- Current injury classification ≠ future injury prediction.
- Statistical significance ≠ clinical relevance.
- Group average ≠ individual patient profile.

Analyses must examine speed and other confounders. Any future model validation must split by participant, including all sessions/trials from that participant in one group. Reference percentiles will be called **dataset reference distributions**, not validated clinical thresholds.

## Reproduce Milestone 1

Run commands from this folder. The local `.venv` currently uses the installed scientific Python environment via `--system-site-packages`; for an independent environment use:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/acquire_data.py --sample 10 --index-archives
.venv\Scripts\python.exe scripts/acquire_external.py
.venv\Scripts\python.exe scripts/profile_external.py
.venv\Scripts\python.exe scripts/run_milestone1.py
.venv\Scripts\python.exe -m unittest discover -s tests -p test_ingestion.py -v
.venv\Scripts\python.exe scripts/verify_notebooks.py --metadata-only
```

The acquisition commands need network access. Report generation and tests use local snapshots and run offline. See [acquisition details](docs/dataset_acquisition.md), [cohort rules](docs/cohort_definition.md), [methods](docs/methodology.md) and [coordinate conventions](docs/biomechanics_conventions.md). The external source has its own acquisition script and provenance; see [complementary sources](docs/complementary_sources.md).

## Reproduce the technical pilot

The reviewed manifest is `reports/tables/phase02_pilot_manifest.csv`. It is snapshotted by hash during acquisition. Run:

```powershell
.venv\Scripts\python.exe scripts/acquire_data.py --pilot-manifest reports/tables/phase02_pilot_manifest.csv --tutorials
.venv\Scripts\python.exe scripts/run_pilot.py
.venv\Scripts\python.exe scripts/verify_pilot_cache.py
.venv\Scripts\python.exe scripts/update_pilot_notebook.py
.venv\Scripts\python.exe scripts/verify_notebooks.py
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The first command selectively acquires about 276 MB of compressed JSON members plus official tutorials 1–2 and small event-model files. It reuses existing files and uses bounded HTTP ranges, with no full archive fallback. Subsequent commands are offline. Per-file caches include source, registry, metadata and implementation hashes; re-running exports does not require reparsing trajectories when those inputs are unchanged.

The [official processing review](docs/official_processing_review.md) distinguishes inspected source definitions from independent numerical/event validation. Values exported here are provided `dv_r` scalars, not newly reconstructed joint angles. The long table retains original values and flags; the wide matrix exposes only provisionally available values. The [Milestone 2.1 pilot descriptives](reports/milestone_02_1_pilot_descriptives.md) summarize the current 30-person sample by side and show source-provided spatiotemporal values alongside speed, without injury-group tests. To regenerate event indices and compare official discrete variables, run the MATLAB runner documented in the Milestone 3 status report; it requires MATLAB with Statistics and Machine Learning Toolbox and Signal Processing Toolbox.

`scripts/acquire_data.py` refuses to overwrite source files. It checks source CSV/README sizes and MD5 against the Figshare version manifest, validates ZIP member size/CRC, and records SHA-256. It downloads bounded HTTP ranges and refuses a whole-archive fallback. Full archives are about 22.75 GB and 1.39 GB; they are not needed for this milestone.

## Project organization

Follow-up review: [cohort readiness and proposed pilot](reports/milestone_01_readiness_review.md). Regenerate with `python scripts/review_readiness.py`. It audits speed/covariate balance, missingness, label sensitivity and diagnosis feasibility, and prepares a deterministic 30-person acquisition manifest. It does not change primary cohort rules, download new trials or run biomechanical analysis.

```text
data/raw/             immutable original metadata, official code, JSON sample
data/external/        separately namespaced complementary source
data/interim/         manifests, archive indices, structural audits
data/processed/       observations and reproducible candidate cohort audit
notebooks/            investigation and communication, 01–03 active
src/data/             reusable loaders, QC and cohort construction
src/analysis/         descriptive metadata summaries
src/visualization/    exportable descriptive figures
src/biomechanics/     source feature registry and pilot QC; reconstruction deferred
src/features/         reserved for reviewed later stages
src/models/           reserved for reviewed later stages
docs/                 dictionary, conventions, clinical/methodological decisions
reports/              milestone summary, tables and figures
handoff/              reusable feature catalog, findings and integration limits
tests/                ingestion, cohort logic and source integrity regression checks
```

Notebooks 01–04 are active (metadata and technical pilot). Notebooks 05–09 remain planned. Joint-angle reconstruction, waveform inference, clustering and injury-status ML remain later stages. Do not expand to the full cohort before reviewing pilot quality and validating events/cycles.

Read [verification evidence and limits](reports/validation.md). Notebook cells were executed in Python with a fresh namespace per notebook; a Jupyter kernel/UI was not verified.

## Sources and licensing

- [Primary dataset, Figshare v1](https://doi.org/10.25452/figshare.plus.24255795.v1), CC BY 4.0. Ferber, Brett, Fukuchi, Hettinga and Osis. Preserve attribution in derivative datasets/figures.
- [Data descriptor, Scientific Data 2024](https://doi.org/10.1038/s41597-024-04011-7). Its publication licence is distinct from the dataset licence.
- Original official MATLAB files in `data/raw/official_code/` retain their MIT licence and authorship. They are inspected, not executed or silently ported.
- Complementary data and code retain their own upstream terms and citation. No external participant is merged with a Calgary participant without a verified crosswalk.

## Public project and release

- Interactive project site: [running-injury-clinic.vercel.app](https://running-injury-clinic.vercel.app) (static `site/` directory; animated SVG is conceptual and not participant data).
- Source repository: [github.com/victorgomezadapty/running-injury-clinic](https://github.com/victorgomezadapty/running-injury-clinic).
- Small Kaggle release: [Running Injury Clinic Kinematic Technical Pilot](https://www.kaggle.com/datasets/vctorandrsgmezlpez/running-injury-clinic-kinematic-pilot). It contains only the selected, identifier-stripped 30-person pilot table and its dictionary; exact public source measurements may remain linkable.
- Portfolio project index: [Victor Gómez portfolio](https://victor-gomez-portfolio.vercel.app) and GitHub profile README.

The site includes the evidence discussion, all DOI references, limits, attribution and licensing. Dataset rights remain CC BY 4.0, supplied MATLAB code retains its MIT notice, and new repository code is MIT. See [attribution and licensing](docs/attribution_and_licensing.md). Do not interpret the site or pilot as a clinical tool or validated model.

## Hosting and release

Vercel serves `site/` as a static root. When connected to GitHub, commits to the production branch deploy automatically and pull requests receive previews. Kaggle packaging is rebuilt with `python scripts/build_kaggle_release.py`; source archives and credential files are excluded from Git. Do not commit Kaggle API credentials or `.vercel/` state.

## Literature discussion

Read the [focused literature review](docs/literature_review.md) and [reference list](docs/references.md). The discussion is narrative, not a registered systematic review. It explains why the current-status outcome, heterogeneous injury labels, running speed and event/cycle quality constrain interpretation.
