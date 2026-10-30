import copy
from contextlib import nullcontext
import json
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch
import uuid
import zipfile

from build_arm_compilers import digest, save
from native_ci_probe import paired_order
from x64_rust_thin_incremental import (
    block, configuration, unpack, validate_configs, verify_pair, verify_profiles,
)


class IncrementalThinTests(unittest.TestCase):
    def setUp(self):
        self.root = Path.cwd() / f".thin-test-{uuid.uuid4().hex}"
        self.root.mkdir()
        self.addCleanup(shutil.rmtree, self.root)
        self.tools = {
            "files": {name: {"path": f"C:/Microsoft Visual Studio/{name}", "sha256": name}
                      for name in ("link.exe", "lib.exe")},
            "msvc": "14", "sdk": "10",
        }

    def pair(self):
        common = {
            "build_complete": True, "protocol": {"study": "fixture"}, "run_id": "1",
            "attempt": "1", "harness_sha": "sha", "source_patch_sha256": "patch",
            "native_inputs": {"headers": "hash"}, "stage0_cargo_sha256": "cargo",
            "stdlib": {"libstd.rlib": "std"}, "image": "image", "tools": self.tools,
        }
        return [
            {**copy.deepcopy(common), "variant": arm,
             "configuration": configuration(Path("D:/ri/clang/bin"), self.tools, arm, Path("D:/ri/profiles"))}
            for arm in ("baseline", "rust-thin")
        ]

    def test_only_rust_lto_can_differ(self):
        baseline, treatment = self.pair()
        verify_pair(baseline, treatment)
        for old, new in (("thin-lto = false", "thin-lto = true"),
                         ("jobs = 4", "jobs = 8"), ('linker = "link.exe"', 'linker = "lld-link.exe"')):
            with self.subTest(change=new), self.assertRaises(RuntimeError):
                validate_configs(baseline["configuration"], treatment["configuration"].replace(old, new))

    def test_pair_rejects_unqualified_mismatched_and_cross_run_inputs(self):
        baseline, treatment = self.pair()
        for key in ("run_id", "attempt", "native_inputs", "stage0_cargo_sha256",
                    "stdlib", "image", "protocol", "harness_sha", "source_patch_sha256"):
            altered = {**treatment, key: "changed"}
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                verify_pair(baseline, altered)
        altered = copy.deepcopy(treatment)
        altered["tools"]["files"]["link.exe"]["sha256"] = "changed"
        with self.assertRaisesRegex(RuntimeError, "tool binaries"):
            verify_pair(baseline, altered)
        with self.assertRaises(RuntimeError):
            verify_pair({**baseline, "build_complete": False}, treatment)

    def test_rejects_corrupted_or_injected_package(self):
        content = b"fixture"
        archive = self.root / "package.zip"
        with zipfile.ZipFile(archive, "w") as bundle:
            bundle.writestr("bin/rustc.exe", content)
        file = self.root / "fixture"
        file.write_bytes(content)
        record = {"build_complete": True, "archive_sha256": digest(archive),
                  "files": {"bin/rustc.exe": digest(file)}}
        save(self.root / "result.json", record)
        unpack(self.root, self.root / "good")
        save(self.root / "result.json", {**record, "archive_sha256": "wrong"})
        with self.assertRaisesRegex(RuntimeError, "checksum"):
            unpack(self.root, self.root / "bad")
        with zipfile.ZipFile(archive, "w") as bundle:
            bundle.writestr("../escape", content)
        save(self.root / "result.json", {**record, "archive_sha256": digest(archive)})
        with self.assertRaisesRegex(RuntimeError, "Unsafe"):
            unpack(self.root, self.root / "unsafe")

    def test_frozen_profiles_require_exact_bytes_and_completed_training(self):
        training = {
            "complete": True, "run_id": "1", "attempt": "1",
            **dict.fromkeys(("rust_sha", "llvm_sha", "rustc_perf_sha", "fixed_helper_git_blob",
                             "clang_installer_sha256"), "fixture"),
            "llvm_training_coverage": {name: {"active_functions": 1}
                                      for name in ("X86TargetLowering", "InstCombine")},
        }
        profile = self.root / "llvm-pgo.profdata"
        profile.write_bytes(b"frozen profile")
        training["profiles"] = {"llvm": {"sha256": digest(profile)}}
        save(self.root / "result.json", training)
        save(self.root / "provenance.json", {"identity": "fixture"})
        protocol = {
            **{k: v for k, v in training.items() if k.endswith("sha") or k.endswith("sha256")
               or k == "fixed_helper_git_blob"},
            "profile_run": "1", "profile_attempt": "1", "profiles": {"llvm": digest(profile)},
            "training_result_sha256": digest(self.root / "result.json"),
            "training_provenance_sha256": digest(self.root / "provenance.json"),
        }
        verify_profiles(self.root, protocol)
        profile.write_bytes(b"changed")
        with self.assertRaisesRegex(RuntimeError, "profile changed"):
            verify_profiles(self.root, protocol)
        profile.write_bytes(b"frozen profile")
        training["complete"] = False
        save(self.root / "result.json", training)
        protocol["training_result_sha256"] = digest(self.root / "result.json")
        with self.assertRaisesRegex(RuntimeError, "unqualified"):
            verify_profiles(self.root, protocol)

    def test_round_order_counterbalances_without_reusing_targets(self):
        variants = ["baseline", "rust-thin"]
        orders = [paired_order(variants, 1, index) for index in range(4)]
        self.assertEqual(orders, [variants, variants[::-1], variants, variants[::-1]])
        self.assertEqual(variants, ["baseline", "rust-thin"])

    def test_command_failure_cannot_complete_a_consumer_block(self):
        output = self.root / "failed-block"
        with patch("x64_rust_thin_incremental.telemetry_executables", return_value=[]), \
                patch("x64_rust_thin_incremental.measurement_session", return_value=nullcontext()), \
                patch("x64_rust_thin_incremental.measure", return_value={
                    "exit_code": 7, "wall_seconds": 1, "cpu_seconds": 2,
                }) as measured:
            with self.assertRaisesRegex(RuntimeError, "Consumer command failed"):
                block(self.root, output, Path("rustc.exe"), Path("cargo.exe"),
                      {"cores": 4}, {}, correctness_env={"PUBLIC": r"C:\Users\Public"})
        result = json.loads((output / "results.json").read_text())
        self.assertFalse(result["complete"])
        self.assertEqual(result["rows"][0]["exit_code"], 7)
        command = measured.call_args.args[0]
        self.assertEqual(command, ["cargo.exe", "build", "-p", "xtask", "--frozen",
                                   "--timings", "--message-format=json"])
        self.assertEqual(measured.call_args.args[2]["CARGO_NET_OFFLINE"], "true")
        self.assertNotIn("PUBLIC", measured.call_args.args[2])
        self.assertTrue((output / "target").exists())

    def test_correctness_excludes_doctests_but_not_native_feature_tests(self):
        commands = []
        environments = []

        def fake_measure(command, *args, **kwargs):
            commands.append(command)
            environments.append(args[1])
            return {"exit_code": 0, "wall_seconds": 1, "cpu_seconds": 2}

        with patch("x64_rust_thin_incremental.telemetry_executables", return_value=[]), \
                patch("x64_rust_thin_incremental.measurement_session", return_value=nullcontext()), \
                patch("x64_rust_thin_incremental.measure", side_effect=fake_measure):
            result = block(self.root, self.root / "correctness", Path("rustc.exe"),
                           Path("cargo.exe"), {"cores": 4}, {}, correctness=True,
                           correctness_env={"PUBLIC": r"C:\Users\Public"})
        self.assertTrue(result["complete"])
        self.assertEqual(len(commands), 5)
        self.assertEqual(commands[1], ["cargo.exe", "test", "--workspace",
                                      "--tests", "--frozen"])
        self.assertNotIn("--lib", commands[1])
        self.assertNotIn("--bins", commands[1])
        self.assertTrue(all("--no-run" not in command for command in commands))
        self.assertIn("native-tls,smartcard", commands[-1])
        self.assertTrue(all(env["PUBLIC"] == r"C:\Users\Public" for env in environments))


if __name__ == "__main__":
    unittest.main()
