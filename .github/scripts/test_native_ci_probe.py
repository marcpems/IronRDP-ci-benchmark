import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from arm_ab_probe import extract_compiler
from install_optimized_rust import check_hash, install
from native_ci_probe import COMMANDS, PROFILE_ENV, build_environment, paired_order
from offline_benchmark import NATIVE_COMMANDS, COMMON_COMMAND, WASM_COMMAND


class NativeCiTests(unittest.TestCase):
    def test_exact_original_commands_and_profiles(self):
        self.assertEqual(COMMANDS, [*NATIVE_COMMANDS, ("common", COMMON_COMMAND), ("wasm", WASM_COMMAND)])
        self.assertEqual(len(COMMANDS), 7)
        env = build_environment({"GH_TOKEN": "fixture", "PATH": "path"}, Path("compiler"))
        self.assertNotIn("GH_TOKEN", env)
        self.assertEqual({k: env[k] for k in PROFILE_ENV}, PROFILE_ENV)
        self.assertFalse(any("OPT_LEVEL" in k or "CODEGEN_UNITS" in k for k in env))
        for key in ("CARGO_PROFILE_TEST_DEBUG", "CARGO_PROFILE_DEV_CODEGEN_UNITS", "RUSTFLAGS", "RUSTC_WRAPPER", "RUSTC"):
            with self.assertRaises(RuntimeError):
                build_environment({key: "unexpected"}, Path("compiler"))

    def test_two_variant_order_reverses_each_round(self):
        variants = ["official", "optimized"]
        for vm in range(1, 6):
            self.assertNotEqual(paired_order(variants, vm, 1), paired_order(variants, vm, 2))
            self.assertEqual(paired_order(variants, vm, 1), paired_order(variants, vm, 3))
            self.assertEqual(paired_order(["official"], vm, 0), ["official"])
        self.assertEqual(variants, ["official", "optimized"])

    def test_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "artifact"
            path.write_bytes(b"original")
            check_hash(path, hashlib.sha256(b"original").hexdigest())
            with self.assertRaisesRegex(RuntimeError, "Checksum mismatch"):
                check_hash(path, "wrong")

    def test_archive_paths_checked_before_extraction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "fixture.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("bin/rustc.exe", b"fixture")
                z.writestr("../escape", b"bad")
            with self.assertRaisesRegex(RuntimeError, "unsafe path"):
                extract_compiler(archive, root / "output")
            self.assertFalse((root / "output").exists())
            self.assertFalse((root / "escape").exists())

    def test_failed_install_is_atomic_and_existing_install_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "installed"
            manifest = {"repository": "owner/repo", "release": "release", "metadata_sha256": "hash"}
            with patch("install_optimized_rust.download", side_effect=RuntimeError("download failed")):
                with self.assertRaisesRegex(RuntimeError, "download failed"):
                    install(destination, manifest, Path("official"))
            self.assertFalse(destination.exists())
            destination.mkdir()
            (destination / "optimized.json").write_text(json.dumps({"old": True}))
            with self.assertRaisesRegex(RuntimeError, "Checksum mismatch"):
                install(destination, manifest, Path("official"))
            self.assertEqual(json.loads((destination / "optimized.json").read_text()), {"old": True})


if __name__ == "__main__":
    unittest.main()
