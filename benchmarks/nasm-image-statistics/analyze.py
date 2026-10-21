"""Collect a NASM campaign and bootstrap image effects by scheduling block."""
import collections
import json
import math
import os
import pathlib
import random
import statistics
import subprocess
import sys

GH = os.environ.get("GH_EXECUTABLE", "gh")
REPO = "marcpems/IronRDP-ci-benchmark"
HERE = pathlib.Path(__file__).parent
OLD, NEW = "20261013.183.4", "20261018.189.1"


def api(path):
    return json.loads(subprocess.check_output([GH, "api", path]))


def quantile(values, p):
    values = sorted(values)
    position = (len(values) - 1) * p
    lower, upper = math.floor(position), math.ceil(position)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def describe(values):
    return dict(n=len(values), median=statistics.median(values), mean=statistics.mean(values),
                p10=quantile(values, 0.1), p90=quantile(values, 0.9),
                minimum=min(values), maximum=max(values))


offline = sys.argv[1:2] == ["--data"]
rows = json.loads(pathlib.Path(sys.argv[2]).read_text()) if offline else []
runs = []
if offline:
    for run_id in sorted(set(r["run_id"] for r in rows)):
        subset = [r for r in rows if r["run_id"] == run_id]
        runs.append(dict(id=run_id, url=f"https://github.com/{REPO}/actions/runs/{run_id}",
                         head_sha=subset[0]["workflow_commit"], jobs=len(subset)))
for run_id in ([] if offline else [arg for arg in sys.argv[1:] if arg != "--cobalt100-only"]):
    folder = HERE / f"nasm-{run_id}"
    snapshot = HERE / f"nasm-{run_id}-jobs.json"
    if snapshot.exists():
        saved = json.loads(snapshot.read_text())
        run, jobs = saved["run"], saved["jobs"]
    else:
        run = api(f"repos/{REPO}/actions/runs/{run_id}")
        jobs = []
        for page in range(1, 10):
            batch = api(f"repos/{REPO}/actions/runs/{run_id}/jobs?per_page=100&page={page}")["jobs"]
            jobs.extend(batch)
            if len(batch) < 100:
                break
        if run["status"] != "completed":
            raise RuntimeError(f"run {run_id} is not complete")
        snapshot.write_text(json.dumps({"run": run, "jobs": jobs}, indent=2))
    runs.append(dict(id=run["id"], url=run["html_url"], head_sha=run["head_sha"],
                     conclusion=run["conclusion"], jobs=len(jobs)))
    if not folder.exists():
        subprocess.run([GH, "run", "download", run_id, "--repo", REPO, "--dir", str(folder)], check=True)
    measurements = {}
    for file in folder.rglob("nasm-statistics.json"):
        row = json.loads(file.read_text(encoding="utf-8-sig"))
        key = f"{row['label']} / {row['storage']} / {row['block']}"
        if key in measurements:
            raise ValueError(f"duplicate measurement {key}")
        measurements[key] = row
    for job in jobs:
        row = measurements.get(job["name"], {"outcome": "missing-artifact", "run_id": run_id})
        row["job"] = job["name"]
        row["job_conclusion"] = job["conclusion"]
        row["job_url"] = job["html_url"]
        row["workflow_commit"] = run["head_sha"]
        row["steps"] = [
            dict(name=s["name"], conclusion=s["conclusion"],
                 started_at=s.get("started_at"), completed_at=s.get("completed_at"))
            for s in job["steps"]
        ]
        rows.append(row)

valid = [
    r for r in rows if r["job_conclusion"] == "success" and r["outcome"] == "success"
    and r["image_version"] in (OLD, NEW)
]
cobalt100_only = "--cobalt100-only" in sys.argv
if cobalt100_only:
    valid = [r for r in valid if r["cpu_name"] == ["Cobalt 100"]]
for row in valid:
    p = row["phases"]
    row["phase_seconds"] = {
        "startup_to_banner": p["chocolatey_banner"],
        "resolution_and_package": p["package_ready"] - p["chocolatey_banner"],
        "logged_package_download": p["package_ready"] - p["package_download_started"],
        "package_script_setup": p["installer_started"] - p["package_ready"],
        "installer": p["installer_completed"] - p["installer_started"],
        "finish": row["command_seconds"] - p["installer_completed"],
    }
    if any(v < 0 for v in row["phase_seconds"].values()):
        raise ValueError("non-monotonic phase timestamps")
    if any(row["whole_machine"][key] < 0 for key in (
            "cpu_busy_seconds", "disk_read_bytes", "disk_write_bytes",
            "network_received_bytes", "network_sent_bytes")):
        raise ValueError("negative machine counter delta")

groups = collections.defaultdict(list)
for row in valid:
    groups[(row["image_version"], row["storage"])].append(row)

summary = {"runs": runs, "total_jobs": len(rows), "valid_jobs": len(valid),
           "outcomes": dict(collections.Counter((r["job_conclusion"] + "/" + r["outcome"]) for r in rows)),
           "cells": [], "image_effects": []}
summary["analysis_cohort"] = "Cobalt 100 only (sensitivity)" if cobalt100_only else "All successful requested-image jobs (primary)"
summary["hardware_counts"] = dict(collections.Counter(
    " / ".join(r.get("cpu_name", ["unknown"])) for r in rows))
