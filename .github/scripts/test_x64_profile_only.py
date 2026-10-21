import copy
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from build_arm_compilers import digest, save
from native_ci_probe import PROFILE_ENV, paired_order
from offline_benchmark import NATIVE_COMMANDS
from qualify_x64_profile_existing import verify_retained_evidence
from preserve_x64_profile_control import recovered_result
from x64_profile_only import audit_profile_use, load_profiles, tests_only_helper, verify_pair
from x64_profile_replay import checked_compiler, summarize


class ProfileOnlyTests(unittest.TestCase):
    def test_replay_from_prior_run_requires_pinned_metadata_and_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "a/x64-profile-official-evidence"
            dist = root / "a/x64-profile-official-dist"
            evidence.mkdir(parents=True)
            dist.mkdir()
            protocol = {"rust_version": "1.94.1", "host": "x86_64-pc-windows-msvc",
                        "llvm_profile_sha256": {"official": "profile"}}
            name = "rustc-1.94.1-x86_64-pc-windows-msvc"
            fixture = root / "rustc.exe"
            fixture.write_bytes(b"compiler fixture")
            archive = dist / f"{name}.tar.xz"
            with tarfile.open(archive, "w:xz") as bundle:
                bundle.add(fixture, arcname=f"{name}/rustc/bin/rustc.exe")
            save(evidence / "result.json", {
                "complete": True, "protocol": protocol, "variant": "official",
                "run_id": "release", "attempt": "1", "llvm_profile_sha256": "profile"})
            save(evidence / "dist-manifest.json", [{
                "name": archive.name, "bytes": archive.stat().st_size, "sha256": digest(archive)}])
            inputs = {"release_run": "release", "release_attempt": "1",
                      "compiler_metadata_sha256": {"official": digest(evidence / "result.json")},
                      "compiler_archive_sha256": {"official": digest(archive)},
                      "compiler_archive_bytes": {"official": archive.stat().st_size}}
            with patch.dict("os.environ", {"GITHUB_RUN_ID": "replay", "GITHUB_RUN_ATTEMPT": "1"}):
                with self.assertRaisesRegex(RuntimeError, "Unqualified or wrong"):
                    checked_compiler(root, root / "e", "official", protocol)
                changed = copy.deepcopy(inputs)
                changed["compiler_metadata_sha256"]["official"] = "changed"
                with self.assertRaisesRegex(RuntimeError, "metadata differs"):
                    checked_compiler(root, root / "e", "official", protocol, changed)
                changed = copy.deepcopy(inputs)
                changed["compiler_archive_sha256"]["official"] = "changed"
                with self.assertRaisesRegex(RuntimeError, "archive differs"):
                    checked_compiler(root, root / "e", "official", protocol, changed)
                _, compiler, _ = checked_compiler(root, root / "e", "official", protocol, inputs)
                self.assertEqual(compiler.read_bytes(), fixture.read_bytes())

    def test_preserved_control_keeps_production_and_qualification_identities(self):
        expected = {"run_id": "production", "attempt": "1"}
        protocol = {"scope": "one profile-only pair"}
        qualification = {
            "complete": True, "original_evidence": expected, "production_run_id": "production",
            "production_attempt": "1", "qualification_run_id": "39608556774", "qualification_attempt": "1",
            "original_provenance": {"protocol": protocol, "variant": "official", "run_id": "production"},
            "production_measurement": {"exit_code": 0, "wall_seconds": 100},
            "qualification_seconds": 10, "qualification": "upstream tests passed",
        }
        result = recovered_result(qualification, expected, protocol, "continuation", "1")
        self.assertEqual(result["run_id"], "continuation")
        self.assertEqual(result["production_run_id"], "production")
        self.assertEqual(result["qualification_run_id"], "39608556774")
        self.assertEqual(result["production_seconds"], 100)
        self.assertTrue(result["recovered_control"])
        with self.assertRaisesRegex(RuntimeError, "designated qualified control"):
            recovered_result({**qualification, "complete": False}, expected, protocol, "continuation", "1")
        with self.assertRaisesRegex(RuntimeError, "designated qualified control"):
            recovered_result({**qualification, "qualification_run_id": "wrong"}, expected, protocol, "continuation", "1")

    def test_recovery_rejects_changed_or_failed_production_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save(root / "provenance.json", {"run_id": "original", "attempt": "1", "variant": "official"})
            save(root / "fixed-profile-dist.json", {"exit_code": 0, "wall_seconds": 100})
            expected = {"run_id": "original", "attempt": "1", "evidence_sha256": {
                name: digest(root / name) for name in ("provenance.json", "fixed-profile-dist.json")}}
            _, measurement = verify_retained_evidence(root, expected)
            self.assertEqual(measurement["wall_seconds"], 100)
            save(root / "fixed-profile-dist.json", {"exit_code": 1, "wall_seconds": 100})
            with self.assertRaisesRegex(RuntimeError, "evidence changed"):
                verify_retained_evidence(root, expected)
            expected["evidence_sha256"]["fixed-profile-dist.json"] = digest(root / "fixed-profile-dist.json")
            with self.assertRaisesRegex(RuntimeError, "successful production"):
                verify_retained_evidence(root, expected)

    def test_profile_audit_retains_only_standalone_utility_main_collisions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, profile = root / "r", root / "rustc-pgo.profdata"
            prefix = f"warning: {source}/src/llvm-project/llvm"
            suffix = (": function control flow change detected (hash mismatch) main "
                      "Hash = 123 up to 501 count discarded [-Wbackend-plugin]")
            expected = [prefix + "/tools/llc/llc.cpp" + suffix,
                        prefix + "/utils/FileCheck/FileCheck.cpp" + suffix]
            rejected = [prefix + "/lib/CodeGen/CodeGen.cpp" + suffix,
                        (prefix + "/tools/llc/llc.cpp" + suffix).replace("main Hash", "compileModule Hash"),
                        "warning: profile data may be out of date",
                        prefix.replace(str(source), str(root / "other")) + "/tools/llc/llc.cpp" + suffix]
            (root / "fixed-profile-dist.stdout").write_text(
                f'"-Cprofile-use={profile}"\n' + "\n".join(expected + rejected), encoding="utf-8")
            (root / "fixed-profile-dist.stderr").write_text("", encoding="utf-8")
            audit = audit_profile_use(source, root, profile)
            self.assertTrue(audit["rustc_profile_use"])
            self.assertEqual(audit["standalone_llvm_utility_main_warnings"], expected)
            self.assertEqual(audit["rejected_profile_mismatch_warnings"], rejected)
            self.assertEqual(audit["profile_mismatch_warnings"], expected + rejected)

    def test_pair_rejects_common_input_changes_but_allows_only_llvm_profile(self):
        control = {
            "complete": True, "variant": "official", "protocol": {"fixed": True},
            "configuration": "identical", "rustc_profile_sha256": "shared",
            "clang_installer_sha256": "clang", "run_id": "one", "attempt": "1",
            "patches": {}, "test_module_sha256": "unchanged", "runner": "x64",
            "llvm_profile_sha256": "official",
            "tools": {"msvc": "msvc", "sdk": "sdk", "files": {"link.exe": {"sha256": "msvc"}}},
        }
        candidate = {**control, "complete": False, "variant": "repaired", "llvm_profile_sha256": "repaired"}
        verify_pair(control, candidate)
        for key in ("configuration", "rustc_profile_sha256", "run_id", "attempt", "test_module_sha256"):
            with self.subTest(key=key), self.assertRaisesRegex(RuntimeError, "common input"):
                verify_pair(control, {**candidate, key: "changed"})
        changed = copy.deepcopy(candidate)
        changed["tools"]["files"]["link.exe"]["sha256"] = "lld"
        with self.assertRaisesRegex(RuntimeError, "Native tool"):
            verify_pair(control, changed)
        with self.assertRaisesRegex(RuntimeError, "qualified"):
            verify_pair({**control, "complete": False}, candidate)

    def test_tests_only_dispatch_does_not_modify_test_implementation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "src/tools/opt-dist/src"
            folder.mkdir(parents=True)
            (folder / "main.rs").write_text("let result = execute_pipeline(&env, &mut timer, build_args);")
            (folder / "tests.rs").write_bytes(b"unmodified upstream tests\n")
            original = digest(folder / "tests.rs")
            tests_only_helper(root)
            self.assertIn('timer.section("Run tests", |_| run_tests(&env))', (folder / "main.rs").read_text())
            self.assertEqual(original, digest(folder / "tests.rs"))
            with self.assertRaisesRegex(RuntimeError, "dispatch changed"):
                tests_only_helper(root)

    def test_profile_inputs_are_hash_pinned_and_share_rustc_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = root / "inputs"
            inputs.mkdir()
            (inputs / "rustc-pgo.profdata").write_bytes(b"shared rust")
            (inputs / "llvm-pgo.profdata").write_bytes(b"official llvm")
            (inputs / "repaired").mkdir()
            (inputs / "repaired/llvm-pgo.profdata").write_bytes(b"repaired llvm")
            with tarfile.open(inputs / "official.tar.xz", "w:xz") as bundle:
                for name in ("rustc", "llvm"):
                    bundle.add(inputs / f"{name}-pgo.profdata", arcname=f"official/{name}-pgo.profdata")
            protocol = {"official_bundle_sha256": digest(inputs / "official.tar.xz"),
                        "rustc_profile_sha256": digest(inputs / "rustc-pgo.profdata"),
                        "llvm_profile_sha256": {
                            "official": digest(inputs / "llvm-pgo.profdata"),
                            "repaired": digest(inputs / "repaired/llvm-pgo.profdata")}}
            for variant in ("official", "repaired"):
                output = root / variant
                output.mkdir()
                profiles = load_profiles(root, output, variant, protocol)
                self.assertEqual(digest(profiles["rustc"]), protocol["rustc_profile_sha256"])
                self.assertEqual(digest(profiles["llvm"]), protocol["llvm_profile_sha256"][variant])
            (inputs / "repaired/llvm-pgo.profdata").write_bytes(b"unexpected")
            output = root / "tampered"
            output.mkdir()
            with self.assertRaisesRegex(RuntimeError, "Wrong llvm profile"):
                load_profiles(root, output, "repaired", protocol)

    def test_summary_uses_measured_rounds_and_rejects_incomplete_or_tampered_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = {"variants": ["official", "repaired"], "warmup_rounds": 1,
                        "measured_rounds": 3, "cores": 4, "build_cores": 16, "source_sha": "source",
                        "scope": "one machine"}
            index = {"protocol": protocol, "versions": {"official": "rust", "repaired": "rust"},
                     "run_id": "one", "attempt": "1", "correctness_environment": {"TEMP": "C:\\tests"},
                     "runs": []}
            for round_index in range(4):
                for position, variant in enumerate(paired_order(protocol["variants"], 1, round_index)):
                    name = f"{round_index}-{variant}"
                    seconds = 1000 if round_index == 0 else (10 if variant == "official" else 8)
                    measurements = [
                        {"name": command, "command": ["cargo", *args, "--frozen", "--timings", "--message-format=json"],
                         "wall_seconds": seconds, "cpu_seconds": seconds * 2,
                         "user_seconds": seconds, "kernel_seconds": seconds,
                         "exit_code": 0, "compiled_artifacts": 1, "target_directory": name, "affinity": [0, 1, 2, 3]}
                        for command, args in NATIVE_COMMANDS]
                    meta = {"variant": variant, "round": round_index, "source_sha": "source",
                            "profile_environment": PROFILE_ENV, "logical_cpus": 16, "rustc": "rust",
                            "environment": {"GITHUB_RUN_ID": "one", "GITHUB_RUN_ATTEMPT": "1"},
                            "lock_lf_sha256": "lock", "cargo": "cargo",
                            "cold_target_directories": {"native": name}, "approved_background_executables": []}
                    checks = [{"name": command, "command": ["cargo", *(arg for arg in args if arg != "--no-run"), "--frozen"],
                               "exit_code": 0, "environment_overrides": index["correctness_environment"]}
                              for command, args in NATIVE_COMMANDS[1:]] if round_index == 0 else []
                    path = root / f"{name}.json"
                    save(path, {"metadata": meta, "measurements": measurements, "correctness": checks})
                    index["runs"].append({"variant": variant, "round": round_index, "position": position, "path": path.name})
            result = summarize(root, index)
            self.assertAlmostEqual(result["wall_reduction_percent"], 20)
            self.assertEqual(result["seconds_saved"], 10)
            self.assertEqual(len(result["paired_rounds"]), 3)
            with self.assertRaisesRegex(RuntimeError, "matrix"):
                summarize(root, {**index, "runs": index["runs"][:-1]})
            last = root / index["runs"][-1]["path"]
            changed = json.loads(last.read_text())
            changed["measurements"][0]["cpu_seconds"] = float("nan")
            save(last, changed)
            with self.assertRaisesRegex(RuntimeError, "accounting"):
                summarize(root, index)


if __name__ == "__main__":
    unittest.main()
