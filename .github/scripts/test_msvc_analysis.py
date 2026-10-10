import copy
import json
from pathlib import Path
import tempfile
import unittest

from analyze_msvc_experiment import HOSTS, analyze, build_summary, contrast, markdown
from msvc_experiment import VARIANTS
from msvc_ironrdp_probe import validate_metadata
from native_ci_probe import COMMANDS, NATIVE_COMMANDS, paired_order
from build_arm_compilers import digest


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
                for phase in ("rustc-profile", "llvm-profile", "baseline", "pgo", "pgo-rust-thin"):
                    directory = root / f"{host}-{phase}"
                    directory.mkdir()
                    item = compiler_metadata(host)["baseline" if phase == "baseline" else "pgo"]
                    item["phase"] = phase
                    item["profiles"] = {}
                    names = [] if phase == "baseline" else ["rustc-pgo.profdata"]
                    if phase not in ("baseline", "rustc-profile"):
                        names.append("llvm-pgo.profdata")
                    for name in names:
                        profile = directory / name
                        profile.write_bytes(name.encode())
                        item["profiles"][name] = digest(profile)
                    if phase.endswith("-profile"):
                        item["run_id"] = phase
                    if phase in ("llvm-profile", "pgo", "pgo-rust-thin"):
                        parent = "rustc-profile" if phase == "llvm-profile" else "llvm-profile"
                        item["profile_parent_sha256"] = digest(root / f"{host}-{parent}/metadata.json")
                    (directory / "metadata.json").write_text(json.dumps(item))
                    stages = ["build"] + (["training-tools", "training", "merge"] if phase.endswith("-profile") else [])
                    for stage in stages:
                        (directory / f"{stage}.json").write_text(json.dumps({
                            "exit_code": 0, "wall_seconds": 120, "cpu_seconds": 400}))
            result["compiler_metadata"] = {
                host: {variant: json.loads((root / f"{host}-{variant}/metadata.json").read_text())
                       for variant in VARIANTS}
                for host in HOSTS
            }
            summary, text = build_summary(root, result)
            self.assertEqual(len(summary["stages"]), 10)
            self.assertIn("not a pure offline", text)
            self.assertIn("Profile merge (min)", text)
            parent_path = root / f"{HOSTS[0]}-llvm-profile/metadata.json"
            original_parent = parent_path.read_text()
            broken_parent = json.loads(original_parent)
            broken_parent["profile_parent_sha256"] = "wrong"
            parent_path.write_text(json.dumps(broken_parent))
            with self.assertRaisesRegex(ValueError, "profile parent mismatch"):
                build_summary(root, result)
            parent_path.write_text(original_parent)
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
                    "independent_vms_per_arch": 5, "warmup_rounds": 1, "measured_rounds": 3,
                    "correctness_test_threads": 1}
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
                                "correctness": [{"name": command, "exit_code": 0,
                                                 "environment_overrides": {"RUST_TEST_THREADS": "1"}}
                                                for command, _ in NATIVE_COMMANDS[1:]] if r == 0 else [],
                            }
                            (directory / name).write_text(json.dumps(block))
                    (directory / "index.json").write_text(json.dumps(index))
            result = analyze(root, protocol)
            self.assertEqual(result["architectures"][HOSTS[0]]["native-total/wall_seconds"]["means"]["baseline"], 50)
            report = markdown(result)
            self.assertIn("CPU 95% interval", report)
            self.assertIn("Baseline CPU (s)", report)
            self.assertIn("Common-package and WASM", report)
            self.assertIn("| baseline->pgo | 20.00% | 20.00% to 20.00% | 20.00% |", report)
            with self.assertRaisesRegex(ValueError, "Unexpected or duplicate VM"):
                analyze(root, protocol, (HOSTS[0],))
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
            selected.write_text(json.dumps(original))
            arm_root = root / "arm-only"
            arm_root.mkdir()
            for vm in range(1, 6):
                (root / f"{HOSTS[1]}-{vm}").rename(arm_root / str(vm))
            single = analyze(arm_root, protocol, (HOSTS[1],))
            self.assertEqual(single["included_hosts"], [HOSTS[1]])
            self.assertEqual(set(single["architectures"]), {HOSTS[1]})
            with self.assertRaisesRegex(ValueError, "Incomplete architecture/VM matrix"):
                analyze(arm_root, protocol)


if __name__ == "__main__":
    unittest.main()
