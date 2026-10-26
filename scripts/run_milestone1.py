"""Build the Milestone 1 reports offline from the acquired source snapshots."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import platform
from importlib.metadata import version, PackageNotFoundError
import hashlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
from src.data.load_metadata import load_metadata, first_observation, clean_text, NO_INJURY
from src.data.validation import add_quality_flags, build_cohort
from src.data.load_trials import inspect_trial, locate_trial
from src.analysis.metadata_summary import frequency, numerical_summary, missingness, diagnosis_counts, markdown_table


def write_table(frame, name):
    frame.to_csv(ROOT / "reports/tables" / f"{name}.csv", index=False)


def main():
    for folder in ["reports/tables", "reports/figures", "data/processed", "docs", "handoff"]:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    df = add_quality_flags(load_metadata(ROOT / "data/raw"))
    run, walk = df[df.task.eq("running")].copy(), df[df.task.eq("walking")].copy()
    first_run, first_all = first_observation(run), first_observation(df)
    archive = json.loads((ROOT / "data/interim/provenance/ric_data_index.json").read_text())
    paths = {item["filename"] for item in archive if item["filename"].endswith(".json")}
    cohort = build_cohort(df, paths)
    # Attach structural sample audits, one JSON at a time and by exact subject/file.
    audits = []
    for path in sorted((ROOT / "data/raw/sample").rglob("*.json")):
        audit = inspect_trial(path)
        audit["file"] = path.relative_to(ROOT).as_posix()
        audit["participant_id"] = path.parent.name
        audit["filename"] = path.name
        matches = df[(df.participant_id == path.parent.name) & (df.filename == path.name)]
        audit["metadata_links"] = matches[["participant_id", "filename", "task", "speed_m_s"]].to_dict("records")
        audits.append(audit)
        matched = (cohort.participant_id == path.parent.name) & (cohort.filename == path.name)
        branch = audit["tasks"]["running"]
        cohort.loc[matched, "raw_qc_status"] = "structural_warnings" if branch["warnings"] else ("structural_pass_only" if branch["present"] else "running_absent")
    (ROOT / "data/interim/sample_trial_audit.json").write_text(json.dumps(audits, indent=2, allow_nan=False), encoding="utf-8")
    df.to_csv(ROOT / "data/processed/metadata_observations.csv", index=False)
    cohort.to_csv(ROOT / "data/processed/running_cohort_audit.csv", index=False)
    candidate = first_observation(cohort[cohort.candidate_included])
    candidate.to_csv(ROOT / "data/processed/candidate_running_participants.csv", index=False)
    r_ids, w_ids = set(run.participant_id), set(walk.participant_id)
    counts = {"unique_participants": len(r_ids | w_ids), "running_participants": len(r_ids), "walking_participants": len(w_ids), "both": len(r_ids & w_ids), "running_only": len(r_ids - w_ids), "walking_only": len(w_ids - r_ids), "running_observations": len(run), "walking_observations": len(walk), "archive_json_files": len(paths), "archive_participants": len({Path(p).parent.name for p in paths}), "candidate_running_observations": int(cohort.candidate_included.sum()), "candidate_running_participants": len(candidate), "adjusted_complete_candidate_participants": int(candidate.adjusted_complete_candidate.sum()), "sample_json_audited": len(audits), "full_usable_running_count": None}
    all_sessions = df.drop_duplicates(["participant_id", "filename"])
    repeats = all_sessions.groupby("participant_id").agg(json_files=("filename", "nunique"), distinct_timestamps=("session_time", "nunique"), collection_days=("session_date", "nunique"))
    repeats["running_observations"] = run.groupby("participant_id").size().reindex(repeats.index, fill_value=0)
    repeats["walking_observations"] = walk.groupby("participant_id").size().reindex(repeats.index, fill_value=0)
    write_table(repeats.reset_index(), "participant_sessions")
    counts["participants_multiple_json"] = int(repeats.json_files.gt(1).sum())
    counts["participants_multiple_days"] = int(repeats.collection_days.gt(1).sum())
    counts["participants_multiple_running_observations"] = int(repeats.running_observations.gt(1).sum())
    changes = run.groupby("participant_id").agg(status_categories=("injury_status", "nunique"), diagnosis_categories=("diagnosis", "nunique"))
    write_table(changes.reset_index(), "running_status_changes")
    counts["running_participants_status_changes"] = int(changes.status_categories.gt(1).sum())
    counts["timestamp_recoveries_from_filename"] = int(df.session_time_source.eq("filename_recovery").sum())
    counts["csv_filename_timestamp_disagreements"] = int(df.timestamp_disagreement.sum())
    alternate = run.copy()
    alternate["session_time"] = pd.to_datetime(alternate.filename.str.removesuffix(".json"), format="%Y%m%dT%H%M%S", errors="coerce")
    alternate_first = first_observation(alternate).set_index("participant_id")
    counts["first_running_choice_changed_using_filename_time"] = int(first_run.set_index("participant_id").filename.ne(alternate_first.filename).sum())
    write_table(df.loc[df.session_time_source.ne("csv") | df.timestamp_disagreement, ["participant_id", "task", "datestring", "filename", "session_time", "session_time_source", "timestamp_disagreement"]], "timestamp_audit")
    write_table(pd.DataFrame(counts.items(), columns=["metric", "value"]), "cohort_counts")
    (ROOT / "reports/tables/cohort_counts.json").write_text(json.dumps(counts, indent=2), encoding="utf-8")
    fields = [c for c in pd.read_csv(ROOT / "data/raw/run_data_meta.csv", nrows=0).columns]
    categorical = ["injury_status", "severity", "joint", "diagnosis", "injury_side", "gender", "dominant_leg", "athletic_level", "RaceDistance", "joint_secondary", "diagnosis_secondary"]
    for population, table in [("running_first", first_run), ("all_first", first_all), ("running_observations", run), ("walking_first", first_observation(walk))]:
        write_table(pd.concat([frequency(table, col) for col in categorical]), population + "_categories")
        numeric = ["age_analysis", "Height_analysis", "Weight_analysis", "speed_m_s", "YrsRunning_analysis", "InjDuration_analysis", "NumRaces_analysis"]
        write_table(numerical_summary(table, numeric), population + "_numeric")
        write_table(missingness(table, fields if population != "walking_first" else [c if c != "speed_r" else "speed_w" for c in fields]), population + "_missingness")
    quality = pd.DataFrame([{"variable": c.removesuffix("_qc_invalid"), "running_observations_flagged": int(run[c].sum()), "running_first_flagged": int(first_run[c].sum()), "all_observations_flagged": int(df[c].sum())} for c in df if c.endswith("_qc_invalid")])
    write_table(quality, "quality_flags")
    specific = diagnosis_counts(run)
    write_table(specific, "running_diagnosis_ever_participant")
    # Preserve exact raw spellings and normalization mappings for review.
    aliases = run[["SpecInjury", "diagnosis"]].drop_duplicates().sort_values("diagnosis")
    write_table(aliases, "diagnosis_mapping")
    raw_categories = pd.concat([frequency(run, c) for c in fields if c not in ["sub_id", "filename", "datestring", "speed_r"]])
    write_table(raw_categories, "running_raw_category_inventory")
    unresolved = cohort[~cohort.injury_status.isin(["healthy", "injured"])]
    write_table(unresolved[["participant_id", "filename", "InjDefn", "InjJoint", "SpecInjury", "InjJoint2", "SpecInjury2", "injury_status"]], "unresolved_injury_status")
    speed_status = first_run.groupby("injury_status").speed_m_s.agg(["count", "mean", "std", "median", "min", "max"]).reset_index()
    write_table(speed_status, "running_speed_by_status")
    injury_duration = numerical_summary(first_run[first_run.injury_status.eq("injured")], ["InjDuration_analysis"])
    write_table(injury_duration, "injured_first_duration")
    # Verify demographic records agree when one JSON appears in both source CSVs.
    paired = run.merge(walk, on=["participant_id", "filename"], suffixes=("_r", "_w"), validate="one_to_one")
    comparisons = []
    for col in fields:
        if col not in ["sub_id", "filename", "speed_r"]:
            different = paired[col + "_r"].fillna("").ne(paired[col + "_w"].fillna(""))
            comparisons.append({"field": col, "shared_json_rows": len(paired), "disagreements": int(different.sum())})
    write_table(pd.DataFrame(comparisons), "paired_task_metadata_consistency")
    metadata_paths = {f"reformat_data/{r.participant_id}/{r.filename}" for r in df.itertuples()}
    write_table(pd.DataFrame({"archive_member": sorted(paths - metadata_paths)}), "archive_files_without_metadata")
    write_table(pd.DataFrame({"archive_member": sorted(metadata_paths - paths)}), "metadata_files_without_archive")
    # Document every source column against actual values and the official README.
    readme = (ROOT / "data/raw/README.txt").read_text(encoding="utf-8-sig")
    descriptions = {}
    for line in readme.splitlines():
        if ":" in line:
            key, description = line.split(":", 1)
            if key.strip() in fields or key.strip() == "speed_w(r)":
                descriptions[key.strip()] = description.strip()
    dictionary = []
    for col in fields + ["speed_w"]:
        source = walk if col == "speed_w" else run
        clean = clean_text(source[col])
        dictionary.append({"source_column": col, "description": descriptions.get(col, descriptions.get("speed_w(r)", "") if col.startswith("speed_") else ""), "source_type": "text preserved on ingestion", "observed_nonmissing": int(clean.notna().sum()), "observed_missing": int(clean.isna().sum()), "distinct_nonmissing": int(clean.nunique()), "sample_values": "; ".join(clean.dropna().unique()[:6])})
    dd = pd.DataFrame(dictionary)
    write_table(dd, "data_dictionary")
    (ROOT / "docs/data_dictionary.md").write_text("# Data dictionary\n\nActual Figshare v1 columns. Counts refer to all running observations (n=" + str(len(run)) + "); speed_w refers to walking observations (n=" + str(len(walk)) + "). All original columns remain text in the loader, with derived numeric fields appended. Units and definitions come from the official README. Missing means empty/NaN/NULL/N/A; Unknown is retained separately.\n\n" + markdown_table(dd) + "\n\nInjDefn is TEXT, not integer codes. Supported source labels are No injury, Continuing to train in pain, Training volume/intensity affected, and 2 workouts missed in a row. Gender is self-reported gender, not a verified biological-sex measurement. Height is cm, Weight kg, speed m/s, InjDuration days. Injury duration has substantial conditional missingness; blanks among healthy controls are often structurally inapplicable. Some race-time fields contain nonnumeric text and are not converted to performance metrics.\n\nSee `reports/tables/diagnosis_mapping.csv` for every observed primary-diagnosis spelling and its normalized value. See `reports/tables/running_raw_category_inventory.csv` for exact source values. Derived columns and exclusion reasons are documented in `cohort_definition.md` and `methodology.md`.\n", encoding="utf-8")
    # Lightweight charts are optional only if matplotlib is unavailable.
    from src.visualization.clinical_plots import make_metadata_figures
    make_metadata_figures(first_run, counts, specific, missingness(first_run, fields), ROOT / "reports/figures")
    evidence = {"python": platform.python_version(), "packages": {}}
    for package in ["pandas", "numpy", "matplotlib", "requests", "inflate64", "nbformat", "nbclient"]:
        try:
            evidence["packages"][package] = version(package)
        except PackageNotFoundError:
            evidence["packages"][package] = None
    evidence["raw_sha256"] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / "data/raw").rglob("*")) if p.is_file()}
    (ROOT / "reports/tables/run_provenance.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    sample_summary = pd.DataFrame([{"participant_id": a["participant_id"], "filename": a["filename"], "task": task, "present": b["present"], "sampling_hz": b["sampling_hz"] if b["present"] else None, "markers": len(b["trajectories"]), "warnings": ";".join(b["warnings"])} for a in audits for task,b in a["tasks"].items()])
    write_table(sample_summary, "sample_trial_summary")
    external_path = ROOT / "data/external/bmc_ric/data/metadata.txt"
    external_section = "Complementary source not yet acquired; no external participants added to the primary cohort."
    if external_path.exists():
        external = pd.read_csv(external_path, sep="\t", index_col=0)
        external_counts = external.groupby("Group").agg(source_rows=("Subject", "size"), participants=("Subject", "nunique")).reset_index()
        external_section = f"""The official [BMC–RIC interlaboratory supplement](https://github.com/regifukuchi/BMC-RIC-running-biomechanics) is acquired separately, pinned to commit `21f5a4607c9e4f6a365caa6e6d85c96787517844` with Git-blob/SHA-256 integrity checks and upstream CC BY 4.0 attribution. The observed metadata contain {len(external)} rows, {len(external.columns)} fields and {int(external.isna().sum().sum())} missing cells.

{markdown_table(external_counts)}

Observed fields: {', '.join(external.columns)}. Subject numbers repeat across centres, so identity requires Group + Subject. Rows are labelled Trial in the source; they must not be counted as independent participants or assumed to be separate clinical sessions. There are no injury-status, diagnosis or gender columns and no verified crosswalk to Calgary sub_id. The notebook is retained as source documentation and was not executed. Waveform data were not downloaded or analyzed.

This complement prepares a protocol-compatibility benchmark from the outset. It does not increase the primary Calgary cohort, fill missing patient fields, or establish independent external validation. Possible RIC overlap remains unresolved. See `../docs/complementary_sources.md` and `../docs/external_compatibility.md` for source-specific definitions and limitations; the separate metadata profile can be regenerated with `python scripts/profile_external.py`."""
    summary = f"""# Milestone 1 — Dataset & Cohort Understanding

Sports Rehabilitation & Human Performance · Running Biomechanics & Injury Phenotyping

Scope: metadata, archive manifest and a bounded JSON ingestion sample. No machine learning or advanced kinematic analysis was run. Acquisition pinned to [Figshare v1](https://doi.org/10.25452/figshare.plus.24255795.v1); study methods: [Ferber et al., Scientific Data 2024](https://doi.org/10.1038/s41597-024-04011-7). Report generated from local source files by `python scripts/run_milestone1.py`. Counts below are recalculated, not copied from the paper.

## What data do we actually have?

{markdown_table(pd.DataFrame(counts.items(), columns=['metric', 'value']))}

Metadata rows are task observations, not unique people or necessarily unique visits. The same JSON may contain both tasks. Distinct timestamps and distinct collection days are reported separately in `tables/participant_sessions.csv`. The two CSVs share {len(paired)} participant-file keys. Archive files without metadata: {len(paths - metadata_paths)}; metadata files without archive members: {len(metadata_paths - paths)}.

The actual archive root is `reformat_data/`, despite the documentation naming ric_data. Only {len(audits)} JSON files have been opened. `full_usable_running_count` is deliberately unknown: the count of usable running observations after complete biomechanical QC cannot be established from metadata or a small sample. Candidate membership is provisional.

Structural ingestion sample (a convenience sample plus selected task/status examples; not representative):

{markdown_table(sample_summary)}

The timestamp audit identifies {counts['timestamp_recoveries_from_filename']} missing CSV times recovered from filenames and {counts['csv_filename_timestamp_disagreements']} task rows with conflicting CSV/filename times. CSV time is preferred when present; a sensitivity check selecting by filename time changed the earliest running file in {counts['first_running_choice_changed_using_filename_time']} participants. These fields are not validated longitudinal follow-up dates. Review `tables/timestamp_audit.csv` before any temporal interpretation.

## Who is represented?

Primary descriptive unit: each participant's earliest running observation, n={len(first_run)}. All-participant earliest records and all-observation sensitivity tables are also supplied. Later injury histories are retained; an earliest healthy observation does not imply lifelong absence of injury.

{markdown_table(numerical_summary(first_run, ['age_analysis', 'Height_analysis', 'Weight_analysis', 'speed_m_s', 'YrsRunning_analysis', 'InjDuration_analysis', 'NumRaces_analysis']))}

{markdown_table(pd.concat([frequency(first_run, col) for col in ['gender', 'dominant_leg', 'athletic_level', 'injury_status', 'severity']]))}

These are clinic/research volunteers measured on a treadmill. There is no population-representative sampling frame. Height, weight, age and running experience contain implausible entries. Original values are retained and flagged; no outlier is silently corrected. Broad plausibility bounds are engineering decisions, not validated clinical thresholds.

{markdown_table(quality)}

![Participant availability](figures/cohort_overview.png)
![Age and body measurements](figures/demographics.png)
![Running background](figures/running_background.png)

## Which injuries are sufficiently represented?

The following counts are unique running participants EVER recording each specific diagnosis in an injury-positive observation, using primary and secondary fields. A person may appear in several rows. Only README-supported aliases are merged. N >= 30 is an initial descriptive screening rule, not a power calculation or evidence of a diagnostic biomarker.

{markdown_table(specific, 25)}

The full diagnosis inventory, raw variants, joint/side/severity distributions and secondary injuries are in `tables/`. Generic pain, other, tendonitis and form-placeholder text remain visible descriptively but do not define a specific diagnosis group. Recorded diagnoses are not independently adjudicated here. Missing/discordant injury status is kept distinct from controls. Status changes across running observations occur in {counts['running_participants_status_changes']} participants.

![Injury metadata](figures/injury_overview.png)

Duration among injury-positive earliest running observations (days, no imputation):

{markdown_table(injury_duration)}

Speed by earliest running injury status (m/s):

{markdown_table(speed_status)}

Missingness refers to source cells, not failure to satisfy plausibility checks. Injury duration and secondary injury fields can be structurally inapplicable. Analysis fields additionally mask flagged values. See all missingness tables and `quality_flags.csv`.

![Missing data](figures/missingness.png)

## What can this dataset legitimately answer?

It supports descriptive and, after QC, cross-sectional investigation of running kinematics associated with current injury status and recorded diagnoses. Repeated observations permit within-dataset robustness checks. Future biomechanical phenotypes may cut across diagnoses, subject to stability and interpretability assessment. Dataset reference distributions can be explored after sample definition and speed/covariate evaluation.

The metadata-supported primary candidate contains {len(candidate)} participants with an eligible indexed running observation. Select the earliest eligible observation after exclusions, preserving all later observations for sensitivity analyses. This differs from the earliest-observation descriptive tables. {int(candidate.adjusted_complete_candidate.sum())} candidates also have the currently required complete plausible covariates. Neither count is a fully motion-QC-confirmed cohort. See `../docs/cohort_definition.md` and `../data/processed/running_cohort_audit.csv` for every row and exclusion.

### Complementary source prepared in parallel

{external_section}

## What can it NOT answer?

There is no prospective injury follow-up here. Associations cannot establish causation or future injury risk. Classification would distinguish biomechanical patterns associated with current injury status within this dataset; it would not demonstrate clinical diagnosis. Statistical significance does not imply clinical relevance, group averages do not define individual profiles, and biomechanical differences do not establish diagnostic biomarkers. The contralateral limb cannot automatically be treated as healthy. No participant-level merge with unrelated datasets is justified.

The JSON sample provides structural ingestion evidence only. Full-cohort marker completeness, gait-event quality, usable cycle count, and motion-derived features remain unverified. Potential selection, repeated-session dependence, diagnosis imbalance, speed confounding, missingness and equipment/marker-set differences require explicit analysis.

## What should Phase 2 analyze?

1. Review the unresolved injury records, alias mapping, plausibility screens and candidate cohort; define minimum usable-cycle and marker criteria with the official pipeline.
2. Expand to a stratified small sample across status, diagnosis, gender, speed and marker availability; validate static-array orientation, task branches, sampling frequencies, and official event warnings.
3. Audit speed overlap and demographic/experience differences before any adjusted group comparisons. Specify covariates and missing-data sensitivity analyses.
4. Choose interpretable hip/knee/ankle features only after verifying the actual descriptive-variable definitions and coordinate conventions. Preserve whole waveforms for a later milestone.
5. Plan effect sizes, uncertainty and multiplicity control. Treat n30 diagnosis screening as provisional; conduct precision/power and subgroup feasibility assessments before inference.
6. Use the complementary interlaboratory source as a separate compatibility benchmark, subject to its source-specific protocol and possible RIC overlap. See `../docs/complementary_sources.md`.

**Review gate: stop after Milestone 1.** No joint-angle reconstruction, waveform inference, clustering or classification has been performed.

Verification methods and their limits are recorded in [validation.md](validation.md).
"""
    (ROOT / "reports/milestone_01_summary.md").write_text(summary, encoding="utf-8")
    (ROOT / "handoff/findings.md").write_text("# Milestone 1 findings\n\n" + markdown_table(pd.DataFrame(counts.items(), columns=["metric", "value"])) + "\n\nSee ../reports/milestone_01_summary.md for denominators, observed distributions and the review gate. No prospective injury predictions or biomechanical outcome estimates have been made.\n", encoding="utf-8")
    print(json.dumps(counts, indent=2))
    print("Milestone 1 report generated. STOP for review.")


if __name__ == "__main__":
    main()
