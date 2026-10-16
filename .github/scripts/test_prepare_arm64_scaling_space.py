import json
from pathlib import Path
import tempfile
import unittest

from build_arm_compilers import digest, save
from matched_release import RUST, SCALING_STUDY, SCALING_VARIANT
from prepare_arm64_scaling_space import verify_cell


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


if __name__ == "__main__":
    unittest.main()
