"""Static, exportable scientific charts with explicit denominators."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.analysis.metadata_summary import frequency

COLOR = "#176b87"


def bar(ax, data, field, title, limit=12):
    freq = frequency(data, field).head(limit).iloc[::-1]
    ax.barh(freq.category, freq.n, color=COLOR)
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold")
    ax.set_xlabel("Participants")
    ax.spines[["top", "right"]].set_visible(False)


def make_metadata_figures(first, counts, diagnoses, missing, destination):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.titlepad": 12, "figure.facecolor": "white", "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(8, 4), layout="constrained")
    labels = ["Walking only", "Both tasks", "Running only"]
    values = [counts["walking_only"], counts["both"], counts["running_only"]]
    bars = ax.barh(labels, values, color=["#95b9c7", COLOR, "#d18448"])
    ax.bar_label(bars, padding=5)
    ax.set_xlim(0, max(values) * 1.16)
    ax.set_xlabel("Unique participants")
    ax.set_title(f"Task availability · {counts['unique_participants']:,} participants", loc="left", fontweight="bold")
    fig.savefig(destination / "cohort_overview.png", dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    for ax, col, title in zip(axes.flat, ["age_analysis", "Height_analysis", "Weight_analysis", "YrsRunning_analysis"], ["Age (years)", "Height (cm)", "Weight (kg)", "Running experience (years)"]):
        values = first[col].dropna().astype(float)
        ax.hist(values, bins=25, color=COLOR, edgecolor="white")
        ax.set_title(f"{title} · valid n={len(values):,}", loc="left", fontweight="bold")
        ax.set_ylabel("Participants")
        ax.set_xlabel(title)
    fig.suptitle("Earliest running observation per participant · flagged values omitted", fontsize=14)
    fig.savefig(destination / "demographics.png", dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), layout="constrained")
    axes[0].hist(first.speed_m_s.astype(float), bins=25, color=COLOR, edgecolor="white")
    axes[0].set_title("Running speed", loc="left", fontweight="bold")
    axes[0].set_xlabel("m/s")
    axes[0].set_ylabel("Participants")
    bar(axes[1], first, "athletic_level", "Self-reported athletic level")
    bar(axes[2], first, "RaceDistance", "Preferred distance · top 10", limit=10)
    fig.suptitle(f"Running background · first observation · n={len(first):,}", fontsize=14)
    fig.savefig(destination / "running_background.png", dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), layout="constrained")
    for ax, field, title in zip(axes.flat, ["injury_status", "joint", "injury_side", "severity"], ["Conservative injury status", "Primary injury location", "Recorded injury side", "Self-reported severity"]):
        bar(ax, first, field, title)
    fig.suptitle(f"Injury metadata · first running observation · n={len(first):,}", fontsize=14)
    fig.savefig(destination / "injury_overview.png", dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(11, 8), layout="constrained")
    data = missing.sort_values("missing_percent")
    ax.barh(data.field, data.missing_percent, color=COLOR)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Missing source cells (%) · plausibility exclusions shown separately")
    ax.set_title(f"Metadata completeness · first running observation · n={len(first):,}", loc="left", fontweight="bold")
    fig.savefig(destination / "missingness.png", dpi=160)
    plt.close(fig)
