import copy
import json
from pathlib import Path
import tempfile
import tomllib
import unittest

from msvc_experiment import PHASES, configuration, equivalent_tools, verify_profiles
from build_arm_compilers import digest


class ConfigurationTests(unittest.TestCase):
    def test_only_rust_lto_differs_between_pgo_variants(self):
        for host in ("x86_64-pc-windows-msvc", "aarch64-pc-windows-msvc"):
            configs = {}
            for phase in PHASES:
                config = tomllib.loads(configuration(
                    host, Path("C:/clang"), Path("C:/vs/link.exe"),
                    Path("C:/vs/lib.exe"), phase, Path("C:/profiles")))
                configs[phase] = config
                self.assertFalse(config["llvm"]["thin-lto"])
                self.assertFalse(config["llvm"]["link-shared"])
                self.assertTrue(config["target"][host]["linker"].endswith("/link.exe"))
                self.assertTrue(config["target"][host]["ar"].endswith("/lib.exe"))
                self.assertEqual(config["build"]["host"], [host])
            treatment = configs["pgo-rust-thin"]
            self.assertEqual(treatment["rust"]["lto"], "thin")
            treatment["rust"]["lto"] = "thin-local"
            self.assertEqual(treatment, configs["pgo"])
            self.assertEqual(configs["baseline"]["pgo"], {"rustc": {}, "llvm": {}})
            self.assertIn("generate", configs["rustc-profile"]["pgo"]["rustc"])
            self.assertIn("generate", configs["llvm-profile"]["pgo"]["llvm"])
            self.assertIn("use", configs["llvm-profile"]["pgo"]["rustc"])

    def test_tool_comparison_ignores_install_location_not_binary(self):
        left = {"msvc": "v1", "sdk": "s1", "files": {"link.exe": {"path": "a", "sha256": "hash"}}}
        right = copy.deepcopy(left)
        right["files"]["link.exe"]["path"] = "b"
        self.assertTrue(equivalent_tools(left, right))
        right["files"]["link.exe"]["sha256"] = "other"
        self.assertFalse(equivalent_tools(left, right))

    def test_profiles_require_matching_source_tools_phase_and_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / "rustc-pgo.profdata"
            profile.write_bytes(b"profile")
            tools = {"msvc": "v1", "sdk": "s1", "files": {}}
            metadata = {"phase": "rustc-profile", "rust_sha": "source", "host": "host",
                        "tools": tools, "profiles": {profile.name: digest(profile)}}
            (root / "metadata.json").write_text(json.dumps(metadata))
            verify_profiles(root, "llvm-profile", tools, "source", "host")
            for phase, source in (("pgo", "source"), ("llvm-profile", "wrong")):
                with self.assertRaises(RuntimeError):
                    verify_profiles(root, phase, tools, source, "host")
            profile.write_bytes(b"modified")
            with self.assertRaises(RuntimeError):
                verify_profiles(root, "llvm-profile", tools, "source", "host")


if __name__ == "__main__":
    unittest.main()
