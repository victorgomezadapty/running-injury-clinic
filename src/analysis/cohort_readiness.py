"""Descriptive readiness checks; no biomechanical effects or models are fit."""
from __future__ import annotations
import hashlib
import math
import pandas as pd
from src.data.load_metadata import first_observation, NO_INJURY, UNSPECIFIC
from src.data.validation import build_cohort
from src.analysis.metadata_summary import diagnosis_counts

NUMERIC = ["speed_m_s", "age_analysis", "Height_analysis", "Weight_analysis", "YrsRunning_analysis"]


def group_balance(candidate):
    """SMD sign is injured minus healthy; denominator uses unweighted variances."""
    healthy = candidate[candidate.injury_status.eq("healthy")]
    injured = candidate[candidate.injury_status.eq("injured")]
    rows = []
    for field in NUMERIC:
        h = pd.to_numeric(healthy[field], errors="coerce").dropna().astype(float)
        i = pd.to_numeric(injured[field], errors="coerce").dropna().astype(float)
        denominator = math.sqrt((h.var(ddof=1) + i.var(ddof=1)) / 2)
        difference = i.mean() - h.mean()
        rows.append({"variable": field, "healthy_n": len(h), "injured_n": len(i),
                     "healthy_mean": h.mean(), "injured_mean": i.mean(),
                     "injured_minus_healthy": difference,
                     "standardized_mean_difference": difference / denominator if denominator > 0 else None})
    return pd.DataFrame(rows)


def covariate_availability(candidate):
    valid = pd.DataFrame(index=candidate.index)
    for field in NUMERIC:
        valid[field] = candidate[field].notna()
    valid["gender"] = candidate.gender.isin(["female", "male"])
    valid["athletic_level"] = candidate.athletic_level.isin(["recreational", "competitive"])
    core_fields = ["speed_m_s", "age_analysis", "Height_analysis", "Weight_analysis", "gender"]
    rows = []
    for status, frame in candidate.groupby("injury_status"):
        subset = valid.loc[frame.index]
        for name, retained in [("all_candidates", pd.Series(True, index=subset.index)),
                               ("core_covariates", subset[core_fields].all(axis=1)),
                               ("expanded_covariates", subset.all(axis=1))]:
            rows.append({"injury_status": status, "covariate_set": name, "available_n": int(retained.sum()),
                         "candidate_n": len(subset), "retained_percent": 100 * retained.mean()})
    missing = []
    for status, frame in candidate.groupby("injury_status"):
        for field in valid:
            n = int((~valid.loc[frame.index, field]).sum())
            missing.append({"injury_status": status, "field": field, "unavailable_n": n,
                            "denominator": len(frame), "unavailable_percent": 100 * n / len(frame)})
    reasons = candidate[["participant_id", "filename", "injury_status"]].copy()
    reasons["unavailable_covariates"] = valid.apply(lambda r: ";".join(r.index[~r].tolist()), axis=1)
    reasons["expanded_complete"] = valid.all(axis=1)
    return pd.DataFrame(rows), pd.DataFrame(missing), reasons


def label_sensitivity(df, archive_paths):
    """Compare labelled scenarios without replacing the primary definition."""
    base = build_cohort(df, archive_paths)
    primary = first_observation(base[base.candidate_included]).set_index("participant_id")
    rows = []
    for scenario in ["current_conservative", "primary_fields_controls", "severity_only_exploratory"]:
        trial = base.copy()
        if scenario != "current_conservative":
            no = trial.severity.eq("no_injury")
            if scenario == "primary_fields_controls":
                evidence = ~trial.joint.isin(NO_INJURY) | ~trial.diagnosis.isin(NO_INJURY)
                trial.loc[no, "injury_status"] = evidence.loc[no].map({True: "discordant", False: "healthy"})
            else:
                trial.loc[no, "injury_status"] = "healthy"
        eligible = ~trial.identity_qc_invalid & ~trial.speed_qc_invalid & trial.archive_file_present & trial.injury_status.isin(["healthy", "injured"])
        selected = first_observation(trial[eligible]).set_index("participant_id")
        shared = selected.index.intersection(primary.index)
        rows.append({"scenario": scenario, "participants": len(selected),
                     "healthy": int(selected.injury_status.eq("healthy").sum()),
                     "injured": int(selected.injury_status.eq("injured").sum()),
                     "added_vs_primary": len(selected.index.difference(primary.index)),
                     "selected_file_changes_shared_ids": int(selected.loc[shared, "filename"].ne(primary.loc[shared, "filename"]).sum())})
    return pd.DataFrame(rows)


