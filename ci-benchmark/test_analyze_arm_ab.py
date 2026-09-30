import json
from pathlib import Path
import tempfile
import unittest

from analyze_arm_ab import ENDPOINTS, analyze, contrasts, load_matrix, markdown

PROTOCOL = json.loads(Path(__file__).with_name("arm64-ab-protocol.json").read_text())


def synthetic_matrix(baseline=200):
    matrix = {}
    for endpoint in ENDPOINTS:
        matrix[endpoint] = {"windows-arm64": {}, "linux-arm64": {}}
        for vm in range(1, 6):
            win = {"official": 200, "baseline-msvc": baseline,
                   "baseline-lld": baseline - 10, "optimized": baseline - 50}
            matrix[endpoint]["windows-arm64"][vm] = {
                variant: {"cpu_seconds": seconds, "wall_seconds": seconds / endpoint[1]}
                for variant, seconds in win.items()
            }
            matrix[endpoint]["linux-arm64"][vm] = {
                "official": {"cpu_seconds": 100, "wall_seconds": 100 / endpoint[1]},
            }
    return matrix


class ArmAnalysisTests(unittest.TestCase):
    def test_known_causal_decomposition(self):
        result = analyze(synthetic_matrix(), PROTOCOL, draws=100)
        self.assertTrue(result["primary_attribution_gate_passed"])
        primary = next(r for r in result["results"] if r["workload"] == "graphics-project"
                       and r["cores"] == 4 and r["metric"] == "cpu_seconds")
        self.assertAlmostEqual(primary["contrasts"]["gap_equivalent_fraction"], 0.4)
        self.assertEqual(primary["ci95"]["gap_equivalent_fraction"], [0.4, 0.4])
        self.assertEqual(primary["contrasts"]["linker_seconds"], 10)
        self.assertIn("40.0%", markdown(result))

    def test_failed_equivalence_blocks_attribution(self):
        result = analyze(synthetic_matrix(baseline=150), PROTOCOL, draws=100)
        self.assertFalse(result["primary_attribution_gate_passed"])
        self.assertIn("do not claim official-gap attribution", markdown(result))

    def test_no_positive_gap_is_not_silently_clamped(self):
        c = contrasts({"official": 90, "baseline-msvc": 90,
                       "baseline-lld": 90, "optimized": 80}, 100)
        self.assertIsNone(c["gap_equivalent_fraction"])
        self.assertEqual(c["official_gap_seconds"], -10)

    def test_resampling_preserves_paired_savings(self):
        matrix = synthetic_matrix()
        for endpoint, platforms in matrix.items():
            for vm, variants in platforms["windows-arm64"].items():
                for metrics in variants.values():
                    for metric in metrics:
                        metrics[metric] += vm * 10 / (endpoint[1] if metric == "wall_seconds" else 1)
        result = analyze(matrix, PROTOCOL, draws=100)
        primary = next(r for r in result["results"] if r["workload"] == "graphics-project"
                       and r["cores"] == 4 and r["metric"] == "cpu_seconds")
        self.assertEqual(primary["ci95"]["optimization_seconds"], [40, 40])

    def test_incomplete_evidence_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "complete matrix"):
                load_matrix(Path(tmp), PROTOCOL)

    def test_pilot_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "index.json").write_text(json.dumps({
                "platform": "windows-arm64", "vm": 1, "pilot": True, "protocol": PROTOCOL,
            }))
            with self.assertRaisesRegex(ValueError, "pilot"):
                load_matrix(Path(tmp), PROTOCOL)

    def test_complete_evidence_and_corrupted_cpu(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corrupt_path = None
            for platform in ("windows-arm64", "linux-arm64"):
                variants = PROTOCOL["windows_variants"] if platform == "windows-arm64" else ["official"]
                for vm in range(1, 6):
                    folder = root / f"{platform}-{vm}"
                    folder.mkdir()
                    index = {
                        "platform": platform, "vm": vm, "pilot": False,
                        "protocol": PROTOCOL, "variants": variants, "runs": [],
                        "compiler_archive_sha256": {
                            v: f"hash-{v}" for v in variants if v != "official"
                        },
                    }
                    for variant in variants:
                        for round_index in range(4):
                            rows = []
                            for workload, cores in sorted(ENDPOINTS):
                                rows.append({
                                    "workload": workload, "cores": cores, "exit_code": 0,
                                    "affinity": list(range(cores)), "cpu_seconds": 10,
                                    "wall_seconds": 10 / cores, "user_seconds": 9,
                                    "kernel_seconds": 1, "processes": 1,
                                })
                            name = f"{variant}-{round_index}.json"
                            result_path = folder / name
                            result_path.write_text(json.dumps({
                                "metadata": {
                                    "source_sha": PROTOCOL["source_sha"],
                                    "rustc": PROTOCOL["rust_sha"],
                                    "lock_lf_sha256": "same",
                                    "profile": {"opt_level": 1, "codegen_units": 16,
                                                "debug": 0, "incremental": False},
                                    "environment": {"BENCHMARK_PLATFORM": platform,
                                                    "BENCHMARK_REPLICATE": str(vm)},
                                },
                                "measurements": rows,
                            }))
                            corrupt_path = result_path
                            index["runs"].append({
                                "variant": variant, "round": round_index,
                                "warmup": round_index == 0, "path": name,
                            })
                    (folder / "index.json").write_text(json.dumps(index))
            self.assertEqual(set(load_matrix(root, PROTOCOL)), ENDPOINTS)
            value = json.loads(corrupt_path.read_text())
            value["measurements"][0]["cpu_seconds"] = 99
            corrupt_path.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError, "CPU accounting"):
                load_matrix(root, PROTOCOL)


if __name__ == "__main__":
    unittest.main()
