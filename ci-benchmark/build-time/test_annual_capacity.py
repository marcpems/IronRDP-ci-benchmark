import unittest

from annual_capacity import (
    YEAR_MINUTES, annual_cost, cancellation_replay, job_kind, queue_replay,
)


class AnnualCapacityTests(unittest.TestCase):
    def test_year_and_active_billing_not_core_minutes(self):
        self.assertEqual(YEAR_MINUTES, 525600)
        row = annual_cost(365, [136], 0.098)
        self.assertEqual(row["runner_wall_minutes"], 49640)
        self.assertAlmostEqual(row["compute_usd"], 4864.72)
        self.assertAlmostEqual(YEAR_MINUTES * 0.098, 51508.8)

    def test_round_jobs_separately_and_do_not_add_retry_multiplier(self):
        row = annual_cost(100, [1.1, 1.1], 0.098)
        self.assertAlmostEqual(row["runner_wall_minutes"], 220)
        self.assertEqual(row["billed_runner_minutes"], 400)

    def test_maintenance_and_utilization_reserve(self):
        row = annual_cost(1000, [200], 0.098)
        self.assertAlmostEqual(row["utilization_of_available_time"], 200000 / (525600 * 0.95))
        self.assertAlmostEqual(row["annual_attempt_capacity_at_70_percent"],
                               525600 * 0.95 * 0.7 / 200)

    def test_job_limit_and_aggregate_capacity_are_independent(self):
        overflow = annual_cost(5000, [200], 0.098)
        self.assertTrue(overflow["fits_job_limit"])
        self.assertFalse(overflow["fits_aggregate_one_runner"])
        split = annual_cost(100, [230, 175], 0.098)
        self.assertTrue(split["fits_job_limit"])
        unsplit = annual_cost(100, [405], 0.098)
        self.assertFalse(unsplit["fits_job_limit"])
        self.assertEqual(split["runner_wall_minutes"], unsplit["runner_wall_minutes"])

    def test_bursts_queue_on_one_runner(self):
        row = queue_replay([0, 0, 0], 10)
        self.assertEqual(row["median_wait_minutes"], 10)
        self.assertEqual(row["max_wait_minutes"], 20)
        self.assertEqual(row["last_completion_after_last_arrival_minutes"], 30)
        self.assertEqual(queue_replay([0, 11, 22], 10)["max_wait_minutes"], 0)

    def test_expired_cancellations_do_not_reserve_a_runner(self):
        jobs = [
            {"arrival": "2026-09-18T00:00:00Z", "conclusion": "success", "completed_at": None},
            {"arrival": "2026-09-18T00:01:00Z", "conclusion": "cancelled",
             "completed_at": "2026-09-18T00:05:00Z"},
        ]
        row = cancellation_replay(jobs, [20])
        self.assertEqual(row["runner_wall_minutes"], 20)
        self.assertEqual(row["cancelled_before_service"], 1)

    def test_running_cancellation_bills_only_consumed_job_parts(self):
        row = cancellation_replay([
            {"arrival": "2026-09-18T00:00:00Z", "conclusion": "cancelled",
             "completed_at": "2026-09-18T00:05:30Z"}], [3.1, 10])
        self.assertAlmostEqual(row["runner_wall_minutes"], 5.5)
        self.assertEqual(row["rounded_job_minutes"], 7)

    def test_native_abi_variants_are_distinct_not_duplicate_artifacts(self):
        self.assertEqual(job_kind("auto - dist-aarch64-msvc"), "dist")
        self.assertEqual(job_kind("auto - dist-aarch64-llvm-mingw"), "gnullvm_dist")
        self.assertEqual(job_kind("try - test-aarch64-msvc-1"), "test")
        self.assertEqual(job_kind("auto - dist-x86_64-msvc"), "other")

    def test_empty_queue_and_invalid_inputs(self):
        self.assertEqual(queue_replay([], 10)["requests"], 0)
        for args in ((-1, [10], 0.098), (1, [], 0.098), (1, [-1], 0.098), (1, [0], 0.098)):
            with self.assertRaises(ValueError):
                annual_cost(*args)
        with self.assertRaises(ValueError):
            annual_cost(1, [10], 0.098, availability=0)


if __name__ == "__main__":
    unittest.main()
