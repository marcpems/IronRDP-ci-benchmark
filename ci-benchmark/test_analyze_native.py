import unittest

from analyze_native import analyze_units, js_json


def unit(name, start, duration, mode="todo", target=""):
    return {"name": name, "version": "1", "start": start, "duration": duration,
            "mode": mode, "target": target, "sections": None}


class TimingTests(unittest.TestCase):
    def test_partition_does_not_double_count_overlapping_units(self):
        units = [
            unit("dep", 1, 4),
            unit("native", 3, 4, "run-custom-build", "build script (run)"),
            unit("workspace", 6, 2, target="test unit (test)"),
        ]
        result = analyze_units(units, 10, {"workspace"})
        partition = result["wall_partition"]
        self.assertEqual(partition["compiler_units_only_seconds"], 3)
        self.assertEqual(partition["build_scripts_only_seconds"], 1)
        self.assertEqual(partition["compiler_and_build_scripts_overlap_seconds"], 3)
        self.assertEqual(partition["outside_tracked_units_seconds"], 3)
        self.assertEqual(sum(partition.values()), 10)
        self.assertEqual(result["sum_unit_seconds"], 10)
        self.assertEqual(result["provenance"]["workspace"]["unit_seconds"], 2)
        self.assertEqual(result["groups"]["test-target-compilation"]["units"], 1)

    def test_same_time_end_start_and_zero_duration(self):
        result = analyze_units([
            unit("a", 0, 2), unit("b", 2, 2), unit("zero", 2, 0),
        ], 4, set())
        self.assertEqual(result["wall_partition"]["compiler_units_only_seconds"], 4)
        self.assertEqual(result["active_unit_concurrency_seconds"], {1: 4})

    def test_empty_units_show_only_untracked_wall(self):
        result = analyze_units([], 0.8, set())
        self.assertEqual(result["wall_partition"]["outside_tracked_units_seconds"], 0.8)

    def test_json_data_is_decoded_not_executed(self):
        html = 'const UNIT_DATA = [{"name":"a; [ ]","duration":1}];\nalert("not evaluated")'
        self.assertEqual(js_json(html, "UNIT_DATA")[0]["duration"], 1)
        with self.assertRaisesRegex(ValueError, "missing Cargo"):
            js_json(html, "CPU_USAGE")

    def test_inconsistent_wall_measurement_fails(self):
        with self.assertRaisesRegex(ValueError, "exceed subprocess"):
            analyze_units([unit("a", 0, 5)], 4, set())

    def test_sections_are_unit_seconds(self):
        value = unit("a", 0, 10)
        value["sections"] = [
            ["frontend", {"start": 0, "end": 4}],
            ["codegen", {"start": 4, "end": 10}],
        ]
        result = analyze_units([value], 11, set())
        self.assertEqual(result["section_unit_seconds"], {"frontend": 4, "codegen": 6})


if __name__ == "__main__":
    unittest.main()