def selected_diagnosis_feasibility(run, candidate):
    ever = diagnosis_counts(run)[["diagnosis", "participants"]].rename(columns={"participants": "ever_participants"})
    selected = diagnosis_counts(candidate)[["diagnosis", "participants"]].rename(columns={"participants": "selected_participants"})
    expanded = diagnosis_counts(candidate[candidate.adjusted_complete_candidate])[["diagnosis", "participants"]].rename(columns={"participants": "expanded_complete_participants"})
    out = ever.merge(selected, on="diagnosis", how="outer").merge(expanded, on="diagnosis", how="outer").fillna(0)
    for field in ["ever_participants", "selected_participants", "expanded_complete_participants"]:
        out[field] = out[field].astype(int)
    out["selected_n30_planning_flag"] = out.selected_participants.ge(30)
    return out.sort_values(["selected_participants", "diagnosis"], ascending=[False, True])


def _rank(text, seed):
    return hashlib.sha256(f"{seed}|{text}".encode()).hexdigest()


def _round_robin(frame, n, fields, seed):
    if not len(frame) or n == 0:
        return frame.head(0).copy()
    frame = frame.copy()
    frame["_stratum"] = frame[fields].astype("string").fillna("missing").agg("|".join, axis=1)
    frame["_rank"] = frame.apply(lambda r: _rank(f"{r.participant_id}|{r.filename}", seed), axis=1)
    buckets = {key: list(group.sort_values("_rank").index) for key, group in frame.groupby("_stratum")}
    keys = sorted(buckets, key=lambda key: _rank(key, seed))
    chosen = []
    while len(chosen) < min(n, len(frame)):
        for key in keys:
            if buckets[key] and len(chosen) < min(n, len(frame)):
                chosen.append(buckets[key].pop(0))
    return frame.loc[chosen].drop(columns=["_stratum", "_rank"])


def plan_pilot(candidate, seed=42, per_status=15):
    """Technical purposive sample, not a population or inferential cohort."""
    frame = candidate.copy()
    if frame.participant_id.duplicated().any():
        raise ValueError("Pilot planning requires one observation per participant")
    bands = pd.qcut(frame.speed_m_s.astype(float), 3, labels=False, duplicates="drop")
    frame["speed_band"] = bands.map(lambda x: f"pooled_speed_tertile_{int(x) + 1}" if pd.notna(x) else "missing")
    controls = _round_robin(frame[frame.injury_status.eq("healthy")], per_status, ["gender", "speed_band"], seed)
    controls["selection_purpose"] = "control_gender_speed_coverage"
    cases = frame[frame.injury_status.eq("injured")]
    major = diagnosis_counts(cases).query("participants >= 30").head(7).diagnosis.tolist()
    chosen, ids = [], set(controls.participant_id)
    for diagnosis in major:
        pool = cases[(cases.diagnosis.eq(diagnosis) | cases.diagnosis_secondary.eq(diagnosis)) & ~cases.participant_id.isin(ids)]
        take = min(2, per_status - sum(len(group) for group in chosen))
        picked = _round_robin(pool, take, ["gender", "speed_band"], seed)
        picked["selection_purpose"] = "major_diagnosis:" + diagnosis
        chosen.append(picked)
        ids.update(picked.participant_id)
    remaining = per_status - sum(len(group) for group in chosen)
    pool = cases[~cases.participant_id.isin(ids)].copy()
    pool["specific_diagnosis_present"] = (~pool.diagnosis.isin(NO_INJURY | UNSPECIFIC) | ~pool.diagnosis_secondary.isin(NO_INJURY | UNSPECIFIC))
    # Include an unspecified injury record if room remains and one is available.
    unspecified = pool[~pool.specific_diagnosis_present]
    if remaining and len(unspecified):
        picked = _round_robin(unspecified, 1, ["gender", "speed_band"], seed)
        picked["selection_purpose"] = "unspecified_injury_ingestion_coverage"
        chosen.append(picked)
        ids.update(picked.participant_id)
        remaining -= 1
    if remaining:
        picked = _round_robin(pool[~pool.participant_id.isin(ids)], remaining, ["gender", "speed_band"], seed)
        picked["selection_purpose"] = "additional_injured_coverage"
        chosen.append(picked)
    return pd.concat([controls, *chosen], ignore_index=True).drop(columns=["specific_diagnosis_present"], errors="ignore")
