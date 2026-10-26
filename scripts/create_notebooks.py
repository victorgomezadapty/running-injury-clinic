"""Initialize notebook communication surfaces and reserved later-phase modules."""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]


def main():
    setup = "from pathlib import Path\nimport sys\nROOT = Path.cwd()\nif not (ROOT / 'src').exists():\n    ROOT = ROOT.parent\nassert (ROOT / 'src').exists(), 'Run from the project root or notebooks folder'\nsys.path.insert(0, str(ROOT))\nfrom src.data.load_metadata import load_metadata, first_observation\nfrom src.data.validation import add_quality_flags\ndf = add_quality_flags(load_metadata(ROOT / 'data/raw'))\nrun = df[df.task.eq('running')].copy()\nfirst = first_observation(run)"
    notebooks = [
        ("01_metadata_understanding", "Metadata understanding", [setup, "from src.analysis.metadata_summary import numerical_summary, frequency, missingness\nfrequency(first, 'injury_status')", "numerical_summary(first, ['age_analysis', 'Height_analysis', 'Weight_analysis', 'speed_m_s', 'YrsRunning_analysis'])", "frequency(first, 'gender')", "frequency(first, 'athletic_level')"]),
        ("02_json_data_structure", "JSON structure and bounded sample audit", [setup, "from src.data.load_trials import inspect_trial\nfiles = sorted((ROOT / 'data/raw/sample').rglob('*.json'))\nassert 0 < len(files) <= 10\naudit = inspect_trial(files[0])\n{k: {'present': v['present'], 'hz': v['sampling_hz'], 'markers': len(v['trajectories']), 'warnings': v['warnings']} for k,v in audit['tasks'].items()}", "audit['tasks']['running']['trajectories'][:5]", "audit['tasks']['running']['calculated_variables'][:10]"]),
        ("03_running_cohort_definition", "Reproducible candidate cohort", [setup, "import json\nfrom src.data.validation import build_cohort\nindex = json.loads((ROOT / 'data/interim/provenance/ric_data_index.json').read_text())\ncohort = build_cohort(df, {r['filename'] for r in index})\ncandidate = first_observation(cohort[cohort.candidate_included])\n{'candidate_participants': len(candidate), 'candidate_observations': int(cohort.candidate_included.sum()), 'full_usable_running_count': None}", "cohort.groupby(['injury_status','candidate_included'], dropna=False).size()"]),
    ]
    (ROOT / "notebooks").mkdir(exist_ok=True)
    for name, title, code in notebooks:
        path = ROOT / "notebooks" / (name + ".ipynb")
        if path.exists():
            continue
        book = nbf.v4.new_notebook()
        book.cells = [nbf.v4.new_markdown_cell(f"# {title}\n\nMilestone 1 only. See the generated report and docs for source/version, units, exclusions and denominators. This notebook calls reusable src functions. Candidate membership is not full raw biomechanical QC. No causal or prospective injury claims.")]
        book.cells += [nbf.v4.new_code_cell(cell) for cell in code]
        book.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
        nbf.write(book, path)
    deferred = ["04_discrete_kinematic_eda", "05_waveform_analysis", "06_injury_group_comparison", "07_biomechanical_phenotypes", "08_classification_exploration", "09_clinical_interpretation"]
    for name in deferred:
        path = ROOT / "notebooks" / (name + ".ipynb")
        if not path.exists():
            book = nbf.v4.new_notebook(cells=[nbf.v4.new_markdown_cell(f"# {name[3:].replace('_', ' ').title()}\n\n**Planned, not executed. Review gate: stop after Milestone 1.**\n\nThis phase requires review of the cohort, metadata quality, official processing definitions, confounders and usable-cycle criteria. No analysis or results are claimed here.")])
            book.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
            nbf.write(book, path)
    reserved = {"biomechanics": ["gait_cycles", "joint_angles", "discrete_features", "waveform_features"], "features": ["demographics", "running_features", "biomechanical_features"], "analysis": ["statistics", "dimensionality", "clustering"], "models": ["classification", "validation"], "visualization": ["gait_plots"]}
    for directory, names in reserved.items():
        folder = ROOT / "src" / directory
        folder.mkdir(exist_ok=True)
        init = folder / "__init__.py"
        if not init.exists():
            init.write_text('"""Reserved for later reviewed milestones."""\n', encoding="utf-8")
        for name in names:
            path = folder / (name + ".py")
            if not path.exists():
                path.write_text('"""Planned module: ' + name + '.\n\nMilestone 1 review required before implementation. No advanced analysis runs here.\n"""\n', encoding="utf-8")
    for folder in ["data/raw", "data/interim", "data/processed", "reports/figures", "reports/tables"]:
        (ROOT / folder / ".gitkeep").touch(exist_ok=True)


if __name__ == "__main__":
    main()
