import copy
import unittest
from unittest.mock import patch

from x64_pr164707_validation import (
    FIXED_HELPER_BLOB, TEST_MODULE_BLOB, verify_patch, verify_sections,
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


if __name__ == "__main__":
    unittest.main()
