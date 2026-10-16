import json
import os
from pathlib import Path
import tempfile
import subprocess
import unittest
from unittest.mock import patch

import relocate_failed_scaling_build as recovery


class RelocationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.build = root / "original" / "build"
        self.build.mkdir(parents=True)
        (self.build / "rustbook.exe").write_bytes(b"retained executable")
        (self.build / "docs").mkdir()
        (self.build / "docs" / "book.md").write_text("retained input")
        self.destination = root / "retained" / "build"
        self.destination.parent.mkdir()
        self.free = patch.object(recovery.shutil, "disk_usage",
                                 return_value=type("Usage", (), {"free": 100 * 1024 ** 3})())
        self.free.start()
        self.addCleanup(self.free.stop)

    def test_verified_copy_precedes_source_removal(self):
        expected = recovery.manifest(self.build)
        recovery.relocate(self.build, self.destination)
        self.assertFalse(self.build.exists())
        self.assertEqual(recovery.manifest(self.destination), expected)
        record = json.loads((self.destination.parent / "relocation.json").read_text())
        self.assertTrue(record["complete"])
        self.assertEqual(record["files"], expected)

    def test_corrupt_copy_keeps_original(self):
        copytree = recovery.shutil.copytree
        def corrupt(source, target, **kwargs):
            with patch.object(recovery.shutil, "copytree", copytree):
                copytree(source, target, **kwargs)
            (target / "rustbook.exe").write_bytes(b"corrupt")
        with patch.object(recovery.shutil, "copytree", side_effect=corrupt):
            with self.assertRaisesRegex(RuntimeError, "checksum verification"):
                recovery.relocate(self.build, self.destination)
        self.assertTrue(self.build.exists())

    def test_existing_destination_keeps_original(self):
        self.destination.mkdir()
        with self.assertRaisesRegex(RuntimeError, "fresh"):
            recovery.relocate(self.build, self.destination)
        self.assertTrue(self.build.exists())

    def test_insufficient_space_keeps_original(self):
        with patch.object(recovery.shutil, "disk_usage",
                          return_value=type("Usage", (), {"free": 1})()):
            with self.assertRaisesRegex(RuntimeError, "50 GiB"):
                recovery.relocate(self.build, self.destination)
        self.assertTrue(self.build.exists())
        self.assertFalse(self.destination.exists())

    @unittest.skipUnless(os.name == "nt", "Windows directory junctions")
    def test_internal_junction_is_retargeted_and_preserved(self):
        subprocess.run([os.environ["COMSPEC"], "/c", "mklink", "/J",
                        str(self.build / "host"), str(self.build / "docs")],
                       check=True, capture_output=True)
        recovery.relocate(self.build, self.destination)
        self.assertEqual((self.destination / "host").resolve(), self.destination / "docs")
        self.assertEqual((self.destination / "host/book.md").read_text(), "retained input")

    @unittest.skipUnless(os.name == "nt", "Windows directory junctions")
    def test_external_junction_is_rejected_without_removing_source(self):
        subprocess.run([os.environ["COMSPEC"], "/c", "mklink", "/J",
                        str(self.build / "outside"), str(self.destination.parent)],
                       check=True, capture_output=True)
        with self.assertRaisesRegex(RuntimeError, "leaves retained tree"):
            recovery.relocate(self.build, self.destination)
        self.assertTrue(self.build.exists())

    @unittest.skipUnless(os.name == "nt", "Windows directory junctions")
    def test_source_root_junction_does_not_copy_or_remove_source(self):
        (self.build.parent / "source.txt").write_text("source remains")
        subprocess.run([os.environ["COMSPEC"], "/c", "mklink", "/J",
                        str(self.build / "rustc-src"), str(self.build.parent)],
                       check=True, capture_output=True)
        recovery.relocate(self.build, self.destination)
        self.assertEqual((self.destination / "rustc-src").resolve(), self.build.parent)
        self.assertEqual((self.build.parent / "source.txt").read_text(), "source remains")
        self.assertFalse((self.destination / "source.txt").exists())

    def test_reconnection_requires_exact_current_run_and_no_surviving_work(self):
        root = Path(r"E:\m16997224t4r1")
        report = {"Runner": "MARCPE-TEST01-X64", "FailedRoot": str(root),
                  "FailedJob": "116693884027", "RecoveryRun": "new-run", "Processes": []}
        recovery.verify_reconnection(report, "MARCPE-TEST01-X64", root, "116693884027", "new-run")
        for key, value in (("Runner", "another-runner"), ("FailedRoot", "another-root"),
                           ("FailedJob", "another-job"), ("RecoveryRun", "old-run"),
                           ("Processes", [{"ProcessId": 123}])):
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                recovery.verify_reconnection({**report, key: value}, "MARCPE-TEST01-X64",
                                             root, "116693884027", "new-run")

    def test_internal_file_symlink_is_preserved_without_following_external_links(self):
        link = self.build / "docs/license"
        link.symlink_to(self.build / "rustbook.exe")
        (self.build / "docs-alias").symlink_to(self.build / "docs", target_is_directory=True)
        recovery.relocate(self.build, self.destination)
        retained = self.destination / "docs/license"
        self.assertTrue(retained.is_symlink())
        self.assertEqual(retained.resolve(), self.destination / "rustbook.exe")
        self.assertEqual(retained.read_bytes(), b"retained executable")
        self.assertTrue((self.destination / "docs-alias").is_symlink())
        self.assertEqual((self.destination / "docs-alias").resolve(), self.destination / "docs")

    def test_external_file_symlink_prevents_relocation(self):
        external = self.destination.parent / "other"
        external.write_bytes(b"outside")
        (self.build / "outside").symlink_to(external)
        with self.assertRaises(RuntimeError):
            recovery.relocate(self.build, self.destination)
        self.assertTrue(self.build.exists())
        self.assertEqual(external.read_bytes(), b"outside")


if __name__ == "__main__":
    unittest.main()
