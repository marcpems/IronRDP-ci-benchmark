import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from process_metrics import measure
from x64_runner_diagnostic import filesystem_probe, topology
from x64_instrumented_compiler_probe import RELATIVE_BIN, verify_retained_compiler
import x64_instrumented_compiler_probe as compiler_probe
from build_arm_compilers import digest, save


@unittest.skipUnless(os.name == "nt", "Native Windows diagnostics")
class X64DiagnosticTests(unittest.TestCase):
    def test_retained_compiler_requires_exact_receipt_and_unchanged_driver(self):
        with tempfile.TemporaryDirectory() as name:
            retained = Path(name)
            build = retained / "build"
            binary = build / RELATIVE_BIN
            binary.mkdir(parents=True)
            compiler, driver = binary / "rustc.exe", binary / "rustc_driver-test.dll"
            compiler.write_bytes(b"compiler")
            driver.write_bytes(b"driver")
            record = {
                "complete": True,
                "source": r"E:\m16997224t4r1\r\build", "destination": str(build),
                "files": [{"path": str(path.relative_to(build)), "bytes": path.stat().st_size,
                           "sha256": digest(path)} for path in (compiler, driver)],
            }
            save(retained / "relocation.json", record)
            with patch.object(compiler_probe, "RECEIPT_SHA256", digest(retained / "relocation.json")):
                self.assertEqual(verify_retained_compiler(retained), compiler)
                driver.write_bytes(b"changed")
                with self.assertRaisesRegex(RuntimeError, "no longer matches"):
                    verify_retained_compiler(retained)
                record["source"] = r"E:\another-build"
                save(retained / "relocation.json", record)
                with self.assertRaisesRegex(RuntimeError, "receipt differs"):
                    verify_retained_compiler(retained)

    def test_topology_masks_are_disjoint_and_nonempty(self):
        cores = topology()
        self.assertTrue(cores)
        logical = [cpu for core in cores for cpu in core]
        self.assertTrue(all(cores))
        self.assertEqual(len(logical), len(set(logical)))

    def test_worker_cpu_is_included_in_job_accounting(self):
        with tempfile.TemporaryDirectory() as name:
            prefix = Path(name) / "cpu"
            result = measure([sys.executable, str(Path(__file__).with_name("x64_runner_diagnostic.py")),
                              "--load", "4", "--seconds", "1"], Path.cwd(), os.environ.copy(),
                             4, prefix, timeout=60)
            self.assertEqual(result["exit_code"], 0)
            output = json.loads(prefix.with_suffix(".stdout").read_text())
            self.assertEqual(len(output["workers"]), 4)
            self.assertTrue(all(row["work_units"] > 0 for row in output["workers"]))
            self.assertGreater(result["cpu_seconds"], 0)
            self.assertLessEqual(sum(row["cpu_seconds"] for row in output["workers"]),
                                 result["cpu_seconds"] + 0.2)
            self.assertEqual(result["affinity"], [0, 1, 2, 3])

    def test_filesystem_probe_verifies_payloads_and_removes_only_its_own_trees(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            unrelated = root / "keep"
            unrelated.write_text("unchanged")
            output = root / "report.json"
            filesystem_probe(str(root), output)
            rows = json.loads(output.read_text())
            self.assertEqual([row["bytes"] for row in rows],
                             [1024 * 4096] * 2 + [16 * 4 * 1024 * 1024] * 2)
            self.assertEqual([row["fsync_per_file"] for row in rows], [False, True, False, True])
            self.assertEqual(unrelated.read_text(), "unchanged")
            self.assertEqual({path.name for path in root.iterdir()}, {"keep", "report.json"})


if __name__ == "__main__":
    unittest.main()
