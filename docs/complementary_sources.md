# Complementary source selected at Milestone 1

The selected complement is the official [BMC–RIC running biomechanics supplement](https://github.com/regifukuchi/BMC-RIC-running-biomechanics), supporting Fukuchi, Duarte and Ferber, [Interlaboratory Study Toward Combining Gait Kinematics Data Sets of Long-Distance Runners](https://pubmed.ncbi.nlm.nih.gov/39117317/), DOI [10.1123/jab.2024-0007](https://doi.org/10.1123/jab.2024-0007). It directly addresses compatibility between running kinematics datasets, rather than contributing unrelated patient attributes.

## What is acquired now

Pinned commit: `21f5a4607c9e4f6a365caa6e6d85c96787517844`. The upstream repository supplies CC BY 4.0 terms. The acquisition script checks original Git blob hashes and records SHA-256 in `data/external/bmc_ric/manifest.json`. Four unchanged sources are cached: metadata.txt, README.md, LICENSE.txt and the official analysis notebook. No waveform file is downloaded, and the notebook is not executed.

The actual TSV has 1,614 rows and eight data fields after removing its exported index column. It represents 23 BMC IDs (791 records) and 23 RIC IDs (823 records), with zero missing source cells. The identity key is Group + Subject, since Subject numbers 1–23 repeat at each centre. These counts were calculated from the downloaded file and can be reproduced by `python scripts/profile_external.py`.

The source labels rows as Trial. Inspection of the official notebook shows these records enter 101-point × 9-angle arrays, followed by a median across records per Group–Subject. Treat them as normalized waveform records in that workflow; do not interpret them as independent people, clinical visits or prospective follow-up sessions.

## What it adds

It provides a concrete benchmark for later checks of laboratory/protocol compatibility, feature definitions and representation of running waveforms. Age, height, mass and speed metadata support an initial source-specific comparison plan. The companion study is a reason to investigate compatibility, not proof that all joint planes or coordinate conventions are interchangeable. Current work is limited to acquisition, metadata profiling and documentation.

There are no injury-status, diagnosis, gender or running-experience fields in this metadata file. It cannot fill those fields for the main cohort. No verified mapping connects its RIC Subject IDs to Calgary sub_id. The RIC subset may overlap the primary source, so it neither increases the main sample count nor establishes independent external validation. The BMC group is kept separately identified too.

## Decision

Prepare this source in parallel now, with separate IDs, files and reports. Do not pool participant rows, analyze its waveform outcomes or execute its analysis notebook before the Milestone 1 review. The broader training-exposure and injury-burden projects remain separate future studies. Additional sources can be considered later if they answer a defined gap that this complement cannot address.

Read [compatibility details](external_compatibility.md), [the external metadata summary](../reports/external_metadata_summary.md) and the machine-readable profile in `reports/tables/external_metadata_profile.json`.
