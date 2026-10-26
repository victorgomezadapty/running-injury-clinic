"""Metadata plausibility flags and explicit, provisional cohort rules."""
import numpy as np
import pandas as pd


def add_quality_flags(df):
    df = df.copy()
    # Broad engineering plausibility screens, not clinical normal ranges.
    bounds = {"age": (18, 100), "Height": (100, 230), "Weight": (30, 250), "YrsRunning": (0, 100), "InjDuration": (0, 36500), "NumRaces": (0, 365)}
    for col, (lower, upper) in bounds.items():
        numeric = df[col + "_numeric"]
        invalid = numeric.notna() & (~np.isfinite(numeric.astype(float)) | ~numeric.between(lower, upper))
        if col == "YrsRunning":
            invalid |= numeric.notna() & df.age_numeric.notna() & (numeric > df.age_numeric)
        if col == "InjDuration":
            invalid |= numeric.notna() & df.age_numeric.notna() & (numeric > df.age_numeric * 365.25)
        df[col + "_qc_invalid"] = invalid.fillna(False)
        df[col + "_analysis"] = numeric.mask(df[col + "_qc_invalid"])
    df["speed_qc_invalid"] = (~np.isfinite(df.speed_m_s.astype(float)) | df.speed_m_s.le(0)).fillna(True)
    df["identity_qc_invalid"] = df.participant_id.isna() | df.session_time.isna() | df.filename.eq("")
    df["metadata_candidate"] = ~df.speed_qc_invalid & ~df.identity_qc_invalid & df.injury_status.isin(["healthy", "injured"])
    df["adjusted_complete_candidate"] = df.metadata_candidate & df[["age_analysis", "Height_analysis", "Weight_analysis", "YrsRunning_analysis"]].notna().all(axis=1) & df.gender.isin(["female", "male"]) & df.athletic_level.isin(["recreational", "competitive"])
    return df


def build_cohort(df, archive_paths: set[str]):
    """Keep a reason per row; a metadata candidate is not full raw-data QC."""
    out = df.loc[df.task.eq("running")].copy()
    out["archive_member"] = out.apply(lambda r: f"reformat_data/{r.participant_id}/{r.filename}", axis=1)
    out["archive_file_present"] = out.archive_member.isin(archive_paths)
    out["candidate_included"] = out.metadata_candidate & out.archive_file_present
    out["exclusion_reason"] = out.apply(lambda r: ";".join(reason for flag, reason in [
        (r.identity_qc_invalid, "invalid_identity_or_time"),
        (r.speed_qc_invalid, "invalid_or_missing_speed"),
        (r.injury_status not in {"healthy", "injured"}, "unresolved_injury_status"),
        (not r.archive_file_present, "not_found_in_archive_index"),
    ] if flag), axis=1)
    out["raw_qc_status"] = "not_audited"
    return out
