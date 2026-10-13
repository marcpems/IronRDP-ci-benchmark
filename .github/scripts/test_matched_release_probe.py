import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from build_arm_compilers import digest
from matched_release import LLVM, PERF, RUST, VARIANTS
from matched_release_probe import install, one_file, release_runs


class ReleaseProbeTests(unittest.TestCase):
    def test_actual_archive_hashes_and_common_std(self):
        host, arch, vm, run = "aarch64-pc-windows-msvc", "arm64", 1, "release"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for variant in VARIANTS:
                evidence = root / f"release-{arch}-{variant}-{vm}-evidence"
                dist = root / f"release-{arch}-{variant}-{vm}-dist"
                evidence.mkdir()
                dist.mkdir()
                metadata = {
                    "complete": True, "rust_sha": RUST, "llvm_sha": LLVM, "perf_sha": PERF,
                    "host": host, "variant": variant, "run_id": run, "vm": vm,
                    "pilot": False, "attempt": "1",
                    "tools": {"msvc": "same", "sdk": "same", "files": {}},
                }
                (evidence / "result.json").write_text(json.dumps(metadata))
                components = {
                    f"rustc-nightly-{host}": {
                        "rustc/bin/rustc.exe": variant.encode(),
                        f"rustc/lib/rustlib/{host}/lib/old.rlib": b"must disappear",
                    }
                }
                if variant == "baseline":
                    components[f"cargo-nightly-{host}"] = {"cargo/bin/cargo.exe": b"cargo"}
                    components[f"rust-std-nightly-{host}"] = {
                        f"rust-std-{host}/lib/rustlib/{host}/lib/std.rlib": b"shared"}
                manifest = []
                for component, files in components.items():
                    archive = dist / (component + ".tar.xz")
                    with tarfile.open(archive, "w:xz") as bundle:
                        for relative, value in files.items():
                            info = tarfile.TarInfo(component + "/" + relative)
                            info.size = len(value)
                            bundle.addfile(info, io.BytesIO(value))
                    manifest.append({"name": archive.name, "sha256": digest(archive)})
                (evidence / "dist-manifest.json").write_text(json.dumps(manifest))
            args = (arch, host, vm, run, False, {"llvm_sha": LLVM, "perf_sha": PERF})
            compilers, cargo, metadata, evidence, std = install(root, root / "installed", *args)
            self.assertEqual(cargo.read_bytes(), b"cargo")
            self.assertEqual(set(compilers), set(VARIANTS))
            self.assertEqual(set(std), {"std.rlib"})
            for variant, compiler in compilers.items():
                self.assertEqual(compiler.read_bytes(), variant.encode())
                self.assertEqual((compiler.parent.parent / f"lib/rustlib/{host}/lib/std.rlib").read_bytes(),
                                 b"shared")
                self.assertFalse((compiler.parent.parent / f"lib/rustlib/{host}/lib/old.rlib").exists())
            runner = {"runner_class": "self-hosted-arm64-highcore", "runner_name": "GB300-Arm64",
                      "build_affinity_count": 64, "build_jobs": 64, "logical_cpus": 72}
            runs = {variant: str(100 + n) for n, variant in enumerate(VARIANTS)}
            originals = {}
            for variant in VARIANTS:
                path = root / f"release-{arch}-{variant}-{vm}-evidence" / "result.json"
                originals[path] = path.read_text()
                item = {**json.loads(originals[path]), **runner, "full_distribution": True,
                        "run_id": runs[variant]}
                (path.parent / "bootstrap.toml").write_text("[build]\njobs = 64\n")
                path.write_text(json.dumps(item))
            selfhost_args = (arch, host, vm, runs, False, args[-1])
            actual = install(root, root / "selfhost", *selfhost_args, runner=runner)
            self.assertEqual(set(actual[0]), set(VARIANTS))
            baseline = root / f"release-{arch}-baseline-{vm}-evidence" / "result.json"
            legacy = json.loads(baseline.read_text())
            del legacy["build_jobs"]
            baseline.write_text(json.dumps(legacy))
            actual = install(root, root / "legacy", *selfhost_args, runner=runner)
            self.assertEqual(actual[3]["baseline"]["runner_configuration"]["build_jobs_source"],
                             "bootstrap.toml")
            config = baseline.parent / "bootstrap.toml"
            config.write_text("[build]\njobs = 4\n")
            with self.assertRaisesRegex(RuntimeError, "bootstrap worker count"):
                install(root, root / "wrong-config", *selfhost_args, runner=runner)
            config.write_text("[build]\njobs = 64\n")
            with self.assertRaisesRegex(RuntimeError, "machine or resource-class"):
                install(root, root / "wrong-machine", *selfhost_args,
                        runner={**runner, "runner_name": "other"})
            with self.assertRaisesRegex(RuntimeError, "identity"):
                install(root, root / "wrong-run", arch, host, vm,
                        {**runs, "baseline": "999"}, False, args[-1], runner=runner)
            for path, original in originals.items():
                path.write_text(original)
            archive = one_file(root / f"release-{arch}-baseline-{vm}-dist",
                               f"rustc-nightly-{host}.tar.xz")
            archive.write_bytes(b"corrupt")
            with self.assertRaisesRegex(RuntimeError, "checksum mismatch"):
                install(root, root / "rejected", *args)

    def test_hosted_and_selfhost_provenance_cannot_be_mixed(self):
        runs = dict.fromkeys(VARIANTS, "123")
        with self.assertRaisesRegex(RuntimeError, "hosted benchmarks require one"):
            release_runs(runs, None)
        for invalid in ("123", {"baseline": "123"}, {**runs, "baseline": "not-a-run"}):
            with self.assertRaisesRegex(RuntimeError, "per-variant numeric"):
                release_runs(invalid, {"runner_class": "self-hosted-x64"})

    def test_duplicate_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("one", "two"):
                (root / name).mkdir()
                (root / name / "result.json").write_text("{}")
            with self.assertRaisesRegex(RuntimeError, "exactly one"):
                one_file(root, "result.json")


if __name__ == "__main__":
    unittest.main()
