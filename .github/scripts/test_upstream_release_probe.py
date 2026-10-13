import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from build_arm_compilers import digest
from upstream_release_probe import (
    BUILD_SCRIPT, CONTINUATION_RUN, RUST, continuation_command, validate_config,
    validate_continuation,
)


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
    def continuation_fixture(self, root):
        evidence, source = root / "evidence", root / "source"
        (evidence / "e").mkdir(parents=True)
        (evidence / "r/opt-artifacts").mkdir(parents=True)
        tools = {"cl.exe": {"sha256": "original-tool"}}
        provenance = {
            "run_id": CONTINUATION_RUN, "attempt": "1", "rust_sha": RUST,
            "host": "x86_64-pc-windows-msvc", "setting": "baseline",
            "source_changes": False, "image": "original-image", "tools": tools,
        }
        (evidence / "e/provenance.json").write_text(json.dumps(provenance))
        config = fixture(provenance["host"])
        (evidence / "r/bootstrap.toml").write_text("\n".join(
            f"[{section}]\n" + "\n".join(f"{k} = {json.dumps(v)}" for k, v in values.items())
            for section, values in config.items()))
        command = continuation_command(source)
        (evidence / "e/upstream-ci.stderr").write_text(
            "Section `Stage 1 (Rustc + rustdoc + cargo + clippy PGO)` ended: OK (100s)\n"
            "Section `Stage 2 (LLVM PGO)` ended: OK (200s)\n"
            f"Executing `{command} [at {source}]`\n")
        for component in ("llvm", "rustc", "rustdoc", "clippy", "cranelift"):
            (evidence / f"r/opt-artifacts/{component}-pgo.profdata").write_bytes(b"sample-profile")
        expected = {"files": {p.relative_to(evidence).as_posix(): digest(p)
                              for p in evidence.rglob("*") if p.is_file()}}
        return evidence, source, provenance["host"], "baseline", tools, "original-image", expected

    def test_continuation_keeps_all_profile_consumers(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = self.continuation_fixture(Path(tmp))
            command, config = validate_continuation(*args)
            self.assertEqual(config, fixture(args[2]))
            self.assertEqual(command.count("--set pgo."), 6)
            self.assertEqual(command.count("rustc-pgo.profdata"), 2)
            self.assertIn("pgo.cranelift.use=", command)
            self.assertNotIn("--keep-stage", command)
            self.assertEqual(command + " --keep-stage 0", continuation_command(args[1]))

    def test_continuation_rejects_tool_image_architecture_or_setting_drift(self):
        for index, value in ((2, "aarch64-pc-windows-msvc"), (3, "jobs6"),
                             (4, {"cl.exe": {"sha256": "changed"}}), (5, "new-image")):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as tmp:
                args = list(self.continuation_fixture(Path(tmp)))
                args[index] = value
                with self.assertRaises(RuntimeError):
                    validate_continuation(*args)

    def test_continuation_rejects_changed_evidence(self):
        for relative in ("r/opt-artifacts/cranelift-pgo.profdata", "e/upstream-ci.stderr",
                         "r/bootstrap.toml", "e/provenance.json"):
            with self.subTest(file=relative), tempfile.TemporaryDirectory() as tmp:
                args = self.continuation_fixture(Path(tmp))
                (args[0] / relative).write_bytes(b"changed")
                with self.assertRaisesRegex(RuntimeError, "hash mismatch"):
                    validate_continuation(*args)

    def test_continuation_requires_completed_training_and_exact_final_command(self):
        for needle in ("Stage 2 (LLVM PGO)", "--keep-stage 0"):
            with self.subTest(needle=needle), tempfile.TemporaryDirectory() as tmp:
                args = self.continuation_fixture(Path(tmp))
                log = args[0] / "e/upstream-ci.stderr"
                log.write_text(log.read_text().replace(needle, "removed"))
                args[-1]["files"]["e/upstream-ci.stderr"] = digest(log)
                with self.assertRaises(RuntimeError):
                    validate_continuation(*args)

    def test_continuation_requires_every_profile_to_be_pinned(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = self.continuation_fixture(Path(tmp))
            del args[-1]["files"]["r/opt-artifacts/cranelift-pgo.profdata"]
            with self.assertRaisesRegex(RuntimeError, "missing pinned profile"):
                validate_continuation(*args)

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
