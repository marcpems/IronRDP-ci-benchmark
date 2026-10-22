import argparse
import collections
import datetime
import json
import pathlib
import random
import re
import statistics

HERE = pathlib.Path(__file__).resolve().parent


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def elapsed(start, end):
    return (datetime.datetime.fromisoformat(end) - datetime.datetime.fromisoformat(start)).total_seconds()


def distribution(values):
    return {"n": len(values), "mean": statistics.mean(values), "median": statistics.median(values),
            "minimum": min(values), "maximum": max(values)} if values else {"n": 0}


def collect(artifacts, jobs_path, caches_path, run_id):
    jobs = [job for page in load(jobs_path) for job in page["jobs"]]
    caches = [cache for page in load(caches_path) for cache in page["actions_caches"]]
    observations = []
    for job in jobs:
        block, variant = job["name"].split(" / ")
        folder = artifacts / f"measurements-{block}-{variant}"
        host = load(next(folder.rglob("x64-host.json")))
        html = next(folder.rglob("cargo-timing.html")).read_text(encoding="utf-8")
        preparation = list(folder.rglob("x64-storage-preparation.json"))
        observations.append({
            "block": int(block), "variant": variant, "job_id": job["id"], "host": host,
            "preparation": load(preparation[0]) if preparation else None,
            "cargo_seconds": float(re.search(r"Total time:</td><td>([\d.]+)s", html)[1]),
            "fresh_units": int(re.search(r"Fresh units:</td><td>(\d+)", html)[1]),
            "units": json.JSONDecoder().raw_decode(html.split("const UNIT_DATA = ", 1)[1])[0],
        })
    return {"run_id": run_id, "jobs": jobs, "caches": caches, "observations": observations}


