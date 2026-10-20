import copy
import json
from pathlib import Path
import tempfile
import unittest

from analyze_x64_pgo_replay import METRICS, NATIVE_COMMANDS, PROFILE_ENV, analyze, load_matrix, paired_order

PROTOCOL = json.loads(Path(__file__).with_name("x64-pgo-replay-protocol.json").read_text())


def fixture(root):
    for vm in range(1, 6):
        directory = root / str(vm)
        directory.mkdir()
        version = f"release: 1.94.1\nhost: {PROTOCOL['host']}\n{PROTOCOL['rust_sha']}\n"
        index = {"complete": True, "protocol": PROTOCOL, "vm": vm, "variants": PROTOCOL["variants"],
                 "stdlib": {"libstd-shared.rlib": "hash"}, "cargo_sha256": "cargo",
                 "benchmark_run": "run", "attempt": "1", "artifact_evidence": {}, "compiler_metadata": {},
                 "versions": dict.fromkeys(PROTOCOL["variants"], version), "runs": []}
        for variant in ("upstream", "local"):
            index["artifact_evidence"][variant] = {
                "archive_sha256": PROTOCOL["compiler_archive_sha256"][variant],
                "result_sha256": PROTOCOL["compiler_metadata_sha256"][variant]}
            index["compiler_metadata"][variant] = {
                "complete": True, "variant": variant, "run_id": PROTOCOL["release_run"],
                "attempt": "1", "rust_sha": PROTOCOL["rust_sha"]}
        for r in range(4):
            for position, variant in enumerate(paired_order(PROTOCOL["variants"], vm, r)):
                name = f"round-{r}-{variant}"
                folder = directory / name
                folder.mkdir()
                target = str(folder / "native")
                rows = [{"name": n, "command": ["cargo", *args, "--frozen", "--timings", "--message-format=json"],
                         "exit_code": 0, "compiled_artifacts": 1, "target_directory": target,
                         "affinity": [0, 1, 2, 3], "wall_seconds": 10, "cpu_seconds": 20,
                         "user_seconds": 18, "kernel_seconds": 2} for n, args in NATIVE_COMMANDS]
                meta = {"source_sha": PROTOCOL["source_sha"], "profile_environment": PROFILE_ENV,
                        "logical_cpus": 4, "variant": variant, "round": r, "rustc": version,
                        "lock_lf_sha256": "lock", "cargo": "cargo", "approved_background_executables": [],
                        "cold_target_directories": {"native": target},
                        "environment": {"BENCHMARK_PLATFORM": "windows-x64", "BENCHMARK_REPLICATE": str(vm),
                                        "BENCHMARK_HOST": PROTOCOL["host"], "GITHUB_RUN_ID": "run",
                                        "GITHUB_RUN_ATTEMPT": "1"}}
                meta["compiler_executable"] = (
                    f"D:/xp/rustup/toolchains/1.94.1-{PROTOCOL['host']}/bin/rustc.exe" if variant == "official"
                    else f"D:/xp/e/compilers/{variant}/rustc-1.94.1-{PROTOCOL['host']}/rustc/bin/rustc.exe")
                checks = [{"name": n, "command": ["cargo", *(a for a in args if a != "--no-run"), "--frozen"],
                           "exit_code": 0} for n, args in NATIVE_COMMANDS[1:]] if r == 0 else []
                (folder / "results.json").write_text(json.dumps({
                    "metadata": meta, "measurements": rows, "correctness": checks}))
                index["runs"].append({"variant": variant, "round": r, "position": position,
                                      "warmup": r == 0, "path": f"{name}/results.json"})
        (directory / "index.json").write_text(json.dumps(index))


class FreshReplayAnalysisTests(unittest.TestCase):
    def test_whole_vm_pairing_preserves_constant_savings_and_regressions(self):
        matrix = {vm: {variant: {"native-total": {metric: value for metric in METRICS}}
                       for variant, value in (("official", vm * 100), ("local", vm * 100 - 20),
                                              ("upstream", vm * 100 + 10))} for vm in range(1, 6)}
        rows = analyze(matrix, draws=100)
        local = next(row for row in rows if row["baseline"] == "official" and row["candidate"] == "local")
        self.assertEqual(local["ci95"]["saved_seconds"], [20, 20])
        upstream = next(row for row in rows if row["baseline"] == "official" and row["candidate"] == "upstream")
        self.assertEqual(upstream["ci95"]["saved_seconds"], [-10, -10])
        self.assertLess(upstream["reduction_fraction"], 0)

    def test_complete_matrix_and_rejection_of_changed_measurements(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture(root)
            matrix, run = load_matrix(root, PROTOCOL)
            self.assertEqual(run, ("run", "1"))
            self.assertEqual(matrix[1]["local"]["native-total"]["wall_seconds"], 50)
            path = root / "1/round-1-local/results.json"
            original = json.loads(path.read_text())
            for mutation, message in (
                (lambda data: data["measurements"][0]["command"].append("--release"), "native command"),
                (lambda data: data["measurements"][0].update(cpu_seconds=500), "CPU accounting"),
                (lambda data: data["metadata"]["environment"].update(GITHUB_RUN_ATTEMPT="2"), "workflow"),
                (lambda data: data["metadata"].update(compiler_executable="wrong/rustc.exe"), "compiler executable"),
            ):
                data = copy.deepcopy(original)
                mutation(data)
                path.write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError, message):
                    load_matrix(root, PROTOCOL)
            path.write_text(json.dumps(original))
            index_path = root / "1/index.json"
            index = json.loads(index_path.read_text())
            index["complete"] = False
            index_path.write_text(json.dumps(index))
            with self.assertRaisesRegex(ValueError, "Incomplete VM"):
                load_matrix(root, PROTOCOL)


if __name__ == "__main__":
    unittest.main()
