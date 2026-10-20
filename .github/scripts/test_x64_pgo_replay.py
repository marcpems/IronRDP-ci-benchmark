import json
from pathlib import Path
import tempfile
import unittest

from build_arm_compilers import digest
from x64_pgo_replay import checked_release, share_native_libraries


class X64PgoReplayTests(unittest.TestCase):
    def test_release_gate_rejects_corrupt_or_unqualified_compiler(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = root / "x64-pgo-local-evidence"
            dist = root / "x64-pgo-local-dist"
            evidence.mkdir()
            dist.mkdir()
            archive = dist / "rustc-1.94.1-x86_64-pc-windows-msvc.tar.xz"
            archive.write_bytes(b"fixture compiler archive")
            protocol = {
                "rust_version": "1.94.1", "rust_sha": "pinned", "host": "x86_64-pc-windows-msvc",
                "release_run": "123", "release_attempt": "1",
                "compiler_archive_sha256": {"local": digest(archive)},
            }
            result = {"complete": True, "variant": "local", "run_id": "123", "attempt": "1",
                      "rust_sha": "pinned"}
            (evidence / "result.json").write_text(json.dumps(result))
            protocol["compiler_metadata_sha256"] = {"local": digest(evidence / "result.json")}
            (evidence / "dist-manifest.json").write_text(json.dumps([
                {"name": archive.name, "sha256": digest(archive), "bytes": archive.stat().st_size}]))
            self.assertEqual(checked_release(root, "local", protocol)[1], archive)
            (evidence / "result.json").write_text(json.dumps(dict(result, extra="changed")))
            with self.assertRaisesRegex(RuntimeError, "metadata differs"):
                checked_release(root, "local", protocol)
            (evidence / "result.json").write_text(json.dumps(dict(result, complete=False)))
            with self.assertRaisesRegex(RuntimeError, "Unqualified"):
                checked_release(root, "local", protocol)
            (evidence / "result.json").write_text(json.dumps(dict(result, attempt="2")))
            with self.assertRaisesRegex(RuntimeError, "Unqualified"):
                checked_release(root, "local", protocol)
            (evidence / "result.json").write_text(json.dumps(result))
            archive.write_bytes(b"wrong compiler archive")
            with self.assertRaisesRegex(RuntimeError, "differs from preregistered"):
                checked_release(root, "local", protocol)

    def test_shared_libraries_replace_only_extracted_target_libraries(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            official = root / "official/bin/rustc.exe"
            compiler = root / "local/bin/rustc.exe"
            source = root / "official/lib/rustlib/host/lib"
            target = root / "local/lib/rustlib/host/lib"
            source.mkdir(parents=True)
            target.mkdir(parents=True)
            (source / "libstd-pinned.rlib").write_bytes(b"official standard library")
            (target / "libstd-other.rlib").write_bytes(b"other standard library")
            compiler.parent.mkdir(parents=True)
            compiler.write_bytes(b"compiler")
            standard = share_native_libraries(official, compiler, "host")
            self.assertEqual(set(standard), {"libstd-pinned.rlib"})
            self.assertEqual((target / "libstd-pinned.rlib").read_bytes(), b"official standard library")
            self.assertFalse((target / "libstd-other.rlib").exists())
            self.assertEqual(compiler.read_bytes(), b"compiler")

    def test_missing_official_standard_library_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "official/lib/rustlib/host/lib").mkdir(parents=True)
            with self.assertRaisesRegex(RuntimeError, "standard library is missing"):
                share_native_libraries(root / "official/bin/rustc.exe", root / "local/bin/rustc.exe", "host")


if __name__ == "__main__":
    unittest.main()
