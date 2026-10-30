import copy
import os
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch

from x64_pr164707_validation import (
    FIXED_HELPER_BLOB, TEST_MODULE_BLOB, comparison_identity, release_configuration,
    verify_no_compiler_cache, verify_patch, verify_reference, verify_sections,
)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.sections = {
            "unfinished": [],
            "completed": [
                {"name": name, "status": "OK"}
                for name in (
                    "Stage 1 (Rustc + rustdoc + cargo + clippy PGO)",
                    "Stage 2 (LLVM PGO)", "Stage 5 (final build)", "Run tests",
                )
            ],
        }

    def test_complete_pipeline(self):
        verify_sections(self.sections)

    def test_rejects_missing_training_or_tests(self):
        for index in range(4):
            with self.subTest(index=index):
                sections = copy.deepcopy(self.sections)
                sections["completed"].pop(index)
                with self.assertRaisesRegex(RuntimeError, "Missing successful"):
                    verify_sections(sections)

    def test_rejects_failed_or_unfinished_sections(self):
        for failure in ("failed", "unfinished"):
            with self.subTest(failure=failure):
                sections = copy.deepcopy(self.sections)
                if failure == "failed":
                    sections["completed"].append({"name": "Nested build", "status": "FAIL"})
                else:
                    sections["unfinished"].append({"name": "Nested build"})
                with self.assertRaisesRegex(RuntimeError, "unfinished or failed"):
                    verify_sections(sections)

    @patch("x64_pr164707_validation.subprocess.check_output")
    def test_exact_user_patch(self, output):
        output.side_effect = [
            "1\t0\tsrc/bootstrap/src/utils/helpers.rs\n",
            FIXED_HELPER_BLOB + "\n", TEST_MODULE_BLOB + "\n",
        ]
        verify_patch("source")

    @patch("x64_pr164707_validation.subprocess.check_output")
    def test_rejects_additional_source_changes(self, output):
        output.return_value = "1\t0\tsrc/bootstrap/src/utils/helpers.rs\n1\t0\tsrc/tools/opt-dist/src/main.rs\n"
        with self.assertRaisesRegex(RuntimeError, "Unexpected Rust source changes"):
            verify_patch("source")

    @patch("x64_pr164707_validation.subprocess.check_output")
    def test_rejects_changed_fix_or_release_tests(self, output):
        for helper, tests in (("different", TEST_MODULE_BLOB), (FIXED_HELPER_BLOB, "different")):
            with self.subTest(helper=helper, tests=tests):
                output.side_effect = ["1\t0\tsrc/bootstrap/src/utils/helpers.rs\n", helper, tests]
                with self.assertRaisesRegex(RuntimeError, "locally tested input"):
                    verify_patch("source")

    def test_worker_configuration_changes_only_jobs(self):
        baseline = tomllib.loads(release_configuration(Path(r"D:\reference\clang"), 16))
        for workers in (4, 8, 16):
            current = tomllib.loads(release_configuration(Path(r"D:\reference\clang"), workers))
            self.assertEqual(current["build"]["jobs"], workers)
            current["build"]["jobs"] = 16
            self.assertEqual(current, baseline)
        with self.assertRaises(ValueError):
            release_configuration(Path("clang"), 3)

    @patch.dict(os.environ, {"GITHUB_RUN_ATTEMPT": "1"})
    def test_matching_reference_and_rejection_of_drift(self):
        tools = {"files": {"link.exe": {"sha256": "link"}, "lib.exe": {"sha256": "lib"}},
                 "msvc": "version", "sdk": "sdk"}
        hardware = {"physical_core_masks": [[0, 1]], "memory_bytes": 100}
        identity = comparison_identity(release_configuration(Path(r"D:\first\clang"), 16),
                                       tools, "wix", hardware)
        smaller = comparison_identity(release_configuration(Path(r"D:\second\clang"), 4),
                                      tools, "wix", hardware)
        self.assertEqual(smaller, identity)
        reference = {"complete": True, "build_workers": 16, "run_id": "123", "attempt": "1",
                     "comparison_identity": identity}
        verify_reference(reference, smaller, "123")
        for key, value in (("complete", False), ("build_workers", 8), ("run_id", "124"), ("attempt", "2")):
            with self.subTest(key=key):
                with self.assertRaisesRegex(RuntimeError, "Scaling reference"):
                    verify_reference({**reference, key: value}, smaller, "123")
        for key in ("configuration", "native_tool_sha256", "hardware"):
            altered = copy.deepcopy(smaller)
            altered[key]["changed"] = True
            with self.subTest(key=key):
                with self.assertRaisesRegex(RuntimeError, "Scaling reference"):
                    verify_reference(reference, altered, "123")

    def test_compiler_cache_audit_rejects_launchers(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for component in ("llvm", "lld"):
                (root / f"{component}-CMakeCache.txt").write_text("CMAKE_C_COMPILER:FILEPATH=clang-cl.exe\n")
            self.assertIsNone(verify_no_compiler_cache(root)["hit_rate"])
            for component in ("llvm", "lld"):
                path = root / f"{component}-CMakeCache.txt"
                for key in ("CMAKE_C_COMPILER_LAUNCHER", "CMAKE_CXX_COMPILER_LAUNCHER", "RULE_LAUNCH_COMPILE"):
                    with self.subTest(component=component, key=key):
                        path.write_text(f"{key}:STRING=sccache\n")
                        with self.assertRaisesRegex(RuntimeError, "compiler-cache launcher"):
                            verify_no_compiler_cache(root)
                    path.write_text("")


if __name__ == "__main__":
    unittest.main()
