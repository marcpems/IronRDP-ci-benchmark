import copy
import json
import os
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch
import uuid

from breadth_audit import overlap, selectors, sha256
from breadth_probe import cargo_artifacts, compiler_environment, metered, run_scenario
from breadth_resolved_audit import main as resolved_main, postprocess


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

    def test_explicit_target_is_used_for_seed_measurement_and_correctness(self):
        target = "x86_64-pc-windows-msvc"
        with patch("breadth_probe.verify_source", return_value="index"), \
                patch("breadth_probe.metered", side_effect=self.fake_meter):
            result = run_scenario(
                self.source, self.root / "output", self.project, self.scenario,
                Path("cargo"), Path("rustc"), {}, 1, target=target,
            )
        self.assertEqual(result["target"], target)
        for row in [*result["setup"], result["measurement"], *result["correctness"]]:
            self.assertEqual(row["command"][-2:], ["--target", target])

    def test_paired_measured_cell_can_explicitly_defer_correctness_to_warmup(self):
        with patch("breadth_probe.verify_source", return_value="index"), \
                patch("breadth_probe.metered", side_effect=self.fake_meter) as measured:
            result = run_scenario(
                self.source, self.root / "output", self.project, self.scenario,
                Path("cargo"), Path("rustc"), {}, 1, run_correctness=False,
            )
        self.assertEqual(result["correctness"], [])
        self.assertEqual(result["correctness_policy"], "not-run-in-this-cell")
        self.assertEqual([call.args[4].name for call in measured.call_args_list], ["seed", "measured"])
        self.assertEqual(result["measurement"]["compiled_artifacts"], 0)
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


