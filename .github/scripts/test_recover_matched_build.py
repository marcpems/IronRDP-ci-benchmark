import json
from pathlib import Path
import tempfile
import unittest

from build_arm_compilers import digest, save
from matched_release import RUST, SCALING_STUDY, SCALING_VARIANT
from recover_matched_build import recover


class RecoveryTests(unittest.TestCase):
    def fixture(self, parent, scaling_cores=None):
        root = Path(parent) / ("m82254692b1" if scaling_cores is None else f"m82254692t{scaling_cores}r1")
        dist = root / "r" / "build" / "dist"
        dist.mkdir(parents=True)
        (dist / "rustc.tar.xz").write_bytes(b"archive")
        (root / "r" / "build" / "metrics.json").write_text("{}")
        (root / "r" / "opt-artifacts").mkdir()
        (root / "r" / "opt-artifacts" / "rustc.profdata").write_bytes(b"profile")
        evidence = root / "e"
        evidence.mkdir()
        save(evidence / "result.json", {
            "complete": True, "full_distribution": True, "rust_sha": RUST,
            "runner_class": "self-hosted-arm64-highcore", "runner_name": "GB300-Arm64",
            "run_id": "38282254692", "variant": "baseline" if scaling_cores is None else SCALING_VARIANT,
            "vm": 1, "attempt": "1",
            "paths": {"source": str(root / "r")},
            **({"scaling_study": SCALING_STUDY, "build_jobs": scaling_cores,
                "build_affinity_count": scaling_cores} if scaling_cores is not None else {}),
        })
        save(evidence / "dist-manifest.json", [{
            "name": "rustc.tar.xz", "bytes": 7, "sha256": digest(dist / "rustc.tar.xz"),
        }])
        return root

    def test_scaling_recovery_requires_matching_explicit_cpu_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(tmp, scaling_cores=32)
            for wrong in (None, 4, 64):
                with self.subTest(wrong=wrong), self.assertRaises(RuntimeError):
                    recover(root, "self-hosted-arm64-highcore", "38282254692", SCALING_VARIANT, 1, wrong)
                self.assertTrue((root / "r" / "build" / "dist").is_dir())
            recover(root, "self-hosted-arm64-highcore", "38282254692", SCALING_VARIANT, 1, 32)
            self.assertTrue((root / "retained-dist" / "rustc.tar.xz").is_file())

    def test_preserves_archives_evidence_profiles_and_supports_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixture(tmp)
            for _ in range(2):
                recover(root, "self-hosted-arm64-highcore", "38282254692", "baseline", 1)
                self.assertFalse((root / "r" / "build").exists())
                self.assertEqual((root / "retained-dist" / "rustc.tar.xz").read_bytes(), b"archive")
                self.assertTrue((root / "e" / "build-metrics-before-cleanup.json").is_file())
                self.assertTrue((root / "r" / "opt-artifacts" / "rustc.profdata").is_file())
                self.assertTrue(json.loads((root / "e" / "space-recovery.json").read_text())["complete"])

    def test_bad_archive_and_unqualified_result_prevent_deletion(self):
        for invalid in ("archive", "qualification", "runner", "extra-file"):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as tmp:
                root = self.fixture(tmp)
                dist = root / "r" / "build" / "dist"
                if invalid == "archive":
                    (dist / "rustc.tar.xz").write_bytes(b"corrupt")
                elif invalid == "extra-file":
                    (dist / "unexpected").write_bytes(b"keep")
                else:
                    path = root / "e" / "result.json"
                    result = json.loads(path.read_text())
                    result["complete" if invalid == "qualification" else "runner_name"] = False
                    save(path, result)
                with self.assertRaises(RuntimeError):
                    recover(root, "self-hosted-arm64-highcore", "38282254692", "baseline", 1)
                self.assertTrue(dist.is_dir())


if __name__ == "__main__":
    unittest.main()
