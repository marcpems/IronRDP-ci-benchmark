import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "benchmark", Path(__file__).with_name("offline_benchmark.py"),
)
benchmark = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(benchmark)


class BenchmarkTests(unittest.TestCase):
    def test_measures_process_only_and_copies_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            timings = target / "cargo-timings"
            timings.mkdir(parents=True)
            (timings / "cargo-timing.html").write_text("timings")

            def execute(command, **kwargs):
                self.assertIn("--frozen", command)
                self.assertIn("--no-run", command)
                self.assertEqual(kwargs["env"]["CARGO_NET_OFFLINE"], "true")
                self.assertEqual(kwargs["env"]["CARGO_TARGET_DIR"], str(target))
                for fresh in (False, True):
                    kwargs["stdout"].write((json.dumps({
                        "reason": "compiler-artifact", "fresh": fresh,
                    }) + "\n").encode())
                return subprocess.CompletedProcess(command, 0)

            with patch.object(benchmark.subprocess, "run", side_effect=execute):
                with patch.object(benchmark.time, "perf_counter", side_effect=[10, 12.5]):
                    row = benchmark.measure(
                        "test", ["test", "--no-run"], root, target, root, {},
                    )
            self.assertEqual(row["seconds"], 2.5)
            self.assertEqual(row["compiled_artifacts"], 1)
            self.assertEqual(row["fresh_artifacts"], 1)
            self.assertEqual((root / "test.timings.html").read_text(), "timings")

    def test_failed_build_preserves_failure_and_raises(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(benchmark.subprocess, "run", return_value=
                              subprocess.CompletedProcess(["cargo"], 101)):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(subprocess.CalledProcessError):
                        benchmark.measure("bad", ["build"], root, root, root, {})
            row = json.loads((root / "bad.measurement.json").read_text())
            self.assertEqual(row["exit_code"], 101)
            self.assertFalse((root / "results.json").exists())

    def test_all_matrix_cells_required_and_ratios_use_medians(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for platform in ("linux-x64", "windows-x64", "linux-arm64", "windows-arm64"):
                for replicate in (1, 2, 3):
                    cell = root / f"{platform}-{replicate}"
                    cell.mkdir()
                    seconds = (2 if platform.startswith("windows") else 1) * replicate
                    result = {
                        "metadata": {
                            "source_sha": "sha", "lock_sha256": "lock", "cargo": "cargo",
                            "environment": {
                                "BENCHMARK_PLATFORM": platform,
                                "BENCHMARK_REPLICATE": str(replicate),
                            },
                        },
                        "measurements": [
                            {"name": name, "seconds": seconds, "exit_code": 0}
                            for name in [*(n for n, _ in benchmark.NATIVE_COMMANDS),
                                         "common", "wasm"]
                        ],
                    }
                    (cell / "results.json").write_text(json.dumps(result))
            summary = benchmark.summarize(root)
            self.assertIn("Windows/Linux x64 native-total: 2.000x", summary)
            self.assertIn("Windows/Linux arm64 wasm: 2.000x", summary)
            for path in root.glob("*/results.json"):
                result = json.loads(path.read_text())
                blob = b"lock\r\n" if "windows" in path.parent.name else b"lock\n"
                result["metadata"]["lock_sha256"] = hashlib.sha256(blob).hexdigest()
                path.write_text(json.dumps(result))
            with self.assertRaisesRegex(RuntimeError, "provide --source"):
                benchmark.summarize(root)
            with patch.object(benchmark.subprocess, "check_output", return_value=b"lock\n"):
                self.assertIn("2.000x", benchmark.summarize(root, root))
            with patch.object(benchmark.subprocess, "check_output", return_value=b"different\n"):
                with self.assertRaisesRegex(RuntimeError, "do not match"):
                    benchmark.summarize(root, root)
            (root / "linux-x64-1" / "results.json").unlink()
            with patch.object(benchmark.subprocess, "check_output", return_value=b"lock\n"):
                with self.assertRaisesRegex(RuntimeError, "invalid matrix"):
                    benchmark.summarize(root, root)

    def test_compile_only_commands_do_not_execute_tests(self):
        for _, command in benchmark.NATIVE_COMMANDS:
            if command[0] == "test":
                self.assertIn("--no-run", command)
        self.assertIn("--no-run", benchmark.COMMON_COMMAND)

    def test_runner_keeps_workload_targets_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Cargo.lock").write_text("fixture lock")
            env = {
                "CARGO_INCREMENTAL": "0", "CARGO_PROFILE_DEV_DEBUG": "0",
                "CARGO_BUILD_JOBS": "4", "CARGO_NET_OFFLINE": "true",
                "BENCHMARK_HOST": "aarch64-pc-windows-msvc",
                "BENCHMARK_PLATFORM": "windows-arm64", "BENCHMARK_REPLICATE": "2",
                "RUNNER_TEMP": directory, "GITHUB_RUN_ID": "1",
                "GITHUB_RUN_ATTEMPT": "1",
            }
            calls = []

            def measure(name, args, source, target, output, child_env):
                calls.append((name, target))
                return {"name": name, "seconds": 1, "exit_code": 0}

            with (
                patch.dict(benchmark.os.environ, env, clear=True),
                patch.object(benchmark.os, "cpu_count", return_value=4),
                patch.object(benchmark.platform, "platform", return_value="fixture-os"),
                patch.object(benchmark.platform, "machine", return_value="ARM64"),
                patch.object(benchmark.subprocess, "check_output",
                             side_effect=["host: aarch64-pc-windows-msvc\n",
                                          "source-sha\n", "cargo 1.94.1\n", "{}", "{}"]),
                patch.object(benchmark.subprocess, "run"),
                patch.object(benchmark, "measure", side_effect=measure),
            ):
                benchmark.run(root, root / "output")
            self.assertEqual([n for n, _ in calls],
                             ["wasm", "common", *(n for n, _ in benchmark.NATIVE_COMMANDS)])
            native_targets = {t for n, t in calls if n not in ("wasm", "common")}
            self.assertEqual(len(native_targets), 1)
            self.assertNotIn(calls[0][1], native_targets)
            self.assertNotIn(calls[1][1], native_targets)
            self.assertNotEqual(calls[0][1], calls[1][1])
            self.assertTrue((root / "output" / "results.json").exists())

    def test_empty_results_are_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "no successful"):
                benchmark.summarize(Path(directory))

    def test_commands_match_pinned_xtask_implementation(self):
        source = Path(__file__).resolve().parents[2]
        check = (source / "xtask" / "src" / "check.rs").read_text(encoding="utf-8")
        section = check.split("pub fn tests_compile(")[1].split("pub fn tests_run(")[0]
        commands = [
            [arg for arg in shlex.split(command) if arg != "--locked"]
            for command in re.findall(r'"\{CARGO\} ([^"]+)"', section)
        ]
        self.assertEqual(commands, [args for _, args in benchmark.NATIVE_COMMANDS[1:]])
        wasm = (source / "xtask" / "src" / "wasm.rs").read_text(encoding="utf-8")
        command = re.search(r'"\{CARGO\} ([^"]+)"', wasm).group(1)
        args = [arg.replace("{package}", "ironrdp-web")
                for arg in shlex.split(command) if arg != "--locked"]
        self.assertEqual(args, benchmark.WASM_COMMAND)


if __name__ == "__main__":
    unittest.main()
