import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from build_arm_compilers import digest, save
from x64_profile_only import profile_arguments, verify_training_input
from x64_profile_train import stop_after_training


class NewReleaseProfileTests(unittest.TestCase):
    def test_new_profile_interface_keeps_cargo_and_rustdoc_controlled(self):
        profiles = {name: Path(f"D:/profile inputs/{name}.profdata") for name in ("rustc", "llvm", "rustdoc")}
        arguments = profile_arguments(profiles)
        settings = dict(item.split("=", 1) for item in arguments[1::2])
        self.assertEqual(arguments[::2], ["--set"] * 4)
        self.assertEqual(settings["pgo.cargo.use"], settings["pgo.rustc.use"])
        self.assertEqual(settings["pgo.rustdoc.use"], '"D:/profile inputs/rustdoc.profdata"')
        self.assertEqual(settings["pgo.llvm.use"], '"D:/profile inputs/llvm.profdata"')
        self.assertEqual(profile_arguments({"rustc": Path("r"), "llvm": Path("l")}),
                         ["--rust-profile-use", Path("r"), "--llvm-profile-use", Path("l")])

    def test_training_boundary_rejects_repeated_or_changed_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            main = root / "src/tools/opt-dist/src/main.rs"
            main.parent.mkdir(parents=True)
            main.write_text("    let bolt_profiles = if env.use_bolt() {\n")
            stop_after_training(root)
            self.assertIn("return Ok(());", main.read_text())
            with self.assertRaisesRegex(RuntimeError, "boundary changed"):
                stop_after_training(root)

    def test_frozen_training_rejects_relabelled_or_changed_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tools = {"msvc": "version", "sdk": "version", "files": {"link.exe": {"sha256": "link"}}}
            template = {"rust_version": "1.99.1", "llvm_profile_sha256": {"official": "official", "repaired": None}}
            training = {"complete": True, "run_id": "run", "attempt": "1", "protocol": template,
                        "tools": tools, "profiles": {"llvm": {"sha256": "trained"}},
                        "llvm_coverage": {name: {"active_functions": 1}
                                          for name in ("X86TargetLowering", "InstCombine")}}
            save(root / "provenance.json", {"source": "pinned"})
            save(root / "result.json", training)
            frozen = copy.deepcopy(template)
            frozen["llvm_profile_sha256"]["repaired"] = "trained"
            frozen["training_identity"] = {"run_id": "run", "attempt": "1",
                                           "provenance_sha256": digest(root / "provenance.json")}
            with patch.dict("os.environ", {"GITHUB_RUN_ID": "run", "GITHUB_RUN_ATTEMPT": "1"}):
                verify_training_input(root, frozen, tools)
                changed = copy.deepcopy(frozen)
                changed["rust_version"] = "1.94.1"
                with self.assertRaisesRegex(RuntimeError, "protocol changed"):
                    verify_training_input(root, changed, tools)
                changed = copy.deepcopy(frozen)
                changed["training_identity"]["attempt"] = "2"
                with self.assertRaisesRegex(RuntimeError, "identity"):
                    verify_training_input(root, changed, tools)
                training["llvm_coverage"]["InstCombine"]["active_functions"] = 0
                save(root / "result.json", training)
                with self.assertRaisesRegex(RuntimeError, "backend coverage"):
                    verify_training_input(root, frozen, tools)
