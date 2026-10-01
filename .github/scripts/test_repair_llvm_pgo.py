import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from build_arm_compilers import configuration
from repair_llvm_pgo import archive_llvm, coverage, trimmed_configuration


class RepairPgoTests(unittest.TestCase):
    def test_coverage_rejects_empty_and_zero_counters(self):
        for output in ("Counters:\n", "    Block counts: [0, 0]\n"):
            with patch("repair_llvm_pgo.subprocess.check_output", return_value=output):
                with self.assertRaisesRegex(RuntimeError, "did not exercise"):
                    coverage("profdata", "profile", {})

    def test_coverage_requires_both_codegen_and_optimization(self):
        with patch("repair_llvm_pgo.subprocess.check_output", side_effect=[
            "    Block counts: [7, 0]\n", "    Block counts: [0, 0]\n",
        ]):
            with self.assertRaisesRegex(RuntimeError, "InstCombine"):
                coverage("profdata", "profile", {})
        with patch("repair_llvm_pgo.subprocess.check_output", return_value=
                   "    Block counts: [7, 0]\n    Block counts: [0]\n"):
            result = coverage("profdata", "profile", {})
        self.assertEqual(result["AArch64TargetLowering"],
                         {"functions": 2, "nonzero_functions": 1, "max_block_count": 7})

    def test_trimmed_tools_preserve_all_compiler_configuration(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("llvm-config", "llvm-profdata", "opt", "llvm-dis"):
                directory = root / "src" / "llvm-project" / "llvm" / "tools" / name
                directory.mkdir(parents=True)
                (directory / "CMakeLists.txt").touch()
            _, text, disabled = trimmed_configuration(root, root, root)
            actual = tomllib.loads(text)
            for name in disabled:
                self.assertEqual(actual["llvm"]["build-config"].pop(name), "OFF")
            self.assertEqual(actual["llvm"]["build-config"].pop("LLVM_TOOL_LLVM_DWARFDUMP_BUILD"), "ON")
            self.assertFalse(actual["rust"]["llvm-tools"])
            actual["rust"]["llvm-tools"] = True
            self.assertEqual(actual, tomllib.loads(configuration(root, root, "optimized", 8)[1]))
            self.assertEqual(set(disabled), {"LLVM_TOOL_OPT_BUILD", "LLVM_TOOL_LLVM_DIS_BUILD"})

    def test_archive_preserves_previous_output_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "llvm").mkdir()
            (root / "llvm" / "evidence").write_text("original")
            archive_llvm(root, "old")
            self.assertEqual((root / "llvm-old" / "evidence").read_text(), "original")
            (root / "llvm").mkdir()
            with self.assertRaises(FileExistsError):
                archive_llvm(root, "old")


if __name__ == "__main__":
    unittest.main()
