import copy
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from upstream_release_probe import BUILD_SCRIPT, validate_config


def fixture(host):
    return {
        "dist": {"compression-profile": "balanced", "compression-formats": ["xz"]},
        "build": {
            "build": host, "host": [host],
            "target": [host] + (["arm64ec-pc-windows-msvc"] if host.startswith("aarch64") else []),
            "extended": True, "profiler": True,
        },
        "rust": {
            "codegen-units": 1 if host.startswith("x86_64") else 16,
            "codegen-units-std": 1,
            "codegen-backends": ["llvm", "cranelift"] if host.startswith("x86_64") else ["llvm"],
        },
        "llvm": {},
    }


class UpstreamReleaseTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Windows Git Bash wrapper")
    def test_cache_shutdown_runs_and_preserves_build_errors(self):
        for build_status, stop_status, expected in ((0, 0, 0), (7, 0, 7), (0, 9, 9), (7, 9, 7)):
            with self.subTest(build=build_status, stop=stop_status), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                script = root / "src/ci/scripts/run-build-from-ci.sh"
                script.parent.mkdir(parents=True)
                script.write_text(f"#!/bin/sh\nexit {build_status}\n")
                tools = root / "tools"
                tools.mkdir()
                (tools / "sccache").write_text(
                    f'#!/bin/sh\n[ "$1" = "--stop-server" ] || exit 88\n'
                    f'echo stopped > "{root.as_posix()}/stopped.txt"\nexit {stop_status}\n')
                result = subprocess.run(
                    [r"C:\Program Files\Git\bin\bash.exe", "--noprofile", "--norc", "-c", BUILD_SCRIPT],
                    cwd=root, env={**os.environ, "NATIVE_MSVC_BIN": str(tools)},
                    capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, expected, result.stderr)
                self.assertTrue((root / "stopped.txt").is_file())

    def test_only_scheduling_settings_differ(self):
        for host in ("x86_64-pc-windows-msvc", "aarch64-pc-windows-msvc"):
            for setting in ("baseline", "jobs6", "link1"):
                config = fixture(host)
                if setting == "jobs6":
                    config["build"]["jobs"] = 6
                if setting == "link1":
                    config["llvm"]["link-jobs"] = 1
                with self.subTest(host=host, setting=setting):
                    validate_config(config, host, setting)

    def test_quality_or_coverage_changes_are_rejected(self):
        host = "x86_64-pc-windows-msvc"
        for section, key, value in (
            ("dist", "compression-profile", "fast"),
            ("dist", "compression-formats", ["gz"]),
            ("build", "docs", False),
            ("build", "extended", False),
            ("build", "profiler", False),
            ("build", "target", []),
            ("rust", "codegen-units", 16),
            ("rust", "codegen-units-std", 16),
            ("rust", "codegen-backends", ["llvm"]),
            ("build", "jobs", 6),
            ("llvm", "link-jobs", 1),
        ):
            config = copy.deepcopy(fixture(host))
            config[section][key] = value
            with self.subTest(section=section, key=key):
                with self.assertRaises(RuntimeError):
                    validate_config(config, host, "baseline")

    def test_missing_experimental_setting_is_rejected(self):
        host = "aarch64-pc-windows-msvc"
        for setting in ("jobs6", "link1"):
            with self.subTest(setting=setting), self.assertRaises(RuntimeError):
                validate_config(fixture(host), host, setting)


if __name__ == "__main__":
    unittest.main()
