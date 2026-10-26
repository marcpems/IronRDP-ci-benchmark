import json
from pathlib import Path
import tempfile
import unittest

from upstream_51dae_replay import NATIVE_COMMANDS, PROFILE_ENV, REVISIONS, SOURCE_SHA, summarize


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.runs = []
        for round_index in range(2):
            for variant in REVISIONS:
                path = f"{round_index}-{variant}.json"
                seconds = 100 if variant == "parent" else 87
                result = {
                    "metadata": {
                        "variant": variant, "round": round_index, "source_sha": SOURCE_SHA,
                        "profile_environment": PROFILE_ENV, "cargo": "common-cargo",
                        "lock_lf_sha256": "same-lock", "rustc": f"commit-hash: {REVISIONS[variant]}\n",
                        "cold_target_directories": {"native": path},
                    },
                    "measurements": [
                        {"name": name, "wall_seconds": seconds, "cpu_seconds": seconds * 3,
                         "exit_code": 0, "compiled_artifacts": 1, "affinity": [0, 1, 2, 3],
                         "command": ["cargo", *args, "--frozen", "--timings", "--message-format=json"]}
                        for name, args in NATIVE_COMMANDS
                    ],
                }
                (self.root / path).write_text(json.dumps(result))
                self.runs.append({"round": round_index, "variant": variant, "path": path})

    def test_paired_reduction(self):
        result = summarize(self.root, self.runs)
        self.assertAlmostEqual(result["wall_reduction_percent"], 13)
        self.assertAlmostEqual(result["cpu_reduction_percent"], 13)
        self.assertAlmostEqual(result["workspace_reduction_percent"], 13)
        self.assertEqual(result["means"]["parent"]["wall_seconds"], 500)
        self.assertTrue(all(abs(row["wall_reduction_percent"] - 13) < 1e-9
                            for row in result["paired_rounds"]))

    def test_rejects_missing_or_duplicate_round(self):
        for runs in (self.runs[:-1], [*self.runs[:-1], self.runs[0]]):
            with self.subTest(runs=runs), self.assertRaisesRegex(RuntimeError, "Incomplete or duplicate"):
                summarize(self.root, runs)

    def test_rejects_failed_build_and_changed_compiler(self):
        path = self.root / self.runs[-1]["path"]
        original = path.read_text()
        for corruption in ("exit", "compiler", "affinity", "target", "cargo"):
            with self.subTest(corruption=corruption):
                result = json.loads(original)
                if corruption == "exit":
                    result["measurements"][0]["exit_code"] = 1
                elif corruption == "compiler":
                    result["metadata"]["rustc"] = "wrong compiler"
                elif corruption == "affinity":
                    result["measurements"][0]["affinity"] = [0, 1]
                elif corruption == "target":
                    result["metadata"]["cold_target_directories"]["native"] = self.runs[0]["path"]
                else:
                    result["metadata"]["cargo"] = "other-cargo"
                path.write_text(json.dumps(result))
                with self.assertRaises(RuntimeError):
                    summarize(self.root, self.runs)


if __name__ == "__main__":
    unittest.main()
