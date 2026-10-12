import ctypes
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from process_metrics import measure, measurement_session


@unittest.skipUnless(os.name == "nt", "Windows process paths and Job Objects")
class WindowsMeasurementTests(unittest.TestCase):
    def short_python(self):
        buffer = ctypes.create_unicode_buffer(32768)
        size = ctypes.windll.kernel32.GetShortPathNameW(str(Path(sys.executable).resolve()), buffer, len(buffer))
        if not size or size >= len(buffer):
            raise ctypes.WinError()
        return buffer.value

    def test_short_path_child_matches_exact_approved_executable(self):
        short = self.short_python()
        if os.path.normcase(short) == os.path.normcase(str(Path(sys.executable).resolve())):
            self.skipTest("Python executable has no distinct 8.3 path")
        with tempfile.TemporaryDirectory() as tmp, measurement_session([sys.executable]) as session:
            command = [sys.executable, "-c",
                       f"import subprocess; subprocess.Popen([{short!r}, '-c', 'import time; time.sleep(30)'])"]
            result = measure(command, tmp, dict(os.environ), 1, Path(tmp) / "approved",
                             session=session, timeout=10)
            self.assertEqual(result["exit_code"], 0)
            self.assertGreater(result["peak_job_memory_bytes"], 0)
            self.assertGreater(result["peak_process_memory_bytes"], 0)
            self.assertTrue(result["background_processes_at_completion"])
            self.assertTrue(any(
                os.path.normcase(row["image"]) != os.path.normcase(str(Path(row["image"]).resolve()))
                for row in result["background_processes_at_completion"]
            ))
            self.assertEqual(
                os.path.normcase(str(Path(short).resolve())),
                os.path.normcase(str(Path(sys.executable).resolve())),
            )

    def test_unapproved_descendant_still_fails(self):
        with tempfile.TemporaryDirectory() as tmp, measurement_session([]) as session:
            command = [sys.executable, "-c",
                       f"import subprocess; subprocess.Popen([{sys.executable!r}, '-c', 'import time; time.sleep(30)'])"]
            with self.assertRaisesRegex(RuntimeError, "left running descendants"):
                measure(command, tmp, dict(os.environ), 1, Path(tmp) / "unapproved",
                        session=session, timeout=10)

    def test_workflow_root_names_remain_distinct_after_expression_rendering(self):
        workflow = Path(__file__).parents[1] / "workflows" / "matched-release.yml"
        line = next(line.strip() for line in workflow.read_text().splitlines()
                    if '$name = "m$' in line)
        script = "$env:GITHUB_RUN_ID='38231778023';"
        for variant in ("b", "m", "l"):
            for vm in (1, 2, 3):
                rendered = line.replace("${{ matrix.vm }}", str(vm))
                script += f"$variantCode='{variant}'; {rendered}; Write-Output $name;"
        result = subprocess.check_output(["powershell", "-NoProfile", "-Command", script], text=True)
        self.assertEqual(result.splitlines(),
                         [f"m31778023{variant}{vm}" for variant in ("b", "m", "l") for vm in (1, 2, 3)])


if __name__ == "__main__":
    unittest.main()
