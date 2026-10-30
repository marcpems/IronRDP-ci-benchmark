import copy
import json
from pathlib import Path
import shutil
import subprocess
import time
import unittest
from unittest.mock import patch
import uuid

from monitor_x64_rust_thin import command, identity
from verify_x64_rust_thin import COMMANDS, reduction, verify_block


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.root = Path.cwd() / f".thin-collection-test-{uuid.uuid4().hex}"
        self.root.mkdir()
        self.addCleanup(shutil.rmtree, self.root)

    def test_monitor_rejects_changed_run_head_attempt_or_branch(self):
        run = {"id": 1, "head_sha": "sha", "run_attempt": 1,
               "head_branch": "experiment/x64-rust-thin-incremental",
               "path": ".github/workflows/x64-rust-thin-incremental.yml"}
        identity(run, "1", "sha", 1)
        for key in run:
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                identity({**run, key: "changed"}, "1", "sha", 1)

    def test_network_failure_is_retained_and_retried(self):
        responses = [
            subprocess.CompletedProcess([], 1, "", "HTTP 502"),
            subprocess.CompletedProcess([], 0, '{"status":"in_progress"}', ""),
        ]
        events = self.root / "network.jsonl"
        with patch("monitor_x64_rust_thin.subprocess.run", side_effect=responses) as run, \
                patch("monitor_x64_rust_thin.time.sleep"):
            result = command(Path("gh"), ["api", "fixture"], time.monotonic() + 60, events)
        self.assertEqual(json.loads(result)["status"], "in_progress")
        self.assertEqual(run.call_count, 2)
        self.assertIn("HTTP 502", events.read_text())
        with self.assertRaises(TimeoutError):
            command(Path("gh"), [], time.monotonic() - 1, events)

    def test_reductions_round_half_up_and_preserve_regressions(self):
        self.assertEqual(reduction("100", "87.655")["reduction_percent_2dp"], "12.35")
        self.assertEqual(reduction("100", "112.345")["reduction_percent_2dp"], "-12.35")
        for baseline in (0, "NaN", "Infinity"):
            with self.subTest(baseline=baseline), self.assertRaises(RuntimeError):
                reduction(baseline, 1)

    def test_verifier_recomputes_each_command_and_rejects_failed_or_changed_receipts(self):
        rows = []
        for name, args in COMMANDS:
            row = {
                "name": name, "command": [r"D:\ri\baseline\bin\cargo.exe", *args,
                                         "--frozen", "--timings", "--message-format=json"],
                "exit_code": 0, "affinity": [0, 1, 2, 3], "wall_seconds": 2.5,
                "cpu_seconds": 4, "user_seconds": 3, "kernel_seconds": 1,
                "compiled_artifacts": 1,
            }
            rows.append(row)
            (self.root / f"{name}.json").write_text(json.dumps(row))
            (self.root / f"{name}.stdout").write_text(
                json.dumps({"reason": "compiler-artifact", "fresh": False}) + "\n")
            (self.root / f"{name}.stderr").write_text("")
            (self.root / f"{name}.timings.html").write_text("fixture")
        result = {"complete": True, "correctness": False, "rows": rows,
                  "wall_seconds": 12.5, "cpu_seconds": 20}
        (self.root / "results.json").write_text(json.dumps(result))
        self.assertEqual(verify_block(self.root, False)["cpu_seconds"], 20)
        for field, value in (("exit_code", 1), ("affinity", [0]), ("cpu_seconds", 5)):
            altered = copy.deepcopy(result)
            altered["rows"][0][field] = value
            (self.root / "results.json").write_text(json.dumps(altered))
            (self.root / "xtask-bootstrap.json").write_text(json.dumps(altered["rows"][0]))
            with self.subTest(field=field), self.assertRaises(RuntimeError):
                verify_block(self.root, False)
        result["correctness"] = True
        for row, (name, args) in zip(rows, COMMANDS):
            args = [arg for arg in args if arg != "--no-run"]
            if name == "workspace-tests":
                args += ["--lib", "--bins", "--tests"]
            row["command"] = [r"D:\ri\baseline\bin\cargo.exe", *args, "--frozen"]
            row["correctness_environment"] = {"PUBLIC": r"C:\Users\Public"}
            (self.root / f"{name}.json").write_text(json.dumps(row))
            (self.root / f"{name}.stdout").write_text(
                "test result: ok. 2 passed; 0 failed; 1 ignored; 0 measured; 0 filtered out;\n")
        (self.root / "results.json").write_text(json.dumps(result))
        checked = verify_block(self.root, True)
        self.assertEqual(checked["native_test_counts"]["workspace-tests"]["passed"], 2)
        (self.root / "workspace-tests.stdout").write_text("no tests executed")
        with self.assertRaisesRegex(RuntimeError, "Missing native test outcomes"):
            verify_block(self.root, True)


if __name__ == "__main__":
    unittest.main()
