"""Tests focus on scientific misclassification, dependence and source integrity."""
import hashlib
import json
from pathlib import Path
import unittest
import zlib
import pandas as pd
from src.data.load_metadata import load_metadata, first_observation, injury_label
from src.data.validation import add_quality_flags, build_cohort
from src.data.load_trials import inspect_trial, locate_trial

ROOT = Path(__file__).resolve().parents[1]


class IngestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = add_quality_flags(load_metadata(ROOT / "data/raw"))

    def test_versioned_source_integrity(self):
        manifest = json.loads((ROOT / "data/interim/provenance/file_manifest.json").read_text())
        for entry in manifest:
            path = ROOT / "data/raw" / entry["name"]
            if path.is_file():
                self.assertEqual(path.stat().st_size, entry["size"])
                self.assertEqual(hashlib.md5(path.read_bytes()).hexdigest(), entry["computed_md5"])

    def test_participant_counts_and_shared_tasks(self):
        r = set(self.df.loc[self.df.task.eq("running"), "participant_id"])
        w = set(self.df.loc[self.df.task.eq("walking"), "participant_id"])
        self.assertEqual((len(r | w), len(r), len(w), len(r & w)), (1798, 1402, 1686, 1290))
        self.assertFalse(self.df.duplicated(["participant_id", "filename", "task"]).any())

    def test_missing_severity_cannot_create_control(self):
        row = dict(severity="unknown", joint="", diagnosis="", joint_secondary="", diagnosis_secondary="")
        self.assertEqual(injury_label(row), "unknown")
        row["severity"] = "no_injury"
        self.assertEqual(injury_label(row), "healthy")
        row["diagnosis_secondary"] = "achilles tendonitis"
        self.assertEqual(injury_label(row), "discordant")
        row["severity"] = "training_with_pain"
        self.assertEqual(injury_label(row), "injured")

    def test_invalid_values_are_flagged_without_source_mutation(self):
        bad = self.df[self.df.age_numeric.eq(255)]
        self.assertGreater(len(bad), 0)
        self.assertTrue(bad.age_qc_invalid.all())
        self.assertTrue(bad.age_analysis.isna().all())
        self.assertTrue(bad.age.eq("255").all())

    def test_recovered_timestamp_has_provenance(self):
        recovered = self.df[self.df.session_time_source.eq("filename_recovery")]
        self.assertGreater(len(recovered), 0)
        self.assertTrue(recovered.session_time.notna().all())
        self.assertTrue(recovered.datestring.eq("NaT").all())

    def test_earliest_selection_does_not_duplicate_participants(self):
        frame = pd.DataFrame({"participant_id": ["A", "A", "B"], "session_time": pd.to_datetime(["2022-01-03", "2021-01-03", "2023-01-03"]), "filename": ["later", "earlier", "other"]})
        first = first_observation(frame)
        self.assertEqual(len(first), 2)
        self.assertEqual(first.loc[first.participant_id.eq("A"), "filename"].item(), "earlier")

    def test_cohort_needs_exact_participant_file_archive_key(self):
        run = self.df[self.df.task.eq("running")].head(3)
        row = run.iloc[0]
        archive = {f"reformat_data/{row.participant_id}/{row.filename}"}
        cohort = build_cohort(run, archive)
        self.assertEqual(int(cohort.archive_file_present.sum()), 1)
        self.assertTrue(cohort.loc[~cohort.archive_file_present, "exclusion_reason"].str.contains("not_found_in_archive_index").all())

    def test_small_raw_sample_links_to_real_metadata(self):
        files = sorted((ROOT / "data/raw/sample").rglob("*.json"))
        self.assertGreaterEqual(len(files), 5)
        self.assertLessEqual(len(files), 10)
        for path in files:
            self.assertEqual(locate_trial(ROOT / "data/raw/sample", path.parent.name, path.name), path)
            match = self.df[(self.df.participant_id == path.parent.name) & (self.df.filename == path.name)]
            self.assertGreater(len(match), 0)
            audit = inspect_trial(path)
            for task, branch in audit["tasks"].items():
                if branch["present"]:
                    self.assertGreater(branch["sampling_hz"], 0)
                    self.assertTrue(all(len(r["shape"]) == 2 and r["shape"][1] == 3 for r in branch["trajectories"]))
                    self.assertIn(task, set(match.task))

    def test_sample_integrity_against_pinned_archive_index(self):
        index = {r["filename"]: r for r in json.loads((ROOT / "data/interim/provenance/ric_data_index.json").read_text())}
        for path in (ROOT / "data/raw/sample").rglob("*.json"):
            member = path.relative_to(ROOT / "data/raw/sample").as_posix()
            content = path.read_bytes()
            self.assertEqual(len(content), index[member]["size"])
            self.assertEqual(zlib.crc32(content), index[member]["crc32"])


if __name__ == "__main__":
    unittest.main()
