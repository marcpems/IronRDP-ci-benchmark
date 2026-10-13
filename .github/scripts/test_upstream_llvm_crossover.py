import copy
from contextlib import nullcontext
import json
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from test_upstream_release_probe import fixture
from upstream_llvm_crossover import (
    cmake_cache, normalized_cache, normalized_config, run_crossover, trial_order,
)


class CrossoverTests(unittest.TestCase):
    def test_each_setting_occupies_each_execution_position(self):
        orders = [trial_order(first) for first in ("baseline", "jobs6", "link1")]
        for position in range(3):
            self.assertEqual({order[position] for order in orders}, {"baseline", "jobs6", "link1"})
        with self.assertRaises(ValueError):
            trial_order("unknown")

    def test_config_comparison_ignores_only_scheduling_and_its_recorded_arguments(self):
        baseline = fixture("x86_64-pc-windows-msvc")
        baseline["build"]["configure-args"] = ["--enable-full-tools"]
        candidate = copy.deepcopy(baseline)
        candidate["build"]["jobs"] = 6
        candidate["build"]["configure-args"] += ["--set", "build.jobs=6"]
        self.assertEqual(normalized_config(candidate), baseline)
        self.assertEqual(candidate["build"]["jobs"], 6)
        candidate["dist"]["compression-profile"] = "fast"
        self.assertNotEqual(normalized_config(candidate), baseline)
        candidate["build"]["configure-args"] = ["build.jobs=6"]
        with self.assertRaises(RuntimeError):
            normalized_config(candidate)

    def test_cache_comparison_keeps_profile_and_optimization_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CMakeCache.txt"
            path.write_text("// comment\n# generated\nLLVM_PROFDATA_FILE:FILEPATH=D:/p.profdata\n"
                            "LLVM_PARALLEL_COMPILE_JOBS:STRING=6\nLLVM_ENABLE_ASSERTIONS:BOOL=OFF\n")
            values = cmake_cache(path)
            normalized = normalized_cache(values)
            self.assertNotIn("LLVM_PARALLEL_COMPILE_JOBS", normalized)
            self.assertEqual(normalized["LLVM_PROFDATA_FILE"]["value"], "D:/p.profdata")
            self.assertEqual(normalized["LLVM_ENABLE_ASSERTIONS"]["value"], "OFF")

    def simulate_crossover(self, root, change_optimization=False):
        source, output = root / "source", root / "evidence"
        source.mkdir()
        output.mkdir()
        (source / "opt-artifacts").mkdir()
        (source / "opt-artifacts/llvm-pgo.profdata").write_bytes(b"common-profile")
        host = "x86_64-pc-windows-msvc"
        config = fixture(host)
        environments = []

        def measure(command, cwd, env, cores, prefix, **kwargs):
            self.assertEqual(cwd, source)
            self.assertEqual(cores, 4)
            self.assertIn("src/llvm-project/llvm src/llvm-project/lld", env["SCRIPT"])
            is_dry = "--dry-run" in env["SCRIPT"]
            setting = ("jobs6" if "build.jobs=6" in env["RUST_CONFIGURE_ARGS"] else
                       "link1" if "llvm.link-jobs=1" in env["RUST_CONFIGURE_ARGS"] else "baseline")
            current = copy.deepcopy(config)
            if setting == "jobs6":
                current["build"]["jobs"] = 6
            if setting == "link1":
                current["llvm"]["link-jobs"] = 1
            (source / "bootstrap.toml").write_text("\n".join(
                f"[{section}]\n" + "\n".join(f"{key} = {json.dumps(value)}" for key, value in values.items())
                for section, values in current.items()))
            if not is_dry:
                environments.append(env)
                for name, count in (("llvm", 1000), ("lld", 1)):
                    build = source / "build" / host / name
                    self.assertFalse(build.exists(), "trial reused previous build output")
                    (build / "build").mkdir(parents=True)
                    (build / "bin").mkdir()
                    (build / "bin/llvm-config.exe").write_bytes(b"binary")
                    for i in range(count):
                        (build / "build" / f"source-{i}.obj").touch()
                    cache = (
                        f"LLVM_PROFDATA_FILE:FILEPATH={(source / 'opt-artifacts/llvm-pgo.profdata').as_posix()}\n"
                        f"LLVM_PARALLEL_COMPILE_JOBS:STRING={6 if setting == 'jobs6' else 4}\n"
                        f"LLVM_PARALLEL_LINK_JOBS:STRING={'1' if setting == 'link1' else ''}\n"
                        f"LLVM_ENABLE_ASSERTIONS:BOOL={'ON' if change_optimization and setting == 'jobs6' else 'OFF'}\n"
                    )
                    (build / "build/CMakeCache.txt").write_text(cache)
                seconds = {"baseline": 10, "jobs6": 8, "link1": 11}[setting]
                metrics = {"system_stats": {"cpu_threads_count": 4}, "invocations": [{
                    "cmdline": env["SCRIPT"], "duration_including_children_sec": seconds,
                    "children": [{"type": "bootstrap::llvm::Llvm",
                                  "duration_excluding_children_sec": seconds, "children": []}],
                }]}
                (source / "build/metrics.json").write_text(json.dumps(metrics))
            return {"exit_code": 0, "wall_seconds": 20}

        def run(command, **kwargs):
            if Path(command[0]).name == "llvm-dis.exe":
                Path(command[-1]).write_text("define i32 @main() {\n  ret i32 42\n}\n")
            return SimpleNamespace(returncode=42 if Path(command[0]).name == "probe.exe" else 0)

        provenance = {"host": host, "job_started_unix": time.time(),
                      "tools": {"sccache.exe": {"path": "sccache.exe"}}}
        env = {
            "RUST_CONFIGURE_ARGS": "--original", "SCCACHE_DIR": str(root / "preparation-cache"),
            "SCRIPT": "RUST_BACKTRACE=full python x.py dist bootstrap --include-default-paths "
                      f'--set pgo.llvm.use="{(source / "opt-artifacts/llvm-pgo.profdata").as_posix()}"',
        }
        with patch("upstream_llvm_crossover.measure", side_effect=measure), \
                patch("upstream_llvm_crossover.measurement_session", return_value=nullcontext()), \
                patch("upstream_llvm_crossover.telemetry_executables", return_value=[]), \
                patch("upstream_llvm_crossover.shutil.disk_usage", return_value=SimpleNamespace(free=100 * 1024**3)), \
                patch("upstream_llvm_crossover.subprocess.run", side_effect=run), \
                patch("upstream_llvm_crossover.subprocess.check_output", return_value="same-version-or-targets"):
            run_crossover(source, output, "baseline", env, provenance, config)
        return json.loads((output / "result.json").read_text()), environments

    def test_crossover_rebuilds_objects_and_separates_caches_and_component_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, envs = self.simulate_crossover(Path(tmp))
            self.assertTrue(result["complete"])
            self.assertFalse(result["full_distribution_qualified"])
            self.assertEqual(len(result["samples"]), 3)
            self.assertEqual(len({env["SCCACHE_DIR"] for env in envs}), 3)
            self.assertEqual(len({env["SCRIPT"] for env in envs}), 1)
            self.assertAlmostEqual(result["paired_component_change_percent"]["jobs6"], -20)
            self.assertAlmostEqual(result["paired_component_change_percent"]["link1"], 10)
            self.assertEqual(len(list((Path(tmp) / "llvm-crossover-retained").iterdir())), 6)

    def test_crossover_rejects_unexpected_cmake_optimization_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "CMake configuration changed"):
                self.simulate_crossover(Path(tmp), change_optimization=True)
            self.assertFalse((Path(tmp) / "evidence/result.json").exists())


if __name__ == "__main__":
    unittest.main()
