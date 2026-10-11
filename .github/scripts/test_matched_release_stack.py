import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from build_arm_compilers import digest
from matched_release import LLVM, PERF, RUST
from matched_release_stack import HOST, PARENT_RUN, compiler_archive, verified_profiles


class StackDiagnosticTests(unittest.TestCase):
    def test_profiles_require_exact_parent_and_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent = {"run_id": PARENT_RUN, "host": HOST, "variant": "msvc-pgo",
                      "rust_sha": RUST, "llvm_sha": LLVM, "perf_sha": PERF, "attempt": "1"}
            metadata = root / "provenance.json"
            metadata.write_text(json.dumps(parent))
            hashes = {}
            for name in ("rustc-pgo.profdata", "llvm-pgo.profdata"):
                file = root / name
                file.write_bytes(name.encode())
                hashes[name] = digest(file)
            (root / "profiles.json").write_text(json.dumps(hashes))
            actual, paths = verified_profiles(root)
            self.assertEqual(actual, parent)
            self.assertEqual(set(paths), set(hashes))
            metadata.write_text(json.dumps({**parent, "run_id": "other"}))
            with self.assertRaisesRegex(RuntimeError, "unexpected diagnostic profile parent"):
                verified_profiles(root)
            metadata.write_text(json.dumps(parent))
            (root / "llvm-pgo.profdata").write_bytes(b"changed")
            with self.assertRaisesRegex(RuntimeError, "hash mismatch"):
                verified_profiles(root)

    def test_archive_keeps_symbols_without_traversing_source_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sysroot = root / "sysroot"
            expected = {"bin/rustc.exe", "bin/rustc_driver-test.dll",
                        "bin/rustc_driver-test.pdb", f"lib/rustlib/{HOST}/lib/libstd-test.rlib"}
            for name in expected | {"bin/cargo.exe", "lib/rustlib/src/rust/secret-test-fixture"}:
                file = sysroot / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(b"fixture")
            archive = root / "compiler.zip"
            compiler_archive(sysroot, archive)
            with zipfile.ZipFile(archive) as bundle:
                self.assertEqual(set(bundle.namelist()), expected)


if __name__ == "__main__":
    unittest.main()
