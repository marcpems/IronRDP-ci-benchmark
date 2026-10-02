"""Reduce saved public GitHub run/job API responses into auditable timing data."""

import argparse
from datetime import datetime
import json
from pathlib import Path


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def minutes(start, end):
    return round((timestamp(end) - timestamp(start)).total_seconds() / 60, 3)


def read_pages(path):
    text = path.read_text(encoding="utf-8-sig")
    decoder = json.JSONDecoder()
    while text.strip():
        value, end = decoder.raw_decode(text.lstrip())
        yield value
        text = text.lstrip()[end:]


def summarize(directory, run_id):
    run = next(read_pages(directory / f"run-{run_id}.json"))
    jobs = [job for page in read_pages(directory / f"jobs-{run_id}.json") for job in page["jobs"]]
    selected = []
    for job in jobs:
        if not any(name in job["name"] for name in ("aarch64-msvc", "dist-x86_64-msvc")):
            continue
        build = next(step for step in job["steps"] if step["name"] == "run the build")
        selected.append({
            "name": job["name"], "job_id": job["id"], "url": job["html_url"],
            "labels": job["labels"], "started": job["started_at"],
            "job_minutes": minutes(job["started_at"], job["completed_at"]),
            "build_minutes": minutes(build["started_at"], build["completed_at"]),
            "other_step_minutes": round(
                minutes(job["started_at"], job["completed_at"]) -
                minutes(build["started_at"], build["completed_at"]), 3),
        })
    return {
        "run_id": run_id, "url": run["html_url"], "sha": run["head_sha"],
        "created": run["created_at"], "conclusion": run["conclusion"],
        "created_to_updated_minutes": minutes(run["created_at"], run["updated_at"]),
        "job_span_minutes": minutes(min(j["started_at"] for j in jobs),
                                   max(j["completed_at"] for j in jobs)),
        "matrix_jobs": len(jobs),
        "selected_jobs": selected,
        "last_finishing_jobs": [
            {"name": j["name"], "id": j["id"], "completed": j["completed_at"],
             "job_minutes": minutes(j["started_at"], j["completed_at"])}
            for j in sorted(jobs, key=lambda j: j["completed_at"])[-5:]
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("run_ids", nargs="+", type=int)
    args = parser.parse_args()
    print(json.dumps([summarize(args.directory, run_id) for run_id in args.run_ids], indent=2))
