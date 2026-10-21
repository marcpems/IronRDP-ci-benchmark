"""Collect only relevant facts from public GitHub job logs; retain no credentials."""
import argparse
import json
import pathlib
import re
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--jobs", type=pathlib.Path, required=True)
parser.add_argument("--gh", required=True)
parser.add_argument("--output", type=pathlib.Path, required=True)
args = parser.parse_args()
jobs = json.loads(args.jobs.read_text(encoding="utf-8-sig"))["jobs"]
run_id = jobs[0]["run_id"]
caches = json.loads(subprocess.check_output([
    args.gh, "api",
    f"repos/marcpems/IronRDP-ci-benchmark/actions/caches?key=nasm-omission-{run_id}&per_page=100",
], encoding="utf-8"))
if caches["total_count"] > len(caches["actions_caches"]):
    raise RuntimeError("Cache inventory requires pagination")
args.output.with_name("cache-inventory.json").write_text(json.dumps(caches, indent=2) + "\n")
details = []
for job in jobs:
    if job["status"] != "completed":
        raise RuntimeError(f"Job {job['id']} is not complete")
    log = subprocess.check_output([
        args.gh, "api",
        f"repos/marcpems/IronRDP-ci-benchmark/actions/jobs/{job['id']}/logs",
        "--allow-escape-sequences",
    ], encoding="utf-8", errors="replace")
    log = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", log)
    images = re.findall(r"Image: (win[\w-]+) (\d{8}\.\d+\.\d+)", log)
    cpus = sorted(set(re.findall(r'"Name": "(Cobalt \d+)"', log)))
    if len(images) != 1 or len(cpus) != 1:
        raise RuntimeError(f"Missing or ambiguous runner metadata for job {job['id']}")
    label, package, variant, sample = job["name"].split(" / ")
    prefix = f"nasm-omission-{run_id}-{label}-{package}-{variant}-{sample}-"
    details.append({
        "job_id": job["id"], "name": job["name"], "conclusion": job["conclusion"],
        "image": images[0][0], "image_version": images[0][1], "cpu": cpus[0],
        "nasm_absence_verified": bool(re.search(r"Z NASM is absent; native Arm release build must succeed without it\.", log)),
        "link_errors": [line for line in log.splitlines() if re.search(r"error LNK\d+", line)],
        "missing_symbols": sorted(set(re.findall(r"__imp_(?:floor|lrintf)", log))),
        "cache_persisted": any(cache["key"].startswith(prefix) for cache in caches["actions_caches"]),
    })
args.output.write_text(json.dumps(details, indent=2) + "\n")
print(json.dumps(details, indent=2))
