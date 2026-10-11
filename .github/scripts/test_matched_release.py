import json
from pathlib import Path
import tomllib
import unittest
from unittest.mock import patch

import matched_release as release


class MatchedReleaseTests(unittest.TestCase):
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
