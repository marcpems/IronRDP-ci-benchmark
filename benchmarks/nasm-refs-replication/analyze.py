import argparse
import collections
import datetime
import json
import pathlib
import random
import re
import statistics

ROOT = pathlib.Path(__file__).parent
VARIANTS = ("baseline", "without-nasm", "without-nasm-wait")


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def elapsed(start, end):
    return (datetime.datetime.fromisoformat(end) - datetime.datetime.fromisoformat(start)).total_seconds()


def collect(artifacts, jobs_path, caches_path):
    jobs, caches = load(jobs_path), load(caches_path)
    observations = []
    for job in jobs:
        block, variant = job["name"].split(" / ")
        folder = artifacts / f"timings-{block}-{variant}"
        html = next(folder.rglob("cargo-timing.html")).read_text(encoding="utf-8")
        units = json.JSONDecoder().raw_decode(html.split("const UNIT_DATA = ", 1)[1])[0]
        native_output = next(folder.rglob("output")).read_text(encoding="utf-8")
        observations.append({
            "block": int(block),
            "variant": variant,
            "job_id": job["id"],
            "host": load(next(folder.rglob("nasm-host.json"))),
            "build_measurement": load(next(folder.rglob("nasm-build-measurement.json"))),
            "pre_treatment": load(next(folder.rglob("nasm-pre-treatment.json"))),
            "cargo_seconds": float(re.search(r"Total time:</td><td>([\d.]+)s", html)[1]),
            "fresh_units": int(re.search(r"Fresh units:</td><td>(\d+)", html)[1]),
            "units": units,
            "native_configuration": [
                line for line in native_output.splitlines()
                if line.startswith("cargo:warning=")
            ],
        })
    return {"run_id": 39747378333, "jobs": jobs, "caches": caches, "observations": observations}


def distribution(values):
    return {
        "n": len(values), "mean": statistics.mean(values), "median": statistics.median(values),
        "minimum": min(values), "maximum": max(values),
    }


def unit_identity(units):
    return collections.Counter(
        (u["name"], u["version"], u["target"], tuple(u["features"])) for u in units
    )


