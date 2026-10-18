import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import hosted_x64_baseline as hosted
from process_metrics import measure, measurement_session


class HostedBaselineTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value), encoding="utf-8")

    def test_timer_sections_retain_completed_and_censored_nested_phases(self):
        path = self.root / "fresh-pgo-full-dist.stderr"
        path.write_text(
            "[2026-10-11T20:45:56.149Z INFO  opt_dist::timer] Section `Stage 1` starts\n"
            "[2026-10-11T20:45:56.149Z INFO  opt_dist::timer] Section `Stage 1 > Build` starts\n"
            "[2026-10-11T22:30:31.623Z INFO  opt_dist::timer] Section `Stage 1 > Build` ended: OK (6275.47s)`\n"
            "[2026-10-11T22:30:31.623Z INFO  opt_dist::timer] Section `Stage 1 > Gather` starts\n",
            encoding="utf-8",
        )
        sections = hosted.timer_sections(path)
        self.assertEqual(sections["completed"][0]["wall_seconds"], 6275.47)
        self.assertEqual(sections["completed"][0]["status"], "OK")
        self.assertEqual([row["name"] for row in sections["unfinished"]], ["Stage 1", "Stage 1 > Gather"])

    def test_timeout_reports_censored_not_full_and_keeps_production_boundary(self):
        self.write("hosted-attempt.json", {"stop_reason": "error", "finished_unix": 1000})
        self.write("failure.json", {"error_type": "TimeoutExpired", "complete": False})
        self.write("production-start.json", {"started_unix": 100})
        summary = hosted.summarize(self.root, self.root)
        self.assertEqual(summary["status"], "censored-deadline")
        self.assertFalse(summary["complete"])
        self.assertIsNone(summary["full_release_wall_seconds"])
        self.assertEqual(summary["censored_production_elapsed_seconds"], 900)

    def test_qualification_failure_is_not_censored_or_full_even_if_distribution_finished(self):
        self.write("distribution-timing.json", {"wall_seconds": 123})
        self.write("failure.json", {"error_type": "RuntimeError", "complete": False})
        summary = hosted.summarize(self.root, self.root)
        self.assertEqual(summary["status"], "failed")
        self.assertFalse(summary["complete"])
        self.assertIsNone(summary["full_release_wall_seconds"])
        self.assertEqual(summary["production_finished_before_qualification"]["wall_seconds"], 123)

    def test_only_qualified_hosted_matched_results_are_full(self):
        result = {
            "complete": True, "qualification": "passed", "full_distribution": True,
            "hosted_baseline": hosted.release.HOSTED_BASELINE,
            "variant": hosted.release.SCALING_VARIANT, "rust_sha": hosted.release.RUST,
            "runner_class": "github-hosted",
        }
        self.write("distribution-timing.json", {"wall_seconds": 123})
        self.write("result.json", result)
        self.assertEqual(hosted.summarize(self.root, self.root)["full_release_wall_seconds"], 123)
        for field in result:
            changed = {key: value for key, value in result.items() if key != field}
            self.write("result.json", changed)
            self.assertFalse(hosted.summarize(self.root, self.root)["complete"], field)

    def test_outer_timeout_covers_preparation_and_preserves_failure_exit(self):
        with patch.dict(hosted.os.environ, {"RELEASE_JOB_STARTED": "100"}), \
                patch.object(hosted.release, "validate_runner"), \
                patch.object(hosted.release, "validate_recipe"), \
                patch.object(hosted.release, "hosted_baseline", return_value=True), \
                patch.object(hosted.release, "build_cores", return_value=4), \
                patch.object(hosted.time, "time", return_value=100 + 340 * 60), \
                patch.object(hosted, "sample_storage"), \
                patch.object(hosted, "execute", side_effect=subprocess.TimeoutExpired(["build"], 600)) as execute:
            self.assertEqual(hosted.run(self.root, self.root, self.root), 1)
            self.assertEqual(execute.call_args.kwargs["timeout"], 600)
            self.assertEqual(execute.call_args.kwargs["cores"], 4)
        summary = json.loads((self.root / "hosted-summary.json").read_text())
        self.assertEqual(summary["status"], "censored-deadline")
        self.assertFalse(summary["complete"])

    def test_missing_setup_evidence_is_failure_not_zero_time_success(self):
        summary = hosted.summarize(self.root, self.root)
        self.assertEqual(summary["status"], "failed")
        self.assertIsNone(summary["full_release_wall_seconds"])
        self.assertEqual(summary["production_sections"]["completed"], [])

    def test_interrupted_json_write_does_not_prevent_partial_summary(self):
        (self.root / "result.json").write_text('{"complete":', encoding="utf-8")
        self.write("build-opt-dist.json", {"wall_seconds": 10, "exit_code": 0, "affinity": [0, 1, 2, 3]})
        summary = hosted.summarize(self.root, self.root)
        self.assertFalse(summary["complete"])
        self.assertEqual(summary["unreadable_evidence"][0]["file"], "result.json")
        self.assertEqual(summary["completed_commands"][0]["wall_seconds"], 10)

    def test_workflow_has_one_standard_runner_and_separate_upload(self):
        text = (Path(__file__).parents[1] / "workflows" / "matched-hosted-x64-baseline.yml").read_text()
        self.assertIn("runs-on: windows-2022", text)
        self.assertNotIn("strategy:", text)
        self.assertNotIn("continue-on-error:", text)
        self.assertNotIn("RELEASE_SCALING_STUDY:", text)
        self.assertNotIn("RELEASE_BUILD_CORES:", text)
        self.assertIn("timeout-minutes: 360", text)
        self.assertIn("if: always() && env.MATCHED_ROOT != ''", text)
        self.assertIn(hosted.release.RUST, text)

    @unittest.skipUnless(os.name == "nt", "Windows nested Job Object integration")
    def test_nested_measurement_timeout_terminates_owned_descendants(self):
        import ctypes
        from ctypes import wintypes

        pid_file = self.root / "descendant.pid"
        leaf = f"import os,time,pathlib; pathlib.Path({str(pid_file)!r}).write_text(str(os.getpid())); time.sleep(30)"
        script = "\n".join([
            "import os,sys,pathlib",
            f"sys.path.insert(0, {str(Path(hosted.__file__).parent)!r})",
            "from process_metrics import measure, measurement_session",
            "with measurement_session() as session:",
            f"    measure([sys.executable, '-c', {leaf!r}], pathlib.Path.cwd(), dict(os.environ), 4, "
            "'inner', session=session, timeout=20)",
        ])
        with self.assertRaises(subprocess.TimeoutExpired), measurement_session() as session:
            measure([hosted.sys.executable, "-c", script], self.root, dict(os.environ), 4,
                    self.root / "outer", session=session, timeout=5)
        self.assertTrue(pid_file.is_file(), "nested descendant must have started before outer timeout")
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        process = kernel.OpenProcess(0x1000, False, int(pid_file.read_text()))
        if process:
            try:
                code = wintypes.DWORD()
                self.assertTrue(kernel.GetExitCodeProcess(process, ctypes.byref(code)))
                self.assertNotEqual(code.value, 259, "owned descendant is still active")
            finally:
                kernel.CloseHandle(process)


if __name__ == "__main__":
    unittest.main()
