import hashlib
import json
import os
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch
import zipfile

from arm_ab_probe import extract_compiler
from install_optimized_rust import check_hash, install
from native_ci_probe import COMMANDS, PROFILE_ENV, build_environment, paired_order
from offline_benchmark import NATIVE_COMMANDS, COMMON_COMMAND, WASM_COMMAND
from process_metrics import measure, measurement_session


class NativeCiTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Windows persistent descendant validation")
    def test_shared_job_rejects_unapproved_persistent_child(self):
        parent = "import subprocess,sys;subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'])"
        with tempfile.TemporaryDirectory() as tmp, measurement_session() as session:
            with self.assertRaisesRegex(RuntimeError, "left running descendants"):
                measure([sys.executable, "-c", parent], Path(tmp), dict(os.environ), 1,
                        Path(tmp) / "unexpected", session=session)

    @unittest.skipUnless(os.name == "nt", "Windows shared Job Object accounting")
    def test_shared_job_counts_active_helper_cpu_without_waiting_for_its_lifetime(self):
        worker = (
            "import time;from pathlib import Path\n"
            "while not Path('start').exists(): time.sleep(0.01)\n"
            "t=time.process_time()\nwhile time.process_time()-t<0.3: pass\n"
            "Path('done').touch()\ntime.sleep(30)"
        )
        trigger = (
            "import time;from pathlib import Path\nPath('start').touch()\n"
            "while not Path('done').exists(): time.sleep(0.01)"
        )
        parent = f"import subprocess,sys;subprocess.Popen([sys.executable,'-c',{worker!r}])"
        with tempfile.TemporaryDirectory() as tmp, measurement_session([sys.executable]) as session:
            root, env = Path(tmp), dict(os.environ)
            first = measure([sys.executable, "-c", parent], root, env, 1, root / "first", session=session)
            self.assertTrue(first["background_processes_at_completion"])
            second = measure([sys.executable, "-c", trigger],
                             root, env, 1, root / "second", session=session, timeout=10)
            self.assertGreaterEqual(second["cpu_seconds"], 0.25)
            self.assertEqual(second["processes"], 1)
            with self.assertRaisesRegex(RuntimeError, "Cannot change affinity"):
                measure([sys.executable, "-c", "pass"], root, env, 2, root / "wrong", session=session)

    def test_correctness_timeout_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp, measurement_session() as session:
            import subprocess
            with self.assertRaises(subprocess.TimeoutExpired):
                measure([sys.executable, "-c", "import time;time.sleep(30)"],
                        Path(tmp), dict(os.environ), 1, Path(tmp) / "timeout", session=session, timeout=0.1)

    @unittest.skipUnless(os.name == "nt", "Windows Job Object shutdown accounting")
    def test_cpu_meter_waits_for_short_lived_descendants(self):
        burn = "import time;t=time.process_time();\nwhile time.process_time()-t<0.3: pass"
        parent = f"import subprocess,sys;subprocess.Popen([sys.executable,'-c',{burn!r}])"
        with tempfile.TemporaryDirectory() as tmp:
            row = measure([sys.executable, "-c", parent], Path(tmp), dict(os.environ), 1, Path(tmp) / "late-child")
            self.assertEqual(row["exit_code"], 0)
            self.assertGreaterEqual(row["cpu_seconds"], 0.25)
            self.assertGreater(row["wall_seconds"], row["root_process_wall_seconds"])

    def test_exact_original_commands_and_profiles(self):
        self.assertEqual(COMMANDS, [*NATIVE_COMMANDS, ("common", COMMON_COMMAND), ("wasm", WASM_COMMAND)])
        self.assertEqual(len(COMMANDS), 7)
        env = build_environment({"GH_TOKEN": "fixture", "PATH": "path"}, Path("compiler"))
        self.assertNotIn("GH_TOKEN", env)
        self.assertEqual({k: env[k] for k in PROFILE_ENV}, PROFILE_ENV)
        self.assertFalse(any("OPT_LEVEL" in k or "CODEGEN_UNITS" in k for k in env))
        for key in ("CARGO_PROFILE_TEST_DEBUG", "CARGO_PROFILE_DEV_CODEGEN_UNITS", "RUSTFLAGS", "RUSTC_WRAPPER", "RUSTC"):
            with self.assertRaises(RuntimeError):
                build_environment({key: "unexpected"}, Path("compiler"))

    def test_two_variant_order_reverses_each_round(self):
        variants = ["official", "optimized"]
        for vm in range(1, 6):
            self.assertNotEqual(paired_order(variants, vm, 1), paired_order(variants, vm, 2))
            self.assertEqual(paired_order(variants, vm, 1), paired_order(variants, vm, 3))
            self.assertEqual(paired_order(["official"], vm, 0), ["official"])
        self.assertEqual(variants, ["official", "optimized"])

    def test_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "artifact"
            path.write_bytes(b"original")
            check_hash(path, hashlib.sha256(b"original").hexdigest())
            with self.assertRaisesRegex(RuntimeError, "Checksum mismatch"):
                check_hash(path, "wrong")

    def test_archive_paths_checked_before_extraction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "fixture.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("bin/rustc.exe", b"fixture")
                z.writestr("../escape", b"bad")
            with self.assertRaisesRegex(RuntimeError, "unsafe path"):
                extract_compiler(archive, root / "output")
            self.assertFalse((root / "output").exists())
            self.assertFalse((root / "escape").exists())

    def test_failed_install_is_atomic_and_existing_install_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "installed"
            manifest = {"repository": "owner/repo", "release": "release", "metadata_sha256": "hash"}
            with patch("install_optimized_rust.download", side_effect=RuntimeError("download failed")):
                with self.assertRaisesRegex(RuntimeError, "download failed"):
                    install(destination, manifest, Path("official"))
            self.assertFalse(destination.exists())
            destination.mkdir()
            (destination / "optimized.json").write_text(json.dumps({"old": True}))
            with self.assertRaisesRegex(RuntimeError, "Checksum mismatch"):
                install(destination, manifest, Path("official"))
            self.assertEqual(json.loads((destination / "optimized.json").read_text()), {"old": True})


if __name__ == "__main__":
    unittest.main()
