import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from process_metrics import measure
from x64_runner_diagnostic import filesystem_probe, topology


@unittest.skipUnless(os.name == "nt", "Native Windows diagnostics")
class X64DiagnosticTests(unittest.TestCase):
    def test_topology_masks_are_disjoint_and_nonempty(self):
        cores = topology()
        self.assertTrue(cores)
        logical = [cpu for core in cores for cpu in core]
        self.assertTrue(all(cores))
        self.assertEqual(len(logical), len(set(logical)))

    def test_worker_cpu_is_included_in_job_accounting(self):
        with tempfile.TemporaryDirectory() as name:
            prefix = Path(name) / "cpu"
            result = measure([sys.executable, str(Path(__file__).with_name("x64_runner_diagnostic.py")),
                              "--load", "4", "--seconds", "1"], Path.cwd(), os.environ.copy(),
                             4, prefix, timeout=60)
            self.assertEqual(result["exit_code"], 0)
            output = json.loads(prefix.with_suffix(".stdout").read_text())
            self.assertEqual(len(output["workers"]), 4)
            self.assertTrue(all(row["work_units"] > 0 for row in output["workers"]))
            self.assertGreater(result["cpu_seconds"], 0)
            self.assertLessEqual(sum(row["cpu_seconds"] for row in output["workers"]),
                                 result["cpu_seconds"] + 0.2)
            self.assertEqual(result["affinity"], [0, 1, 2, 3])

    def test_filesystem_probe_verifies_payloads_and_removes_only_its_own_trees(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            unrelated = root / "keep"
            unrelated.write_text("unchanged")
            output = root / "report.json"
            filesystem_probe(str(root), output)
            rows = json.loads(output.read_text())
            self.assertEqual([row["bytes"] for row in rows], [1024 * 4096, 16 * 4 * 1024 * 1024])
            self.assertEqual(unrelated.read_text(), "unchanged")
            self.assertEqual({path.name for path in root.iterdir()}, {"keep", "report.json"})


if __name__ == "__main__":
    unittest.main()
