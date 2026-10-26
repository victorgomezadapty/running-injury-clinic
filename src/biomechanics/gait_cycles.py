"""Independent PCA-event calculation and cycle-order audit for the 200-Hz pilot.

PCA weights are the supplied fixed detection models, not an injury classifier.
All public event indices in this module use MATLAB's one-based frame convention.
"""
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from scipy.signal import find_peaks


def _peaks(signal, distance, height):
    peaks, _ = find_peaks(signal, height=height, distance=distance)
    return peaks


def pca_candidates(angles, hz, code_folder, gait="run"):
    if hz != 200 or gait != "run":
        raise ValueError("Independent parity implementation is restricted to the 200-Hz running pilot")
    td = loadmat(Path(code_folder) / "event_data_TD.mat")
    to = loadmat(Path(code_folder) / "event_data_TO.mat")
    result = {}
    for side in ["L", "R"]:
        acceleration = [np.diff(angles[f"{side}_{joint}"][:, 2], n=2) for joint in ["foot", "ankle", "knee", "hip"]]
        negative = -acceleration[0]
        first = _peaks(negative, 100, .1)
        mask = np.zeros(len(negative))
        for position in first:
            mask[position:min(position + 36, len(mask))] = 1
        locations = _peaks(-negative * mask, 100, .01)
        signals = np.zeros((len(locations), 284))
        for j in range(1, len(locations) - 1):
            centre = locations[j]
            chunks = [x[centre - 35:centre + 36] for x in acceleration]
            if any(len(x) != 71 for x in chunks):
                raise ValueError("Insufficient touchdown model window")
            signals[j] = np.concatenate(chunks)
        projected = signals @ td["coeff"]
        result[side + "_TD"] = (np.polyval(td["p"].ravel(), projected[:, 1]) + locations + 1)[1:-1]
        locations = _peaks(-angles[side + "_foot"][:, 2], 100, 20)
        signals = np.zeros((len(locations), 284))
        for j in range(1, len(locations) - 1):
            centre = locations[j]
            chunks = [x[centre - 70:centre + 1] for x in acceleration]
            if any(len(x) != 71 for x in chunks):
                raise ValueError("Insufficient toe-off model window")
            signals[j] = np.concatenate(chunks)
        projected = signals @ to["coeff"]
        result[side + "_TO"] = (-np.polyval(to["pRun"].ravel(), projected[:, 2]) + locations + 1)[1:-1]
    return result


def audit_cycles(events, flags, nframes, hz):
    events, flags = np.asarray(events, dtype=float), np.asarray(flags, dtype=float)
    if events.ndim != 2 or events.shape[1] != 4 or len(events) < 2:
        raise ValueError("Official output has fewer than two complete ordered event rows")
    rows = []
    for side, td_col, to_col in [("left", 0, 1), ("right", 2, 3)]:
        td, toe = events[:, td_col], events[:, to_col]
        for j in range(len(td) - 1):
            start, off, end = td[j], toe[j], td[j + 1]
            valid = np.isfinite([start, off, end]).all() and 1 <= start < off < end <= nframes
            method_td = int(flags[j, td_col]) if flags.shape == events.shape else None
            method_to = int(flags[j, to_col]) if flags.shape == events.shape else None
            rows.append({"side": side, "cycle_index": j + 1, "td_frame_1based": start,
                         "to_frame_1based": off, "next_td_frame_1based": end,
                         "ordered_in_bounds": bool(valid), "stance_s": (off - start) / hz,
                         "swing_s": (end - off) / hz, "stride_s": (end - start) / hz,
                         "td_pca_used": method_td, "to_pca_used": method_to,
                         "source": "official_algorithm_reference_events", "ground_truth_force_events": False})
    return rows
