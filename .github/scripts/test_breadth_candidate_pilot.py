import copy
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from breadth_candidate_pilot import checked_candidate, digest, install_components, main, package_inventory


class CandidatePilotTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.evidence = self.root / "e"
        self.evidence.mkdir()
        self.dist = self.root / "r/build/dist"
        self.dist.mkdir(parents=True)
        self.selection = {"run_id": "123", "attempt": "1", "source_revision": "source",
                          "llvm_revision": "llvm", "rustc_perf_revision": "perf",
                          "source_patch_sha256": "patch", "runner": "runner", "components": []}
        result = {"complete": True, "run_id": "123", "attempt": "1", "rust_sha": "source",
                  "llvm_sha": "llvm", "rustc_perf_sha": "perf", "patch_sha256": "patch",
                  "runner": "runner", "profiles": {}}
        for name in ("llvm", "rustc", "rustdoc", "clippy", "cranelift"):
            path = self.evidence / f"{name}-pgo.profdata"
            path.write_bytes(name.encode())
            result["profiles"][name] = {"sha256": digest(path), "bytes": path.stat().st_size}
        manifest = []
        for component in ("rustc", "cargo", "rust-std"):
            path = self.dist / f"{component}.tar.xz"
            path.write_bytes(component.encode())
            row = {"name": path.name, "bytes": path.stat().st_size, "sha256": digest(path)}
            manifest.append(row)
            self.selection["components"].append({**row, "component": component})
        for name, data, key in (("result.json", result, "result_sha256"),
                                ("dist-manifest.json", manifest, "dist_manifest_sha256")):
            path = self.evidence / name
            path.write_text(json.dumps(data))
            self.selection[key] = digest(path)

    def tearDown(self):
        self.temporary.cleanup()

    def test_complete_candidate_requires_pinned_receipts_profiles_and_archives(self):
        result, archives = checked_candidate(self.root, self.selection)
        self.assertTrue(result["complete"])
        self.assertEqual(set(archives), {"rustc", "cargo", "rust-std"})
        (self.dist / "rustc.tar.xz").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "archive checksum"):
            checked_candidate(self.root, self.selection)

    def test_failed_or_wrong_candidate_cannot_be_selected_even_with_matching_receipt_hash(self):
        path = self.evidence / "result.json"
        original = json.loads(path.read_text())
        for key, value in (("complete", False), ("run_id", "different"),
                           ("patch_sha256", "different"), ("profiles", {})):
            with self.subTest(key=key):
                result = {**original, key: value}
                path.write_text(json.dumps(result))
                self.selection["result_sha256"] = digest(path)
                with self.assertRaises(ValueError):
                    checked_candidate(self.root, self.selection)

    def test_changed_profile_and_duplicate_component_manifest_rejected(self):
        path = self.evidence / "llvm-pgo.profdata"
        path.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "profile checksum"):
            checked_candidate(self.root, self.selection)
        path.write_bytes(b"llvm")
        manifest_path = self.evidence / "dist-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest.append(copy.deepcopy(manifest[0]))
        manifest_path.write_text(json.dumps(manifest))
        self.selection["dist_manifest_sha256"] = digest(manifest_path)
        with self.assertRaisesRegex(ValueError, "manifest mismatch"):
            checked_candidate(self.root, self.selection)

    def test_component_install_preserves_rustdoc_and_installs_matching_std(self):
        host = "x86_64-pc-windows-msvc"
        members = {"rustc": ["rustc/bin/rustc.exe", "rustc/bin/rustdoc.exe"],
                   "cargo": ["cargo/bin/cargo.exe"],
                   "rust-std": [f"rust-std-{host}/lib/rustlib/{host}/lib/libstd-fixture.rlib"]}
        archives = {}
        for component, names in members.items():
            name = f"{component}-nightly-{host}"
            archive = self.root / f"{name}.tar.xz"
            with tarfile.open(archive, "w:xz") as bundle:
                for suffix in names:
                    entry = tarfile.TarInfo(f"{name}/{suffix}")
                    entry.size = 4
                    bundle.addfile(entry, io.BytesIO(b"data"))
            archives[component] = archive
        compiler, cargo, rustdoc = install_components(archives, self.root / "installed", host)
        self.assertTrue(all(p.is_file() for p in (compiler, cargo, rustdoc)))
        self.assertEqual((compiler.parent.parent /
                          f"lib/rustlib/{host}/lib/libstd-fixture.rlib").read_bytes(), b"data")
        with self.assertRaises(FileExistsError):
            install_components(archives, self.root / "installed", host)

    def test_archive_traversal_is_not_extracted(self):
        archive = self.root / "bad.tar.xz"
        with tarfile.open(archive, "w:xz") as bundle:
            entry = tarfile.TarInfo("../escaped")
            entry.size = 1
            bundle.addfile(entry, io.BytesIO(b"x"))
        with self.assertRaises(tarfile.FilterError):
            install_components({"rustc": archive}, self.root / "installed", "host")
        self.assertFalse((self.root / "escaped").exists())

    def test_frozen_package_inventory_rejects_missing_extra_or_changed_archives(self):
        source = self.root / "source"
        source.mkdir()
        cache = self.root / "cargo/registry/cache/index"
        cache.mkdir(parents=True)
        package = cache / "example-1.0.crate"
        package.write_bytes(b"original")
        (source / "Cargo.lock").write_text(
            'version = 3\n[[package]]\nname = "example"\nversion = "1.0"\n'
            f'checksum = "{digest(package)}"\n')
        self.assertEqual(len(package_inventory(source, self.root / "cargo")), 1)
        package.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "does not match"):
            package_inventory(source, self.root / "cargo")
        package.unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            package_inventory(source, self.root / "cargo")

    def test_metadata_uses_utf8_even_with_windows_legacy_default_encoding(self):
        selection = {**self.selection, "host": "host", "logical_processors": 16,
                     "pilot_scenarios": []}
        manifest = {"cores": 16, "host": "host", "rust_version": "version",
                    "training": {"rust_sha": "source", "rustc_perf_sha": "perf"},
                    "projects": [{"id": "fd", "revision": "fd-sha", "lock_sha256": "lock",
                                  "selected_packages": ["fd-find"]}]}
        pilot = self.root / "pilot"
        (pilot / "e").mkdir(parents=True)
        tools = pilot / "toolchain"
        tools.mkdir()
        for name in ("rustc.exe", "cargo.exe", "rustdoc.exe"):
            (tools / name).write_bytes(b"fixture")
        files = {}
        for name, value in (("selection", selection), ("manifest", manifest),
                            ("training-audit", {})):
            files[name] = self.root / f"{name}.json"
            files[name].write_text(json.dumps(value), encoding="utf-8")
        argv = ["pilot", "--root", str(pilot), "--retained", str(self.root / "retained"),
                "--perf", str(self.root / "perf")]
        for name, path in files.items():
            argv.extend((f"--{name}", str(path)))
        original_read = Path.read_text

        def windows_read(path, *args, **kwargs):
            kwargs.setdefault("encoding", "cp1252")
            return original_read(path, *args, **kwargs)

        def logged(command, source, env, prefix):
            if prefix.name == "metadata":
                prefix.with_suffix(".stdout").write_text(json.dumps(
                    {"packages": [{"id": "root", "name": "fd-find", "source": None,
                                   "description": "\u0141"}]}, ensure_ascii=False), encoding="utf-8")
            return {"command": command, "exit_code": 0}

        with patch.object(sys, "argv", argv), \
                patch.dict(os.environ, {"RUNNER_NAME": "runner", "RUNNER_ENVIRONMENT": "self-hosted",
                                        "GITHUB_RUN_ID": "test", "GITHUB_RUN_ATTEMPT": "1"}), \
                patch("breadth_candidate_pilot.os.name", "nt"), \
                patch("breadth_candidate_pilot.os.cpu_count", return_value=16), \
                patch("breadth_candidate_pilot.checked_candidate", return_value=({}, {})), \
                patch("breadth_candidate_pilot.install_components",
                      return_value=tuple(tools / name for name in ("rustc.exe", "cargo.exe", "rustdoc.exe"))), \
                patch("breadth_candidate_pilot.verify_source"), \
                patch("breadth_candidate_pilot.compiler_environment", return_value={}), \
                patch("breadth_candidate_pilot.subprocess.check_output",
                      return_value="host: host\nrelease: version\ncommit-hash: source\n"), \
                patch("breadth_candidate_pilot.validate_meter"), \
                patch("breadth_candidate_pilot.run_logged", side_effect=logged), \
                patch("breadth_candidate_pilot.package_inventory", return_value=[]), \
                patch("breadth_candidate_pilot.telemetry_executables", return_value=[]), \
                patch.object(Path, "read_text", windows_read):
            main()
        self.assertEqual(json.loads((pilot / "e/pilot.json").read_text())["status"],
                         "passed-candidate-only-pilot-not-comparative-qualification")


if __name__ == "__main__":
    unittest.main()
