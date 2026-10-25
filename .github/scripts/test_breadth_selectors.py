import unittest

from breadth_audit import selectors


class TrainingSelectorTests(unittest.TestCase):
    def test_historical_and_shared_backend_names_preserve_two_phase_schema(self):
        for constant in ("LLVM_PGO_CRATES", "BACKEND_PGO_CRATES"):
            with self.subTest(constant=constant):
                source = (
                    f'pub const {constant}: &[&str] = &["syn", "cargo"];\n'
                    'pub const RUSTC_PGO_CRATES: &[&str] = &["cargo", "externs"];'
                )
                self.assertEqual(selectors(source), {
                    "llvm": ["syn", "cargo"], "rustc": ["cargo", "externs"],
                })

    def test_dual_or_duplicate_backend_declarations_are_rejected(self):
        for second in ("LLVM_PGO_CRATES", "BACKEND_PGO_CRATES"):
            with self.subTest(second=second):
                source = (
                    'pub const LLVM_PGO_CRATES: &[&str] = &["syn"];\n'
                    f'pub const {second}: &[&str] = &["syn"];\n'
                    'pub const RUSTC_PGO_CRATES: &[&str] = &["externs"];'
                )
                with self.assertRaisesRegex(ValueError, "ambiguous"):
                    selectors(source)

    def test_missing_or_malformed_backend_and_frontend_fail_closed(self):
        cases = (
            'pub const RUSTC_PGO_CRATES: &[&str] = &["externs"];',
            'pub const BACKEND_PGO_CRATES: &[&str] = &["syn"];',
            'pub const BACKEND_PGO_CRATES: &[&str] = other;\n'
            'pub const RUSTC_PGO_CRATES: &[&str] = &["externs"];',
        )
        for source in cases:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    selectors(source)


if __name__ == "__main__":
    unittest.main()
