import copy
from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest
from unittest.mock import patch

from x64_pgo_release import (
    HOST, check_distribution, configuration, preserve_literal_release_batch, validate_reference,
)


class X64PgoReleaseTests(unittest.TestCase):
    def test_literal_crlf_blob_is_accepted_without_changing_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            relative = "llvm/utils/release/build_llvm_release.bat"
            batch = root / relative
            batch.parent.mkdir(parents=True)
            original = b"@echo off\r\necho pinned\n"
            batch.write_bytes(original)
            (root / ".gitattributes").write_text("*.bat text eol=crlf\n")
            subprocess.run(["git", "init", "--quiet", root], check=True)
            subprocess.run(["git", "-C", root, "add", ".gitattributes"], check=True, capture_output=True)
            blob = subprocess.check_output(
                ["git", "-C", root, "hash-object", "-w", "--stdin", "--no-filters"], input=original,
            ).decode().strip()
            subprocess.run(["git", "-C", root, "update-index", "--add", "--cacheinfo",
                            "100644", blob, relative], check=True)
            subprocess.run(["git", "-C", root, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                            "commit", "--quiet", "-m", "fixture"], check=True)
            batch.write_bytes(original.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
            before = subprocess.run(["git", "-C", root, "diff", "--quiet", "HEAD"])
            self.assertEqual(before.returncode, 1)
            result = preserve_literal_release_batch(root)
            self.assertTrue(result["raw_blob_identity_verified"])
            self.assertTrue(result["checkout_line_endings_restored"])
            self.assertEqual(batch.read_bytes(), original)
            subprocess.run(["git", "-C", root, "diff", "--exit-code", "HEAD"], check=True)
            self.assertFalse(preserve_literal_release_batch(root)["checkout_line_endings_restored"])
            batch.write_bytes(original + b"echo changed\r\n")
            with self.assertRaisesRegex(RuntimeError, "differs beyond CRLF conversion"):
                preserve_literal_release_batch(root)

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
