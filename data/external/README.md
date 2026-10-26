# External sources

`bmc_ric/` contains the unchanged small files from the [official BMC–RIC running biomechanics supplement](https://github.com/regifukuchi/BMC-RIC-running-biomechanics), pinned to commit `21f5a4607c9e4f6a365caa6e6d85c96787517844`. Retain the upstream CC BY 4.0 licence and authorship. Reacquire with `python scripts/acquire_external.py`; profile offline with `python scripts/profile_external.py`.

The original metadata are a TSV with an exported index column and eight data columns: Group, Subject, Trial, Filename, Speed, Age, Height, Mass. Use Group + Subject as identity. There are 46 composite IDs and 1,614 waveform-record metadata rows, not 1,614 independent participants. No injury/gender fields or verified Calgary identifier crosswalk are provided.

Source data remain separate from `data/raw/` and the primary cohort. The original notebook is documentation only and was not executed. Waveforms are excluded from this milestone. Generated summaries belong in `reports/` and `reports/tables/`. Read `docs/complementary_sources.md` and `docs/external_compatibility.md` before reuse.
