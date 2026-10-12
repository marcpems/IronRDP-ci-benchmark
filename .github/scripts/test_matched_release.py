import json
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch

import matched_release as release


class MatchedReleaseTests(unittest.TestCase):
    def test_highcore_is_a_separate_native_arm64_resource_class(self):
        with patch.dict(release.os.environ, {
            "RELEASE_MACHINE_CLASS": "self-hosted-arm64-highcore",
            "RUNNER_ENVIRONMENT": "self-hosted", "RUNNER_NAME": "GB300-Arm64",
        }), patch.object(release.os, "name", "nt"), \
                patch.object(release.os, "cpu_count", return_value=72), \
                patch.object(release.platform, "machine", return_value="ARM64"):
            release.validate_runner("aarch64-pc-windows-msvc")
            self.assertEqual(release.build_cores(), 64)
            for variant in release.VARIANTS:
                config = tomllib.loads(release.configuration(
                    "aarch64-pc-windows-msvc", Path("C:/clang/bin"), Path("C:/VS/lib.exe"), variant))
                self.assertEqual(config["build"]["jobs"], 64)
                self.assertEqual(config["llvm"]["link-jobs"], 2)
                self.assertIn("arm64ec-pc-windows-msvc", config["build"]["target"])
                self.assertTrue(config["build"]["docs"])
            with patch.dict(release.os.environ, {"RUNNER_NAME": "MARCPE-D4-Arm64"}):
                with self.assertRaisesRegex(RuntimeError, "unexpected self-hosted"):
                    release.validate_runner("aarch64-pc-windows-msvc")
            with patch.object(release.os, "cpu_count", return_value=32):
                with self.assertRaisesRegex(RuntimeError, "unexpected self-hosted"):
                    release.validate_runner("aarch64-pc-windows-msvc")
            with self.assertRaisesRegex(RuntimeError, "native Windows"):
                release.validate_runner("x86_64-pc-windows-msvc")

    def test_x64_selfhost_requires_matching_identity_architecture_and_capacity(self):
        with patch.object(release.os, "name", "nt"), \
                patch.object(release.os, "cpu_count", return_value=8), \
                patch.object(release.platform, "machine", return_value="AMD64"), \
                patch.dict(release.os.environ, {
                    "RELEASE_MACHINE_CLASS": "self-hosted-x64",
                    "RUNNER_ENVIRONMENT": "self-hosted", "RUNNER_NAME": "MARCPE-TEST01-X64",
                }):
            host = "x86_64-pc-windows-msvc"
            release.validate_runner(host)
            for override in ({"RUNNER_NAME": "MARCPE-D4-Arm64"},
                             {"RUNNER_ENVIRONMENT": "github-hosted"},
                             {"RELEASE_MACHINE_CLASS": "self-hosted-arm64"},
                             {"RELEASE_MACHINE_CLASS": "github-hosted"}):
                with self.subTest(override=override), patch.dict(release.os.environ, override):
                    with self.assertRaises(RuntimeError):
                        release.validate_runner(host)
            with patch.object(release.os, "cpu_count", return_value=2):
                with self.assertRaises(RuntimeError):
                    release.validate_runner(host)
            with patch.object(release.platform, "machine", return_value="ARM64"):
                with self.assertRaisesRegex(RuntimeError, "native Windows"):
                    release.validate_runner(host)

    def test_selfhost_runner_is_explicit_and_cannot_impersonate_hosted(self):
        with patch.object(release.os, "name", "nt"), \
                patch.object(release.os, "cpu_count", return_value=12), \
                patch.object(release.platform, "machine", return_value="ARM64"), \
                patch.dict(release.os.environ, {
                    "RELEASE_MACHINE_CLASS": "self-hosted-arm64",
                    "RUNNER_ENVIRONMENT": "self-hosted", "RUNNER_NAME": "MARCPE-D4-Arm64",
                }):
            release.validate_runner("aarch64-pc-windows-msvc")
            with patch.dict(release.os.environ, {"RUNNER_NAME": "other"}):
                with self.assertRaisesRegex(RuntimeError, "unexpected self-hosted"):
                    release.validate_runner("aarch64-pc-windows-msvc")
            with patch.dict(release.os.environ, {"RELEASE_MACHINE_CLASS": "github-hosted"}), \
                    patch.object(release.os, "cpu_count", return_value=4):
                with self.assertRaisesRegex(RuntimeError, "GitHub-hosted"):
                    release.validate_runner("aarch64-pc-windows-msvc")

    def test_selfhost_deadline_reserves_upload_time(self):
        for architecture in ("arm64", "x64", "arm64-highcore"):
            with self.subTest(architecture=architecture):
                self.check_selfhost_deadline(architecture)

    def check_selfhost_deadline(self, architecture):
        with patch.dict(release.os.environ, {
            "RELEASE_JOB_STARTED": "100", "RELEASE_MACHINE_CLASS": f"self-hosted-{architecture}",
        }), patch.object(release.time, "time", return_value=100 + 400 * 60), \
                patch.object(release, "execute") as execute, patch.object(release, "save"):
            release.run(["build"], Path("."), {}, Path("."), "full-dist")
            self.assertEqual(execute.call_args.kwargs["timeout"], 130 * 60)
            with patch.object(release.time, "time", return_value=100 + 530 * 60):
                with self.assertRaisesRegex(TimeoutError, "530-minute"):
                    release.run(["build"], Path("."), {}, Path("."), "full-dist")

    def test_preparation_checks_declared_source_before_building(self):
        roots = tuple(Path(f"C:/mr/{name}") for name in ("r", "l", "e"))
        for revision in (release.RUST, "diagnostic-parent"):
            with patch.object(release.os, "name", "nt"), \
                    patch.object(release.os, "cpu_count", return_value=4), \
                    patch.object(release.platform, "machine", return_value="ARM64"), \
                    patch.object(release.subprocess, "check_output",
                                 side_effect=[revision, "wrong-llvm-revision"]) as checkout:
                kwargs = {} if revision == release.RUST else {"rust_revision": revision}
                with self.assertRaisesRegex(RuntimeError, "llvm-project"):
                    release.prepare(*roots, "aarch64-pc-windows-msvc", "msvc-pgo", **kwargs)
                self.assertEqual(checkout.call_count, 2)

    def test_qualification_uses_upstream_build_root_and_restores_config(self):
        host = "aarch64-pc-windows-msvc"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output = root / "rust", root / "evidence"
            source.mkdir()
            output.mkdir()
            original = b'profile = "dist"\n'
            (source / "bootstrap.toml").write_bytes(original)
            llvm = source / "build" / host / "llvm/bin/llvm-config.exe"
            llvm.parent.mkdir(parents=True)
            llvm.write_bytes(b"fixture")
            unpacked = source / "build/unpacked-dist"

            def extract(command, check):
                self.assertTrue(check)
                self.assertEqual(command[:2], ["tar", "-xJf"])
                self.assertEqual(command[-1], unpacked)
                name = command[2].name.removesuffix(".tar.xz")
                relative = {
                    f"rustc-nightly-{host}": "rustc/bin/rustc.exe",
                    f"rust-std-nightly-{host}": f"rust-std-{host}/lib/rustlib/{host}/lib/std.rmeta",
                    f"cargo-nightly-{host}": "cargo/bin/cargo.exe",
                    "rust-src-nightly": "rust-src/lib/rustlib/src/rust/library/lib.rs",
                }[name]
                file = unpacked / name / relative
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(b"fixture")

            def fail_test(*args):
                config = tomllib.loads((source / "bootstrap.toml").read_text())
                compiler = Path(config["build"]["rustc"])
                self.assertTrue(compiler.is_relative_to(source / "build"))
                self.assertTrue(compiler.is_file())
                raise RuntimeError("test failure")

            with patch.object(release.subprocess, "run", side_effect=extract), \
                    patch.object(release, "run", side_effect=fail_test):
                with self.assertRaisesRegex(RuntimeError, "test failure"):
                    release.qualify_distribution(source, output, host, {})
            self.assertEqual((source / "bootstrap.toml").read_bytes(), original)
            self.assertFalse((output / "extracted").exists())

    def test_long_physical_roots_fail_before_expensive_builds(self):
        release.check_build_paths(Path("C:/mr/r"), Path("C:/mr/l"), Path("C:/mr/e"))
        with self.assertRaisesRegex(RuntimeError, "short physical build roots"):
            release.check_build_paths(Path("C:/a/IronRDP-ci-benchmark/rust-source"))

    def test_workflows_relocate_on_workspace_volume(self):
        workflows = Path(__file__).parents[1] / "workflows"
        for name in ("matched-release.yml", "matched-release-ironrdp.yml"):
            text = (workflows / name).read_text()
            self.assertIn("GetPathRoot($env:GITHUB_WORKSPACE)", text)
            self.assertIn("[System.IO.Directory]::Move", text)
            self.assertNotIn("$env:SystemDrive", text)

    def test_full_scope_and_only_declared_configuration_differences(self):
        for host in ("x86_64-pc-windows-msvc", "aarch64-pc-windows-msvc"):
            configs = {}
            for variant in release.VARIANTS:
                configs[variant] = tomllib.loads(release.configuration(
                    host, Path("C:/clang/bin"),
                    Path("C:/clang/bin/llvm-lib.exe" if variant == "llvm-pgo-thin" else "C:/VS/lib.exe"),
                    variant))
            self.assertEqual(configs["baseline"], configs["msvc-pgo"])
            base = configs["baseline"]
            self.assertTrue(base["build"]["extended"])
            self.assertTrue(base["build"]["docs"])
            self.assertTrue(base["rust"]["llvm-bitcode-linker"])
            self.assertFalse(base["llvm"]["thin-lto"])
            self.assertEqual(base["rust"]["lto"], "thin-local")
            self.assertFalse(base["llvm"]["download-ci-llvm"])
            self.assertEqual(base["build"]["jobs"], 4)
            llvm = configs["llvm-pgo-thin"]
            self.assertTrue(llvm["llvm"]["thin-lto"])
            self.assertEqual(llvm["rust"]["lto"], "thin")
            self.assertEqual(llvm["target"][host]["linker"], "lld-link.exe")
            self.assertEqual(base["target"][host]["linker"], "link.exe")
            self.assertEqual("arm64ec-pc-windows-msvc" in base["build"]["target"],
                             host.startswith("aarch64"))
            self.assertEqual(base["build"], llvm["build"])
            self.assertFalse(llvm["llvm"]["link-shared"])

    def test_manifest_rejects_compiler_only_and_missing_arm64ec(self):
        host = "aarch64-pc-windows-msvc"
        names = [f"{name}-nightly-{host}.{suffix}" for name, suffix in (
            ("rustc", "tar.xz"), ("rust-std", "tar.xz"), ("cargo", "tar.xz"),
            ("rust-docs", "tar.xz"), ("rustfmt", "tar.xz"), ("clippy", "tar.xz"),
            ("rust-analyzer", "tar.xz"), ("rust", "msi"))]
        names.append("rust-src-nightly.tar.xz")
        with self.assertRaisesRegex(RuntimeError, "arm64ec"):
            release.check_manifest([Path(name) for name in names], host)
        names.append("rust-std-nightly-arm64ec-pc-windows-msvc.tar.xz")
        release.check_manifest([Path(name) for name in names], host)
        with self.assertRaisesRegex(RuntimeError, "incomplete full distribution"):
            release.check_manifest([Path(names[0])], host)

    def test_deadline_is_global_and_never_reports_success(self):
        with patch.dict(release.os.environ, {"RELEASE_JOB_STARTED": "100"}), \
                patch.object(release.time, "time", return_value=100 + 350 * 60), \
                patch.object(release, "execute") as execute:
            with self.assertRaises(TimeoutError):
                release.run(["build"], Path("."), {}, Path("."), "full-dist")
            execute.assert_not_called()

    def test_protocol_does_not_transfer_old_results(self):
        protocol = json.loads((Path(__file__).parents[2] /
                               "ci-benchmark/matched-release/protocol.json").read_text())
        self.assertEqual(protocol["rust_sha"], release.RUST)
        self.assertEqual(protocol["variants"], list(release.VARIANTS))
        self.assertEqual(protocol["release_repetitions_per_cell"], 3)
        self.assertTrue(protocol["pilot_excluded"])
        self.assertIn("right-censored", protocol["timeouts"])


if __name__ == "__main__":
    unittest.main()
