import json
from pathlib import Path
import shutil
import tempfile
import tomllib
import unittest

from arm_ab_probe import variant_order, verify_custom, verify_shared_stdlib
from build_arm_compilers import configuration, digest, excluded_sysroot_entries, HOST, OFFICIAL_STD, RUST_SHA


class ArmAbTests(unittest.TestCase):
    def test_order_is_deterministic_and_rotates_positions(self):
        variants = ["official", "baseline-msvc", "baseline-lld", "optimized"]
        for vm in range(1, 6):
            for round_index in range(4):
                order = variant_order(variants, vm, round_index)
                self.assertCountEqual(order, variants)
                self.assertEqual(order, variant_order(variants, vm, round_index))
        self.assertEqual(
            {variant_order(variants, vm, 0)[0] for vm in range(1, 5)}, set(variants),
        )

    def test_configs_hold_codegen_units_and_linkage_constant(self):
        root, msvc = Path("D:\\experiment"), Path("D:\\msvc")
        configs = {
            v: tomllib.loads(configuration(root, msvc, v, 8)[1])
            for v in ("baseline-msvc", "baseline-lld", "optimized")
        }
        for config in configs.values():
            self.assertNotIn("codegen-units", config["rust"])
            self.assertFalse(config["llvm"]["link-shared"])
            self.assertEqual(config["rust"]["codegen-units-std"], 1)
        a, b, c = (configs[v] for v in ("baseline-msvc", "baseline-lld", "optimized"))
        self.assertEqual(a["llvm"], b["llvm"])
        self.assertEqual(a["rust"], b["rust"])
        self.assertNotEqual(a["target"][HOST]["linker"], b["target"][HOST]["linker"])
        self.assertEqual(b["target"], c["target"])
        self.assertTrue(c["llvm"]["thin-lto"])
        self.assertEqual(c["rust"]["lto"], "thin")
        self.assertNotIn("use-linker", c["llvm"])

    def test_custom_compiler_verification_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "optimized" / "bin" / "rustc.exe"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"fixture")
            manifest = {"variant": "optimized", "rust_sha": RUST_SHA,
                        "evaluation_stdlib_sha256": OFFICIAL_STD,
                        "files": {"bin/rustc.exe": digest(path)}}
            (root / "optimized.json").write_text(json.dumps(manifest))
            protocol = {"rust_sha": RUST_SHA, "evaluation_stdlib_sha256": OFFICIAL_STD}
            self.assertEqual(verify_custom(root, "optimized", protocol), path)
            path.write_bytes(b"modified")
            with self.assertRaises(RuntimeError):
                verify_custom(root, "optimized", protocol)

    def test_packaging_excludes_build_tree_source_links(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "stage2"
            for name in ("src", "rustc-src", "aarch64-pc-windows-msvc"):
                directory = source / "lib" / "rustlib" / name
                directory.mkdir(parents=True)
                (directory / "fixture").write_text("fixture")
            destination = root / "package"
            shutil.copytree(
                source, destination,
                ignore=lambda directory, names: excluded_sysroot_entries(source, directory, names),
            )
            self.assertFalse((destination / "lib" / "rustlib" / "src").exists())
            self.assertFalse((destination / "lib" / "rustlib" / "rustc-src").exists())
            self.assertTrue((destination / "lib" / "rustlib" / "aarch64-pc-windows-msvc" / "fixture").is_file())

    def test_official_standard_libraries_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            files = {}
            for target in (HOST, "wasm32-unknown-unknown"):
                relative = f"lib/rustlib/{target}/lib/libstd-fixture.rlib"
                path = root.joinpath(*relative.split("/"))
                path.parent.mkdir(parents=True)
                path.write_bytes(target.encode())
                files[relative] = digest(path)
            verify_shared_stdlib(root / "bin" / "rustc.exe", {"files": files}, HOST)
            path.write_bytes(b"changed")
            with self.assertRaisesRegex(RuntimeError, "standard libraries differ"):
                verify_shared_stdlib(root / "bin" / "rustc.exe", {"files": files}, HOST)


if __name__ == "__main__":
    unittest.main()
