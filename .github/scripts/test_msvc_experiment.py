import copy
import json
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch

from msvc_experiment import PHASES, audit_cmake_tools, cmake_toolchain, configuration, equivalent_tools, train, verify_profiles
from build_arm_compilers import digest


class ConfigurationTests(unittest.TestCase):
    def test_training_builds_and_requires_all_collector_binaries(self):
        for provide_wrapper in (False, True):
            with self.subTest(provide_wrapper=provide_wrapper), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                source, output = root / "source", root / "output"
                fixture = source / "src/tools/rustc-perf/collector/compile-benchmarks/token-stream-stress"
                fixture.mkdir(parents=True)
                (fixture / "Cargo.lock").write_text('[[package]]\nname="token-stream-stress"\nversion="0.0.0"\n')
                output.mkdir()
                stages = []

                def execute(command, cwd, env, directory, name, **kwargs):
                    stages.append(name)
                    if name == "training-tools":
                        self.assertEqual(command[1:], ["build", "--locked", "-p", "collector", "--bins"])
                        binaries = cwd / "target/debug"
                        binaries.mkdir(parents=True)
                        (binaries / "collector.exe").touch()
                        if provide_wrapper:
                            (binaries / "rustc-fake.exe").touch()
                    if name == "training":
                        raise RuntimeError("training reached")

                message = "training reached" if provide_wrapper else "Missing training executable"
                with patch("msvc_experiment.execute", side_effect=execute), \
                     patch("msvc_experiment.training_crates", return_value=["token-stream-stress"]):
                    with self.assertRaisesRegex(RuntimeError, message):
                        train(source, output, "host", {}, False, root / "clang")
                self.assertEqual("training" in stages, provide_wrapper)

    def test_cmake_audit_rejects_a_different_linker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tools = {}
            lines = []
            for variable, name in (("CMAKE_LINKER", "link.exe"), ("CMAKE_AR", "lib.exe"),
                                   ("CMAKE_CXX_COMPILER", "clang-cl.exe")):
                binary = root / name
                binary.write_bytes(name.encode())
                tools[name] = {"sha256": digest(binary)}
                lines.append(f"{variable}:FILEPATH={binary.as_posix()}")
            cache = root / "CMakeCache.txt"
            cache.write_text("\n".join(lines))
            audit_cmake_tools(cache, {"files": tools})
            (root / "link.exe").write_bytes(b"different linker")
            with self.assertRaisesRegex(RuntimeError, "expected pinned link.exe"):
                audit_cmake_tools(cache, {"files": tools})

    def test_cmake_toolchain_pins_native_tools_with_spaces(self):
        with tempfile.TemporaryDirectory() as tmp:
            tools = {"files": {name: {"path": f"C:/Program Files/MSVC/{name}"}
                               for name in ("link.exe", "lib.exe")}}
            text = cmake_toolchain(Path(tmp), tools).read_text()
            self.assertIn('set(CMAKE_LINKER "C:/Program Files/MSVC/link.exe" CACHE FILEPATH "" FORCE)', text)
            self.assertIn('set(CMAKE_AR "C:/Program Files/MSVC/lib.exe" CACHE FILEPATH "" FORCE)', text)

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
                self.assertEqual(config["target"][host]["linker"], "link.exe")
                self.assertTrue(config["target"][host]["ar"].endswith("/lib.exe"))
                self.assertEqual(config["build"]["host"], [host])
                self.assertTrue(config["build"]["profiler"])
                self.assertFalse(config["target"]["wasm32-unknown-unknown"]["profiler"])
            treatment = configs["pgo-rust-thin"]
            self.assertEqual(treatment["rust"]["lto"], "thin")
            treatment["rust"]["lto"] = "thin-local"
            self.assertEqual(treatment, configs["pgo"])
            self.assertEqual(configs["baseline"]["pgo"], {"rustc": {}, "llvm": {}})
            self.assertIn("generate", configs["rustc-profile"]["pgo"]["rustc"])
            self.assertIn("generate", configs["llvm-profile"]["pgo"]["llvm"])
            self.assertIn("use", configs["llvm-profile"]["pgo"]["rustc"])

    def test_bootstrap_linker_flag_has_no_space_separated_path(self):
        config = tomllib.loads(configuration(
            "x86_64-pc-windows-msvc", Path("D:/clang"),
            Path("C:/Program Files/Microsoft Visual Studio/link.exe"),
            Path("C:/Program Files/Microsoft Visual Studio/lib.exe"),
            "baseline", Path("D:/profiles")))
        self.assertEqual(config["target"]["x86_64-pc-windows-msvc"]["linker"], "link.exe")

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
