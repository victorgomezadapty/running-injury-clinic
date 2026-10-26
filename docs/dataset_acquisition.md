# Dataset acquisition and provenance

Primary record: [Figshare DOI, version 1](https://doi.org/10.25452/figshare.plus.24255795.v1). API snapshot: `data/interim/provenance/figshare_24255795_v1.json`. Files and exact download URLs are recorded in `file_manifest.json`. Dataset licence: CC BY 4.0. Code licence: upstream MIT.

| File | Figshare file ID | Size in bytes | Current acquisition |
| --- | --- | --- | --- |
| README.txt | 42637036 | 10,593 | complete, verified |
| run_data_meta.csv | 42637039 | 389,355 | complete, verified |
| walk_data_meta.csv | 42637045 | 427,633 | complete, verified |
| Supplemental_materials.zip | 42637210 | 1,392,459,250 | directory index and small source-code members only |
| ric_data.zip | 42651352 | 22,749,955,646 | directory index and ten JSON members only |

Run `python scripts/acquire_data.py --sample 10 --index-archives`. It selects the first JSON member from each of the first five distinct participant folders in archive order, then one exact metadata-linked example from each of five pools: both-task healthy, both-task injured, both-task unknown, both-task discordant and walking-only. Within each pool it selects the first available distinct participant after sorting by ID/time/filename. This deterministic ingestion sample covers task/status branches; it is not a representative clinical sample or a basis for biomechanical group estimates. Every sampled member is size/CRC checked, including on reuse. A larger stratified biomechanical-QC sample requires Milestone 1 review.

The server must return exact HTTP 206 byte ranges. Requests are bounded to 50 MB per read and 150 MB cumulative per archive reader. If ranges are unsupported or an integrity check fails, stop; no complete-archive download is attempted. Deflate64 ZIP members are decompressed with `inflate64`, without installing a system archive utility. Small original MATLAB text files are extracted; the 1.38 GB cached MAT output is excluded.

The actual JSON archive uses `reformat_data/<sub_id>/<timestamp>.json`. Link using both participant ID and filename. Timestamp alone is not a participant key. Both tasks may live in one JSON. Index membership confirms a listed file, not the presence or biomechanical quality of its running branch.

Raw files are immutable. On a rerun, source files are reused and sizes/MD5 rechecked. The versioned API snapshot is reused. Existing conflicting content causes an error. Outputs belong in interim/processed/reports. SHA-256 checksums are recorded after acquisition and again in report-run provenance. Full archive MD5 is not checked because full archives were not downloaded; individual sampled members are size/CRC checked.

Tutorial `.mlx` notebooks and event model `.mat` files remain in the official supplement and are listed in its index. For Phase 2, acquire these selectively and review the relevant tutorials before any reconstruction. Do not claim the official MATLAB workflow has been executed or validated against a Python implementation.
