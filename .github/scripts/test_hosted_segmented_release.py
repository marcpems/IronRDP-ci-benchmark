import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import hosted_segmented_release as staged


class SegmentedReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.root = self.directory / "workspace"
        (self.root / "r").mkdir(parents=True)
        (self.root / "e").mkdir()
        self.transfer = self.directory / "transfer"
        env = patch.dict(os.environ, {"GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "1",
                                      "GITHUB_SHA": "pinned-sha"})
        env.start()
        self.addCleanup(env.stop)

    def flags(self):
        flags = []
        for name in (*staged.PROFILE_NAMES, "cargo"):
            profile = "rustc" if name == "cargo" else name
            path = self.root / "r/opt-artifacts" / f"{profile}-pgo.profdata"
            flags.extend(["--set", f'pgo.{name}.use="{path.as_posix()}"'])
        return [*flags, "--keep-stage", "0"]

    def test_final_command_requires_all_profiles_and_original_rebuild_policy(self):
        flags = self.flags()
        staged.validate_flags(flags, self.root / "r")
        for changed in (flags[:-2], flags[2:], [*flags, "--set", "build.extended=false"],
                        [*flags[:-1], "2"], [*flags, "--keep-stage", "0"]):
            with self.subTest(flags=changed), self.assertRaises(RuntimeError):
                staged.validate_flags(changed, self.root / "r")

    def test_training_requires_successful_stages_and_only_explicit_final_deferral(self):
        output = self.root / "e"
        staged.save(output / "final-command.json", {"study": staged.STUDY, "exit_code": 75})
        stages = [
            ("Stage 1 (Rustc + rustdoc + cargo + clippy PGO)", "OK"),
            ("Stage 2 (LLVM PGO)", "OK"), ("Stage 5 (final build)", "FAIL")]
        def write(rows):
            (output / "fresh-pgo-full-dist.stderr").write_text("".join(
                f"[2026-10-18T10:00:00Z INFO  opt_dist::timer] Section `{name}` ended: {status} (1.0s)`\n"
                for name, status in rows), encoding="utf-8")
        write(stages)
        staged.verify_training(output)
        for rows in (stages[1:], stages[:-1], [*stages, ("Unexpected failure", "FAIL")]):
            write(rows)
            with self.assertRaises(RuntimeError):
                staged.verify_training(output)

    def test_member_guards_reject_escaping_paths_and_links(self):
        for row in ({"path": r"..\outside", "bytes": 1},
                    {"path": "ok", "symlink": r"..\outside"},
                    {"path": "ok", "junction": r"C:\outside"},
                    {"path": "ok", "source_junction": str(self.root)}):
            with self.subTest(row=row), self.assertRaises(RuntimeError):
                staged.validate_members({"files": [row], "directories": [], "mtime_ns": {}}, self.root)

    @unittest.skipUnless(os.name == "nt" and shutil.which("7z"),
                         "Windows native checkpoint tools")
    def test_native_roundtrip_preserves_hashes_mtimes_empty_directories_and_links(self):
        source = self.root / "r"
        payload = source / "file.txt"
        payload.write_bytes(b"complete checkpoint payload")
        (source / "empty").mkdir()
        deep = source
        for index in range(5):
            deep = deep / (str(index) + ("long directory " * 4).rstrip())
        deep.mkdir(parents=True)
        (deep / "\u00e9.txt").write_bytes(b"long Unicode path")
        os.utime(payload, ns=(1700000000000000000, 1700000000123456700))
        timestamp = payload.stat().st_mtime_ns
        (source / "file-link").symlink_to(payload)
        subprocess.run([os.environ["COMSPEC"], "/c", "mklink", "/J",
                        str(self.root / "e/source-link"), str(source)], check=True, capture_output=True)
        staged.pack(self.root, self.transfer)
        self.root.rename(self.directory / "old-workspace")
        with patch.object(staged.shutil, "disk_usage",
                          return_value=type("Usage", (), {"free": 100 * 1024 ** 3})()):
            staged.unpack(self.root, self.transfer)
        self.assertEqual(payload.read_bytes(), b"complete checkpoint payload")
        self.assertEqual(payload.stat().st_mtime_ns, timestamp)
        self.assertTrue((source / "empty").is_dir())
        self.assertEqual((source / "file-link").resolve(), payload)
        self.assertEqual((self.root / "e/source-link").resolve(), source)
        self.assertTrue(staged.read(self.root / "e/continuation-restore.json")["verified"])

    def test_bad_archive_identity_is_rejected_before_extracting(self):
        self.transfer.mkdir()
        staged.save(self.transfer / "manifest.json", {"study": "wrong"})
        with patch.object(staged.subprocess, "Popen") as popen, self.assertRaises(RuntimeError):
            staged.unpack(self.root, self.transfer)
        popen.assert_not_called()

    def test_qualification_failure_never_produces_a_segmented_success(self):
        output = self.root / "e"
        receipt = {"flags": self.flags(), "profiles": {}, "python": staged.sys.executable}
        identity = {"files": {"lib.exe": {"path": "library-tool", "sha256": "hash"}},
                    "msvc": "same", "sdk": "same", "image": "same"}
        provenance = {"tools": identity}
        for name, data in (
                ("continuation-restore.json", {"verified": True}),
                ("provenance.json", provenance),
                ("training-production.json", {"wall_seconds": 100}),
                ("training-hardware.json", {"phase": "training"}),
                ("continuation-hardware.json", {"phase": "final"})):
            staged.save(output / name, data)
        for name in ("fresh-pgo-full-dist", "continuation-final-dist"):
            for suffix in ("stdout", "stderr"):
                (output / f"{name}.{suffix}").write_text("recorded output\n")
        with patch.object(staged, "verify_training", return_value=receipt), \
                patch.object(staged, "tool_identity", return_value=identity), \
                patch.object(staged, "environment", return_value={}), \
                patch.object(staged.release, "run", return_value={"wall_seconds": 200}), \
                patch.object(staged.release, "validate_distribution",
                             side_effect=RuntimeError("qualification failed")):
            with self.assertRaisesRegex(RuntimeError, "qualification failed"):
                staged.finish(self.root)
        self.assertFalse((output / "segmented-result.json").exists())
        self.assertFalse((output / "result.json").exists())
        timing = staged.read(output / "segmented-production.json")
        self.assertEqual(timing["aggregate_active_production_seconds"], 300)
        self.assertIsNone(timing["continuous_full_release_seconds"])

    def test_segmented_workflow_preserves_dependency_and_standard_runner(self):
        workflows = Path(staged.__file__).parents[1] / "workflows"
        chain = (workflows / "matched-hosted-x64-segmented.yml").read_text()
        reusable = (workflows / "matched-hosted-x64-baseline.yml").read_text()
        self.assertIn("needs: training", chain)
        self.assertIn("segment: train", chain)
        self.assertIn("segment: finish", chain)
        self.assertIn("runs-on: windows-2022", reusable)
        self.assertNotIn("continue-on-error:", reusable)
        self.assertIn("retention-days: 2", reusable)


if __name__ == "__main__":
    unittest.main()
