import copy
import json
import os
from pathlib import Path
import tempfile
import subprocess
import tomllib
import unittest
import zipfile
from unittest.mock import patch

from msvc_experiment import PHASES, audit_cmake_tools, clang_profile_preflight, cmake_toolchain, configuration, equivalent_tools, preserve_training_compiler, train, verify_profiles
from build_arm_compilers import digest


class ConfigurationTests(unittest.TestCase):
    def test_clang_runtime_preflight_uses_matching_runtime_and_microsoft_linker(self):
        for host, suffix in (("aarch64-pc-windows-msvc", "aarch64"),
                             ("x86_64-pc-windows-msvc", "x86_64")):
            for fail_merge in (False, True):
                with self.subTest(host=host, fail_merge=fail_merge), tempfile.TemporaryDirectory() as tmp:
                    output = Path(tmp)
                    resource = output / "resource"
                    runtime = resource / "lib/windows" / f"clang_rt.profile-{suffix}.lib"
                    runtime.parent.mkdir(parents=True)
                    runtime.write_bytes(b"runtime")
                    calls = []

                    def execute(command, cwd, env, directory, name, **kwargs):
                        calls.append((name, command))
                        if name == "clang-profile-run-0":
                            (cwd / "raw/shared_123.profraw").touch()
                        if name == "clang-profile-merge" and fail_merge:
                            raise RuntimeError("malformed profile")

                    with patch("msvc_experiment.subprocess.check_output", return_value=str(resource)), \
                         patch("msvc_experiment.execute", side_effect=execute):
                        arguments = (output, output / "clang", {},
                                     {"files": {"link.exe": {"path": "native-link.exe"}}}, host)
                        if fail_merge:
                            with self.assertRaisesRegex(RuntimeError, "malformed profile"):
                                clang_profile_preflight(*arguments)
                        else:
                            provenance = clang_profile_preflight(*arguments)
                            self.assertEqual(provenance["sha256"], digest(runtime))
                    link = dict(calls)["clang-profile-link"]
                    self.assertEqual(link[0], "native-link.exe")
                    self.assertIn(runtime, link)
                    self.assertEqual(sum(name.startswith("clang-profile-run-") for name, _ in calls), 8)
                    self.assertEqual(calls[-1][1][0], output / "clang/llvm-profdata.exe")

    def test_failed_training_archive_is_explicitly_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output = Path(tmp) / "source", Path(tmp) / "output"
            for path in (source / "build/host/stage2/bin/rustc.exe",
                         source / "build/host/stage0/bin/cargo.exe",
                         output / "training/target/debug/collector.exe",
                         output / "training/target/debug/rustc-fake.exe",
                         *(source / name for name in ("COPYRIGHT", "LICENSE-MIT", "LICENSE-APACHE"))):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"fixture")
            rustlib = source / "build/host/stage2/lib/rustlib"
            rustlib.mkdir(parents=True)
            if os.name == "nt":
                subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                                f"New-Item -ItemType Junction -Path '{rustlib / 'src'}' "
                                f"-Target '{source}' | Out-Null"], check=True)
            else:
                (rustlib / "src").symlink_to(source, target_is_directory=True)
            preserve_training_compiler(source, output, "host")
            metadata = json.loads((output / "instrumented-diagnostic.json").read_text())
            self.assertTrue(metadata["diagnostic_only"])
            self.assertEqual(metadata["archive_sha256"], digest(output / "instrumented-diagnostic.zip"))
            with zipfile.ZipFile(output / "instrumented-diagnostic.zip") as archive:
                self.assertIn("sysroot/bin/rustc.exe", archive.namelist())
                self.assertIn("training-tools/rustc-fake.exe", archive.namelist())
                self.assertFalse(any(name.startswith("sysroot/lib/rustlib/src/") for name in archive.namelist()))
            self.assertFalse((output / "metadata.json").exists())
            self.assertFalse((output / "compiler.zip").exists())
            self.assertFalse((output / "instrumented-diagnostic.partial").exists())

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
