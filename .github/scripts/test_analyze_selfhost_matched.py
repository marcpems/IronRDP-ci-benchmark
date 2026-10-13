from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest

from analyze_selfhost_matched import analyze, word_document
from build_arm_compilers import digest, save
from matched_release import LLVM, PERF, RUST, VARIANTS
from native_ci_probe import NATIVE_COMMANDS, paired_order


class SelfhostAnalysisTests(unittest.TestCase):
    def fixture(self, root, highcore=False):
        protocol = {"rust_sha": RUST, "llvm_sha": LLVM, "perf_sha": PERF,
                    "source_sha": "workload", "cores": 4}
        arch = "arm64" if highcore else "x64"
        machine = "self-hosted-arm64-highcore" if highcore else "self-hosted-x64"
        host = "aarch64-pc-windows-msvc" if highcore else "x86_64-pc-windows-msvc"
        cores = 64 if highcore else 4
        runner = {"runner_class": machine, "runner_name": "GB300-Arm64" if highcore else "MARCPE-TEST01-X64",
                  "build_affinity_count": cores, "build_jobs": cores, "logical_cpus": 72 if highcore else 16}
        tools = {"msvc": "same", "sdk": "same", "files": {}}
        releases, output = root / "releases", root / "benchmark"
        releases.mkdir()
        output.mkdir()
        index = {"runner": runner, "selfhost_schema": 1, "complete": True, "pilot": True,
                 "benchmark_attempt": "1", "benchmark_run": "555", "host": host, "vm": 1,
                 "protocol": {**protocol, "cores": cores, "resource_class": machine}, "tools": tools,
                 "release_runs": {}, "compiler_metadata": {}, "artifact_evidence": {}, "runs": []}
        jobs = {"jobs": []}
        now = datetime(2026, 10, 13, tzinfo=timezone.utc)
        for n, variant in enumerate(VARIANTS):
            run_id = str(100 + n)
            folder = releases / f"release-{arch}-{variant}-1-evidence"
            folder.mkdir()
            item = {**runner, **{key: protocol[key] for key in ("rust_sha", "llvm_sha", "perf_sha")},
                    "complete": True, "full_distribution": True, "pilot": True,
                    "run_id": run_id, "variant": variant, "host": host, "vm": 1,
                    "attempt": "1", "tools": tools}
            save(folder / "result.json", item)
            save(folder / "distribution-timing.json", {"wall_seconds": 100 * (n + 1)})
            save(folder / "extracted-dist-tests.json", {"exit_code": 0, "wall_seconds": 10})
            names = [f"rustc-nightly-{host}.tar.xz"]
            if variant == "baseline":
                names += [f"cargo-nightly-{host}.tar.xz", f"rust-std-nightly-{host}.tar.xz"]
            hashes = dict.fromkeys(names, "hash")
            save(folder / "dist-manifest.json", [{"name": k, "sha256": v} for k, v in hashes.items()])
            index["release_runs"][variant] = run_id
            index["compiler_metadata"][variant] = item
            checksum = digest(folder / "result.json")
            index["artifact_evidence"][variant] = {"result_sha256": checksum, "archives": hashes}
            jobs["jobs"].append({
                "id": n + 1, "run_id": int(run_id), "run_attempt": 1, "status": "completed",
                "conclusion": "success", "name": f"{arch} / {variant} / 1",
                "started_at": now.isoformat(), "completed_at": (now + timedelta(seconds=500)).isoformat(),
                "steps": [{
                    "name": "Reclaim qualified self-hosted build space after uploads",
                    "conclusion": "success", "started_at": (now + timedelta(seconds=450)).isoformat(),
                    "completed_at": (now + timedelta(seconds=470)).isoformat(),
                }] if n else [],
            })
            if n:
                maintenance = releases / f"release-{arch}-{variant}-1-maintenance"
                maintenance.mkdir()
                save(maintenance / "space-recovery.json", {
                    "complete": True, "result_sha256": checksum, "started_unix": 450, "finished_unix": 465,
                })
            block = {
                "metadata": {"source_sha": "workload", "variant": variant, "round": 0,
                             "profile_environment": {"CARGO_NET_OFFLINE": "true", "CARGO_BUILD_JOBS": str(cores)}},
                "measurements": [{"name": name, "exit_code": 0, "wall_seconds": 20 - n * 2,
                                  "cpu_seconds": 30, "affinity": list(range(cores)),
                                  "command": ["cargo", "--frozen"], "compiled_artifacts": 1}
                                 for name, _ in NATIVE_COMMANDS],
                "correctness": [{"name": name, "exit_code": 0,
                                 "environment_overrides": {"RUST_TEST_THREADS": "1"}}
                                for name, _ in NATIVE_COMMANDS[1:]],
            }
            save(output / f"{variant}.json", block)
            index["runs"].append({
                "variant": variant, "round": 0, "warmup": False, "path": f"{variant}.json",
                "position": paired_order(list(VARIANTS), 1, 0).index(variant),
            })
        save(output / "index.json", index)
        return releases, output / "index.json", jobs, protocol

    def test_observed_pilot_percentages_and_full_maintenance_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = self.fixture(Path(tmp))
            result = analyze(*args)
            self.assertTrue(result["pilot"])
            self.assertEqual(result["repetitions"], 1)
            self.assertEqual(result["variants"]["msvc-pgo"]["production_increase_percent"], 100)
            self.assertAlmostEqual(result["variants"]["msvc-pgo"]["ironrdp_saving_percent"], 10)
            self.assertEqual(result["variants"]["msvc-pgo"]["maintenance_seconds"], 20)
            self.assertNotIn("ci95", json.dumps(result))
            document = Path(tmp) / "fixture.docx"
            word_document([result], document)
            self.assertTrue(document.is_file())

    def test_highcore_requires_matching_64_worker_measurements(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = self.fixture(Path(tmp), highcore=True)
            self.assertEqual(analyze(*args)["runner"]["build_jobs"], 64)
            path = args[1].parent / "baseline.json"
            block = json.loads(path.read_text())
            block["metadata"]["profile_environment"]["CARGO_BUILD_JOBS"] = "4"
            save(path, block)
            with self.assertRaisesRegex(ValueError, "environment"):
                analyze(*args)

    def test_failure_mixing_and_missing_maintenance_are_rejected(self):
        for problem in ("timeout", "wrong-run", "hosted", "wrong-tools", "missing-cleanup", "unqualified"):
            with self.subTest(problem=problem), tempfile.TemporaryDirectory() as tmp:
                releases, path, jobs, protocol = self.fixture(Path(tmp))
                index = json.loads(path.read_text())
                if problem == "timeout":
                    jobs["jobs"][1]["conclusion"] = "timed_out"
                elif problem == "wrong-run":
                    index["release_runs"]["baseline"] = "999"
                elif problem == "hosted":
                    index["runner"]["runner_class"] = "github-hosted"
                elif problem == "wrong-tools":
                    index["tools"] = deepcopy(index["tools"])
                    index["tools"]["msvc"] = "other"
                elif problem == "missing-cleanup":
                    jobs["jobs"][1]["steps"] = []
                else:
                    file = releases / "release-x64-msvc-pgo-1-evidence" / "result.json"
                    item = json.loads(file.read_text())
                    item["complete"] = False
                    save(file, item)
                save(path, index)
                with self.assertRaises(ValueError):
                    analyze(releases, path, jobs, protocol)


if __name__ == "__main__":
    unittest.main()
