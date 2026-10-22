import unittest

from audit_official_profiles import coverage


class ProfileAuditTests(unittest.TestCase):
    def test_missing_and_inactive_profiles_are_not_confused_with_active_coverage(self):
        self.assertEqual(coverage("Functions shown: 0\n"), {"functions": 0, "active": 0})
        self.assertEqual(
            coverage("    Block counts: [0, 0]\n    Block counts: [0, 7]\nFunctions shown: 2\n"),
            {"functions": 2, "active": 1})

    def test_changed_or_truncated_reader_output_is_rejected(self):
        for text in ("Total functions: 4\n", "Functions shown: 1\n",
                     "Block counts: [1]\nFunctions shown: 0\n"):
            with self.subTest(text=text), self.assertRaises(RuntimeError):
                coverage(text)
