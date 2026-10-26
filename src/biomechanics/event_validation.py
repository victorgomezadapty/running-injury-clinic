"""Cross-engine numerical comparisons and source-cycle traceability checks.

Algorithmic consistency is distinct from force/pressure-based ground truth.
"""
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.signal import butter, filtfilt, find_peaks

ANGLE_ATOL_DEG = 1e-7
PCA_ATOL_FRAMES = 1e-5
STANCE_ATOL_DEG = 1e-6


def independent_heel_events(data):
    hz = float(data["hz_r"])
    b, a = butter(2, 5 / (hz / 2))
    result = {}
    left_heel = None
    for side in ["L", "R"]:
        neutral = np.stack([np.asarray(data["neutral"][f"{side}_foot_{i}"], float).reshape(3) for i in [1,2,3]])
        order = np.argsort(neutral[:,0], kind="stable")
        candidates = order[1:3] if side == "L" else order[:2]
        marker = candidates[0] if neutral[candidates[0],1] < neutral[candidates[1],1] else candidates[1]
        heel = np.asarray(data["running"][f"{side}_foot_{marker+1}"], float)
        if side == "L":
            left_heel = heel
        filtered = filtfilt(b, a, heel[:,2], padlen=3*(max(len(a),len(b))-1))
        result[side + "_TD"] = find_peaks(-filtered, distance=int(round(.35*hz)))[0] + 1
        result[side + "_TO"] = find_peaks(filtered, distance=int(round(.35*hz)))[0] + 1
    positions, _ = find_peaks(np.diff(left_heel[:,2]), distance=int(round(.5*hz)), height=0)
    result["independent_speed_m_s"] = float(hz * np.median(np.diff(left_heel[:,2])[positions]) / 1000)
    return result


def support_final_events(events, flags, candidates, baseline):
    rows = []
    for column, name in enumerate(["L_TD", "L_TO", "R_TD", "R_TO"]):
        for j, frame in enumerate(events[:,column]):
            flag = flags[j,column] if flags.shape == events.shape else np.nan
            predicted = candidates.get(name, np.array([])) if flag == 1 else baseline.get(name, np.array([]))
            error = float(np.min(np.abs(np.asarray(predicted)-frame))) if len(predicted) else None
            tolerance = .500001 if flag == 1 else 1.0
            rows.append({"event_row": j+1, "event": name, "frame_1based": float(frame),
                         "source_pca_flag": int(flag) if np.isfinite(flag) else None,
                         "nearest_independent_candidate_error_frames": error,
                         "tolerance_frames": tolerance,
                         "supported_by_independent_signal": bool(flag in [0,1] and error is not None and error <= tolerance)})
    return rows


def normalize_and_match(angles, events, reference_norm):
    """Match each retained source stance to independently interpolated raw angles.

    Do not assume the official rejection function preserves unique cycle IDs.
    Repeated matches are reported as duplicates rather than new usable cycles.
    """
    matches, counts, reconstructed_norm, retained_sets = [], [], {}, {}
    for side, prefix, td_col, to_col in [("left","L",0,1),("right","R",2,3)]:
        for joint in ["ankle", "knee", "hip"]:
            key = prefix + "_" + joint
            candidates, original_ids = [], []
            for j, (td, toe) in enumerate(events[:,[td_col,to_col]]):
                if not np.isfinite([td,toe]).all() or not (1 <= td < toe <= len(angles[key])):
                    continue
                td, toe = int(td), int(toe)
                curve = PchipInterpolator(np.arange(td,toe+1),angles[key][td-1:toe],axis=0)(np.linspace(td,toe,101))
                candidates.append(curve)
                original_ids.append(j+1)
            source = np.asarray(reference_norm[key], float)
            if source.ndim == 2 and source.shape == (101,3):
                source = source[:,None,:]
            if source.ndim != 3 or source.shape[0] != 101 or source.shape[2] != 3 or not candidates:
                raise ValueError("Invalid/empty normalized stance array: " + key)
            all_curves = np.stack(candidates,axis=1)
            mapped, rebuilt, errors = [], [], []
            for k in range(source.shape[1]):
                costs = np.max(np.abs(all_curves-source[:,k:k+1,:]),axis=(0,2))
                best = int(np.argmin(costs))
                error = float(costs[best])
                event_id = original_ids[best]
                matches.append({"side": side, "joint": joint, "retained_curve_index": k+1,
                                "matched_event_row": event_id, "maximum_curve_error_deg": error,
                                "numerical_match": bool(np.isfinite(error) and error <= STANCE_ATOL_DEG)})
                mapped.append(event_id)
                rebuilt.append(all_curves[:,best,:])
                errors.append(error)
            reconstructed_norm[key] = np.stack(rebuilt,axis=1)
            retained_sets[key] = set(mapped)
            counts.append({"side": side, "joint": joint, "source_retained_entries": len(mapped),
                           "unique_event_stances": len(set(mapped)), "duplicate_retained_entries": len(mapped)-len(set(mapped)),
                           "maximum_curve_error_deg": max(errors) if errors else None})
    common = {}
    for side, prefix in [("left","L"),("right","R")]:
        matched = set.intersection(*(retained_sets[prefix+"_"+joint] for joint in ["ankle","knee","hip"]))
        common[side] = sorted(row for row in matched if row < len(events))
    return matches, counts, reconstructed_norm, common


def independently_aggregate(norm, events, hz, speed):
    """The 13 whitelisted definitions, calculated without MATLAB source calls."""
    result = {}
    for side, prefix, td_col, to_col in [("left","L",0,1),("right","R",2,3)]:
        td, toe = events[:,td_col], events[:,to_col]
        ankle, knee, hip = [norm[prefix+"_"+joint] for joint in ["ankle","knee","hip"]]
        left = side == "left"
        result[side] = {
            "STRIDE_RATE": float(np.median(60*hz/np.diff(td))),
            "STRIDE_LENGTH": float(np.median(speed*np.diff(td)/hz)),
            "SWING_TIME": float(np.nanmedian((td[1:]-toe[:-1])/hz)),
            "STANCE_TIME": float(np.nanmedian((toe-td)/hz)),
            "ANKLE_DF_PEAK_ANGLE": float(-np.median(np.min(ankle[:,:,2],axis=0))),
            "ANKLE_EVE_PEAK_ANGLE": float(np.median(np.min(ankle[:,:,0],axis=0)) if left else -np.median(np.max(ankle[:,:,0],axis=0))),
            "ANKLE_ROT_PEAK_ANGLE": float(np.median(np.min(ankle[:,:,1],axis=0)) if left else -np.median(np.max(ankle[:,:,1],axis=0))),
            "KNEE_FLEX_PEAK_ANGLE": float(-np.median(np.max(knee[:70,:,2],axis=0))),
            "KNEE_ADD_PEAK_ANGLE": float(np.median(np.max(knee[:,:,0],axis=0)) if left else -np.median(np.min(knee[:,:,0],axis=0))),
            "KNEE_ROT_PEAK_ANGLE": float(np.median(np.max(knee[:,:,1],axis=0)) if left else -np.median(np.min(knee[:,:,1],axis=0))),
            "HIP_EXT_PEAK_ANGLE": float(-np.median(np.max(hip[:,:,2],axis=0))),
            "HIP_ADD_PEAK_ANGLE": float(np.median(np.max(hip[:60,:,0],axis=0)) if left else -np.median(np.min(hip[:60,:,0],axis=0))),
            "HIP_ROT_PEAK_ANGLE": float(np.median(np.max(hip[:,:,1],axis=0)) if left else -np.median(np.min(hip[:,:,1],axis=0))),
        }
    return result
