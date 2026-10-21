import json
import os
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch
import uuid

from breadth_audit import overlap, selectors
from breadth_probe import cargo_artifacts, compiler_environment, metered, run_scenario


def events(fresh):
    return "\n".join(json.dumps(row) for row in (
        {"reason": "compiler-artifact", "fresh": fresh},
        {"reason": "build-finished", "success": True},
    ))


class BreadthTests(unittest.TestCase):
    def setUp(self):
        self.root = Path.cwd() / f".breadth-fixture-{uuid.uuid4().hex}"
        self.source = self.root / "source"
        self.source.mkdir(parents=True)
        (self.source / "lib.rs").write_bytes(b"pub fn value() -> u32 { 1 }\n")
        self.original = (self.source / "lib.rs").read_bytes()
        self.project = {
            "id": "fixture", "revision": "fixture", "lock_sha256": "fixture",
            "source_edit": "lib.rs", "cargo_args": [],
            "correctness": [["test"]],
        }
        self.scenario = {"id": "fixture", "mode": "noop", "cargo_command": ["build"]}

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_noop_accepts_only_fresh_artifacts(self):
        self.assertEqual(cargo_artifacts(events(True), "noop")["compiled_artifacts"], 0)
        with self.assertRaisesRegex(ValueError, "no-op"):
            cargo_artifacts(events(False), "noop")

    def test_full_and_edit_reject_all_fresh_artifacts(self):
        for mode in ("full", "edit"):
            with self.subTest(mode=mode):
                with self.assertRaisesRegex(ValueError, "compiled no"):
                    cargo_artifacts(events(True), mode)
                self.assertEqual(cargo_artifacts(events(False), mode)["compiled_artifacts"], 1)

    def test_failed_missing_or_duplicate_finish_is_rejected(self):
        for text in (
            "", '{"reason":"build-finished","success":false}',
            events(True) + '\n{"reason":"build-finished","success":true}',
            '{"reason":"compiler-artifact"}',
        ):
            with self.subTest(text=text), self.assertRaises(ValueError):
                cargo_artifacts(text, "noop")

    def test_lock_reuse_requires_source_and_checksum_not_just_package_name(self):
        package = {"name": "syn", "version": "2.0.101", "source": "registry+fixture",
                   "checksum": "abc"}
        training = {"syn-fixture": [package, {"name": "local", "version": "1"}]}
        different = {**package, "checksum": "changed"}
        result = overlap([package, different, {"name": "local", "version": "1"}], training)
        self.assertEqual(len(result["exact_locked_registry_or_git_reuse"]), 1)
        self.assertEqual([r["name"] for r in result["name_reuse_including_different_versions"]],
                         ["local", "syn"])

    def test_missing_training_selectors_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "missing training selector"):
            selectors("pub const LLVM_PGO_CRATES: &[&str] = &[\"one\"];")

    def test_profiles_preserved_and_inherited_target_overrides_rejected(self):
        env = compiler_environment({"PATH": "fixture"}, Path("rustc"), 4, "1")
        self.assertNotIn("CARGO_PROFILE_DEV_DEBUG", env)
        self.assertEqual(env["CARGO_INCREMENTAL"], "1")
        for key in ("CARGO_PROFILE_DEV_DEBUG", "CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_RUSTFLAGS",
                    "RUSTDOC", "RUSTC_BOOTSTRAP"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                compiler_environment({key: "unexpected"}, Path("rustc"), 4, "0")

    def fake_meter(self, command, source, env, cores, prefix, background):
        prefix.with_suffix(".stdout").write_text(events(prefix.name == "measured"
                                                       and self.scenario["mode"] == "noop"))
        return {"command": command, "exit_code": 0, "wall_seconds": 1, "cpu_seconds": 2,
                "peak_job_memory_bytes": 1234}

    def run_fixture(self, meter=None):
        with patch("breadth_probe.verify_source", return_value="index"), \
                patch("breadth_probe.metered", side_effect=meter or self.fake_meter):
            return run_scenario(self.source, self.root / "output", self.project, self.scenario,
                                Path("cargo"), Path("rustc"), {}, 1)

    def test_noop_keeps_seed_and_correctness_outside_measurement(self):
        result = self.run_fixture()
        self.assertEqual(len(result["setup"]), 1)
        self.assertEqual(len(result["correctness"]), 1)
        self.assertEqual(result["measurement"]["compiled_artifacts"], 0)
        self.assertEqual(result["measurement"]["wall_seconds"], 1)
        self.assertEqual(result["status"], "non-qualifying-smoke")
        self.assertEqual((self.source / "lib.rs").read_bytes(), self.original)

    def test_comment_edit_is_restored_even_on_measured_failure(self):
        self.scenario["mode"] = "edit"

        def fail(command, source, env, cores, prefix, background):
            if prefix.name == "measured":
                self.assertNotEqual((source / "lib.rs").read_bytes(), self.original)
                raise RuntimeError("fixture measurement failure")
            return self.fake_meter(command, source, env, cores, prefix, background)

        with self.assertRaisesRegex(RuntimeError, "fixture measurement"):
            self.run_fixture(fail)
        self.assertEqual((self.source / "lib.rs").read_bytes(), self.original)
        record = json.loads((self.root / "output" / "results.json").read_text())
        self.assertEqual(record["status"], "failed-non-qualifying-smoke")
        self.assertNotIn("measurement", record)

    def test_correctness_failure_is_not_a_successful_sample(self):
        def fail(command, source, env, cores, prefix, background):
            if prefix.name.startswith("correctness"):
                raise RuntimeError("fixture correctness failure")
            return self.fake_meter(command, source, env, cores, prefix, background)

        with self.assertRaisesRegex(RuntimeError, "fixture correctness"):
            self.run_fixture(fail)
        record = json.loads((self.root / "output" / "results.json").read_text())
        self.assertEqual(record["status"], "failed-non-qualifying-smoke")
        self.assertIn("measurement", record)

    def test_existing_output_and_source_nested_output_rejected(self):
        (self.root / "output").mkdir()
        with self.assertRaises(FileExistsError):
            self.run_fixture()
        with self.assertRaisesRegex(ValueError, "outside the source"):
            run_scenario(self.source, self.source / "output", self.project, self.scenario,
                         Path("cargo"), Path("rustc"), {}, 1)

    @unittest.skipUnless(os.name == "nt", "native Windows Job Object meter")
    def test_real_meter_memory_peak_is_not_carried_from_previous_command(self):
        env = dict(os.environ)
        large = metered(
            [sys.executable, "-c",
             "x=bytearray(64*1024*1024); import time; time.sleep(0.05)"],
            self.root, env, 1, self.root / "large", (),
        )
        small = metered([sys.executable, "-c", "pass"],
                        self.root, env, 1, self.root / "small", ())
        self.assertGreater(large["peak_job_memory_bytes"], small["peak_job_memory_bytes"])
        self.assertGreater(large["peak_job_memory_bytes"], 64 * 1024 * 1024)
        self.assertEqual(len(small["affinity"]), 1)


if __name__ == "__main__":
    unittest.main()
