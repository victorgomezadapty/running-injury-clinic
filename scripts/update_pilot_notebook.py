"""Activate notebook 04 as a communication surface for the completed pilot."""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / "notebooks/04_discrete_kinematic_eda.ipynb"
    old = nbf.read(path, as_version=4) if path.exists() else None
    if old and any(c.cell_type == "code" for c in old.cells) and not old.metadata.get("pilot_generated"):
        raise FileExistsError("Preserving an independently edited notebook; update it manually")
    book = nbf.v4.new_notebook()
    book.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
    book.metadata["pilot_generated"] = True
    book.cells = [
        nbf.v4.new_markdown_cell("# Discrete kinematics: technical pilot\n\n30 selected participants, 15 healthy and 15 injured. This notebook communicates checked source values and technical quality only. No clinical group-effect estimates or diagnostic models are fit. Source scalars are preserved, including negative angles. Event detection and valid cycle counts remain unverified.\n\nRun `scripts/run_pilot.py` before using this notebook; raw files are processed sequentially by reusable src functions."),
        nbf.v4.new_code_cell("from pathlib import Path\nimport sys, json\nimport pandas as pd\nROOT = Path.cwd()\nif not (ROOT / 'src').exists():\n    ROOT = ROOT.parent\nsys.path.insert(0, str(ROOT))\nfrom src.biomechanics.feature_registry import build_registry\nregistry, placeholders = build_registry(ROOT)\nfeatures = pd.read_csv(ROOT / 'data/processed/pilot_features_long.csv', dtype={'participant_id': 'string'})\nqc = pd.read_csv(ROOT / 'reports/tables/pilot_qc_trials.csv', dtype={'participant_id': 'string'})\nsummary = json.loads((ROOT / 'reports/tables/pilot_summary.json').read_text())"),
        nbf.v4.new_code_cell("{key: summary[key] for key in ['participants', 'features_per_side', 'finite_source_values', 'provisionally_available_values', 'structural_pass_trials', 'independently_validated_events_trials']}"),
        nbf.v4.new_markdown_cell("## Verified definitions and units\n\nStance-normalized peaks are defined by the original source code. Knee flexion uses the first 70 of 101 stance samples; hip adduction uses the first 60. STRIDE_RATE is strides/min, not Hz or steps/min. The listed code definitions do not independently validate the historical processing of every JSON."),
        nbf.v4.new_code_cell("pd.DataFrame(registry)[['feature', 'unit', 'phase', 'definition', 'source_line_start']]"),
        nbf.v4.new_code_cell("features[['participant_id', 'side', 'feature', 'value', 'unit', 'value_qc', 'analysis_value', 'events_qc']].head(15)"),
        nbf.v4.new_markdown_cell("## Technical quality and coverage\n\nEach participant contributes two side-specific slots per feature. Slots are not independent people. Source fields that are unassigned placeholders are excluded; exactly-zero selected angles remain preserved and require review."),
        nbf.v4.new_code_cell("features.groupby(['feature', 'unit']).agg(expected_slots=('side', 'size'), finite_source_values=('value', 'count'), available_slots=('provisionally_available', 'sum'))"),
        nbf.v4.new_code_cell("qc[['participant_id', 'qc_status', 'sampling_hz', 'time_span_s', 'provisionally_available_slots', 'events_qc']]"),
        nbf.v4.new_markdown_cell("![Technical pilot quality](../reports/figures/pilot_quality_overview.png)\n\nSee `reports/milestone_02_pilot_summary.md` and `docs/official_processing_review.md` for traceability, engineering review triggers and remaining event/reconstruction validation. Later waveform inference, phenotyping and classification remain separate stages."),
    ]
    nbf.validate(book)
    nbf.write(book, path)
    print("Notebook 04 updated from the completed pilot outputs.")


if __name__ == "__main__":
    main()
