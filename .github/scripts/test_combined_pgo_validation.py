import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import combined_pgo_validation as validation
from combined_pgo_replay import extract_distribution, verify_pair


class CombinedValidationTests(unittest.TestCase):
    def test_candidate_applies_only_the_reviewed_patch(self):
        reviewed = (validation.INPUTS / "reviewed.patch").read_bytes()
        with patch.object(validation.subprocess, "check_output",
                          return_value=validation.protocol()["base_sha"]), \
                patch.object(validation.subprocess, "run") as run, \
                patch.object(validation, "source_diff", side_effect=[b"", reviewed, reviewed]):
            self.assertEqual(validation.prepare(Path("source"), "candidate"), reviewed)
        self.assertEqual(len(run.call_args_list), 3)
        self.assertEqual(run.call_args_list[0].args[0][3:5], ["apply", "--check"])

    def test_rejects_patch_tampering_and_dirty_control(self):
        for variant in ("control", "candidate"):
            with self.subTest(variant=variant), \
                    patch.object(validation.subprocess, "check_output",
                                 return_value=validation.protocol()["base_sha"]), \
                    patch.object(validation, "source_diff", return_value=b"unexpected"), \
                    patch.object(validation.subprocess, "run") as run:
                with self.assertRaisesRegex(RuntimeError, "clean pinned"):
                    validation.prepare(Path("source"), variant)
                run.assert_not_called()
        with patch.object(validation.subprocess, "check_output",
                          return_value=validation.protocol()["base_sha"]), \
                patch.object(validation, "source_diff", return_value=b""), \
                patch.object(validation, "digest", return_value="wrong"):
            with self.assertRaisesRegex(RuntimeError, "checksum"):
                validation.prepare(Path("source"), "candidate")

    def test_rejects_applied_diff_drift(self):
        with patch.object(validation.subprocess, "check_output",
                          return_value=validation.protocol()["base_sha"]), \
                patch.object(validation.subprocess, "run"), \
                patch.object(validation, "source_diff", side_effect=[b"", b"not reviewed"]):
            with self.assertRaisesRegex(RuntimeError, "differs"):
                validation.prepare(Path("source"), "candidate")

    def test_qualification_requires_all_successful_sections(self):
        sections = {
            "unfinished": [],
            "completed": [{"name": name, "status": "OK"} for name in (
                "Stage 1 (Rustc + rustdoc + cargo + clippy PGO)",
                "Stage 2 (LLVM PGO)", "Stage 5 (final build)", "Run tests",
            )],
        }
        validation.verify_sections(sections)
        missing = copy.deepcopy(sections)
        missing["completed"].pop()
        with self.assertRaises(RuntimeError):
            validation.verify_sections(missing)
        sections["completed"][-1]["status"] = "FAIL"
        with self.assertRaises(RuntimeError):
            validation.verify_sections(sections)

    def test_cache_server_stops_after_command_failure(self):
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(validation.subprocess, "run") as run, \
                patch.object(validation.subprocess, "check_output", return_value="stats"), \
                patch.object(validation.subprocess, "Popen", side_effect=OSError("probe failure")), \
                patch.object(validation.socket, "socket") as socket, \
                patch.dict(os.environ, {"SCCACHE_SERVER_PORT": "12345"}):
            socket.return_value.__enter__.return_value.connect_ex.return_value = 1
            with self.assertRaisesRegex(OSError, "probe failure"):
                validation.cache_command(Path("cache.exe"), Path(folder) / "stats", ["probe"])
            self.assertEqual(run.call_args_list[-1].args[0], [Path("cache.exe"), "--stop-server"])

    def test_pair_rejects_different_build_inputs(self):
        plan = validation.protocol()
        common = {
            "complete": True, "protocol": plan, "base_sha": plan["base_sha"], "run_id": "42",
            "attempt": "1", "qualification": "passed", "patch_sha256": plan["patch_sha256"],
            "clang_installer_sha256": "clang", "wix_archive_sha256": "wix",
            "sccache_sha256": "cache", "runner": "runner", "harness_sha": "harness",
            "tools": {"msvc": "v", "sdk": "s", "files": {"link": {"sha256": "link"}}},
        }
        pair = []
        for variant in plan["variants"]:
            row = {**copy.deepcopy(common), "variant": variant,
                   "applied_patch_sha256": (plan["patch_sha256"] if variant == "candidate"
                                            else hashlib.sha256(b"").hexdigest())}
            row["configuration"] = (
                f'[build]\nccache="D:/{variant}/sccache.exe"\njobs=16\n'
                f'[llvm]\nclang-cl="D:/{variant}/clang-cl.exe"\n'
                f'[target.{validation.HOST}]\nar="D:/{variant}/lib.exe"\n'
            )
            pair.append(row)
        with patch.dict(os.environ, {"GITHUB_RUN_ID": "42"}):
            verify_pair(*pair)
            pair[1]["configuration"] = pair[1]["configuration"].replace("jobs=16", "jobs=8")
            with self.assertRaisesRegex(RuntimeError, "settings differ"):
                verify_pair(*pair)
            pair[1]["complete"] = False
            with self.assertRaisesRegex(RuntimeError, "Unqualified"):
                verify_pair(*pair)

    def test_extracts_each_distributions_own_payload_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            artifacts, output = root / "artifacts", root / "output"
            output.mkdir()
            for variant in ("control", "candidate"):
                evidence = artifacts / f"combined-{variant}-evidence"
                dist = artifacts / f"combined-{variant}-dist"
                evidence.mkdir(parents=True)
                dist.mkdir()
                (evidence / "result.json").write_text(json.dumps({"variant": variant}))
                manifest = []
                for component in ("rustc", "cargo", "rust-std"):
                    payload = root / f"{component}.txt"
                    payload.write_text(variant)
                    name = f"{component}-nightly-{validation.HOST}"
                    archive = dist / f"{name}.tar.xz"
                    subdir = f"rust-std-{validation.HOST}" if component == "rust-std" else component
                    with tarfile.open(archive, "w:xz") as bundle:
                        bundle.add(payload, arcname=f"{name}/{subdir}/{component}.txt")
                    manifest.append({"name": archive.name, "sha256": validation.digest(archive),
                                     "bytes": archive.stat().st_size})
                (evidence / "dist-manifest.json").write_text(json.dumps(manifest))
                installed, _, _ = extract_distribution(artifacts, output, variant)
                self.assertEqual({p.read_text() for p in installed.iterdir()}, {variant})
            archive.write_bytes(b"tampered")
            other = root / "other"
            other.mkdir()
            with self.assertRaisesRegex(RuntimeError, "integrity"):
                extract_distribution(artifacts, other, "candidate")


if __name__ == "__main__":
    unittest.main()