summary["telemetry_quality"] = {
    "disk_latency_used": False,
    "reason": "Raw average-timer deltas can wrap or reset; original snapshots were not retained. Do not infer latency from these fields.",
    "jobs_with_negative_latency": [
        r["job_url"] for r in rows if any(
            r.get("whole_machine", {}).get(k) is not None and r["whole_machine"][k] < 0
            for k in ("disk_mean_read_ms", "disk_mean_write_ms"))
    ],
}
for (image, storage), group in sorted(groups.items()):
    result = dict(image=image, storage=storage, **describe([r["command_seconds"] for r in group]))
    result["labels"] = dict(collections.Counter(r["label"] for r in group))
    result["nasm_versions"] = dict(collections.Counter(r["versions"]["nasm"] for r in group))
    result["chocolatey_versions"] = dict(collections.Counter(r["versions"]["chocolatey"] for r in group))
    result["phase_medians"] = {
        field: statistics.median(r["phase_seconds"][field] for r in group)
        for field in group[0]["phase_seconds"]
    }
    resource_fields = [
        "cpu_busy_seconds", "cpu_utilization_percent", "disk_read_bytes", "disk_write_bytes",
        "network_received_bytes", "network_sent_bytes", "disk_reads", "disk_writes",
    ]
    result["machine_medians"] = {
        field: statistics.median(r["whole_machine"][field] for r in group if r["whole_machine"].get(field) is not None)
        for field in resource_fields
        if any(r["whole_machine"].get(field) is not None for r in group)
    }
    summary["cells"].append(result)

blocks = collections.defaultdict(list)
for row in valid:
    blocks[(row["run_id"], row["block"])].append(row)
block_values = list(blocks.values())
rng = random.Random(20261021)
draws = {mode: {"absolute": [], "relative": []} for mode in ("default", "refs")}
storage_draws = {image: [] for image in (OLD, NEW)}
interaction_draws = []
for _ in range(10000):
    samples = collections.defaultdict(list)
    for block in rng.choices(block_values, k=len(block_values)):
        for row in block:
            samples[(row["image_version"], row["storage"])].append(row["command_seconds"])
    for mode in draws:
        if samples[(OLD, mode)] and samples[(NEW, mode)]:
            old = statistics.median(samples[(OLD, mode)])
            new = statistics.median(samples[(NEW, mode)])
            draws[mode]["absolute"].append(new - old)
            draws[mode]["relative"].append(100 * (new / old - 1))
    if all(samples[(image, mode)] for image in (OLD, NEW) for mode in ("default", "refs")):
        medians = {key: statistics.median(value) for key, value in samples.items()}
        for image in (OLD, NEW):
            storage_draws[image].append(medians[(image, "refs")] - medians[(image, "default")])
        interaction_draws.append(storage_draws[NEW][-1] - storage_draws[OLD][-1])
for mode in draws:
    if not groups[(OLD, mode)] or not groups[(NEW, mode)]:
        continue
    old = statistics.median(r["command_seconds"] for r in groups[(OLD, mode)])
    new = statistics.median(r["command_seconds"] for r in groups[(NEW, mode)])
    summary["image_effects"].append({
        "storage": mode, "new_minus_old_seconds": new - old, "new_vs_old_percent": 100 * (new / old - 1),
        "absolute_ci95": [quantile(draws[mode]["absolute"], p) for p in (0.025, 0.975)],
        "relative_ci95": [quantile(draws[mode]["relative"], p) for p in (0.025, 0.975)],
        "bootstrap_replicates": len(draws[mode]["absolute"]),
    })

summary["exploratory_storage_effects"] = []
for image in (OLD, NEW):
    if groups[(image, "refs")] and groups[(image, "default")]:
        delta = statistics.median(r["command_seconds"] for r in groups[(image, "refs")]) - statistics.median(
            r["command_seconds"] for r in groups[(image, "default")])
        summary["exploratory_storage_effects"].append({
            "image": image, "refs_minus_default_seconds": delta,
            "absolute_ci95": [quantile(storage_draws[image], p) for p in (0.025, 0.975)],
        })
if len(summary["exploratory_storage_effects"]) == 2:
    summary["exploratory_interaction"] = {
        "difference_of_median_differences_seconds": (
            summary["exploratory_storage_effects"][1]["refs_minus_default_seconds"] -
            summary["exploratory_storage_effects"][0]["refs_minus_default_seconds"]),
        "absolute_ci95": [quantile(interaction_draws, p) for p in (0.025, 0.975)],
    }

summary["per_label_medians"] = []
for label in sorted(set(r["label"] for r in valid)):
    for image in (OLD, NEW):
        for mode in ("default", "refs"):
            subset = [r for r in valid if r["label"] == label and r["image_version"] == image and r["storage"] == mode]
            if subset:
                summary["per_label_medians"].append({
                    "label": label, "image": image, "storage": mode,
                    **describe([r["command_seconds"] for r in subset]),
                })

summary["sampling"] = {
    "blocks": len(blocks), "seed": 20261021, "bootstrap_unit": "run ID and balanced scheduling block",
    "needs_count_driven_top_up": any(len(groups[(image, mode)]) < 25 for image in (OLD, NEW) for mode in ("default", "refs")),
}
name = ("offline-cobalt100" if cobalt100_only else "offline") if offline else "-".join(sys.argv[1:])
(HERE / f"nasm-measurements-{name}.json").write_text(json.dumps(rows, indent=2) + "\n")
(HERE / f"nasm-summary-{name}.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