class ResolvedBreadthTests(unittest.TestCase):
    def setUp(self):
        self.lock = b"""
version = 3
[[package]]
name = "syn"
version = "2.0.101"
[[package]]
name = "syn"
version = "2.0.101"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "abc"
[[package]]
name = "proc"
version = "1.0.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "def"
[[package]]
name = "platform-only"
version = "1.0.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "ghi"
[[package]]
name = "unrelated"
version = "1.0.0"
"""
        self.manifest = {
            "host": "x86_64-pc-windows-msvc", "training": {"rustc_perf_sha": "pinned"},
            "projects": [{"id": "example", "revision": "pinned-project",
                          "lock_sha256": sha256(self.lock), "selected_packages": ["syn"],
                          "cargo_args": ["-p", "syn", "--all-features"]}],
            "scenarios": [{"id": "full-check", "mode": "full", "cargo_command": ["check"]}],
        }
        self.audit = {
            "schema": 1, "training": self.manifest["training"],
            "selectors": {"llvm": ["fixture"], "rustc": ["fixture"]},
            "fixtures": [{"fixture": "fixture", "lock_sha256": sha256(self.lock)}],
        }
        self.locks = {"fixture": self.lock}
        self.root_id = "path+file:///D:/fixture#syn@2.0.101"
        self.registry_id = "registry+https://github.com/rust-lang/crates.io-index#syn@2.0.101"
        ids = [self.root_id, self.registry_id, "opaque-proc-id", "opaque-platform-id",
               "path+file:///D:/fixture/unrelated#1.0.0"]
        names = ["syn", "syn", "proc", "platform-only", "unrelated"]
        self.metadata = {
            "version": 1,
            "packages": [
                {"id": key, "name": name, "version": "2.0.101" if name == "syn" else "1.0.0",
                 "source": ("registry+https://github.com/rust-lang/crates.io-index"
                            if index in (1, 2, 3) else None),
                 "manifest_path": f"D:\\fixture\\{index}\\Cargo.toml"}
                for index, (key, name) in enumerate(zip(ids, names))
            ],
            "resolve": {"nodes": [
                {"id": key, "dependencies": (
                    [ids[1], ids[3]] if index == 0 else [ids[2]] if index == 1 else []),
                 "features": ["default"]}
                for index, key in enumerate(ids)
            ]},
        }
        target = self.manifest["host"]
        self.capture = {
            "schema": 1, "project": "example", "scenario": "full-check",
            "source_revision": "pinned-project", "target": target,
            "selected_package_ids": [self.root_id],
            "metadata": {"command": ["cargo", "metadata", "--format-version=1", "--frozen",
                                     "--all-features"], "exit_code": 0, "filter_platform": None},
            "cargo": {"command": ["cargo", "check", "-p", "syn", "--all-features", "--frozen",
                                  "--message-format=json", "--target", target], "exit_code": 0},
        }
        self.events = [
            {"reason": "compiler-artifact", "package_id": key, "fresh": fresh,
             "features": ["default"],
             "target": {"name": names[index], "kind": ["proc-macro" if index == 2 else "lib"]}}
            for index, (key, fresh) in enumerate(zip(ids[:3], (False, False, True)))
        ] + [{"reason": "build-finished", "success": True}]

    def run_audit(self):
        return postprocess(self.manifest, self.audit, self.locks, self.lock, self.metadata,
                           "\n".join(json.dumps(event) for event in self.events), self.capture)

    def test_selected_resolve_artifact_and_compiled_scopes_remain_distinct(self):
        result = self.run_audit()
        self.assertEqual(result["resolve_scope"], "unfiltered-selected-root-reachability")
        self.assertEqual([result[key]["package_count"] for key in
                          ("selected_resolve", "observed_artifacts", "compiled_artifacts",
                           "fresh_artifacts")], [4, 3, 2, 1])
        phase = result["compiled_artifacts"]["phases"]["rustc"]
        exact = phase["exact_locked_registry_or_git_reuse"]
        self.assertEqual(len(exact), 1)
        self.assertEqual(exact[0]["package"]["checksum"], "abc")
        self.assertEqual(exact[0]["training_fixtures"], ["fixture"])
        local = next(row for row in result["compiled_artifacts"]["packages"]
                     if row["package_id"] == self.root_id)
        self.assertNotIn("source", local["package"])
        self.assertIsNone(local["metadata_source"])
        self.assertEqual(result["artifacts"][2]["target"]["kind"], ["proc-macro"])

    def test_filtered_metadata_uses_only_reachable_nodes_not_all_workspace_packages(self):
        self.capture["metadata"]["filter_platform"] = self.capture["target"]
        self.capture["metadata"]["command"].extend(("--filter-platform", self.capture["target"]))
        self.metadata["resolve"]["nodes"][0]["dependencies"] = [self.registry_id]
        result = self.run_audit()
        self.assertEqual(result["resolve_scope"], "platform-filtered-selected-root-reachability")
        self.assertEqual(result["selected_resolve"]["package_count"], 3)
        names = result["selected_resolve"]["phases"]["llvm"]["name_reuse_including_different_versions"]
        self.assertEqual([row["name"] for row in names], ["proc", "syn"])

    def test_all_fresh_capture_reports_no_compilation_without_inventing_reuse(self):
        for row in self.events[:-1]:
            row["fresh"] = True
        self.assertEqual(self.run_audit()["compiled_artifacts"]["package_count"], 0)

    def test_package_can_have_both_compiled_and_fresh_targets(self):
        self.events.insert(1, {**self.events[0], "fresh": True,
                               "target": {"name": "build-script-build", "kind": ["custom-build"]}})
        result = self.run_audit()
        self.assertIn(self.root_id, [row["package_id"] for row in result["compiled_artifacts"]["packages"]])
        self.assertIn(self.root_id, [row["package_id"] for row in result["fresh_artifacts"]["packages"]])
        self.assertEqual(len(result["artifacts"]), 4)

    def test_metadata_only_requires_explicit_mode_and_has_no_observation_fallback(self):
        del self.capture["cargo"]
        result = postprocess(self.manifest, self.audit, self.locks, self.lock,
                             self.metadata, None, self.capture, resolved_only=True)
        self.assertEqual(result["observation_status"], "resolved-not-observed")
        self.assertEqual(result["selected_resolve"]["package_count"], 4)
        for key in ("observed_artifacts", "compiled_artifacts", "fresh_artifacts", "artifacts"):
            self.assertIsNone(result[key])
        for messages, resolved_only in ((None, False), ("", True)):
            with self.subTest(messages=messages, resolved_only=resolved_only), self.assertRaises(ValueError):
                postprocess(self.manifest, self.audit, self.locks, self.lock,
                            self.metadata, messages, self.capture, resolved_only)
        self.capture["cargo"] = {"exit_code": 1}
        with self.assertRaisesRegex(ValueError, "must not include"):
            postprocess(self.manifest, self.audit, self.locks, self.lock,
                        self.metadata, None, self.capture, resolved_only=True)

    def test_input_preparation_metadata_receipt_retains_non_study_tools(self):
        self.capture["metadata"].update({
            "command": ["cargo", "metadata", "--format-version", "1", "--locked", "--offline",
                        "--filter-platform", self.capture["target"], "--all-features"],
            "filter_platform": self.capture["target"],
            "compiler_version": "rustc 1.93.0 ARM64 input-preparation only",
            "source_revision": "pinned-project", "source_status": "",
            "lock_sha256": sha256(self.lock),
        })
        del self.capture["cargo"]
        result = postprocess(self.manifest, self.audit, self.locks, self.lock,
                             self.metadata, None, self.capture, resolved_only=True)
        self.assertEqual(result["capture"]["metadata"]["compiler_version"],
                         "rustc 1.93.0 ARM64 input-preparation only")
        for key, value in (("exit_code", 1), ("source_revision", "wrong"),
                           ("lock_sha256", "wrong"), ("source_status", " M Cargo.toml")):
            original = self.capture["metadata"][key]
            self.capture["metadata"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                postprocess(self.manifest, self.audit, self.locks, self.lock,
                            self.metadata, None, self.capture, resolved_only=True)
            self.capture["metadata"][key] = original

    def test_failed_truncated_malformed_and_inconsistent_artifacts_fail_closed(self):
        original = copy.deepcopy(self.events)
        variants = [
            [], original[:-1], original + [original[-1]],
            original[:-1] + [{"reason": "build-finished", "success": False}],
            original + [original[0]], [None, original[-1]],
            [{"reason": "compiler-message", "message": {"level": "error"}}, *original],
            [{**original[0], "fresh": 0}, original[-1]],
            [{**original[0], "package_id": "missing"}, original[-1]],
            [{**original[0], "target": None}, original[-1]],
            [{**original[0], "features": ["not-resolved"]}, original[-1]],
            [{**original[0], "package_id": self.metadata["packages"][-1]["id"]}, original[-1]],
            [{"reason": "unknown"}, *original],
        ]
        for events in variants:
            with self.subTest(events=events), self.assertRaises(ValueError):
                self.events = events
                self.run_audit()
        self.events = original
        with self.assertRaises(ValueError):
            postprocess(self.manifest, self.audit, self.locks, self.lock, self.metadata,
                        "not JSON", self.capture)

    def test_missing_failure_and_mismatched_capture_provenance_rejected(self):
        original = copy.deepcopy(self.capture)
        for section, key, value in (
            ("cargo", "exit_code", None), ("cargo", "exit_code", 1),
            ("metadata", "exit_code", False), ("metadata", "filter_platform", "other"),
            ("metadata", "command", ["cargo", "metadata", "--no-deps"]),
            ("cargo", "command", ["cargo", "check"]),
            (None, "source_revision", "other"), (None, "target", "other"),
            (None, "selected_package_ids", [self.registry_id]),
            (None, "selected_package_ids", [self.root_id, self.root_id]),
        ):
            self.capture = copy.deepcopy(original)
            (self.capture[section] if section else self.capture)[key] = value
            with self.subTest(section=section, key=key, value=value), self.assertRaises(ValueError):
                self.run_audit()

    def test_identity_and_training_hash_mismatches_rejected(self):
        self.metadata["packages"][1]["source"] = "registry+https://different.example/index"
        with self.assertRaisesRegex(ValueError, "lock identity"):
            self.run_audit()
        self.metadata["packages"][1]["source"] = "registry+https://github.com/rust-lang/crates.io-index"
        self.locks["fixture"] += b"\n"
        with self.assertRaisesRegex(ValueError, "training lockfile"):
            self.run_audit()
        self.locks["fixture"] = self.lock
        self.manifest["projects"][0]["lock_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "project lockfile"):
            self.run_audit()

    def test_checksum_and_git_source_are_reconciled_without_parsing_opaque_ids(self):
        training_lock = self.lock.replace(b'checksum = "abc"', b'checksum = "changed"')
        self.locks["fixture"] = training_lock
        self.audit["fixtures"][0]["lock_sha256"] = sha256(training_lock)
        result = self.run_audit()
        self.assertEqual(result["compiled_artifacts"]["phases"]["rustc"]
                         ["exact_locked_registry_or_git_reuse"], [])
        git_source = "git+https://example.invalid/repo?rev=pinned#0123456789abcdef"
        self.lock = self.lock.replace(
            b'source = "registry+https://github.com/rust-lang/crates.io-index"\nchecksum = "abc"',
            f'source = "{git_source}"'.encode())
        self.manifest["projects"][0]["lock_sha256"] = sha256(self.lock)
        self.locks["fixture"] = self.lock
        self.audit["fixtures"][0]["lock_sha256"] = sha256(self.lock)
        self.metadata["packages"][1]["source"] = git_source
        result = self.run_audit()
        exact = result["compiled_artifacts"]["phases"]["rustc"]["exact_locked_registry_or_git_reuse"]
        self.assertEqual(exact[0]["package"]["source"], git_source)
        self.assertEqual(exact[0]["package"]["checksum"], "")

    def test_incomplete_metadata_resolve_is_not_a_root_only_success(self):
        original = copy.deepcopy(self.metadata)
        for change in ("no-resolve", "missing-node", "unknown-edge", "duplicate-id"):
            self.metadata = copy.deepcopy(original)
            if change == "no-resolve":
                self.metadata["resolve"] = None
            elif change == "missing-node":
                self.metadata["resolve"]["nodes"].pop()
            elif change == "unknown-edge":
                self.metadata["resolve"]["nodes"][0]["dependencies"].append("missing")
            else:
                self.metadata["packages"].append(self.metadata["packages"][0])
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.run_audit()

    def test_cli_hashes_exact_inputs_and_loads_pinned_git_blobs(self):
        root = Path.cwd() / f".breadth-resolved-fixture-{uuid.uuid4().hex}"
        root.mkdir()
        try:
            values = {"manifest": self.manifest, "training-audit": self.audit,
                      "metadata": self.metadata, "capture": self.capture}
            argv = ["breadth_resolved_audit"]
            for name in ("manifest", "training-audit", "metadata", "capture", "lock", "messages"):
                path = root / name
                data = (json.dumps(values[name]).encode() if name in values else self.lock
                        if name == "lock" else
                        "\n".join(json.dumps(event) for event in self.events).encode())
                path.write_bytes(data)
                argv.extend((f"--{name}", str(path)))
            output = root / "result.json"
            argv.extend(("--perf", str(root / "perf"), "--output", str(output)))
            with patch.object(sys, "argv", argv), \
                    patch("breadth_resolved_audit.git", return_value=self.lock) as git_mock:
                resolved_main()
            git_mock.assert_called_once_with(
                root / "perf", "show", "pinned:collector/compile-benchmarks/fixture/Cargo.lock")
            result = json.loads(output.read_bytes())
            for name, row in result["inputs"].items():
                self.assertEqual(row["sha256"], sha256(Path(row["path"]).read_bytes()), name)
            self.assertEqual(result["status"], "preparation-not-candidate-qualification")
            (root / "messages").write_bytes(b"{}\n")
            output.unlink()
            with patch.object(sys, "argv", argv), \
                    patch("breadth_resolved_audit.git", return_value=self.lock), \
                    self.assertRaises(ValueError):
                resolved_main()
            self.assertFalse(output.exists())
            del self.capture["cargo"]
            self.capture["metadata"]["sha256"] = {"stdout": sha256((root / "metadata").read_bytes())}
            (root / "capture").write_text(json.dumps(self.capture), encoding="utf-8")
            index = argv.index("--messages")
            del argv[index:index + 2]
            argv.append("--resolved-only")
            with patch.object(sys, "argv", argv), \
                    patch("breadth_resolved_audit.git", return_value=self.lock):
                resolved_main()
            result = json.loads(output.read_bytes())
            self.assertEqual(result["observation_status"], "resolved-not-observed")
            self.assertIsNone(result["compiled_artifacts"])
            self.assertNotIn("messages", result["inputs"])
            (root / "metadata").write_bytes((root / "metadata").read_bytes() + b"\n")
            output.unlink()
            with patch.object(sys, "argv", argv), \
                    patch("breadth_resolved_audit.git", return_value=self.lock), \
                    self.assertRaisesRegex(ValueError, "stdout hash mismatch"):
                resolved_main()
            self.assertFalse(output.exists())
        finally:
            shutil.rmtree(root)


if __name__ == "__main__":
    unittest.main()
