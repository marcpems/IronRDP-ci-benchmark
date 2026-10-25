import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from analyze_breadth_pairs import estimate, load_matrix, paired_order


class PairedBreadthAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.protocol = {"projects": ["small", "large"], "scenarios": ["check", "noop"],
                         "analysis": {"bootstrap_seed": 1012026, "bootstrap_draws": 100}}
        self.matrix = {
            project: {vm: {
                "check": {"base": scale * vm, "test": scale * vm * ratio},
                "noop": {"base": 1.0, "test": 1.0}}
                for vm in range(1, 6)}
            for project, scale, ratio in (("small", 1, .8), ("large", 100, 1.2))
        }

    def test_reports_regressions_and_equal_project_weighting(self):
        report = estimate(self.matrix, self.protocol)
        rows = {(r["project"], r["scenario"]): r for r in report["cells"]}
        self.assertAlmostEqual(rows["small", "check"]["reduction_fraction"], .2)
        self.assertAlmostEqual(rows["large", "check"]["reduction_fraction"], -.2)
        self.assertLess(rows["large", "check"]["ci95"]["reduction_fraction"][1], 0)
        family = next(r for r in report["families"] if r["scenario"] == "check")
        self.assertAlmostEqual(family["equal_project_reduction_fraction"], 1 - (.8 * 1.2) ** .5)
        noop = next(r for r in report["families"] if r["scenario"] == "noop")
        self.assertEqual(noop["conclusion"], "inconclusive")
        self.assertEqual(noop["ci95"], [0, 0])

    def test_bootstrap_is_reproducible_and_preserves_same_vm_pairs(self):
        first = estimate(self.matrix, self.protocol)
        self.assertEqual(first, estimate(self.matrix, self.protocol))
        row = next(r for r in first["cells"] if r["project"] == "small" and r["scenario"] == "check")
        for bound in row["ci95"]["reduction_fraction"]:
            self.assertAlmostEqual(bound, .2)


class PairedMatrixValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.protocol = {
            "projects": ["fd"], "scenarios": ["full-check"], "variants": ["base", "test"],
            "independent_vms": 1, "warmup_rounds": 1, "measured_rounds": 2,
            "cores": 4, "host": "host", "rust_version": "1.94.1",
            "corpus_sha256": "corpus", "rustdoc_sha256": "doc",
            "compiler_pins": {v: {"rustc_sha256": v, "driver_sha256": {}} for v in ("base", "test")},
        }
        project = {"id": "fd", "revision": "source", "lock_sha256": "lock",
                   "cargo_args": [], "correctness": [["test"]]}
        scenario = {"id": "full-check", "mode": "full", "cargo_command": ["check"], "incremental": "0"}
        self.corpus = {"projects": [project], "scenarios": [scenario]}
        evidence = {"archive_sha256": "archive", "result_sha256": "result"}
        self.reference = {"stdlib": {"libstd.rlib": "std"}, "cargo_sha256": "cargo",
                          "compiler_metadata": {"local": {"complete": True}},
                          "artifact_evidence": {"local": evidence},
                          "versions": {"official": "base-version", "local": "test-version"}}
        home = "D:/bp/rustup/toolchains/1.94.1-host/bin/"
        tools = {
            "variants": {v: {**self.protocol["compiler_pins"][v], "rustc_verbose_version": v + "-version"}
                         for v in ("base", "test")},
            "stdlib": self.reference["stdlib"], "cargo_sha256": "cargo", "rustdoc_sha256": "doc",
            "compiler_metadata": {"complete": True}, "artifact_evidence": evidence,
            "cargo_version": "cargo", "rustdoc": home + "rustdoc.exe",
        }
        self.write("toolchain.json", tools)
        self.index = {
            "complete": True, "status": "passed", "protocol": self.protocol, "protocol_sha256": "protocol",
            "corpus_sha256": "corpus", "project": "fd", "replicate": 1, "vm": 1, "cores": 4,
            "run_id": "123", "attempt": "1", "tool_identity": tools, "runs": [],
        }
        for r in range(3):
            for position, variant in enumerate(paired_order(["base", "test"], 1, r)):
                folder = f"r{r}-{variant}-full-check"
                warmup = r == 0
                policy = "original-commands" if warmup else "not-run-in-this-cell"
                row = {"command": [home + "cargo.exe", "check", "--frozen", "--message-format=json",
                                   "--target", "host"], "exit_code": 0, "affinity": [0, 1, 2, 3],
                       "wall_seconds": 2 if variant == "base" else 1.8, "cpu_seconds": 1,
                       "user_seconds": .75, "kernel_seconds": .25,
                       "compiled_artifacts": 1, "fresh_artifacts": 0}
                result = {
                    "status": "non-qualifying-smoke", "project": "fd", "scenario": scenario,
                    "source_revision": "source", "lock_sha256": "lock", "target": "host",
                    "tool_identity": {**tools, "variant": variant}, "measurement": row,
                    "git_index_sha256": "git", "edit_original_sha256": "edit",
                    "compiler": (home + "rustc.exe" if variant == "base" else
                                 "D:/bp/e/compilers/rustc-1.94.1-host/rustc/bin/rustc.exe"),
                    "cargo": home + "cargo.exe", "environment": {
                        "CARGO_INCREMENTAL": "0", "CARGO_NET_OFFLINE": "true", "CARGO_BUILD_JOBS": "4"},
                    "setup": [], "correctness_policy": policy,
                    "correctness": [{"exit_code": 0, "command": [
                        home + "cargo.exe", "test", "--frozen", "--target", "host"]}] if warmup else [],
                }
                self.write(folder + "/results.json", result)
                (self.root / folder / "measured.stdout").write_text(
                    '{"reason":"compiler-artifact","fresh":false}\n'
                    '{"reason":"build-finished","success":true}\n')
                if warmup:
                    (self.root / folder / "correctness-0.stdout").write_text(
                        "test result: ok. 10 passed; 0 failed; 2 ignored; 0 measured; 0 filtered out;\n")
                check_path = f"r0-{variant}-full-check/results.json"
                self.index["runs"].append({
                    "round": r, "scenario": "full-check", "position": position, "variant": variant,
                    "status": "passed", "warmup": warmup, "exclusion": "preplanned-warmup" if warmup else None,
                    "path": folder + "/results.json", "measurement": row, "correctness_policy": policy,
                    "correctness_path": check_path,
                    "correctness_sha256": hashlib.sha256((self.root / check_path).read_bytes()).hexdigest(),
                })
        self.write("index.json", self.index)

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def load(self):
        return load_matrix(self.root, self.protocol, self.corpus, self.reference, "protocol")

    def test_complete_matrix_retains_both_variants_and_upstream_ignores(self):
        matrix, attempt, checks = self.load()
        self.assertEqual(matrix["fd"][1]["full-check"], {"base": 2, "test": 1.8})
        self.assertEqual(attempt, ("123", "1"))
        self.assertEqual([r["upstream_ignored"] for r in checks], [2, 2])

    def test_missing_row_or_wrong_order_fails_closed(self):
        for entries in (self.index["runs"][:-1], list(reversed(self.index["runs"]))):
            with self.subTest(entries=len(entries)):
                self.write("index.json", {**self.index, "runs": entries})
                with self.assertRaisesRegex(ValueError, "ordered paired matrix"):
                    self.load()

    def test_measured_row_cannot_link_other_compilers_correctness(self):
        index = copy.deepcopy(self.index)
        index["runs"][2]["correctness_path"] = "r0-base-full-check/results.json"
        self.write("index.json", index)
        with self.assertRaisesRegex(ValueError, "correctness linkage"):
            self.load()

    def test_filtered_correctness_output_fails_closed(self):
        (self.root / "r0-base-full-check/correctness-0.stdout").write_text(
            "test result: ok. 10 passed; 0 failed; 0 ignored; 0 measured; 1 filtered out;\n")
        with self.assertRaisesRegex(ValueError, "filtered correctness"):
            self.load()

    def test_failed_job_is_not_salvaged_as_a_partial_sample(self):
        self.write("index.json", {**self.index, "complete": False, "status": "failed"})
        with self.assertRaisesRegex(ValueError, "Incomplete job"):
            self.load()


if __name__ == "__main__":
    unittest.main()
