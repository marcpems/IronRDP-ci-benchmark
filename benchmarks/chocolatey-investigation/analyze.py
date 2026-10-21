"""Summarize diagnostic artifacts separately from unprofiled timing comparisons."""
import argparse
import collections
import datetime
import json
import pathlib
import random
import statistics


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def median(values):
    return statistics.median(values)


def interval(values):
    values = sorted(values)
    return [values[int((len(values) - 1) * p)] for p in (0.025, 0.975)]


def summarize_recovery(rows, confirmation=False):
    groups = collections.defaultdict(list)
    for row in rows:
        if row["eligible"] and row["outcome"] == "success":
            groups[(row["image_version"], row["mode"])].append(row)
    cells = []
    for (image, mode), data in sorted(groups.items()):
        cells.append({
            "image": image, "mode": mode, "n": len(data),
            "median_seconds": median([r["command_seconds"] for r in data]),
            "cpu_models": dict(collections.Counter(c for r in data for c in r["cpu_name"])),
        })
    rng = random.Random(20261021)
    effects = []
    # Resample complete nominal scheduling blocks, not individual observations.
    blocks = sorted({row["block"] for row in rows})
    for image in sorted({key[0] for key in groups}):
        for treatment in ("refs-temp-c", "refs-direct"):
            if (image, treatment) not in groups or (image, "refs") not in groups:
                continue
            a, b = groups[(image, "refs")], groups[(image, treatment)]
            samples = []
            for _ in range(10000):
                chosen = rng.choices(blocks, k=len(blocks))
                controls = [r["command_seconds"] for block in chosen for r in a if r["block"] == block]
                treated = [r["command_seconds"] for block in chosen for r in b if r["block"] == block]
                if controls and treated:
                    samples.append(median(treated) - median(controls))
            effects.append({
                "image": image, "treatment": treatment, "control": "refs",
                "difference_seconds": median([r["command_seconds"] for r in b]) - median([r["command_seconds"] for r in a]),
                "exploratory_95_percent_block_interval": interval(samples),
                "valid_bootstrap_replicates": len(samples),
                "minimum_cell_size_met": min(len(a), len(b)) >= 8,
                "warning": (
                    "Fixed-size independent follow-up; interpret descriptively if either cell has fewer than eight observations."
                    if confirmation else "Small exploratory cells; four nominal blocks; not confirmatory or multiplicity-adjusted."
                ),
            })
    return {"cells": cells, "effects": effects}


def summarize_diagnostic(raw):
    config = raw["configuration"]
    events = raw["events"]
    processes = raw["processes"]
    modules = processes["modules"]
    main_ids = {
        m["process_id"] for m in modules
        if m["name"].lower() == "choco.exe" and m["version"] == "2.7.4.0"
    }
    phases = {}
    patterns = {
        "banner": "Chocolatey v",
        "package_ready": "package files install completed.",
        "embedded_host": "Calling built-in PowerShell host",
        "host_initialized": "Host version is",
        "installer": "Installing 64-bit nasm",
    }
    for event in events:
        for key, text in patterns.items():
            if key not in phases and text in event["message"]:
                phases[key] = event["elapsed"]
    gaps = []
    previous = 0
    for event in events:
        if event["elapsed"] - previous > 1:
            gaps.append({"seconds": event["elapsed"] - previous, "before": event["message"][:250]})
        previous = event["elapsed"]
    runtimes = {
        (m["name"], m["version"])
        for m in modules if m["process_id"] in main_ids
        and m["name"].lower() in ("clr.dll", "system.management.automation.ni.dll", "mscorlib.ni.dll")
    }
    cpu = sum(max(s["cpu_seconds"] for s in processes["samples"] if s["id"] == pid) for pid in main_ids)
    return {
        "configuration": config,
        "phases": phases,
        "main_process_cpu_seconds_observed": cpu,
        "loaded_runtime_modules": [dict(name=n, version=v) for n, v in sorted(runtimes)],
        "gaps_over_one_second": gaps,
        "caveat": "Profiled execution, not comparable to unprofiled installation timings; process I/O is logical, not physical disk latency.",
    }


