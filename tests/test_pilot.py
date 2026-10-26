from pathlib import Path
import copy
import json
import unittest
import pandas as pd
from src.biomechanics.feature_registry import build_registry
from src.biomechanics.pilot_qc import structural_qc, extract_source_features
from src.data.load_trials import load_trial

ROOT = Path(__file__).resolve().parents[1]


class PilotUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry, cls.placeholders = build_registry(ROOT)
        cls.path = next((ROOT / "data/raw/sample").rglob("*.json"))
        cls.data = load_trial(cls.path)
        dv = cls.data["dv_r"]["left"]
        cls.speed = dv["STRIDE_LENGTH"] * dv["STRIDE_RATE"] / 60

    def test_registry_excludes_unassigned_fields_and_checks_units(self):
        registry = {r["feature"]: r for r in self.registry}
        self.assertEqual(len(registry), 13)
        self.assertEqual(registry["STRIDE_RATE"]["unit"], "strides/min")
        self.assertIn("ANKLE_DF_percent_STANCE", self.placeholders)
        self.assertFalse(set(registry) & set(self.placeholders))
        self.assertIn("first 70", registry["KNEE_FLEX_PEAK_ANGLE"]["phase"])

    def test_original_negative_knee_flexion_and_stride_unit_are_preserved(self):
        rows, _ = extract_source_features(self.data, self.registry, "structural_pass", self.speed)
        knee = next(r for r in rows if r["side"] == "left" and r["feature"] == "KNEE_FLEX_PEAK_ANGLE")
        self.assertLess(knee["value"], 0)
        self.assertEqual(knee["value"], self.data["dv_r"]["left"]["KNEE_FLEX_PEAK_ANGLE"])
        self.assertEqual(knee["analysis_value"], knee["value"])
        stride = next(r for r in rows if r["side"] == "left" and r["feature"] == "STRIDE_RATE")
        self.assertEqual(stride["value"], self.data["dv_r"]["left"]["STRIDE_RATE"])

    def test_missing_zero_and_nonfinite_slots_are_retained_and_flagged(self):
        data = {**self.data, "dv_r": copy.deepcopy(self.data["dv_r"])}
        del data["dv_r"]["left"]["HIP_ADD_PEAK_ANGLE"]
        data["dv_r"]["left"]["STRIDE_RATE"] = float("nan")
        data["dv_r"]["right"]["HIP_EXT_PEAK_ANGLE"] = 0
        rows, _ = extract_source_features(data, self.registry, "structural_pass", self.speed)
        self.assertEqual(len(rows), 26)
        lookup = {(r["side"], r["feature"]): r for r in rows}
        self.assertEqual(lookup["left", "HIP_ADD_PEAK_ANGLE"]["value_qc"], "missing_source_field")
        self.assertIsNone(lookup["left", "STRIDE_RATE"]["value"])
        zero = lookup["right", "HIP_EXT_PEAK_ANGLE"]
        self.assertEqual(zero["value"], 0)
        self.assertIsNone(zero["analysis_value"])
        self.assertEqual(zero["value_qc"], "zero_angle_requires_review")

    def test_missing_markers_and_nonfinite_rate_cannot_pass_structural_checks(self):
        data = {**self.data, "running": dict(self.data["running"]), "hz_r": float("nan")}
        del data["running"]["L_foot_1"]
        qc = structural_qc(data, self.path)
        self.assertEqual(qc["status"], "review_required")
        self.assertIn("invalid_sampling_frequency", qc["flags"])
        self.assertIsNone(qc["valid_cycle_count"])

    def test_temporal_inconsistency_does_not_silently_correct_original_values(self):
        data = {**self.data, "dv_r": copy.deepcopy(self.data["dv_r"])}
        original = data["dv_r"]["left"]["STANCE_TIME"] = 9.0
        rows, consistency = extract_source_features(data, self.registry, "structural_pass", self.speed)
        self.assertTrue(next(r for r in consistency if r["side"] == "left")["review_required"])
        stance = next(r for r in rows if r["side"] == "left" and r["feature"] == "STANCE_TIME")
        self.assertEqual(stance["value"], original)
        self.assertIsNone(stance["analysis_value"])


class PilotIntegrationTests(unittest.TestCase):
    def test_exports_are_exactly_grouped_by_participant_file_side(self):
        data = pd.read_csv(ROOT / "data/processed/pilot_features_long.csv", dtype={"participant_id": "string"})
        self.assertEqual(len(data), 780)
        self.assertEqual(data.participant_id.nunique(), 30)
        self.assertFalse(data.duplicated(["participant_id", "filename", "side", "feature"]).any())
        self.assertTrue(data.groupby("participant_id").size().eq(26).all())
        self.assertTrue(data.loc[data.provisionally_available, "analysis_value"].notna().all())
        self.assertTrue(data.loc[~data.provisionally_available, "analysis_value"].isna().all())

    def test_pilot_does_not_claim_unavailable_event_validation(self):
        summary = json.loads((ROOT / "reports/tables/pilot_summary.json").read_text())
        self.assertEqual((summary["healthy"], summary["injured"]), (15, 15))
        self.assertEqual(summary["independently_validated_events_trials"], 0)
        self.assertIsNone(summary["fully_biomechanically_usable_running_count"])
        journal = json.loads((ROOT / "data/interim/provenance/pilot_acquisition.json").read_text())
        self.assertEqual(len(journal["records"]), 30)
        self.assertTrue(all(r["status"] == "verified" for r in journal["records"]))
