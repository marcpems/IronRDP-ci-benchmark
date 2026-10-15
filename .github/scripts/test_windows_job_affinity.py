import ctypes as c
from ctypes import wintypes as w
import os
import unittest
from unittest.mock import patch

from windows_job_affinity import (
    api, configure_job_groups, requires_group_affinity, selected_groups, verify_job_groups,
)


class GroupSelectionTests(unittest.TestCase):
    def test_scaling_uses_group_zero_even_when_parent_is_in_small_group(self):
        for cores in (4, 16, 32):
            self.assertEqual(selected_groups([64, 8], cores),
                             [{"group": 0, "cpus": list(range(cores))}])
            with patch("windows_job_affinity.api") as kernel:
                kernel.return_value.GetActiveProcessorGroupCount.return_value = 2
                self.assertTrue(requires_group_affinity(cores))
                kernel.return_value.GetActiveProcessorGroupCount.return_value = 1
                self.assertFalse(requires_group_affinity(cores))
        self.assertTrue(requires_group_affinity(64))

    def test_64_processors_across_balanced_groups(self):
        self.assertEqual(selected_groups([36, 36], 64),
                         [{"group": 0, "cpus": list(range(36))},
                          {"group": 1, "cpus": list(range(28))}])
        self.assertEqual(selected_groups([64, 8], 64),
                         [{"group": 0, "cpus": list(range(64))}])
        for counts, cores in (([36, 36], 73), ([12], 64), ([72], 64), ([36, 36], 0)):
            with self.assertRaises(ValueError):
                selected_groups(counts, cores)

    @unittest.skipUnless(os.name == "nt", "Windows Job Object APIs")
    def test_native_kernel_roundtrip_and_reject_mismatched_readback(self):
        kernel = api()
        kernel.CreateJobObjectW.argtypes = [c.c_void_p, w.LPCWSTR]
        kernel.CreateJobObjectW.restype = w.HANDLE
        kernel.CloseHandle.argtypes = [w.HANDLE]
        kernel.CloseHandle.restype = w.BOOL
        job = kernel.CreateJobObjectW(None, None)
        if not job:
            raise c.WinError(c.get_last_error())
        try:
            configured = configure_job_groups(job, 4)
            self.assertEqual(sum(len(row["cpus"]) for row in configured), 4)
            verify_job_groups(job, configured)
            with self.assertRaisesRegex(RuntimeError, "affinity differs"):
                verify_job_groups(job, [{"group": 0, "cpus": [0]}])
        finally:
            kernel.CloseHandle(job)


if __name__ == "__main__":
    unittest.main()
