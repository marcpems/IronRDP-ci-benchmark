import json
import os
from pathlib import Path
import tomllib
import unittest
from unittest.mock import patch

from build_windows_x64_compilers import build_environment, configuration, profile_coverage


class WindowsX64BuildTests(unittest.TestCase):
    def test_control_differs_only_in_lto_and_required_llvm_linker_selection(self):
        control = tomllib.loads(configuration(Path(r"C:\clang"), "pgo-control"))
        optimized = tomllib.loads(configuration(Path(r"C:\clang"), "optimized"))
        self.assertEqual(control["rust"]["codegen-units"], 1)
        self.assertEqual(optimized["rust"]["lto"], "thin")
        self.assertTrue(optimized["llvm"]["thin-lto"])
        self.assertNotIn("use-linker", optimized["llvm"])
        control["rust"]["lto"] = "thin"
        control["llvm"]["thin-lto"] = True
        del control["llvm"]["use-linker"]
        self.assertEqual(control, optimized)

    def test_build_environment_excludes_credentials_and_inherited_overrides(self):
        with patch.dict(os.environ, {"PATH": "tools", "GH_TOKEN": "secret",
                                     "ACTIONS_RUNTIME_TOKEN": "secret", "RUSTFLAGS": "bad"}, clear=True):
            env = build_environment(Path("output"), Path("clang"))
        self.assertNotIn("GH_TOKEN", env)
        self.assertNotIn("ACTIONS_RUNTIME_TOKEN", env)
        self.assertNotIn("RUSTFLAGS", env)

    def test_reject_empty_codegen_profile(self):
        with patch("subprocess.check_output", return_value="    Block counts: [0, 0]\n"):
            with self.assertRaisesRegex(RuntimeError, "No executed X86TargetLowering"):
                profile_coverage(Path("profdata"), Path("profile"), {})
        with patch("subprocess.check_output", return_value="    Block counts: [0, 7]\n"):
            result = profile_coverage(Path("profdata"), Path("profile"), {})
        self.assertEqual(result["InstCombine"]["nonzero_functions"], 1)
        json.dumps(result)


if __name__ == "__main__":
    unittest.main()