def summarize_builds(jobs):
    rows = []
    for job in jobs:
        label, package, variant, sample = job["name"].split(" / ")
        start = datetime.datetime.fromisoformat(job["started_at"].replace("Z", "+00:00"))
        end = datetime.datetime.fromisoformat(job["completed_at"].replace("Z", "+00:00"))
        steps = {}
        for step in job["steps"]:
            if step.get("started_at") and step.get("completed_at"):
                a = datetime.datetime.fromisoformat(step["started_at"].replace("Z", "+00:00"))
                b = datetime.datetime.fromisoformat(step["completed_at"].replace("Z", "+00:00"))
                steps[step["name"]] = {"seconds": (b - a).total_seconds(), "conclusion": step["conclusion"]}
        rows.append({
            "id": job["id"], "url": job["html_url"], "label": label, "package": package,
            "variant": variant, "sample": int(sample), "conclusion": job["conclusion"],
            "job_seconds": (end - start).total_seconds(), "steps": steps,
        })
    groups = collections.defaultdict(list)
    for row in rows:
        if row["conclusion"] == "success":
            groups[(row["label"], row["package"], row["variant"])].append(row["job_seconds"])
    return {
        "jobs": rows,
        "successful_cells": [
            {"label": key[0], "package": key[1], "variant": key[2], "n": len(values), "median_job_seconds": median(values)}
            for key, values in sorted(groups.items())
        ],
        "warning": "Job duration excludes queueing; includes setup, archive, and cache post-steps. Small samples and uncontrolled image/hardware assignment preclude a causal whole-job speedup claim.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", type=pathlib.Path, nargs="?")
    parser.add_argument("--jobs", type=pathlib.Path)
    parser.add_argument("--confirmation", type=pathlib.Path)
    parser.add_argument("--data", type=pathlib.Path)
    parser.add_argument("--save-data", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    if args.data:
        data = load(args.data)
    else:
        if args.artifacts is None:
            parser.error("provide an artifact directory or --data")
        data = {}
        diagnostic = args.artifacts / "choco-diagnostic-39594193280"
        if diagnostic.exists():
            data["diagnostics"] = [{
                "artifact": folder.name,
                "configuration": load(next(folder.rglob("configuration.json"))),
                "events": load(next(folder.rglob("events.json"))),
                "processes": load(next(folder.rglob("processes.json"))),
            } for folder in diagnostic.iterdir() if list(folder.rglob("configuration.json"))]
        recovery = args.artifacts / "choco-recovery-39594438199"
        if recovery.exists():
            data["recovery"] = [load(p) for p in recovery.rglob("nasm-statistics.json")]
        defender = args.artifacts / "defender-39594813812"
        if defender.exists():
            data["defender"] = [{
                "artifact": folder.name,
                "measurement": load(next(folder.rglob("nasm-statistics.json"))),
                "report": load(next(folder.rglob("defender-summary.json"))),
                "status": load(next(folder.rglob("defender-status.json"))),
            } for folder in defender.iterdir()]
        if args.confirmation:
            data["confirmation"] = [load(p) for p in args.confirmation.rglob("nasm-statistics.json")]
        if args.jobs:
            data["build_jobs"] = load(args.jobs)["jobs"]
    if args.save_data:
        args.save_data.write_text(json.dumps(data, indent=2) + "\n")
    result = {}
    if "diagnostics" in data:
        result["diagnostics"] = [summarize_diagnostic(raw) for raw in data["diagnostics"]]
    for name in ("recovery", "confirmation"):
        if name in data:
            result[name] = summarize_recovery(data[name], confirmation=name == "confirmation")
    if "defender" in data:
        result["defender"] = [{
            "artifact": raw["artifact"],
            "image": raw["measurement"]["image_version"],
            "installation_seconds": raw["measurement"]["command_seconds"],
            "recording_seconds": (
                raw["report"]["Overview"]["EndTime"] - raw["report"]["Overview"]["StartTime"]
            ) / 10_000_000,
            "recorded_realtime_scan_seconds": raw["report"]["Overview"]["RealTimeScansDuration"] / 10_000_000,
            "maximum_scan_seconds": raw["report"]["Overview"]["MaxScanDuration"] / 10_000_000,
        } for raw in data["defender"]]
    if "build_jobs" in data:
        result["builds"] = summarize_builds(data["build_jobs"])
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key in ("recovery", "confirmation", "defender")}, indent=2))


if __name__ == "__main__":
    main()