def analyze(data):
    plan = load(HERE / "plan.json")
    jobs = {job["id"]: job for job in data["jobs"]}
    rows = {}
    reference_units = None
    for observation in data["observations"]:
        job = jobs[observation["job_id"]]
        block, variant = observation["block"], observation["variant"]
        assert job["conclusion"] == "success", job["name"]
        assert (block, variant) not in rows
        host = observation["host"]
        assert host["source_commit"] == plan["source_commit"], job["name"]
        assert host["nasm_version"], job["name"]
        assert host["defender"]["RealTimeProtectionEnabled"], job["name"]
        assert observation["fresh_units"] == 0, job["name"]
        units = collections.Counter(
            (unit["name"], unit["version"], unit["target"], tuple(unit["features"]))
            for unit in observation["units"]
        )
        if reference_units is None:
            reference_units = units
        assert units == reference_units, job["name"]
        d_partition = next(p for p in host["partitions"] if p["DriveLetter"] == "D")
        disk = next(d for d in host["disks"] if d["Number"] == d_partition["DiskNumber"])
        assert not disk["IsBoot"] and not disk["IsSystem"]
        d_volume = next(v for v in host["volumes"] if v["DriveLetter"] == "D")
        assert d_volume["FileSystem"] == "NTFS"
        if variant == "refs":
            preparation = observation["preparation"]
            assert preparation and d_partition["Size"] == preparation["before"]["supported_minimum"]
            assert host["cargo_home"] == "R:\\cargo-home"
            assert host["workspace_target"] == "R:\\workspace"
            assert host["runner_temp_target"] == "R:\\runner-temp"
            assert host["temp"] == host["tmp"] == "R:\\build-temp"
            assert next(v for v in host["volumes"] if v["DriveLetter"] == "R")["FileSystem"] == "ReFS"
            assert host["paging_settings"] == preparation["before"]["paging_settings"]
        else:
            assert observation["preparation"] is None
            assert host["cargo_home"].lower().startswith("c:\\")
            assert not host["workspace_target"] and not host["runner_temp_target"]
        cache_prefix = f"x64-refs-rep-{data['run_id']}-{job['run_attempt']}-{block}-{variant}-build-"
        matching = [cache for cache in data["caches"] if cache["key"].startswith(cache_prefix)]
        assert len(matching) == 1 and matching[0]["size_in_bytes"] > 0, job["name"]
        install = next(step for step in job["steps"] if step["name"] == "Install build dependencies")
        assert install["conclusion"] == "success"
        metrics = {
            "job_seconds": elapsed(job["started_at"], job["completed_at"]),
            "cargo_seconds": observation["cargo_seconds"],
        }
        for step in job["steps"]:
            if step["started_at"] and step["completed_at"]:
                metrics[step["name"]] = elapsed(step["started_at"], step["completed_at"])
        rows[block, variant] = {
            "block": block, "variant": variant, "metrics": metrics, "image": host["image"],
            "cpu": host["cpu"][0]["Name"].strip(), "bus": disk["BusType"],
            "partition_style": disk["PartitionStyle"], "paging": host["paging"],
            "d_free_bytes": d_volume["SizeRemaining"], "nasm_version": host["nasm_version"],
        }
    assert set(rows) == {(block, variant) for block in range(1, 9) for variant in plan["variants"]}
    metrics = ("job_seconds", "cargo_seconds", "Install build dependencies", "Rust cache", "Post Rust cache")
    summary = {"variants": {}, "refs_minus_baseline": {}, "hardware_subsets": {}, "rows": list(rows.values())}
    for variant in plan["variants"]:
        selected = [row for (_, v), row in rows.items() if v == variant]
        summary["variants"][variant] = {
            "metrics": {metric: distribution([row["metrics"][metric] for row in selected]) for metric in metrics},
            "cpus": dict(collections.Counter(row["cpu"] for row in selected)),
            "buses": dict(collections.Counter(row["bus"] for row in selected)),
            "images": dict(collections.Counter(row["image"] for row in selected)),
        }
    rng = random.Random(plan["seed"])
    draws = [[rng.randrange(1, 9) for _ in range(8)] for _ in range(10000)]
    for metric in metrics:
        summary["refs_minus_baseline"][metric] = {}
        for label, statistic in (("mean", statistics.mean), ("median", statistics.median)):
            point = statistic(rows[b, "refs"]["metrics"][metric] for b in range(1, 9)) - statistic(
                rows[b, "baseline"]["metrics"][metric] for b in range(1, 9)
            )
            samples = [
                statistic(rows[b, "refs"]["metrics"][metric] for b in draw) - statistic(
                    rows[b, "baseline"]["metrics"][metric] for b in draw
                ) for draw in draws
            ]
            quantiles = statistics.quantiles(samples, n=40, method="inclusive")
            summary["refs_minus_baseline"][metric][label] = {
                "difference": point, "bootstrap_95_interval": [quantiles[0], quantiles[-1]],
            }
    strata = sorted({(row["image"], row["cpu"], row["bus"]) for row in rows.values()})
    for stratum in strata:
        summary["hardware_subsets"][" / ".join(stratum)] = {
            variant: {
                metric: distribution([row["metrics"][metric] for (_, v), row in rows.items()
                                      if v == variant and (row["image"], row["cpu"], row["bus"]) == stratum])
                for metric in ("job_seconds", "cargo_seconds")
            } for variant in plan["variants"]
        }
    summary["verification"] = {
        "successful_jobs": len(rows), "api_confirmed_caches": len(rows), "refs_jobs": 8,
        "identical_compilation_units_and_features": sum(reference_units.values()), "fresh_units_per_job": 0,
        "nasm_versions": sorted({row["nasm_version"] for row in rows.values()}),
    }
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=pathlib.Path)
    parser.add_argument("--jobs", type=pathlib.Path)
    parser.add_argument("--caches", type=pathlib.Path)
    parser.add_argument("--run-id", type=int)
    parser.add_argument("--data", type=pathlib.Path, default=HERE / "measurements.json")
    parser.add_argument("--output", type=pathlib.Path, default=HERE / "summary.json")
    args = parser.parse_args()
    if args.artifacts:
        if not args.jobs or not args.caches or not args.run_id:
            parser.error("--artifacts requires --jobs, --caches and --run-id")
        data = collect(args.artifacts, args.jobs, args.caches, args.run_id)
        args.data.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")
    else:
        data = load(args.data)
    result = analyze(data)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in ("rows", "hardware_subsets")}, indent=2))
