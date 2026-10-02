import json
import unittest
from analyze import ROOT, category, intervals


class TimingTests(unittest.TestCase):
    def test_disjoint_groups_packages_and_unknown(self):
        events = [{"line": i, "text": f"2026-09-04T10:00:{stamp}Z {text}"}
                  for i, (stamp, text) in enumerate([
                      ("01.000", "##[group]Building stage1 compiler artifacts"),
                      ("04.000", "##[endgroup]"),
                      ("05.000", "Dist rust-nightly-aarch64-pc-windows-msvc"),
                      ("09.000", "\tfinished in 4.000 seconds"),
                  ], 1)]
        totals, observed, _, _ = intervals(events, "2026-09-04T10:00:00Z", "2026-09-04T10:00:10Z")
        self.assertEqual(totals, {"Unresolved build": 3.0, "Compiler": 3.0, "Packaging": 4.0})
        self.assertEqual(len(observed), 2)

    def test_nested_opt_dist_timers_do_not_add_to_categories(self):
        events = [{"line": i, "text": f"2026-09-04T10:00:{stamp}Z {text}"}
                  for i, (stamp, text) in enumerate([
                      ("01.000", "Section `Stage 1` starts"),
                      ("02.000", "Section `Stage 1 > Gather profiles` starts"),
                      ("04.000", "Section `Stage 1 > Gather profiles` ended: OK (2.0s)"),
                      ("05.000", "Section `Stage 1` ended: OK (4.0s)"),
                  ], 1)]
        totals, _, timers, _ = intervals(events, "2026-09-04T10:00:00Z", "2026-09-04T10:00:10Z")
        self.assertEqual(totals, {"Unresolved build": 10.0})
        self.assertEqual([t["seconds"] for t in timers], [2.0, 4.0])

    def test_training_is_not_qualification(self):
        self.assertEqual(category("Running benchmarks"), "Training")
        self.assertEqual(category("Testing stage2 with compiletest"), "Tests")

    def test_completed_data_accounting(self):
        data = json.loads((ROOT / "summary.json").read_text())
        self.assertEqual(sum(run["job_count"] for run in data), 313)
        for run in data:
            self.assertEqual(run["run"]["conclusion"], "success")
            for job in run["jobs"]:
                self.assertAlmostEqual(sum(job["actions_categories_seconds"].values()),
                                       job["elapsed_seconds"], places=2)
                if "build_categories_seconds" in job:
                    self.assertAlmostEqual(sum(job["build_categories_seconds"].values()),
                                           job["actions_categories_seconds"]["Main build"], places=2)

    def test_arm_only_does_not_shorten_sampled_global_path(self):
        data = json.loads((ROOT / "critical-path-models.json").read_text())
        self.assertEqual(len(data), 3)
        for run in data:
            self.assertEqual(run["scenarios"][0]["matrix_makespan_saved_seconds"], 0)
            self.assertEqual(run["scenarios"][1]["matrix_makespan_saved_seconds"], 0)


if __name__ == "__main__":
    unittest.main()
