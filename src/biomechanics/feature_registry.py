"""Small, source-checked feature whitelist. No sign changes or angle reconstruction."""
from pathlib import Path
import hashlib
import re
import zlib
import json

CODE_RELATIVE = "data/raw/official_code/Supplemental_materials/Code"
SPECS = [
    ("STRIDE_RATE", 3, "spatiotemporal", "strides/min", "successive ipsilateral touchdowns", "Median of 60*hz/diff(TD); not steps/min and not Hz"),
    ("STRIDE_LENGTH", 4, "spatiotemporal", "m", "successive ipsilateral touchdowns", "Median of source heel-derived speed * diff(TD)/hz"),
    ("SWING_TIME", 5, "spatiotemporal", "s", "toe-off to next ipsilateral touchdown", "Median swing-frame interval / hz"),
    ("STANCE_TIME", 6, "spatiotemporal", "s", "touchdown to toe-off", "Median stance-frame interval / hz"),
    ("ANKLE_DF_PEAK_ANGLE", 11, "ankle", "deg", "whole normalized stance", "Negative median of per-stance minimum axis-3 angle; both sides"),
    ("ANKLE_EVE_PEAK_ANGLE", 15, "ankle", "deg", "whole normalized stance", "Left median minimum axis 1; right negative median maximum axis 1"),
    ("ANKLE_ROT_PEAK_ANGLE", 19, "ankle", "deg", "whole normalized stance", "Preserve exact source left/right rotation convention; see source expressions"),
    ("KNEE_FLEX_PEAK_ANGLE", 23, "knee", "deg", "first 70 of 101 normalized stance samples", "Negative median of per-stance axis-3 maximum in samples 1:70; negative values are allowed"),
    ("KNEE_ADD_PEAK_ANGLE", 27, "knee", "deg", "whole normalized stance", "Left median maximum axis 1; right negative median minimum axis 1"),
    ("KNEE_ROT_PEAK_ANGLE", 35, "knee", "deg", "whole normalized stance", "Left median maximum axis 2; right negative median minimum axis 2"),
    ("HIP_EXT_PEAK_ANGLE", 39, "hip", "deg", "whole normalized stance", "Negative median of per-stance maximum axis-3 angle; both sides"),
    ("HIP_ADD_PEAK_ANGLE", 43, "hip", "deg", "first 60 of 101 normalized stance samples", "Left median maximum axis 1; right negative median minimum axis 1; samples 1:60"),
    ("HIP_ROT_PEAK_ANGLE", 47, "hip", "deg", "whole normalized stance", "Left median maximum axis 2; right negative median minimum axis 2; do not relabel as generic internal rotation"),
]


def normalized_label(label):
    return label.replace("%", "percent_").replace("@", "at_").replace(" ", "_")


def build_registry(root):
    folder = Path(root) / CODE_RELATIVE
    code = (folder / "gait_steps.m").read_text(encoding="utf-8-sig")
    kinematics = (folder / "gait_kinematics.m").read_text(encoding="utf-8-sig")
    index = {i["filename"]: i for i in json.loads((Path(root) / "data/interim/provenance/Supplemental_materials_index.json").read_text())}
    for name in ["gait_steps.m", "gait_kinematics.m"]:
        content = (folder / name).read_bytes()
        if zlib.crc32(content) != index["Supplemental_materials/Code/" + name]["crc32"]:
            raise ValueError("Official processing source differs from the pinned supplement")
    if "* (180/pi)" not in kinematics or "60*hz./diff(L_TD(:))" not in code:
        raise ValueError("Required angle-unit / stride-rate source evidence missing")
    lines = code.splitlines()
    headings = [(n, re.match(r"^%\s*(\d+)%\s*'([^']+)'", text)) for n, text in enumerate(lines, 1)]
    headings = [(line, int(match[1]), match[2]) for line, match in headings if match]
    active = "\n".join(line for line in lines if not line.lstrip().startswith("%"))
    assigned = {int(n) for n in re.findall(r"DISCRETE_VARIABLES\(\s*(\d+)\s*,", active)}
    placeholders = [normalized_label(label) for _, row, label in headings if row != 1 and row not in assigned]
    records = []
    for key, row, domain, unit, phase, definition in SPECS:
        heading = next((h for h in headings if h[1] == row), None)
        if heading is None or normalized_label(heading[2]) != key or row not in assigned:
            raise ValueError(f"Feature has no matching implemented official definition: {key}")
        start = heading[0]
        stop = next((line - 1 for line, _, _ in headings if line > start), len(lines))
        block = lines[start - 1:stop]
        expressions = [line.strip() for line in block if re.match(r"\s*(temp\s*=|DISCRETE_VARIABLES\()", line)]
        records.append({"feature": key, "domain": domain, "unit": unit, "source_matrix_row": row,
                        "phase": phase, "definition": definition, "source_line_start": start, "source_line_end": stop,
                        "source_expressions": " | ".join(expressions),
                        "source_code": (Path(CODE_RELATIVE) / "gait_steps.m").as_posix(),
                        "source_code_sha256": hashlib.sha256((folder / "gait_steps.m").read_bytes()).hexdigest(),
                        "transformation": "identity; preserve upstream scalar and sign",
                        "verification_scope": "source definition / units checked; event and reconstruction parity unverified"})
    return records, placeholders
