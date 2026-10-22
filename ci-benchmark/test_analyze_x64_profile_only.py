import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from analyze_x64_profile_only import analyze


class ProfileOnlyAnalysisTests(unittest.TestCase):
    def test_rust1991_evidence_reproduces_result_and_rejects_changed_training(self):
        folder = Path(__file__).parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with zipfile.ZipFile(folder / "x64-profile-1991-evidence.zip") as archive:
                archive.extractall(root)
            expected = json.loads((folder / "X64-PGO-1991.json").read_text())
            self.assertEqual(analyze(root, "1.99.1"), expected)
            with self.assertRaisesRegex(ValueError, "changed protocol/input pins"):
                analyze(root)
            training_path = root / "training/result.json"
            training = json.loads(training_path.read_text())
            training["profiles"]["llvm"]["sha256"] = "0" * 64
            training_path.write_text(json.dumps(training))
            with self.assertRaisesRegex(ValueError, "Changed frozen training evidence"):
                analyze(root, "1.99.1")

    def test_compact_evidence_reproduces_result_and_rejects_relabelled_inputs(self):
        folder = Path(__file__).parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with zipfile.ZipFile(folder / "x64-profile-only-evidence.zip") as archive:
                archive.extractall(root)
            expected = json.loads((folder / "X64-PROFILE-ONLY.json").read_text())
            self.assertEqual(analyze(root), expected)
            index_path = root / "replay/index.json"
            original = index_path.read_bytes()
            index = json.loads(original)
            index["attempt"] = "2"
            index_path.write_text(json.dumps(index))
            with self.assertRaisesRegex(ValueError, "Wrong replay attempt"):
                analyze(root)
            index_path.write_bytes(original)
            result_path = root / "builds/repaired/result.json"
            result = json.loads(result_path.read_text())
            result["configuration"] += "\n# changed toolchain settings\n"
            result_path.write_text(json.dumps(result))
            with self.assertRaisesRegex(ValueError, "Changed qualified compiler metadata"):
                analyze(root)


if __name__ == "__main__":
    unittest.main()
