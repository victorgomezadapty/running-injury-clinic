"""Structural and internal-consistency checks, not full gait-event validation."""
import math
from itertools import combinations
import numpy as np
from src.data.load_trials import CORE_TRACKING, inspect_trial

ANATOMICAL = {"L_hip", "R_hip", "L_lat_knee", "L_med_knee", "R_lat_knee", "R_med_knee", "L_lat_ankle", "L_med_ankle", "R_lat_ankle", "R_med_ankle"}
SEGMENTS = ["pelvis", "L_thigh", "R_thigh", "L_shank", "R_shank", "L_foot", "R_foot"]


def numeric_scalar(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def structural_qc(data, path):
    audit = inspect_trial(path, data=data)
    branch = audit["tasks"]["running"]
    flags = list(branch["warnings"])
    if not branch["present"]:
        flags.append("running_absent")
    if not numeric_scalar(branch["sampling_hz"]) or branch["sampling_hz"] <= 0:
        flags.append("invalid_sampling_frequency")
    for container, required in [("joints", ANATOMICAL), ("neutral", CORE_TRACKING)]:
        content = data.get(container)
        if not isinstance(content, dict):
            flags.append("missing_static:" + container)
            continue
        for marker in sorted(required):
            try:
                xyz = np.asarray(content[marker], dtype=float).reshape(-1)
                if xyz.shape != (3,) or not np.isfinite(xyz).all():
                    flags.append(f"invalid_static:{container}.{marker}")
            except (KeyError, ValueError, TypeError):
                flags.append(f"missing_or_invalid_static:{container}.{marker}")
    for a, b in [("L_hip", "R_hip"), ("L_lat_knee", "L_med_knee"), ("R_lat_knee", "R_med_knee"), ("L_lat_ankle", "L_med_ankle"), ("R_lat_ankle", "R_med_ankle")]:
        try:
            distance = np.linalg.norm(np.asarray(data["joints"][a], dtype=float) - np.asarray(data["joints"][b], dtype=float))
            if not np.isfinite(distance) or distance <= 0:
                flags.append("coincident_anatomical_markers:" + a + ":" + b)
        except (KeyError, TypeError, ValueError):
            pass  # Missing/invalid anatomical fields are already recorded above.
    geometry = []
    for segment in SEGMENTS:
        try:
            static = np.stack([np.asarray(data["neutral"][f"{segment}_{i}"], dtype=float).reshape(3) for i in range(1, 4)])
            if np.linalg.matrix_rank(static - static.mean(axis=0)) < 2:
                flags.append("degenerate_static_cluster:" + segment)
            relative_mads = []
            for a, b in combinations(range(1, 4), 2):
                left = np.asarray(data["running"][f"{segment}_{a}"], dtype=float)
                right = np.asarray(data["running"][f"{segment}_{b}"], dtype=float)
                distances = np.linalg.norm(left - right, axis=1)
                finite = distances[np.isfinite(distances)]
                median = np.median(finite) if len(finite) else 0
                relative_mads.append(float(np.median(np.abs(finite - median)) / median) if median > 0 else None)
            valid = [x for x in relative_mads if x is not None]
            maximum = max(valid) if valid else None
            geometry.append({"segment": segment, "maximum_pair_distance_relative_mad": maximum})
            if maximum is None or maximum > .05:
                flags.append("rigid_cluster_review:" + segment)
        except (KeyError, TypeError, ValueError, np.linalg.LinAlgError):
            geometry.append({"segment": segment, "maximum_pair_distance_relative_mad": None})
            flags.append("cluster_not_assessable:" + segment)
    frames = branch["frame_counts"][0] if len(branch["frame_counts"]) == 1 else None
    hz = branch["sampling_hz"]
    return {"status": "structural_pass" if not flags else "review_required", "flags": sorted(set(flags)),
            "sampling_hz": hz if numeric_scalar(hz) else None, "frames": frames,
            "time_span_s": (frames - 1) / hz if frames and numeric_scalar(hz) and hz > 0 else None,
            "tracking_markers": len(branch["trajectories"]), "geometry": geometry,
            "events_qc": "not_available_without_official_reprocessing", "valid_cycle_count": None,
            "audit": audit}


def extract_source_features(data, registry, trial_status, metadata_speed):
    """Preserve every expected feature slot, including absent/invalid values."""
    records, consistency = [], []
    dv = data.get("dv_r")
    for side in ["left", "right"]:
        values = dv.get(side, {}) if isinstance(dv, dict) else {}
        values = values if isinstance(values, dict) else {}
        for spec in registry:
            key = spec["feature"]
            value = values.get(key)
            if key not in values:
                status = "missing_source_field"
            elif not numeric_scalar(value):
                status = "nonfinite_or_nonscalar_source_value"
            elif spec["domain"] == "spatiotemporal" and value <= 0:
                status = "nonpositive_spatiotemporal_value"
            elif spec["unit"] == "deg" and value == 0:
                status = "zero_angle_requires_review"
            else:
                status = "source_scalar_checked"
            eligible = status == "source_scalar_checked" and trial_status == "structural_pass"
            records.append({"side": side, "feature": key, "unit": spec["unit"], "domain": spec["domain"],
                            "value": float(value) if numeric_scalar(value) else None, "raw_repr": repr(value)[:120],
                            "analysis_value": float(value) if eligible else None, "value_qc": status,
                            "provisionally_available": eligible, "phase": spec["phase"],
                            "events_qc": "unverified", "extraction": "upstream_dv_r_scalar_no_recomputation"})
        rate, stance, swing, length = [values.get(k) for k in ["STRIDE_RATE", "STANCE_TIME", "SWING_TIME", "STRIDE_LENGTH"]]
        duration_residual, length_residual = None, None
        if all(numeric_scalar(v) and v > 0 for v in [rate, stance, swing]):
            duration_residual = float(abs(stance + swing - 60 / rate) / (60 / rate))
        if all(numeric_scalar(v) and v > 0 for v in [rate, length, metadata_speed]):
            expected = metadata_speed * 60 / rate
            length_residual = float(abs(length - expected) / expected)
        consistency.append({"side": side, "stance_swing_period_relative_residual": duration_residual,
                            "stride_length_speed_relative_residual": length_residual,
                            "review_required": duration_residual is None or length_residual is None or duration_residual > .05 or length_residual > .05,
                            "interpretation": "5% engineering review trigger only; medians need not obey identities exactly"})
    side_reviews = {row["side"]: row["review_required"] for row in consistency}
    for record in records:
        record["temporal_consistency_review"] = side_reviews[record["side"]]
        if side_reviews[record["side"]]:
            record["provisionally_available"] = False
            record["analysis_value"] = None
    return records, consistency