def analyze(data):
    jobs = {j["id"]: j for j in data["jobs"]}
    rows = {}
    reference_units = None
    for observation in data["observations"]:
        job = jobs[observation["job_id"]]
        block, variant = observation["block"], observation["variant"]
        assert job["conclusion"] == "success", job["name"]
        assert (block, variant) not in rows
        host = observation["host"]
        assert host["filesystem"] == "ReFS"
        assert host["cargo_home"] == "D:\\cargo-home"
        assert host["workspace_target"] == "D:\\workspace"
        assert host["defender"]["RealTimeProtectionEnabled"]
        assert "cargo:warning=Building with: CC" in observation["native_configuration"]
        assert "cargo:warning=Target platform: 'aarch64-pc-windows-msvc'" in observation["native_configuration"]
        assert "cargo:warning=Setting CC_aarch64_pc_windows_msvc: clang-cl" in observation["native_configuration"]
        assert observation["fresh_units"] == 0
        identity = unit_identity(observation["units"])
        if reference_units is None:
            reference_units = identity
        assert identity == reference_units, job["name"]
        cache_prefix = f"nasm-rep-{data['run_id']}-1-{block}-{variant}-build-"
        matching = [c for c in data["caches"] if c["key"].startswith(cache_prefix)]
        assert len(matching) == 1 and matching[0]["size_in_bytes"] > 0, job["name"]
        metrics = {
            "job_seconds": elapsed(job["started_at"], job["completed_at"]),
            "cargo_seconds": observation["cargo_seconds"],
            "pre_compile_seconds": min(u["start"] for u in observation["units"]),
            "cpu_busy_percent": observation["build_measurement"]["system_cpu_busy_percent"],
        }
        for step in job["steps"]:
            if step["started_at"] and step["completed_at"]:
                metrics[step["name"]] = elapsed(step["started_at"], step["completed_at"])
        for name, target in (
            ("aws-lc-sys", " build script (run)"), ("windows", ""), ("sspi", ""),
            ("ironrdp-agent", ""), ("ironrdp-agent", ' bin "ironrdp-agent"'),
        ):
            metrics[f"unit:{name}{target}"] = next(
                u["duration"] for u in observation["units"]
                if u["name"] == name and u["target"] == target
            )
        rows[block, variant] = {
            "metrics": metrics, "image": host["image"], "cpu": host["cpu"]["Name"],
            "power_plan": host["power_plan"],
        }
    assert set(rows) == {(block, variant) for block in range(1, 9) for variant in VARIANTS}
    summary = {"variants": {}, "comparisons": {}, "image_subsets": {}}
    metric_names = tuple(next(iter(rows.values()))["metrics"])
    for variant in VARIANTS:
        selected = [rows[b, variant] for b in range(1, 9)]
        summary["variants"][variant] = {
            "metrics": {m: distribution([r["metrics"][m] for r in selected]) for m in metric_names},
            "images": dict(collections.Counter(r["image"] for r in selected)),
            "cpus": dict(collections.Counter(r["cpu"] for r in selected)),
            "power_plans": dict(collections.Counter(r["power_plan"] for r in selected)),
        }
    rng = random.Random(20261022)
    draws = [[rng.randrange(1, 9) for _ in range(8)] for _ in range(10000)]
    for control, treatment in (
        ("baseline", "without-nasm"), ("without-nasm", "without-nasm-wait"),
        ("baseline", "without-nasm-wait"),
    ):
        key = f"{treatment}_minus_{control}"
        comparison = {}
        for metric in ("job_seconds", "cargo_seconds", "Rust cache", "pre_compile_seconds"):
            estimates = {}
            for label, statistic in (("mean", statistics.mean), ("median", statistics.median)):
                point = statistic([rows[b, treatment]["metrics"][metric] for b in range(1, 9)]) - statistic(
                    [rows[b, control]["metrics"][metric] for b in range(1, 9)]
                )
                samples = [
                    statistic([rows[b, treatment]["metrics"][metric] for b in draw]) - statistic(
                        [rows[b, control]["metrics"][metric] for b in draw]
                    ) for draw in draws
                ]
                quantiles = statistics.quantiles(samples, n=40, method="inclusive")
                estimates[label] = {"difference": point, "bootstrap_95_interval": [quantiles[0], quantiles[-1]]}
            comparison[metric] = estimates
        summary["comparisons"][key] = comparison
    for image in sorted({r["image"] for r in rows.values()}):
        summary["image_subsets"][image] = {}
        for variant in VARIANTS:
            selected = [r for (b, v), r in rows.items() if v == variant and r["image"] == image]
            summary["image_subsets"][image][variant] = {
                m: distribution([r["metrics"][m] for r in selected])
                for m in ("job_seconds", "cargo_seconds")
            }
    summary["verification"] = {
        "successful_jobs": len(rows), "verified_refs_jobs": len(rows),
        "api_confirmed_caches": len(data["caches"]),
        "same_compilation_units_and_features": True,
        "compilation_units_per_job": sum(reference_units.values()),
        "fresh_units_per_job": 0,
        "verified_native_clang_jobs": len(rows),
        "defender_enabled_jobs": len(rows),
    }
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=pathlib.Path)
    parser.add_argument("--jobs", type=pathlib.Path)
    parser.add_argument("--caches", type=pathlib.Path)
    parser.add_argument("--data", type=pathlib.Path, default=ROOT / "measurements.json")
    parser.add_argument("--output", type=pathlib.Path, default=ROOT / "summary.json")
    args = parser.parse_args()
    if any((args.artifacts, args.jobs, args.caches)):
        if not all((args.artifacts, args.jobs, args.caches)):
            parser.error("--artifacts, --jobs, and --caches must be supplied together")
        data = collect(args.artifacts, args.jobs, args.caches)
        args.data.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    else:
        data = load(args.data)
    result = analyze(data)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["verification"], indent=2))
    for name, comparison in result["comparisons"].items():
        print(name, json.dumps({metric: values["mean"] for metric, values in comparison.items()}))
