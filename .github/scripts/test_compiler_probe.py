import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from compiler_probe import replay_arguments, select_yuv, validate_meter
from process_metrics import measure


class CompilerProbeTests(unittest.TestCase):
    def test_meter_cpu_descendants_and_sleep(self):
        with tempfile.TemporaryDirectory() as directory:
            validate_meter(Path(directory) / "validation")
            result = json.loads((Path(directory) / "validation" / "self-test.json").read_text())
            self.assertGreater(result["busy_descendant"]["cpu_seconds"], 0.25)

    def test_failure_is_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            row = measure([sys.executable, "-c", "raise SystemExit(17)"],
                          Path(directory), dict(os.environ), 1, Path(directory) / "failed")
            self.assertEqual(row["exit_code"], 17)

    def test_replay_changes_only_output_and_emission(self):
        original = ["rustc", "--crate-name", "yuv", "lib.rs", "--crate-type", "lib",
                    "--emit=dep-info,metadata,link", "--out-dir", "old",
                    "-C", "codegen-units=16", "--extern", "other=dep.rlib"]
        args = replay_arguments(original, Path("new"), "metadata")
        self.assertIn("--emit=metadata", args)
        self.assertEqual(args[args.index("--out-dir") + 1], "new")
        self.assertIn("other=dep.rlib", args)
        self.assertIn("--emit=dep-info,metadata,link", original)
        self.assertIn("--emit=metadata,link", replay_arguments(original, Path("new"), "codegen"))

    def test_selection_rejects_ambiguous_or_missing_unit(self):
        unit = {"argv": ["rustc", "--crate-name", "yuv", "--out-dir", "target"]}
        self.assertEqual(select_yuv([unit]), unit)
        for rows in ([], [unit, unit]):
            with self.assertRaises(RuntimeError):
                select_yuv(rows)

    @unittest.skipUnless(os.environ.get("COMPILER_METER"), "native meter is built on runners")
    def test_native_wrapper_counts_self_not_descendant_cpu(self):
        with tempfile.TemporaryDirectory() as directory:
            burn = "import time;t=time.process_time();\nwhile time.process_time()-t<0.4: pass"
            parent = f"import subprocess,sys;subprocess.run([sys.executable,'-c',{burn!r}],check=True)"
            subprocess.run(
                [os.environ["COMPILER_METER"], sys.executable, "-c", parent], check=True,
                env={**os.environ, "RUST_METRICS_DIR": directory},
            )
            row = json.loads(next(Path(directory).glob("*.json")).read_text())
            self.assertLess(row["user_seconds"] + row["kernel_seconds"], 0.25)


if __name__ == "__main__":
    unittest.main()
