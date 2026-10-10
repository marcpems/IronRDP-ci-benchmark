import copy
import json
from pathlib import Path
import tempfile
import unittest

from analyze_msvc_experiment import HOSTS, analyze, build_summary, contrast
from msvc_experiment import VARIANTS
from msvc_ironrdp_probe import validate_metadata
from native_ci_probe import COMMANDS, NATIVE_COMMANDS, paired_order


def compiler_metadata(host):
    tools = {"msvc": "v1", "sdk": "s1", "files": {}}
    training = {phase: {"coverage": {"function": {"active_functions": 1}}}
                for phase in ("rustc-profile", "llvm-profile")}
    return {
        variant: {
            "phase": variant, "rust_sha": "rust", "host": host, "run_id": "build",
            "tools": tools, "llvm_sha": "llvm", "perf_sha": "perf",
            "profiling_runtime_sources": {"InstrProfilingMerge.c": "merge",
                                          "InstrProfilingPlatformWindows.c": "platform"},
            "profiles": {} if variant == "baseline" else
                {"rustc-pgo.profdata": "rustc-profile", "llvm-pgo.profdata": "llvm-profile"},
            "training": training, "profile_parent_sha256": "parent",
        } for variant in VARIANTS
    }


class AnalysisTests(unittest.TestCase):
    def test_build_summary_requires_all_successful_phases(self):
        result = {"build_run": "build", "protocol": {"rust_sha": "rust"}}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for host in HOSTS:
                for phase in ("baseline", "rustc-profile", "llvm-profile", "pgo", "pgo-rust-thin"):
                    directory = root / f"{host}-{phase}"
                    directory.mkdir()
                    (directory / "metadata.json").write_text(json.dumps({
                        "host": host, "phase": phase, "run_id": "build", "rust_sha": "rust"}))
                    stages = ["build"] + (["training-tools", "training", "merge"] if phase.endswith("-profile") else [])
                    for stage in stages:
                        (directory / f"{stage}.json").write_text(json.dumps({
                            "exit_code": 0, "wall_seconds": 120, "cpu_seconds": 400}))
            summary, text = build_summary(root, result)
            self.assertEqual(len(summary["stages"]), 10)
            self.assertIn("not a pure offline", text)
            (directory / "build.json").write_text(json.dumps({
                "exit_code": 1, "wall_seconds": 120, "cpu_seconds": 400}))
            with self.assertRaises(ValueError):
                build_summary(root, result)

    def test_paired_reduction(self):
        result = contrast([100, 200, 300, 400, 500], [80, 160, 240, 320, 400])
        self.assertAlmostEqual(result["reduction_percent"], 20)
        for value in result["ci95_percent"]:
            self.assertAlmostEqual(value, 20)

    def test_profiles_must_be_identical(self):
        metadata = compiler_metadata(HOSTS[0])
        validate_metadata(metadata, {"rust_sha": "rust"}, HOSTS[0], "build")
        metadata["pgo-rust-thin"]["profiles"]["llvm-pgo.profdata"] = "different"
        with self.assertRaises(RuntimeError):
            validate_metadata(metadata, {"rust_sha": "rust"}, HOSTS[0], "build")

    def test_runtime_source_provenance_is_required_and_identical(self):
        for missing in (False, True):
            metadata = compiler_metadata(HOSTS[0])
            if missing:
                del metadata["pgo"]["profiling_runtime_sources"]
            else:
                metadata["pgo"]["profiling_runtime_sources"]["InstrProfilingMerge.c"] = "different"
            with self.assertRaisesRegex(RuntimeError, "Profiling runtime sources"):
                validate_metadata(metadata, {"rust_sha": "rust"}, HOSTS[0], "build")

    def test_complete_matrix_and_missing_block_rejection(self):
        protocol = {"rust_sha": "rust", "source_sha": "ironrdp", "cores": 4,
                    "independent_vms_per_arch": 5, "warmup_rounds": 1, "measured_rounds": 3}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for host in HOSTS:
                for vm in range(1, 6):
                    directory = root / f"{host}-{vm}"
                    directory.mkdir()
                    index = {
                        "complete": True, "pilot": False, "protocol": protocol, "host": host, "vm": vm,
                        "compiler_metadata": compiler_metadata(host), "variants": list(VARIANTS),
                        "benchmark_run": "benchmark", "benchmark_attempt": "1", "build_run": "build",
                        "stdlibs": {}, "cargo_sha256": "cargo", "rustdoc_sha256": "rustdoc", "runs": [],
                    }
                    for r in range(4):
                        for position, variant in enumerate(paired_order(list(VARIANTS), vm, r)):
                            name = f"{r}-{variant}.json"
                            index["runs"].append({"variant": variant, "round": r, "position": position,
                                                  "warmup": r == 0, "path": name})
                            wall = {"baseline": 10, "pgo": 8, "pgo-rust-thin": 7}[variant]
                            rows = [{"name": command, "wall_seconds": wall, "cpu_seconds": wall * 3,
                                     "exit_code": 0, "compiled_artifacts": 1, "affinity": [0, 1, 2, 3]}
                                    for command, _ in COMMANDS]
                            block = {
                                "metadata": {"variant": variant, "round": r, "source_sha": "ironrdp"},
                                "measurements": rows,
                                "correctness": [{"name": command, "exit_code": 0}
                                                for command, _ in NATIVE_COMMANDS[1:]] if r == 0 else [],
                            }
                            (directory / name).write_text(json.dumps(block))
                    (directory / "index.json").write_text(json.dumps(index))
            result = analyze(root, protocol)
            self.assertEqual(result["architectures"][HOSTS[0]]["native-total/wall_seconds"]["means"]["baseline"], 50)
            selected = directory / "index.json"
            index = json.loads(selected.read_text())
            original = copy.deepcopy(index)
            for mutate in (
                lambda item: item["runs"].pop(),
                lambda item: item.update(benchmark_attempt="2"),
                lambda item: item.update(pilot=True),
                lambda item: item.update(complete=False),
            ):
                candidate = copy.deepcopy(original)
                mutate(candidate)
                selected.write_text(json.dumps(candidate))
                with self.assertRaises(ValueError):
                    analyze(root, protocol)


if __name__ == "__main__":
    unittest.main()
