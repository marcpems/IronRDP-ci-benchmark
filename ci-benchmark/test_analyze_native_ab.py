import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from analyze_native_ab import (
    COMMANDS, METRICS, NATIVE_COMMANDS, PLATFORMS, PROFILE_ENV,
    analyze, load_matrix, markdown, paired_order,
)

PROTOCOL = json.loads(Path(__file__).with_name("native-ab-protocol.json").read_text())


def evidence(root, x64=False):
    protocol = copy.deepcopy(PROTOCOL)
    platforms = ("windows-x64", "linux-x64") if x64 else PLATFORMS
    if x64:
        protocol.update({"platforms": list(platforms), "host": "x86_64-pc-windows-msvc",
                         "windows_variants": ["official", "pgo-control", "optimized"],
                         "compiler_archive_sha256": {}, "compiler_metadata_sha256": {}})
        provenances = {}
        for variant in ("pgo-control", "optimized"):
            data = {"archive_sha256": variant, "host": protocol["host"],
                    "llvm_profile_sha256": "profile",
                    "profiles": {"llvm-pgo.profdata": {"sha256": "profile"}},
                    "llvm_training_coverage": {c: {"nonzero_functions": 1}
                                               for c in ("X86TargetLowering", "InstCombine")}}
            provenances[variant] = json.dumps(data).encode()
            protocol["compiler_archive_sha256"][variant] = variant
            protocol["compiler_metadata_sha256"][variant] = hashlib.sha256(provenances[variant]).hexdigest()
    provenance = json.dumps({"archive_sha256": protocol["optimized_archive_sha256"]}).encode()
    protocol["optimized_metadata_sha256"] = hashlib.sha256(provenance).hexdigest()
    last = None
    for platform in platforms:
        variants = protocol["windows_variants"] if platform == platforms[0] else ["official"]
        for vm in range(1, 6):
            directory = root / f"{platform}-{vm}"
            directory.mkdir()
            if x64 and platform == platforms[0]:
                for variant, raw in provenances.items():
                    (directory / f"{variant}-compiler.json").write_bytes(raw)
            elif platform == "windows-arm64":
                (directory / "optimized-compiler.json").write_bytes(provenance)
                (directory / "installation.json").write_text(json.dumps({
                    "stdlib_identity_verified": True, "native_and_wasm_smoke_passed": True,
                }))
            index = {"platform": platform, "vm": vm, "pilot": False, "protocol": protocol,
                     "variants": variants, "runs": []}
            if x64 and platform == platforms[0]:
                index["identical_windows_stdlibs_verified"] = True
            for r in range(4):
                for position, variant in enumerate(paired_order(variants, vm, r)):
                    name = f"{r}-{variant}"
                    folder = directory / name
                    folder.mkdir()
                    targets = {k: f"{folder}/{k}" for k in ("native", "common", "wasm")}
                    meta = {
                        "source_sha": protocol["source_sha"], "rustc": protocol["rust_sha"] + "\nrelease: 1.94.1\n",
                        "profile_environment": PROFILE_ENV, "logical_cpus": 4, "variant": variant,
                        "round": r, "lock_lf_sha256": "lock", "cargo": "cargo 1.94.1",
                        "compiler_executable": f"/tools/{variant}/bin/rustc.exe",
                        "cold_target_directories": targets,
                        "approved_background_executables": [],
                        "environment": {"BENCHMARK_PLATFORM": platform, "BENCHMARK_REPLICATE": str(vm),
                                        "GITHUB_RUN_ID": "run", "GITHUB_RUN_ATTEMPT": "1"},
                    }
                    rows = []
                    for command_name, args in COMMANDS:
                        wall = 1 if platform == platforms[1] else 2 if variant == "official" else 1.8 if variant == "pgo-control" else 1.6
                        rows.append({
                            "name": command_name, "command": ["cargo", *args, "--frozen", "--timings", "--message-format=json"],
                            "exit_code": 0, "compiled_artifacts": 1, "wall_seconds": wall,
                            "cpu_seconds": wall * 3, "user_seconds": wall * 3, "kernel_seconds": 0,
                            "affinity": [0, 1, 2, 3],
                            "target_directory": targets[command_name if command_name in targets else "native"],
                        })
                        units = [{"name": "fixture", "target": "lib fixture", "mode": "build", "start": 0, "duration": wall / 2}]
                        (folder / f"{command_name}.timings.html").write_text("const UNIT_DATA = " + json.dumps(units) + ";")
                    checks = [{"name": n, "exit_code": 0,
                               "command": ["cargo", *(a for a in args if a != "--no-run"), "--frozen"]}
                              for n, args in NATIVE_COMMANDS[1:]] if r == 0 else []
                    last = folder / "results.json"
                    last.write_text(json.dumps({"metadata": meta, "measurements": rows, "correctness": checks}))
                    index["runs"].append({"variant": variant, "round": r, "position": position,
                                          "warmup": r == 0, "path": f"{name}/results.json"})
            (directory / "index.json").write_text(json.dumps(index))
    return protocol, last


