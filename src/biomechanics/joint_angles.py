"""Independent NumPy transcription of the supplied RIC kinematics equations.

Validation is against the original .m function executed in a separate engine.
Native XYZ, static definitions and angular signs are preserved; no filtering
or extra coordinate rotation is introduced.
"""
import numpy as np


def _unit(vector):
    vector = np.asarray(vector, dtype=float)
    norm = np.linalg.norm(vector)
    if not np.isfinite(norm) or norm <= 0:
        raise ValueError("Degenerate anatomical axis")
    return vector / norm


def reconstruct_angles(data):
    joints = {key: np.asarray(value, dtype=float).reshape(3) for key, value in data["joints"].items()}
    neutral = {key: np.asarray(value, dtype=float).reshape(3) for key, value in data["neutral"].items()}
    dynamic = data["running"]
    hz = float(data["hz_r"])
    centres = {}
    for side, other in [("L", "R"), ("R", "L")]:
        centres[side + "_hip"] = joints[side + "_hip"] + (joints[other + "_hip"] - joints[side + "_hip"]) / 4
        for joint in ["knee", "ankle"]:
            centres[side + "_" + joint] = (joints[f"{side}_lat_{joint}"] + joints[f"{side}_med_{joint}"]) / 2
    systems = {}
    for side in ["L", "R"]:
        foot = np.stack([neutral[f"{side}_foot_{k}"] for k in [1, 2, 3]])
        foot = foot[np.argsort(foot[:, 0], kind="stable")]
        temporary = _unit(foot[1] - foot[2] if side == "L" else foot[0] - foot[1])
        if temporary[1] < 0:
            temporary = -temporary
        x = np.array([0., 0., -1.])
        z = _unit(np.cross(x, temporary))
        y = _unit(np.cross(z, x))
        systems[side + "_foot"] = np.column_stack([x, y, z])
        for segment, upper, lower, marker in [("shank", "knee", "ankle", "ankle"), ("thigh", "hip", "knee", "knee")]:
            y = _unit(centres[f"{side}_{upper}"] - centres[f"{side}_{lower}"])
            temporary = _unit(joints[f"{side}_med_{marker}"] - joints[f"{side}_lat_{marker}"])
            if side == "R":
                temporary = -temporary
            x = _unit(np.cross(y, temporary))
            z = _unit(np.cross(x, y))
            systems[f"{side}_{segment}"] = np.column_stack([x, y, z])
    systems["pelvis"] = np.column_stack([[0., 0., -1.], [0., 1., 0.], [1., 0., 0.]])
    rotations = {}
    for segment, anatomical in systems.items():
        static = np.stack([neutral[f"{segment}_{k}"] for k in range(1, 5)], axis=1)
        local = anatomical.T @ static
        local -= local.mean(axis=1, keepdims=True)
        moving = np.stack([np.asarray(dynamic[f"{segment}_{k}"], dtype=float) for k in range(1, 5)], axis=2)
        moving -= moving.mean(axis=2, keepdims=True)
        covariance = moving @ local.T
        u, _, vh = np.linalg.svd(covariance)
        determinant = np.linalg.det(u @ vh)
        u[:, :, 2] *= determinant[:, None]
        rotations[segment] = u @ vh
    angles = {}
    for side in ["L", "R"]:
        r = rotations[side + "_foot"]
        angles[side + "_foot"] = np.column_stack([
            np.arctan2(r[:, 0, 1], np.hypot(r[:, 1, 1], r[:, 2, 1])),
            np.arctan2((-1 if side == "L" else 1) * r[:, 0, 0], np.hypot(r[:, 1, 0], r[:, 2, 0])),
            np.arctan2(r[:, 1, 0], -r[:, 2, 0])])
        for joint, proximal, distal in [("ankle", side + "_shank", side + "_foot"), ("knee", side + "_thigh", side + "_shank"), ("hip", "pelvis", side + "_thigh")]:
            relative = np.swapaxes(rotations[proximal], 1, 2) @ rotations[distal]
            angles[f"{side}_{joint}"] = np.column_stack([
                np.arctan2(relative[:, 1, 2], np.hypot(relative[:, 0, 2], relative[:, 2, 2])),
                np.arctan2(-relative[:, 0, 2], relative[:, 2, 2]),
                np.arctan2(-relative[:, 1, 0], relative[:, 1, 1])])
    r = rotations["pelvis"]
    angles["pelvis"] = np.column_stack([np.arctan2(r[:, 0, 2], r[:, 2, 2]) - np.pi / 2,
                                         np.arctan(r[:, 1, 2] / r[:, 0, 2]),
                                         np.arctan2(r[:, 1, 0], -r[:, 2, 0])])
    angles = {key: np.rad2deg(value) for key, value in angles.items()}
    velocities = {key: np.diff(value, axis=0) * hz for key, value in angles.items()}
    return angles, velocities
