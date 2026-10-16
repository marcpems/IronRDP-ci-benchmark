import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from build_arm_compilers import digest, save
from matched_release import RUST, SCALING_STUDY, SCALING_VARIANT
from prepare_arm64_scaling_space import cache_disposal_complete, preserve_cache, verify_cell
from cleanup_arm64_investigations import cleanup_cell
import prepare_arm64_scaling_space as space
import relocate_failed_scaling_build as recovery


class CompletedCacheGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "m28610658t16r1"
        for part in ("r/opt-artifacts", "e", "retained-dist"):
            (self.root / part).mkdir(parents=True)
        result = {
            "run_id": "38728610658", "variant": SCALING_VARIANT,
            "scaling_study": SCALING_STUDY, "build_jobs": 16, "build_affinity_count": 16,
            "complete": True, "full_distribution": True, "rust_sha": RUST, "attempt": "1",
            "runner_name": "MARCPE-D4-Arm64", "runner_class": "self-hosted-arm64",
            "paths": {"source": str(self.root / "r")},
        }
        save(self.root / "e/result.json", result)
        archive = self.root / "retained-dist/rustc.tar.xz"
        archive.write_bytes(b"archive")
        save(self.root / "e/dist-manifest.json",
             [{"name": archive.name, "bytes": 7, "sha256": digest(archive)}])
        profiles = {}
        for name in ("rustc", "rustdoc", "clippy", "llvm"):
            path = self.root / "r/opt-artifacts" / f"{name}-pgo.profdata"
            path.write_bytes(b"profile")
            profiles[path.name] = digest(path)
        save(self.root / "e/profiles.json", profiles)

    def test_qualified_cell_is_accepted_without_mutation(self):
        before = digest(self.root / "e/result.json")
        self.assertEqual(verify_cell(self.root, "38728610658", 16), before)
        self.assertTrue((self.root / "retained-dist/rustc.tar.xz").is_file())

    def test_x64_requires_explicit_machine_identity_and_cranelift_profile(self):
        path = self.root / "e/result.json"
        result = json.loads(path.read_text())
        result.update(runner_name="MARCPE-TEST01-X64", runner_class="self-hosted-x64")
        save(path, result)
        with self.assertRaisesRegex(RuntimeError, "completed"):
            verify_cell(self.root, "38728610658", 16)
        with self.assertRaisesRegex(RuntimeError, "profile manifest"):
            verify_cell(self.root, "38728610658", 16, machine="self-hosted-x64")
        profile = self.root / "r/opt-artifacts/cranelift-pgo.profdata"
        profile.write_bytes(b"cranelift profile")
        manifest = self.root / "e/profiles.json"
        profiles = json.loads(manifest.read_text())
        profiles[profile.name] = digest(profile)
        save(manifest, profiles)
        self.assertEqual(verify_cell(self.root, "38728610658", 16,
                                     machine="self-hosted-x64"), digest(path))
        profile.write_bytes(b"changed")
        with self.assertRaisesRegex(RuntimeError, "profile identity"):
            verify_cell(self.root, "38728610658", 16, machine="self-hosted-x64")

    def test_machine_mismatch_or_unsupported_machine_blocks_verification(self):
        with self.assertRaisesRegex(RuntimeError, "completed"):
            verify_cell(self.root, "38728610658", 16, machine="self-hosted-x64")
        with self.assertRaisesRegex(RuntimeError, "Unsupported"):
            verify_cell(self.root, "38728610658", 16, machine="self-hosted-arm64-highcore")

    @unittest.skipUnless(os.name == "nt", "Native Windows runner selection")
    def test_space_preparation_selects_only_the_explicit_machine_and_control(self):
        for machine, runner, root, run_id, cores in (
                ("arm64", "MARCPE-D4-Arm64", r"D:\m28610658t16r1", "38728610658", 16),
                ("x64", "MARCPE-TEST01-X64", r"E:\m69758791t4r1", "38869758791", 4)):
            with self.subTest(machine=machine), \
                    patch("sys.argv", ["prepare", "--machine", machine]), \
                    patch.dict(os.environ, RUNNER_NAME=runner, RUNNER_ENVIRONMENT="self-hosted",
                               RUNNER_TEMP=self.temp.name, GITHUB_RUN_ID="123"), \
                    patch.object(space.shutil, "disk_usage", return_value=SimpleNamespace(free=0)), \
                    patch.object(space, "verify_cell", side_effect=RuntimeError("guard reached")) as verify, \
                    patch.object(space, "preserve_cache") as preserve:
                with self.assertRaisesRegex(RuntimeError, "guard reached"):
                    space.main()
                verify.assert_called_once_with(Path(root), run_id, cores, SCALING_VARIANT,
                                               machine=f"self-hosted-{machine}")
                preserve.assert_not_called()

    def test_incomplete_result_blocks_cache_relocation(self):
        path = self.root / "e/result.json"
        result = json.loads(path.read_text())
        result["complete"] = False
        save(path, result)
        with self.assertRaisesRegex(RuntimeError, "completed"):
            verify_cell(self.root, "38728610658", 16)

    def test_changed_archive_profile_or_remaining_build_is_rejected(self):
        for relative in ("retained-dist/rustc.tar.xz", "r/opt-artifacts/llvm-pgo.profdata"):
            with self.subTest(path=relative):
                path = self.root / relative
                original = path.read_bytes()
                path.write_bytes(b"modified")
                with self.assertRaises(RuntimeError):
                    verify_cell(self.root, "38728610658", 16)
                path.write_bytes(original)
        (self.root / "r/build").mkdir()
        with self.assertRaisesRegex(RuntimeError, "reclaimed"):
            verify_cell(self.root, "38728610658", 16)

    def test_previous_partial_relocation_is_resumed_without_a_new_copy(self):
        cache = self.root / "e/cargo-home"
        cache.mkdir()
        (cache / "payload").write_bytes(b"preserved")
        retained = Path(self.temp.name) / "retained"
        retained.mkdir()
        stem = f"{self.root.name}-cargo"
        with patch.object(recovery.shutil, "rmtree", side_effect=PermissionError("read-only")):
            with self.assertRaises(PermissionError):
                preserve_cache(cache, retained, stem, "1")
        with patch.object(recovery.shutil, "copytree") as copy:
            destination = preserve_cache(cache, retained, stem, "2")
            copy.assert_not_called()
        self.assertEqual(destination.name, f"{stem}-1")
        self.assertEqual((destination / "cache/payload").read_bytes(), b"preserved")
        self.assertFalse(cache.exists())
        self.assertEqual(preserve_cache(cache, retained, stem, "3"), destination)
        verify_cell(self.root, "38728610658", 16)

    def test_ambiguous_receipts_do_not_remove_cache(self):
        cache = self.root / "e/cargo-home"
        cache.mkdir()
        retained = Path(self.temp.name) / "retained"
        stem = f"{self.root.name}-cargo"
        for run_id in ("1", "2"):
            previous = retained / f"{stem}-{run_id}"
            previous.mkdir(parents=True)
            save(previous / "relocation.json", {})
        with self.assertRaisesRegex(RuntimeError, "Ambiguous"):
            preserve_cache(cache, retained, stem, "3")
        self.assertTrue(cache.exists())

    def test_cleanup_removes_only_qualified_caches_and_records_disposal(self):
        cache = self.root / "e/cargo-home"
        cache.mkdir()
        (cache / "payload").write_bytes(b"obsolete")
        training = self.root / "r/opt-artifacts/rustc-perf"
        training.mkdir()
        (training / "payload").write_bytes(b"obsolete training")
        retained = Path(self.temp.name) / "retained"
        retained.mkdir()
        cleanup_cell(self.root, "38728610658", 16, retained)
        self.assertFalse(cache.exists())
        self.assertFalse(training.exists())
        self.assertTrue(cache_disposal_complete(self.root, "cargo"))
        self.assertTrue(cache_disposal_complete(self.root, "training"))
        verify_cell(self.root, "38728610658", 16)
        results = cleanup_cell(self.root, "38728610658", 16, retained)
        self.assertEqual([row["status"] for row in results], ["already-disposed", "already-disposed"])
        cache.mkdir()
        with self.assertRaisesRegex(RuntimeError, "disposal receipt"):
            cache_disposal_complete(self.root, "cargo")

    def test_cleanup_validates_and_removes_relocated_cache_not_receipts(self):
        cache = self.root / "e/cargo-home"
        cache.mkdir()
        (cache / "payload").write_bytes(b"obsolete")
        retained = Path(self.temp.name) / "retained"
        retained.mkdir()
        destination = preserve_cache(cache, retained, f"{self.root.name}-cargo", "1")
        cleanup_cell(self.root, "38728610658", 16, retained)
        self.assertFalse((destination / "cache").exists())
        self.assertTrue((destination / "relocation.json").is_file())
        self.assertTrue(cache_disposal_complete(self.root, "cargo"))
        verify_cell(self.root, "38728610658", 16)

    def test_cleanup_rejects_unqualified_cell_before_removing_cache(self):
        cache = self.root / "e/cargo-home"
        cache.mkdir()
        path = self.root / "e/result.json"
        result = json.loads(path.read_text())
        result["complete"] = False
        save(path, result)
        with self.assertRaisesRegex(RuntimeError, "completed"):
            cleanup_cell(self.root, "38728610658", 16, Path(self.temp.name))
        self.assertTrue(cache.exists())

    def test_cleanup_rejects_changed_retained_cache(self):
        cache = self.root / "e/cargo-home"
        cache.mkdir()
        (cache / "payload").write_bytes(b"obsolete")
        retained = Path(self.temp.name) / "retained"
        retained.mkdir()
        destination = preserve_cache(cache, retained, f"{self.root.name}-cargo", "1")
        (destination / "cache/payload").write_bytes(b"unexpected change")
        with self.assertRaisesRegex(RuntimeError, "no longer matches"):
            cleanup_cell(self.root, "38728610658", 16, retained)
        self.assertTrue((destination / "cache/payload").exists())

    def test_cleanup_rejects_external_symlink_without_deleting_its_target(self):
        cache = self.root / "e/cargo-home"
        cache.mkdir()
        outside = self.root / "e/result.json"
        (cache / "outside").symlink_to(outside)
        retained = Path(self.temp.name) / "retained"
        retained.mkdir()
        with self.assertRaisesRegex(RuntimeError, "leaves retained tree"):
            cleanup_cell(self.root, "38728610658", 16, retained)
        self.assertTrue(outside.exists())
        self.assertTrue(cache.exists())

    def configure_additional_cell(self, name, run_id, cores, variant):
        renamed = self.root.parent / name
        self.root.rename(renamed)
        self.root = renamed
        path = self.root / "e/result.json"
        result = json.loads(path.read_text())
        result.update(run_id=run_id, variant=variant, build_jobs=cores,
                      build_affinity_count=cores, vm=1, paths={"source": str(self.root / "r")})
        if variant != SCALING_VARIANT:
            result.pop("scaling_study")
        save(path, result)
        cache = self.root / "e/cargo-home"
        cache.mkdir()
        (cache / "payload").write_bytes(b"obsolete")
        retained = Path(self.temp.name) / "retained"
        retained.mkdir()
        return cache, retained

    def test_additional_microsoft_pilot_cache_requires_its_exact_recipe(self):
        cache, retained = self.configure_additional_cell(
            "m32798400m1", "38532798400", 4, "msvc-pgo")
        with self.assertRaisesRegex(RuntimeError, "completed"):
            cleanup_cell(self.root, "38532798400", 4, retained)
        self.assertTrue(cache.exists())
        cleanup_cell(self.root, "38532798400", 4, retained, "msvc-pgo")
        self.assertFalse(cache.exists())
        verify_cell(self.root, "38532798400", 4, "msvc-pgo")

    def test_additional_llvm_pilot_cache_preserves_qualified_evidence(self):
        cache, retained = self.configure_additional_cell(
            "m42164879l1", "38542164879", 4, "llvm-pgo-thin")
        cleanup_cell(self.root, "38542164879", 4, retained, "llvm-pgo-thin")
        self.assertFalse(cache.exists())
        verify_cell(self.root, "38542164879", 4, "llvm-pgo-thin")

    def test_additional_eight_cpu_cache_preserves_qualified_evidence(self):
        cache, retained = self.configure_additional_cell(
            "m73093226t8r1", "38873093226", 8, SCALING_VARIANT)
        cleanup_cell(self.root, "38873093226", 8, retained)
        self.assertFalse(cache.exists())
        verify_cell(self.root, "38873093226", 8)


if __name__ == "__main__":
    unittest.main()
