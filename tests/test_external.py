from pathlib import Path
import unittest
from scripts.profile_external import load_external

ROOT = Path(__file__).resolve().parents[1]


class ExternalSourceTests(unittest.TestCase):
    def test_source_integrity_schema_and_identity_collision(self):
        data = load_external(ROOT)
        self.assertEqual(len(data), 1614)
        self.assertEqual(data.Subject.nunique(), 23)
        self.assertEqual(data.external_participant_id.nunique(), 46)
        self.assertEqual(data.groupby("Group").external_participant_id.nunique().to_dict(), {"BMC": 23, "RIC": 23})

    def test_absent_clinical_fields_are_not_invented(self):
        data = load_external(ROOT)
        self.assertFalse(set(data.columns) & {"InjDefn", "injury_status", "diagnosis", "Gender", "sub_id"})
        self.assertEqual(int(data.iloc[:, :8].isna().sum().sum()), 0)
