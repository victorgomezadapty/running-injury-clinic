import unittest
import pandas as pd
from src.analysis.cohort_readiness import group_balance, plan_pilot


class ReadinessTests(unittest.TestCase):
    def test_balance_sign_and_missing_values(self):
        data = pd.DataFrame({"injury_status": ["healthy", "healthy", "injured", "injured"],
                             "speed_m_s": [2., 3., 1., 2.], "age_analysis": [20., 30., 20., None],
                             "Height_analysis": [170., 180., 170., 180.], "Weight_analysis": [60., 70., 60., 70.],
                             "YrsRunning_analysis": [2., 4., 2., 4.]})
        result = group_balance(data).set_index("variable")
        self.assertLess(result.loc["speed_m_s", "standardized_mean_difference"], 0)
        self.assertEqual(result.loc["age_analysis", "injured_n"], 1)
        self.assertEqual(result.loc["Height_analysis", "standardized_mean_difference"], 0)

    def test_planned_pilot_is_deterministic_unique_and_not_source_order_dependent(self):
        from pathlib import Path
        from src.data.load_metadata import load_metadata, first_observation
        from src.data.validation import add_quality_flags, build_cohort
        import json
        root = Path(__file__).resolve().parents[1]
        data = add_quality_flags(load_metadata(root / "data/raw"))
        paths = {r["filename"] for r in json.loads((root / "data/interim/provenance/ric_data_index.json").read_text())}
        rows = build_cohort(data, paths)
        candidate = first_observation(rows[rows.candidate_included])
        pilot = plan_pilot(candidate)
        again = plan_pilot(candidate.sample(frac=1, random_state=7))
        self.assertEqual(pilot.participant_id.tolist(), again.participant_id.tolist())
        self.assertEqual(pilot.participant_id.nunique(), 30)
        self.assertEqual(pilot.injury_status.value_counts().to_dict(), {"healthy": 15, "injured": 15})
        self.assertTrue(set(pilot.participant_id).issubset(set(candidate.participant_id)))
