"""Summarize downloaded diagnostic artifacts without copying compiler packages."""

import argparse
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def summarize(directory, job_path):
    evidence = directory / "harness" / "arm-evidence"
    job = read_json(job_path)
    stages = [json.loads(line) for line in (evidence / "stages.jsonl").read_text().splitlines()]
    resources = [json.loads(line) for line in (evidence / "resources.jsonl").read_text().splitlines()]
    start = datetime.fromisoformat(job["started_at"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(job["completed_at"].replace("Z", "+00:00"))
    gib = 1024 ** 3
    result = {
        "job_id": job["id"], "url": job["html_url"], "conclusion": job["conclusion"],
        "started": job["started_at"], "completed": job["completed_at"],
        "job_minutes": (end - start).total_seconds() / 60,
        "stages": stages,
        "resources": {
            "sample_count": len(resources), "sample_interval_seconds": 60,
            "max_machine_physical_used_gib": max(
                (r["physical_total"] - r["physical_available"]) / gib for r in resources),
            "min_machine_physical_available_gib": min(r["physical_available"] / gib for r in resources),
            "max_machine_commit_used_gib": max(
                (r["commit_limit"] - r["commit_available"]) / gib for r in resources),
            "first_disk_free_gib": resources[0]["disk_free"] / gib,
            "min_disk_free_gib": min(r["disk_free"] / gib for r in resources),
            "last_disk_free_gib": resources[-1]["disk_free"] / gib,
            "note": "Sampled machine-wide values, not process RSS or continuous peak measurements",
        },
    }
    manifest = evidence / "dist-manifest.json"
    if manifest.is_file():
        result["dist_manifest"] = read_json(manifest)
        result["dist_bytes"] = sum(p["bytes"] for p in result["dist_manifest"])
    metrics_path = directory / "rust-source" / "build" / "metrics.json"
    if metrics_path.is_file():
        metrics = read_json(metrics_path)
        result["bootstrap_invocations"] = []
        for invocation in metrics["invocations"]:
            totals = defaultdict(float)

            def walk(nodes):
                for node in nodes:
                    if node["kind"] == "rustbuild_step":
                        category = node["type"].split("::build_steps::", 1)[-1].split("::")[0]
                        totals[category] += node["duration_excluding_children_sec"]
                    walk(node.get("children", []))

            walk(invocation["children"])
            result["bootstrap_invocations"].append({
                "cmdline": invocation["cmdline"],
                "wall_minutes": invocation["duration_including_children_sec"] / 60,
                "exclusive_category_minutes": {k: v / 60 for k, v in sorted(totals.items())},
            })
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("diagnostics", type=Path)
    parser.add_argument("job_json", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.diagnostics, args.job_json), indent=2))
