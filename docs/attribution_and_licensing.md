# Attribution, licensing and reuse

## Materials and terms

| Material | Rights / terms | How this project handles it |
|---|---|---|
| Running Injury Clinic Kinematic Dataset v1 | Creative Commons Attribution 4.0 International (CC BY 4.0), as identified by the versioned Figshare record | Cite Ferber et al. and the versioned DOI; link the licence; identify the pilot feature table as adapted/selected from the source. |
| Supplied upstream MATLAB code | MIT licence, retained with its original notices in the acquired source folder | Do not remove its copyright/license notices. This project invokes/inspects it without claiming authorship. |
| New analysis scripts and website code in this repository | MIT; see the root `LICENSE` | Reusable with attribution under MIT. This does not relicense upstream material. |
| Publications and figures | Each article retains its own copyright and licence | Cite and link publications; do not copy article figures or substantial text into the site. The running illustration is original SVG artwork and is explicitly conceptual. |
| Derived pilot table | A derivative selection of source-provided values, distributed with source attribution and an adaptation notice | Removes source participant IDs, filenames, injury side/joint, and raw trajectories; retains a project pseudonym, current status, sex label, speed and 26 source-provided bilateral values. See privacy caveat below. |

## Recommended dataset attribution

> Adapted from Ferber R, Brett K, Fukuchi R, Hettinga B, Osis S, *Running Injury Clinic Kinematic Dataset*, version 1 (2024), https://doi.org/10.25452/figshare.plus.24255795.v1, licensed under CC BY 4.0. This project selected 30 participants for a technical pilot, removed source identifiers and selected source-provided bilateral discrete values. No new joint-angle reconstruction or independent event/cycle validation is claimed. Changes: selection, column renaming, pseudonymous row IDs and packaging.

The dataset descriptor is a separate publication: Ferber et al., *Scientific Data* (2024), https://doi.org/10.1038/s41597-024-04011-7. The article's publication licence is not the dataset licence.

## Privacy and redistribution caveat

Removing direct identifiers does not guarantee anonymity. Exact biomechanical values may be linkable to the public upstream files, especially in a deliberately selected 30-row pilot. This release is limited to already-public, CC BY-licensed source measurements, contains no raw trajectories or source filenames, and is not a claim of de-identification certification. Anyone reusing it must preserve attribution, respect the source's consent/ethics context, and not attempt participant identification or clinical inference. Kaggle distribution is only of the small derived table and documentation, never the 22.75 GB raw archive.

## Licence links

- Dataset: [CC BY 4.0 legal code](https://creativecommons.org/licenses/by/4.0/)
- Project code: [MIT licence](../LICENSE)
- Original data record: [Figshare v1](https://doi.org/10.25452/figshare.plus.24255795.v1)
- Original data descriptor: [Scientific Data article](https://doi.org/10.1038/s41597-024-04011-7)
