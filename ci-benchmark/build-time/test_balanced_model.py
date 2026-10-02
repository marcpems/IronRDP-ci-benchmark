import math
import unittest

from balanced_model import build, completed_cost, rounded_minutes, scale


class BalancedModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, cls.output = build()

    def test_cold_accounting_does_not_double_count_std_or_vendoring(self):
        cold = self.config["cold_baseline"]
        base = self.output["cold_accounting"]
        self.assertAlmostEqual(base["retained_minutes"], 68.04)
        self.assertAlmostEqual(base["retained_prefix_minutes"], 14.51)
        self.assertAlmostEqual(cold["job_minutes"], base["retained_prefix_minutes"] +
                               base["retained_tail_minutes"] +
                               cold["llvm_minutes"] + cold["rustc_std_minutes"])

    def test_nonlinear_scaling_and_serial_floor(self):
        self.assertEqual(scale(100, 4, 0.2, 0.8), 100)
        self.assertEqual(scale(100, 32, 1, 0.8), 100)
        t16, t32 = (scale(100, c, 0.2, 0.8) for c in (16, 32))
        self.assertGreater(t16, 25)
        self.assertGreater(t32, t16 / 2)
        self.assertGreater(t32, 20)
        self.assertAlmostEqual(scale(100, 16, 0.2, 0.8, 1.25), t16 * 1.25)

    def test_round_each_job_not_elapsed_or_sum(self):
        jobs = [{"duration_minutes": 1.1}, {"duration_minutes": 1.1}]
        self.assertEqual(rounded_minutes(jobs), 4)
        self.assertNotEqual(rounded_minutes(jobs), math.ceil(2.2))

    def test_retry_cost_and_invalid_inputs(self):
        self.assertEqual(completed_cost(10, 5, 1), 10)
        self.assertEqual(completed_cost(10, 5, 0.5), 15)
        for p in (0, -1, 1.1):
            with self.assertRaises(ValueError):
                completed_cost(10, 5, p)
        with self.assertRaises(ValueError):
            scale(100, 2, 0.1, 0.8)

    def test_native_arm_prices_not_x64(self):
        self.assertEqual(self.config["hardware"]["native16"]["sku"], "windows_16_core_arm")
        self.assertEqual(self.config["hardware"]["native16"]["usd_per_minute"], 0.05)
        self.assertEqual(self.config["hardware"]["native32"]["usd_per_minute"], 0.098)

    def test_dependency_barriers_and_billed_sum(self):
        for row in self.output["results"]:
            jobs = row["jobs"]
            self.assertAlmostEqual(row["sum_runner_wall_minutes"],
                                   sum(j["duration_minutes"] for j in jobs))
            if row["layout"] == "four_job":
                fe, llvm, backend, final = jobs
                self.assertEqual(backend["start_minutes"],
                                 max(fe["finish_minutes"], llvm["finish_minutes"]))
                self.assertEqual(final["start_minutes"], backend["finish_minutes"])
                self.assertGreater(row["sum_runner_wall_minutes"], row["elapsed_minutes"])
                self.assertEqual(fe["phases"][-1]["name"], "Handoff/setup")
                self.assertEqual(llvm["phases"][-1]["name"], "Handoff/setup")
                self.assertGreater(row["large_handoff_sensitivity"]["sum_runner_wall_minutes"],
                                   row["sum_runner_wall_minutes"])
            if row["layout"] == "two_job":
                producer, final = jobs
                self.assertEqual(producer["finish_minutes"], final["start_minutes"])
                self.assertAlmostEqual(row["sum_runner_wall_minutes"], row["elapsed_minutes"])
                self.assertFalse(any(p["name"] == "Final compiler" for p in producer["phases"]))
            if row["hardware"] == "public4":
                self.assertEqual(row["billed_compute_minutes"], 0)
                self.assertEqual(row["complete_uncapped_attempt_usd"], 0)

    def test_cold_acceptance_not_rescued_by_cache_average(self):
        for row in self.output["results"]:
            cache = row["cache_sensitivity"]
            self.assertEqual(cache["cold_elapsed_minutes"], row["elapsed_minutes"])
            self.assertAlmostEqual(cache["expected_elapsed_minutes"],
                                   0.2 * cache["cold_elapsed_minutes"] +
                                   0.8 * cache["hit_elapsed_minutes"])
            if not row["fits_350"]:
                self.assertIsNone(row["expected_compute_usd_per_qualified_build"])

    def test_full_core_training_and_tail_retained(self):
        for row in self.output["results"]:
            phases = [p for j in row["jobs"] for p in j["phases"]]
            for required in ("FE training", "LLVM training", "Static relink",
                             "Final compiler", "Full dist remainder", "Qualification"):
                self.assertEqual(sum(p["name"] == required for p in phases), 1)
            self.assertTrue(all(p["minutes"] > 0 for p in phases))


if __name__ == "__main__":
    unittest.main()
