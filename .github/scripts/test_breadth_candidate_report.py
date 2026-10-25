import json
from pathlib import Path
import tempfile
import unittest

from breadth_candidate_report import summarize


class CandidateReportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.folder = self.root / "breadth-candidate-pilot-fd"
        (self.folder / "full-check").mkdir(parents=True)
        manifest = {"cores": 16, "host": "host", "projects": [{
            "id": "fd", "revision": "source", "lock_sha256": "lock",
            "correctness": [["test"]]}]}
        selection = {"pilot_scenarios": ["full-check"], "runner": "runner"}
        row = {"exit_code": 0, "wall_seconds": 1, "cpu_seconds": 2,
               "peak_job_memory_bytes": 3, "fresh_artifacts": 0, "compiled_artifacts": 1}
        checks = [{"exit_code": 0, "command": ["cargo", "test", "--frozen", "--target", "host"]}]
        self.write("current-candidate-corpus.json", manifest)
        self.write("custom-candidate.json", selection)
        self.write("toolchain.json", {"rustc_verbose_version": "rustc", "cargo_version": "cargo",
                                     "executables": {}, "installed_files": {}})
        self.write("pilot.json", {
            "status": "passed-candidate-only-pilot-not-comparative-qualification",
            "project": "fd", "run_id": "123", "attempt": "1",
            "scenarios": [{"name": "full-check", "measurement": row, "correctness": checks}]})
        self.write("full-check/results.json", {
            "status": "non-qualifying-smoke", "project": "fd", "source_revision": "source",
            "lock_sha256": "lock", "measurement": row, "correctness": checks})
        self.write("full-check/resolved-audit.json", {
            scope: {"package_count": 1, "phases": {
                "llvm": {"exact_locked_registry_or_git_reuse": ["dependency"]}}}
            for scope in ("selected_resolve", "observed_artifacts", "compiled_artifacts", "fresh_artifacts")
        })
        (self.folder / "full-check/correctness-0.stdout").write_text(
            "test result: ok. 10 passed; 0 failed; 2 ignored; 0 measured; 0 filtered out;\n")

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, name, value):
        (self.folder / name).write_text(json.dumps(value), encoding="utf-8")

    def change(self, name, key, value):
        data = json.loads((self.folder / name).read_text())
        data[key] = value
        self.write(name, data)

    def test_complete_report_preserves_scope_without_inventing_comparisons(self):
        report = summarize(self.root)
        self.assertEqual(report["rows"][0]["audit_scopes"]["compiled_artifacts"][
            "exact_training_fixture_lock_overlap"], {"llvm": 1})
        self.assertIsNone(report["comparative_effects"])
        self.assertIsNone(report["confidence_intervals"])
        self.assertEqual(len(report["evidence_sha256"]), 7)
        self.assertEqual(report["rows"][0]["test_counts"][0]["upstream_ignored"], 2)

    def test_failed_or_incomplete_pilot_is_not_a_complete_report(self):
        self.change("pilot.json", "status", "failed-candidate-pilot")
        with self.assertRaisesRegex(ValueError, "incomplete or failed"):
            summarize(self.root)

    def test_missing_project_is_rejected(self):
        data = json.loads((self.folder / "current-candidate-corpus.json").read_text())
        self.change("current-candidate-corpus.json", "projects", [*data["projects"], {"id": "missing"}])
        with self.assertRaisesRegex(ValueError, "missing projects"):
            summarize(self.root)

    def test_changed_or_omitted_correctness_is_rejected(self):
        self.change("full-check/results.json", "correctness", [])
        with self.assertRaisesRegex(ValueError, "inconsistent cell"):
            summarize(self.root)

    def test_filtered_test_output_is_rejected(self):
        (self.folder / "full-check/correctness-0.stdout").write_text(
            "test result: ok. 10 passed; 0 failed; 0 ignored; 0 measured; 1 filtered out;\n")
        with self.assertRaisesRegex(ValueError, "filtered tests"):
            summarize(self.root)


if __name__ == "__main__":
    unittest.main()
