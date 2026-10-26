"""Execute the RIC reference source with fully recorded Octave compatibility edits."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import zlib

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "data/raw/official_code/Supplemental_materials/Code"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare_reference():
    originals = [ORIGINAL / name for name in ["gait_kinematics.m", "gait_steps.m", "pca_td.m", "pca_to.m", "event_data_TD.mat", "event_data_TO.mat", "LICENSE.txt"]]
    assets = sorted((ROOT / "src/biomechanics/octave_compat").glob("*.m"))
    index = {row["filename"]: row for row in json.loads((ROOT / "data/interim/provenance/Supplemental_materials_index.json").read_text())}
    for path in originals:
        if zlib.crc32(path.read_bytes()) != index["Supplemental_materials/Code/" + path.name]["crc32"]:
            raise ValueError("Official source integrity check failed")
    inputs = {path.relative_to(ROOT).as_posix(): digest(path) for path in originals + assets + [Path(__file__)]}
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    folder = ROOT / "data/interim/event_validation" / ("reference_" + key[:16])
    code = folder / "code"
    code.mkdir(parents=True, exist_ok=True)
    for path in originals:
        (code / path.name).write_bytes(path.read_bytes())
    source = (ORIGINAL / "gait_steps.m").read_text(encoding="utf-8-sig")
    first = source.index("import classreg.learning.classif.CompactClassificationDiscriminant")
    last = source.index("label = label{1};", first) + len("label = label{1};")
    removed = source[first:last]
    source = source[:first] + "label = 'run'; % Known pilot task; proprietary MATLAB classifier bypassed" + source[last:]
    if source.count("drop_plot = 1;") != 1:
        raise ValueError("Expected one plotting-only source switch")
    source = source.replace("drop_plot = 1;", "drop_plot = 0; % Headless plotting only; numerical rules unchanged")
    (code / "gait_steps.m").write_text(source, encoding="utf-8")
    for path in assets:
        (code / path.name).write_bytes(path.read_bytes())
    manifest = {"reference_id": key, "source_and_adapter_sha256": inputs,
                "engine": "GNU Octave 11.3.0; not a native MATLAB execution",
                "gait_mode": "run, fixed from reviewed running-only input branch",
                "adaptations": [
                    {"kind": "proprietary_gait_classifier_bypass", "removed_exact_source": removed, "replacement": "label = 'run'"},
                    {"kind": "plotting_only", "replacement": "drop_plot = 0"},
                    {"kind": "runtime_compatibility", "files": [p.name for p in assets],
                     "description": "Restricted signed-signal findpeaks, missing-value reductions, no-op MATLAB acceleration toggle; all tracked as source assets"}],
                "unchanged_equations": ["gait_kinematics.m", "pca_td.m", "pca_to.m", "event_data_TD.mat", "event_data_TO.mat"],
                "native_matlab_parity": "not established", "forceplate_ground_truth": False}
    (folder / "adaptation_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (ROOT / "reports/tables/event_reference_adaptations.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return folder, code, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=30, choices=range(1,31))
    args = parser.parse_args()
    runtime = json.loads((ROOT / ".tools/reference_runtime/runtime_manifest.json").read_text())
    folder, code, adaptation = prepare_reference()
    acquisition = json.loads((ROOT / "data/interim/provenance/pilot_acquisition.json").read_text())
    jobs = []
    for row in acquisition["records"][:args.limit]:
        if row["status"] != "verified" or digest(ROOT / row["path"]) != row["sha256"]:
            raise ValueError("Pilot source no longer matches its acquisition hash")
        jobs.append({"participant_id": row["participant_id"], "filename": row["filename"],
                     "raw_path": (ROOT / row["path"]).as_posix(),
                     "output_path": (folder / (row["participant_id"] + "_" + row["filename"].replace(".json", ".mat"))).as_posix()})
    jobs_path = folder / "jobs.json"
    jobs_path.write_text(json.dumps(jobs, indent=2), encoding="utf-8")
    quote = lambda value: str(value).replace("'", "''")
    expression = f"addpath('{quote(code.as_posix())}'); run_reference('{quote(ROOT.as_posix())}','{quote(jobs_path.as_posix())}','{quote(code.as_posix())}');"
    env = os.environ.copy()
    env["OCTAVE_HISTFILE"] = str(folder / "octave_history")
    env["OPENBLAS_NUM_THREADS"] = "1"
    process = subprocess.Popen([str(ROOT / runtime["executable"]), "--no-gui", "--no-history", "--quiet", "--eval", expression],
                               cwd=code, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    with (folder / "execution.log").open("w", encoding="utf-8") as log:
        for line in process.stdout:
            log.write(line)
            log.flush()
            print(line.rstrip(), flush=True)
    status = process.wait()
    results = [{"participant_id": j["participant_id"], "filename": j["filename"], "reference_path": str(Path(j["output_path"]).relative_to(ROOT)),
                "status": "completed" if Path(j["output_path"]).exists() else "failed"} for j in jobs]
    pointer = {"reference_id": adaptation["reference_id"], "reference_directory": folder.relative_to(ROOT).as_posix(),
               "jobs": results, "process_exit_code": status, "runtime_version": runtime["version"]}
    (ROOT / "reports/tables/event_reference_execution.json").write_text(json.dumps(pointer, indent=2), encoding="utf-8")
    print(json.dumps(pointer, indent=2), flush=True)
    if status or any(j["status"] != "completed" for j in results):
        raise RuntimeError("Some reference executions failed; inspect the recorded errors/log, not silent omissions")


if __name__ == "__main__":
    main()
