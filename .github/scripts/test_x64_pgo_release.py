import copy
from pathlib import Path
import tomllib
import unittest
from unittest.mock import patch

from x64_pgo_release import HOST, check_distribution, configuration, validate_reference


class X64PgoReleaseTests(unittest.TestCase):
    def config(self, variant):
        with patch("x64_pgo_release.shutil.which", side_effect=lambda name: f"C:/MSVC/{name}"):
            return configuration(Path("C:/clang"), variant)

    def test_full_distribution_retains_upstream_optimization_defaults(self):
        for variant in ("upstream", "local"):
            config = tomllib.loads(self.config(variant))
            self.assertTrue(config["build"]["docs"])
            self.assertTrue(config["build"]["extended"])
            self.assertEqual(config["build"]["jobs"], 16)
            self.assertEqual(config["rust"]["lto"], "thin-local")
            self.assertEqual(config["rust"]["codegen-units"], 1)
            self.assertFalse(config["llvm"]["thin-lto"])
            self.assertEqual(config["rust"]["codegen-backends"], ["llvm", "cranelift"])
            self.assertEqual(config["dist"]["compression-profile"], "balanced")
        self.assertNotIn("use-linker", tomllib.loads(self.config("upstream"))["llvm"])
        self.assertEqual(tomllib.loads(self.config("local"))["llvm"]["use-linker"], "lld")

    def test_missing_full_distribution_artifact_is_rejected(self):
        files = [Path(f"{component}-1.94.1-{HOST}.tar.xz") for component in (
            "rust", "rustc", "rust-std", "cargo", "rust-docs", "rustfmt", "clippy", "llvm-tools", "rust-analyzer",
        )]
        files += [Path(f"rust-1.94.1-{HOST}.msi"), Path("rust-src-1.94.1.tar.xz")]
        check_distribution(files)
        with self.assertRaisesRegex(RuntimeError, "Incomplete full distribution"):
            check_distribution(files[:-1])

    def test_reference_gate_accepts_only_declared_recipe_difference(self):
        reference = {
            "complete": True, "variant": "upstream", "rust_sha": "rust", "llvm_sha": "llvm",
            "rustc_perf_sha": "perf", "cores": 16, "runner_name": "runner",
            "clang_installer_sha256": "clang",
            "configuration": self.config("upstream"),
            "tools": {"msvc": "msvc", "sdk": "sdk", "files": {"cl.exe": {"sha256": "cl"}}},
        }
        candidate = dict(reference, configuration=self.config("local"))
        validate_reference(reference, candidate)
        for key, value in (("cores", 4), ("rust_sha", "other"), ("clang_installer_sha256", "other")):
            with self.assertRaisesRegex(RuntimeError, "mismatch"):
                validate_reference(reference, dict(candidate, **{key: value}))
        changed = copy.deepcopy(candidate)
        changed["configuration"] = changed["configuration"].replace('lto = "thin-local"', 'lto = "thin"')
        with self.assertRaisesRegex(RuntimeError, "Release settings differ"):
            validate_reference(reference, changed)
        with self.assertRaisesRegex(RuntimeError, "accepted upstream"):
            validate_reference(dict(reference, complete=False), candidate)


if __name__ == "__main__":
    unittest.main()