class NativeAnalysisTests(unittest.TestCase):
    def test_x64_three_variant_matrix_and_thinlto_contrast(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            protocol, _ = evidence(root, x64=True)
            matrix, partitions, _ = load_matrix(root, protocol)
            result = analyze(matrix, protocol, draws=100)
            total = next(r for r in result["results"] if r["component"] == "native-total" and r["metric"] == "wall_seconds")
            self.assertAlmostEqual(total["pgo_control_windows"], 9)
            self.assertAlmostEqual(total["thinlto_saved_seconds"], 1)
            self.assertAlmostEqual(total["thinlto_reduction_fraction"], 1 / 9)
            self.assertEqual(len(partitions), 60)
            self.assertIn("Windows x64", markdown(result))
            self.assertIn("11.1%", markdown(result))
            index_path = root / "windows-x64-1" / "index.json"
            index = json.loads(index_path.read_text())
            index["identical_windows_stdlibs_verified"] = False
            index_path.write_text(json.dumps(index))
            with self.assertRaisesRegex(ValueError, "standard libraries"):
                load_matrix(root, protocol)

    def test_complete_matrix_known_savings_and_tampered_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            protocol, path = evidence(root)
            matrix, partitions, run = load_matrix(root, protocol)
            result = analyze(matrix, protocol, draws=100)
            total = next(r for r in result["results"] if r["component"] == "native-total" and r["metric"] == "wall_seconds")
            self.assertAlmostEqual(total["official_windows"], 10)
            self.assertAlmostEqual(total["optimized_windows"], 8)
            self.assertAlmostEqual(total["reduction_fraction"], 0.2)
            self.assertAlmostEqual(total["gap_closed_fraction"], 0.4)
            self.assertIn("20.0%", markdown(result))
            self.assertEqual(len(partitions), 45)
            self.assertEqual(run, ("run", "1"))
            original = json.loads(path.read_text())
            for mutation, message in (
                (lambda d: d["measurements"][0]["command"].append("--release"), "build command"),
                (lambda d: d["measurements"][0].update(cpu_seconds=100), "CPU accounting"),
                (lambda d: d["measurements"][0].update(background_processes_at_completion=[{"image": "unknown.exe"}]), "surviving process"),
                (lambda d: d["metadata"]["profile_environment"].update(CARGO_PROFILE_DEV_OPT_LEVEL="3"), "profile"),
            ):
                changed = copy.deepcopy(original)
                mutation(changed)
                path.write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, message):
                    load_matrix(root, protocol)
            path.write_text(json.dumps(original))

    def test_incomplete_and_pilot_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, "complete matrix"):
                load_matrix(root, PROTOCOL)
            (root / "index.json").write_text(json.dumps({
                "platform": "windows-arm64", "vm": 1, "pilot": True, "protocol": PROTOCOL,
            }))
            with self.assertRaisesRegex(ValueError, "pilot"):
                load_matrix(root, PROTOCOL)

    def test_bootstrap_preserves_pairing(self):
        matrix = {"native-total": {p: {} for p in PLATFORMS}}
        for vm in range(1, 6):
            matrix["native-total"]["windows-arm64"][vm] = {
                "official": {m: 100 + vm * 10 for m in METRICS},
                "optimized": {m: 80 + vm * 10 for m in METRICS},
            }
            matrix["native-total"]["linux-arm64"][vm] = {"official": {m: 50 for m in METRICS}}
        result = analyze(matrix, PROTOCOL, draws=100)
        self.assertEqual(result["results"][0]["ci95"]["saved_seconds"], [20, 20])


if __name__ == "__main__":
    unittest.main()
