"""Inspect one RIC JSON at a time. No coordinate transformations."""
import json
from pathlib import Path
import numpy as np

# Seven tracked segments, four positions per segment in the official code.
# Some fourth markers are constructed by the upstream processing workflow.
CORE_TRACKING = {f"{segment}_{i}" for segment in ["pelvis", "L_thigh", "R_thigh", "L_shank", "R_shank", "L_foot", "R_foot"] for i in range(1, 5)}


def load_trial(path: str | Path, max_bytes=150_000_000):
    path = Path(path)
    if path.stat().st_size > max_bytes:
        raise ValueError("Trial exceeds configured in-memory size limit")
    with path.open(encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Expected a top-level JSON object")
    return data


def inventory_node(value, path="", records=None):
    """Report shapes and non-finite coordinates, preserving native field paths."""
    records = [] if records is None else records
    if isinstance(value, dict):
        for key, child in value.items():
            inventory_node(child, f"{path}.{key}".strip("."), records)
    elif isinstance(value, list):
        try:
            arr = np.asarray(value, dtype=float)
            record = {"path": path, "shape": list(arr.shape), "n_values": int(arr.size), "nonfinite": int((~np.isfinite(arr)).sum()), "all_zero": bool(arr.size and np.all(arr == 0)), "zero_xyz_frames": int(np.all(arr == 0, axis=1).sum()) if arr.ndim == 2 and arr.shape[1] == 3 else 0}
        except (TypeError, ValueError):
            record = {"path": path, "shape": [len(value)], "numeric": False}
        records.append(record)
    else:
        records.append({"path": path, "scalar": value})
    return records


def inspect_trial(path, data=None):
    data = load_trial(path) if data is None else data
    branches = {}
    for task, suffix in [("running", "r"), ("walking", "w")]:
        motion = data.get(task)
        present = motion is not None and motion != [] and motion != {}
        hz = data.get(f"hz_{suffix}")
        records = inventory_node(motion, task) if present else []
        missing = sorted(CORE_TRACKING - set(motion)) if isinstance(motion, dict) else sorted(CORE_TRACKING)
        lengths = sorted({r["shape"][0] for r in records if len(r.get("shape", [])) == 2})
        variables = data.get(f"dv_{suffix}")
        branches[task] = {"present": present, "sampling_hz": hz, "trajectories": records,
            "missing_core_tracking_fields": missing if present else [], "frame_counts": lengths,
            "calculated_variables": inventory_node(variables, f"dv_{suffix}"),
            "calculated_variable_keys": list(variables) if isinstance(variables, dict) else [],
            "warnings": (["missing_or_nonpositive_sampling_rate"] if present and (not isinstance(hz, (float, int)) or hz <= 0) else []) +
                [f"nonfinite:{r['path']}" for r in records if r.get("nonfinite", 0)] +
                [f"all_zero:{r['path']}" for r in records if r.get("all_zero", False)] +
                [f"empty:{r['path']}" for r in records if r.get("n_values") == 0] +
                [f"zero_xyz_frames:{r['path']}" for r in records if r.get("zero_xyz_frames", 0)] +
                [f"invalid_xyz_shape:{r['path']}" for r in records if len(r.get("shape", [])) != 2 or r["shape"][1] != 3] +
                (["inconsistent_frame_counts"] if len(lengths) > 1 else []) +
                (["missing_core_tracking:" + ",".join(missing)] if present and missing else [])}
    return {"file": str(path), "top_level_keys": list(data), "tasks": branches,
        "static_anatomical": inventory_node(data.get("joints"), "joints"),
        "static_tracking": inventory_node(data.get("neutral"), "neutral"),
        "embedded_qc_fields": [r for r in inventory_node(data) if any(s in r["path"].lower() for s in ["warning", "error", "quality", "flag"])],
        "interpretation": "Structural audit only; no assertion of clinically usable joint waveforms."}


def locate_trial(raw_dir, participant_id, filename):
    """Require participant ID AND timestamp filename; timestamp alone is unsafe."""
    matches = [p for p in Path(raw_dir).rglob(filename) if p.parent.name == str(participant_id)]
    if len(matches) > 1:
        raise ValueError("Ambiguous participant-file match")
    return matches[0] if matches else None
