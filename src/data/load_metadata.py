"""Read the actual RIC CSV schema without losing source values or identifiers."""
from pathlib import Path
import pandas as pd

MISSING = {"", "nan", "nat", "null", "n/a", "na"}
NO_INJURY = {"", "no injury", "no injury,no injury", "no injury, no injury"}
SEVERITIES = {
    "no injury": "no_injury",
    "continuing to train in pain": "training_with_pain",
    "training volume/intensity affected": "training_affected",
    "2 workouts missed in a row": "two_workouts_missed",
}
# Only aliases explicitly documented in the official README are merged.
DIAGNOSIS_ALIASES = {
    "oa": "osteoarthritis", "hip oa": "osteoarthritis", "knee oa": "osteoarthritis",
    "osteroarthritis": "osteoarthritis", "itbs": "itb syndrome",
    "pfps": "patellofemoral pain syndrome",
}
UNSPECIFIC = {"pain", "other", "fill in specifics below", "tendonitis"}
NUMERIC = ["age", "Height", "Weight", "InjDuration", "YrsRunning", "YrPR", "NumRaces"]


def clean_text(series):
    result = series.astype("string").str.strip()
    return result.mask(result.str.lower().isin(MISSING))


def injury_label(row):
    severity = row["severity"]
    primary = row["joint"] not in NO_INJURY or row["diagnosis"] not in NO_INJURY
    secondary = row["joint_secondary"] not in NO_INJURY or row["diagnosis_secondary"] not in NO_INJURY
    if severity == "no_injury":
        return "discordant" if primary or secondary else "healthy"
    if severity in {"training_with_pain", "training_affected", "two_workouts_missed"}:
        return "injured"
    return "unknown"


def load_metadata(raw_dir: str | Path) -> pd.DataFrame:
    frames = []
    for task, filename in [("running", "run_data_meta.csv"), ("walking", "walk_data_meta.csv")]:
        frame = pd.read_csv(Path(raw_dir) / filename, dtype="string", keep_default_na=False, encoding="utf-8-sig")
        if len(frame.columns) != len(set(frame.columns)):
            raise ValueError("Duplicate CSV column names")
        required = {"sub_id", "datestring", "filename", "InjDefn", "InjJoint", "SpecInjury", "speed_r" if task == "running" else "speed_w"}
        if required - set(frame.columns):
            raise ValueError(f"Unexpected metadata schema: {required - set(frame.columns)}")
        frame["task"] = task
        frame["source_file"] = filename
        frame["source_row"] = range(2, len(frame) + 2)
        frames.append(frame)
    df = pd.concat(frames, ignore_index=True)
    df["participant_id"] = clean_text(df["sub_id"])
    csv_time = pd.to_datetime(clean_text(df["datestring"]), format="%Y-%m-%d %H:%M:%S", errors="coerce")
    filename_time = pd.to_datetime(df.filename.str.removesuffix(".json"), format="%Y%m%dT%H%M%S", errors="coerce")
    df["session_time"] = csv_time.fillna(filename_time)
    df["session_time_source"] = "csv"
    df.loc[csv_time.isna() & filename_time.notna(), "session_time_source"] = "filename_recovery"
    df.loc[df.session_time.isna(), "session_time_source"] = "missing"
    df["timestamp_disagreement"] = csv_time.notna() & filename_time.notna() & csv_time.ne(filename_time)
    df["session_date"] = df["session_time"].dt.strftime("%Y-%m-%d")
    for field in NUMERIC:
        df[field + "_numeric"] = pd.to_numeric(clean_text(df[field]), errors="coerce")
    df["speed_m_s"] = pd.to_numeric(clean_text(df["speed_r"].where(df.task.eq("running"), df["speed_w"])), errors="coerce")
    for source, target in [("Gender", "gender"), ("DominantLeg", "dominant_leg"), ("Level", "athletic_level"), ("InjSide", "injury_side"), ("InjJoint", "joint"), ("InjJoint2", "joint_secondary"), ("SpecInjury", "diagnosis"), ("SpecInjury2", "diagnosis_secondary")]:
        df[target] = clean_text(df[source]).str.lower().fillna("")
    df["injury_side"] = df.injury_side.replace({"bi-lateral": "bilateral"})
    for col in ["diagnosis", "diagnosis_secondary"]:
        df[col] = df[col].replace(DIAGNOSIS_ALIASES)
    df["severity"] = clean_text(df.InjDefn).str.lower().map(SEVERITIES).fillna("unknown")
    df["injury_status"] = df.apply(injury_label, axis=1)
    df["diagnosis_specific_recorded"] = ~df.diagnosis.isin(NO_INJURY | UNSPECIFIC)
    return df


def first_observation(df: pd.DataFrame) -> pd.DataFrame:
    """Earliest timestamp per participant; filename breaks same-time ties."""
    return df.sort_values(["participant_id", "session_time", "filename"], na_position="last", kind="stable").drop_duplicates("participant_id").copy()
