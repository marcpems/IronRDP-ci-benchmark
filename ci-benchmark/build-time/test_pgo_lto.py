import unittest
import xml.etree.ElementTree as ET

from project_pgo_lto import ROOT, build, metrics, serial_jobs, stamp


class ProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, cls.output = build()

    def test_stock_partition_and_unchanged_frontier(self):
        for base in self.output["baselines"]:
            self.assertAlmostEqual(base["stock_minutes"], base["retained_minutes"] +
                                   base["stock_llvm_minutes"] + base["stock_compiler_minutes"])
        for case in self.output["results"]:
            self.assertAlmostEqual(case["variants"]["stock"]["workflow_increase_minutes"], 0)
            self.assertAlmostEqual(case["variants"]["stock"]["arm_runner_increase_minutes"], 0)

    def test_fresh_serial_equation(self):
        names = ("seed_llvm", "frontend_instrument", "frontend_training",
                 "frontend_profile_use", "llvm_instrument", "static_relink",
                 "llvm_training", "final_thinlto", "profile_support", "extra_qualification")
        for case in self.output["results"]:
            base = next(b for b in self.output["baselines"] if b["run_id"] == case["baseline_run"])
            budget = self.config["scenarios"][case["scenario"]]
            expected = base["retained_minutes"] + sum(budget[name] for name in names)
            value = case["variants"]["fresh_dual_pgo_thinlto"]
            self.assertAlmostEqual(value["artifact_and_extra_qualification_minutes"], expected)
            self.assertAlmostEqual(value["arm_runner_minutes"], expected)

    def test_frontend_only_does_not_duplicate_final_rebuild(self):
        for case in self.output["results"]:
            phases = case["variants"]["frontend_pgo_only"]["jobs"][0]["phases"]
            self.assertEqual(sum(p["name"] == "FE profile-use" for p in phases), 1)
            self.assertFalse(any(p["name"] in ("Final compiler", "LLVM instrumentation")
                                 for p in phases))

    def test_conservative_static_relink_barrier_and_idle_cost(self):
        for case in self.output["results"]:
            value = case["variants"]["overlap_llvm_build"]
            fe, be, final = value["jobs"]
            preceding = 0
            for phase in be["phases"]:
                if phase["name"] == "Static relink":
                    self.assertGreaterEqual(preceding + 1e-8, fe["finish_minutes"])
                    break
                preceding += phase["minutes"]
            else:
                self.fail("missing mandatory static relink")
            self.assertGreaterEqual(final["start_minutes"], max(fe["finish_minutes"], be["finish_minutes"]))
            self.assertAlmostEqual(value["arm_runner_minutes"],
                                   sum(j["duration_minutes"] for j in value["jobs"]))
            self.assertTrue(any(p["name"] == "Waiting" for p in be["phases"]))

    def test_independent_profiles_have_real_backend_compiler(self):
        for case in self.output["results"]:
            value = case["variants"]["independent_profiles"]
            fe, be, final = value["jobs"]
            self.assertFalse(any(p["name"] == "FE profile-use" for p in fe["phases"]))
            self.assertTrue(any(p["name"] == "Plain FE + static link" for p in be["phases"]))
            self.assertGreaterEqual(final["start_minutes"], max(fe["finish_minutes"], be["finish_minutes"]))
            self.assertGreaterEqual(value["arm_runner_minutes"], value["artifact_and_extra_qualification_minutes"])

    def test_native_four_job_dependencies_need_no_reserved_waiting_runner(self):
        for case in self.output["results"]:
            fe, llvm, backend, final = case["variants"]["native_four_job_dag"]["jobs"]
            self.assertEqual(backend["start_minutes"], max(fe["finish_minutes"], llvm["finish_minutes"]))
            self.assertEqual(final["start_minutes"], backend["finish_minutes"])
            self.assertFalse(any(p["name"] == "Waiting" for j in (fe, llvm, backend, final) for p in j["phases"]))

    def test_profile_reuse_is_not_reported_as_fresh_makespan(self):
        for case in self.output["results"]:
            value = case["variants"]["exact_profile_consumer_only"]
            self.assertFalse(value["fresh_profiles_included"])
            self.assertNotIn("projected_workflow_minutes", value)

    def test_exact_instrument_cache_does_not_remove_training_or_relinks(self):
        for case in self.output["results"]:
            value = case["variants"]["warm_exact_instrumented_llvm"]
            self.assertTrue(value["fresh_profiles_included"])
            phases = {p["name"]: p["minutes"] for p in value["jobs"][0]["phases"]}
            budget = self.config["scenarios"][case["scenario"]]
            self.assertEqual(phases["Instrumented LLVM restore"], budget["instrument_cache_restore"])
            self.assertEqual(phases["FE training"], budget["frontend_training"])
            self.assertEqual(phases["LLVM training"], budget["llvm_training"])
            self.assertEqual(phases["Static relink"], budget["static_relink"])
            self.assertEqual(phases["Final compiler"], budget["final_thinlto"])

    def test_timeout_threshold_closes_at_360(self):
        for case in self.output["results"]:
            if case["scenario"] == "stress":
                self.assertLess(case["thresholds"]["final_build_allowance_at_360_minutes"], 0)
                continue
            base = next(b for b in self.output["baselines"] if b["run_id"] == case["baseline_run"])
            budget = dict(self.config["scenarios"][case["scenario"]])
            budget["final_thinlto"] = case["thresholds"]["final_build_allowance_at_360_minutes"]
            jobs = serial_jobs(base, budget, "fresh_dual_pgo_thinlto")
            value = metrics(base, jobs, self.config)
            self.assertAlmostEqual(value["longest_job_minutes"], 360)

    def test_job_limit_is_not_whole_workflow_limit(self):
        for case in self.output["results"]:
            if case["scenario"] == "stress":
                value = case["variants"]["overlap_llvm_build"]
                self.assertGreater(value["artifact_and_extra_qualification_minutes"], 360)
                self.assertTrue(value["fits_360_minute_job_limit"])
                self.assertFalse(case["variants"]["fresh_dual_pgo_thinlto"]["fits_360_minute_job_limit"])

    def test_x64_duration_and_counterfactual(self):
        history = self.config["historical_x64"]
        reuse = history["profile_reuse_thinlto"]
        actual = (stamp(reuse["completed_at"]) - stamp(reuse["started_at"])).total_seconds() / 60
        self.assertAlmostEqual(actual, reuse["reported_total_minutes"])
        sensitivity = self.output["historical_sensitivity"]
        self.assertAlmostEqual(sensitivity["substituted_fresh_pipeline_minutes"], 474.2315)
        self.assertFalse(history["initial_thinlto_attempt"]["valid_whole_pipeline"])
        self.assertIn("NOT", sensitivity["classification"])

    def test_projection_svgs_parse(self):
        for name in ("optimized-arm64-projection.svg", "optimized-arm64-jobs.svg"):
            tree = ET.parse(ROOT / name)
            self.assertTrue(tree.getroot().tag.endswith("svg"))


if __name__ == "__main__":
    unittest.main()
