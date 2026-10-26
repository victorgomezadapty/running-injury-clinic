"""Reproducible participant-aware descriptive summaries."""
import pandas as pd
from src.data.load_metadata import clean_text, NO_INJURY, UNSPECIFIC


def frequency(df, field):
    values = df[field].astype("string").fillna("missing").replace({"": "missing"})
    out = values.value_counts(dropna=False).rename_axis("category").reset_index(name="n")
    out["denominator"] = len(df)
    out["percent"] = 100 * out.n / len(df) if len(df) else 0
    out["field"] = field
    return out


def numerical_summary(df, fields):
    out = []
    for col in fields:
        values = pd.to_numeric(df[col], errors="coerce").dropna()
        out.append({"variable": col, "n": len(values), "missing": int(df[col].isna().sum()),
                    "mean": values.mean(), "sd": values.std(), "min": values.min(),
                    "p25": values.quantile(.25), "median": values.median(),
                    "p75": values.quantile(.75), "max": values.max()})
    return pd.DataFrame(out)


def missingness(df, fields):
    out = []
    for col in fields:
        missing = clean_text(df[col]).isna()
        unknown = clean_text(df[col]).str.lower().isin(["unknown", "fill in specifics below"])
        out.append({"field": col, "n": len(df), "missing_n": int(missing.sum()),
                    "missing_percent": 100 * missing.mean(), "unknown_or_placeholder_n": int(unknown.sum())})
    return pd.DataFrame(out)


def diagnosis_counts(df):
    """Ever recorded: unique persons per diagnosis; totals are not additive."""
    data = df.loc[df.injury_status.eq("injured")]
    long = pd.concat([data[["participant_id", "diagnosis"]], data[["participant_id", "diagnosis_secondary"]].rename(columns={"diagnosis_secondary": "diagnosis"})])
    long = long[~long.diagnosis.isin(NO_INJURY | UNSPECIFIC)].drop_duplicates()
    out = long.groupby("diagnosis").participant_id.nunique().sort_values(ascending=False).rename("participants").reset_index()
    out["exploratory_n30_screen"] = out.participants.ge(30)
    return out


def markdown_table(df, limit=None):
    data = df.head(limit) if limit else df
    def fmt(value):
        if pd.isna(value):
            return "missing"
        if isinstance(value, float):
            if value.is_integer():
                return f"{int(value):,}"
            return f"{value:.2f}"
        return str(value).replace("|", "/").replace("\n", " ")
    header = "| " + " | ".join(map(str, data.columns)) + " |\n"
    return header + "| " + " | ".join(["---"] * len(data.columns)) + " |\n" + "\n".join("| " + " | ".join(fmt(x) for x in row) + " |" for row in data.itertuples(index=False, name=None))
