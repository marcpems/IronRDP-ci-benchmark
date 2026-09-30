import json
from pathlib import Path
import tempfile
import unittest

from analyze_compiler import PLATFORMS, WORKLOADS, analyze, markdown


class CompilerAnalysisTests(unittest.TestCase):
    def test_complete_matrix_ratios_and_cpu_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for platform in PLATFORMS:
                for replicate in (1, 2, 3):
                    folder = root / f"{platform}-{replicate}"
                    folder.mkdir()
                    measurements = []
                    for workload in WORKLOADS:
                        for cores in (1, 4):
                            scale = 2 if platform.startswith("windows") else 1
                            row = {
                                "workload": workload, "cores": cores, "exit_code": 0,
                                "affinity": list(range(cores)),
                                "wall_seconds": scale * 10 / cores, "cpu_seconds": scale * 10,
                                "user_seconds": scale * 8, "kernel_seconds": scale * 2,
                                "effective_cores": cores,
                            }
                            if workload == "graphics-project":
                                row.update(rustc_user_seconds=scale * 7,
                                           rustc_kernel_seconds=scale * 1,
                                           rustc_processes=3)
                            measurements.append(row)
                    value = {"metadata": {
                        "source_sha": "same", "lock_lf_sha256": "same", "profile": {},
                        "environment": {"BENCHMARK_PLATFORM": platform,
                                        "BENCHMARK_REPLICATE": str(replicate)},
                    }, "measurements": measurements}
                    (folder / "results.json").write_text(json.dumps(value))
            report = markdown(analyze(root))
            self.assertIn("2.000x", report)
            self.assertIn("4.000x", report)
            self.assertIn("80.00%", report)
            path = root / "linux-x64-1" / "results.json"
            value = json.loads(path.read_text())
            value["measurements"][0]["cpu_seconds"] = 999
            path.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError, "CPU accounting mismatch"):
                analyze(root)

    def test_missing_matrix_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "exactly three"):
                analyze(Path(directory))


if __name__ == "__main__":
    unittest.main()
