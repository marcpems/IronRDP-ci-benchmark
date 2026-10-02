import os
from pathlib import Path
import unittest
from unittest.mock import patch

import run


class ExperimentTests(unittest.TestCase):
    def test_pins(self):
        for pin in (run.RUST, run.LLVM, run.PERF):
            self.assertRegex(pin, r"^[0-9a-f]{40}$")

    def test_full_dist_scope_and_isolated_treatment(self):
        root = Path("D:\\experiment")
        baseline = run.configure_args(root, False)
        treatment = run.configure_args(root, True)
        self.assertEqual(treatment[:len(baseline)], baseline)
        self.assertIn("--enable-full-tools", baseline)
        self.assertIn("--enable-profiler", baseline)
        self.assertIn("--target=aarch64-pc-windows-msvc,arm64ec-pc-windows-msvc", baseline)
        self.assertNotIn("llvm.thin-lto=true", baseline)
        self.assertIn("llvm.thin-lto=true", treatment)
        self.assertIn("llvm.link-shared=false", treatment)
        self.assertIn("rust.lto=thin", treatment)
        self.assertTrue(any(arg.endswith("llvm-lib.exe") for arg in treatment))
        self.assertFalse(any("DIA" in arg or "LLVM_TOOL_" in arg for arg in treatment))

    def test_credentials_are_not_in_build_environment(self):
        with patch.dict(os.environ, {
            "PATH": "C:\\tools", "SystemRoot": "C:\\Windows",
            "GITHUB_TOKEN": "secret", "ACTIONS_RUNTIME_TOKEN": "secret",
            "AWS_SECRET_ACCESS_KEY": "secret", "RUSTFLAGS": "-bad",
        }, clear=True), patch.object(Path, "mkdir"):
            env = run.clean_environment(Path("D:\\experiment"))
        self.assertFalse(any("secret" in value for value in env.values()))
        self.assertNotIn("RUSTFLAGS", env)
        self.assertEqual(env["DIST_REQUIRE_ALL_TOOLS"], "1")
        self.assertIn("SYSTEMROOT", {key.upper() for key in env})
        self.assertNotIn("DIST_TRY_BUILD", env)

    def test_helper_is_native_but_distribution_retains_arm64ec(self):
        command = run.helper_command()
        self.assertEqual(command[command.index("--target") + 1], run.HOST)
        self.assertEqual(command[command.index("--host") + 1], run.HOST)
        self.assertTrue(any("arm64ec-pc-windows-msvc" in arg
                            for arg in run.configure_args(Path("D:\\experiment"), True)))


if __name__ == "__main__":
    unittest.main()
