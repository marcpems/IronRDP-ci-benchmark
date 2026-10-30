import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from build_arm_compilers import digest
from x64_factorial_thin import (
    ARMS, HOST, PROTOCOL, effects, file_manifest, order, prove_loaded_driver,
    share_stdlib, summarize, verify_records,
)
from x64_rust_thin_incremental import configuration


class FactorialTests(unittest.TestCase):
    def records(self):
        protocol = json.loads(PROTOCOL.read_text())
        tools = {"files": {name: {"path": f"C:/Microsoft Visual Studio/{name}", "sha256": name}
                           for name in ("link.exe", "lib.exe", "lld-link.exe", "llvm-lib.exe")},
                 "msvc": "14", "sdk": "10"}
        records = {}
        for arm, (rust_thin, llvm_thin) in protocol["lto_factors"].items():
            records[arm] = {
                "variant": arm, "protocol": protocol, "build_complete": True,
                "run_id": "1", "attempt": "1", "harness_sha": "head", "source_patch_sha256": "patch",
                "native_inputs": {"headers": "hash"}, "stage0_cargo_sha256": "cargo", "image": "image",
                "cache": {"enabled": False, "hit_rate": None}, "tools": tools,
                "driver": "bin/rustc_driver-123.dll",
                "configuration": configuration(Path("D:/ri/clang/bin"), tools,
                                               "rust-thin" if rust_thin else "baseline",
                                               Path("D:/ri/profiles"), llvm_thin=llvm_thin, native_tools="lld"),
                "profile_use_audit": {
                    "rustc_profile_use": True, "rejected_profile_mismatch_warnings": [],
                    "driver_thin_flag": rust_thin, "driver_dylib_lto_flag": rust_thin,
                    "driver_embedded_bitcode": rust_thin, "driver_suffix": "-123",
                    "llvm_native_lto": "Thin" if llvm_thin else "OFF",
                },
            }
        return records, protocol

    def test_only_declared_factors_can_differ(self):
        records, protocol = self.records()
        verify_records(records, protocol)
        for old, new in (("jobs = 4", "jobs = 8"), ('linker = "lld-link.exe"', 'linker = "link.exe"'),
                         ("thin-lto = true", "thin-lto = false"),
                         ("link-shared = false", 'link-shared = false\nuse-linker = "lld"')):
            altered = copy.deepcopy(records)
            altered["both-thin"]["configuration"] = altered["both-thin"]["configuration"].replace(old, new)
            with self.subTest(change=new), self.assertRaises(RuntimeError):
                verify_records(altered, protocol)
        with self.assertRaises(ValueError):
            configuration(Path("clang"), records["baseline"]["tools"], "baseline", Path("profiles"),
                          llvm_thin=True)

    def test_rejects_mixed_inputs_and_noop_driver(self):
        records, protocol = self.records()
        for key in ("run_id", "attempt", "image", "harness_sha", "native_inputs", "stage0_cargo_sha256"):
            altered = copy.deepcopy(records)
            altered["llvm-thin"][key] = "changed"
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                verify_records(altered, protocol)
        altered = copy.deepcopy(records)
        altered["rust-thin"]["profile_use_audit"]["driver_dylib_lto_flag"] = False
        with self.assertRaises(RuntimeError):
            verify_records(altered, protocol)

    def test_source_and_profile_locks_equal_the_existing_pilot(self):
        old = json.loads(PROTOCOL.with_name("x64-rust-thin-incremental.json").read_text())
        new = json.loads(PROTOCOL.read_text())
        for key in ("rust_sha", "llvm_sha", "rustc_perf_sha", "source_sha", "profiles",
                    "training_result_sha256", "training_provenance_sha256", "fixed_helper_git_blob"):
            self.assertEqual(old[key], new[key], key)

    def test_order_balances_positions_and_preceding_treatments(self):
        for round_index in range(4):
            orders = [order(vm, round_index) for vm in range(1, 5)]
            self.assertTrue(all(set(row) == set(ARMS) for row in orders))
            for position in range(4):
                self.assertEqual({row[position] for row in orders}, set(ARMS))
            pairs = [(row[i], row[i + 1]) for row in orders for i in range(3)]
            self.assertEqual(len(set(pairs)), 12)

    def test_interaction_is_not_subtraction_of_unrelated_gains(self):
        values = effects(dict(zip(ARMS, (100, 90, 80, 72))))
        self.assertAlmostEqual(values["combined"], 28)
        self.assertAlmostEqual(values["rust_without_llvm"], 10)
        self.assertAlmostEqual(values["llvm_with_rust"], 20)
        self.assertAlmostEqual(values["multiplicative_interaction"], 0)
        self.assertLess(effects(dict(zip(ARMS, (100, 90, 80, 65))))["multiplicative_interaction"], 0)
        with self.assertRaises(ValueError):
            summarize([])

    def test_common_stdlib_changes_only_declared_runtime_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, records = Path(temporary), {}
            for arm in ARMS:
                package = root / arm
                runtime = package / "lib/rustlib" / HOST / "lib"
                runtime.mkdir(parents=True)
                (package / "bin").mkdir()
                (runtime / "std.rlib").write_text(arm)
                (package / "bin/rustc.exe").write_text(arm)
                records[arm] = {"files": file_manifest(package), "stdlib": file_manifest(runtime),
                                "archive_sha256": arm}
            result = share_stdlib(root, records)
            for arm in ARMS:
                self.assertEqual((root / arm / "lib/rustlib" / HOST / "lib/std.rlib").read_text(), "baseline")
                self.assertEqual((root / arm / "bin/rustc.exe").read_text(), arm)
                self.assertEqual(result[arm]["evaluated_files"], file_manifest(root / arm))

    def test_loaded_driver_probe_rejects_another_arms_dll_and_terminates_its_child(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "bin").mkdir()
            for name in ("rustc.exe", "rustc_driver-123.dll"):
                (root / "bin" / name).write_text(name)
            record = {"driver": "bin/rustc_driver-123.dll", "files": file_manifest(root)}
            process = Mock(pid=1234)
            process.poll.return_value = None
            process.communicate.return_value = (b"", b"")
            with patch("x64_factorial_thin.subprocess.Popen", return_value=process), \
                    patch("x64_factorial_thin.subprocess.check_output",
                          return_value=json.dumps(str(root / "wrong/rustc_driver-456.dll"))):
                with self.assertRaisesRegex(RuntimeError, "Wrong or unobserved"):
                    prove_loaded_driver(root, record, {}, root / "proof")
            process.kill.assert_called_once()

    def test_loaded_driver_probe_records_actual_driver_before_compiling_stdin(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "bin").mkdir()
            for name in ("rustc.exe", "rustc_driver-123.dll"):
                (root / "bin" / name).write_text(name)
            record = {"driver": "bin/rustc_driver-123.dll", "files": file_manifest(root)}
            process = Mock(pid=1234, returncode=0)
            process.poll.side_effect = [None, 0]
            process.communicate.return_value = (b"", b"")
            with patch("x64_factorial_thin.subprocess.Popen", return_value=process), \
                    patch("x64_factorial_thin.subprocess.check_output",
                          return_value=json.dumps(str(root / record["driver"]))):
                prove_loaded_driver(root, record, {}, root / "proof")
            proof = json.loads((root / "proof/identity.json").read_text())
            self.assertEqual(proof["files"][record["driver"]], digest(root / record["driver"]))
            self.assertEqual(proof["loaded_driver"], str(root / record["driver"]))
            process.kill.assert_not_called()


if __name__ == "__main__":
    unittest.main()
