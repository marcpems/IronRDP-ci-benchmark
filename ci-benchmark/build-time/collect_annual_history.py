"""Read-only public Rust CI history collection; never dispatches workflows."""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from urllib.parse import urlencode
from collections import Counter

ROOT = Path(__file__).resolve().parent
GH = os.environ.get("GH_EXE", r"D:\copilot\tools\gh\bin\gh.exe")
REPO = "repos/rust-lang/rust"
PIN = "dba8825fe50879b22129271fb865944e384f7cce"


def api(path):
    cache = ROOT / "raw" / "annual-api"
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / (hashlib.sha256(path.encode()).hexdigest() + ".json")
    if target.exists():
        return json.loads(target.read_text(encoding="utf-8"))
    for attempt in range(3):
        process = subprocess.run([GH, "api", path], capture_output=True, encoding="utf-8")
        if process.returncode == 0:
            value = json.loads(process.stdout)
            target.write_text(process.stdout, encoding="utf-8")
            return value
        time.sleep(2 ** attempt)
    raise RuntimeError(f"read failed: {path}: {process.stderr}")


def pages(path, key, params=None):
    result = []
    expected = None
    for page in range(1, 11):
        response = api(path + "?" + urlencode({**(params or {}), "per_page": 100, "page": page}))
        if expected is None:
            expected = response["total_count"]
            if expected > 1000:
                raise ValueError("split sampling window: API search ceiling exceeded")
        result.extend(response[key])
        if len(result) >= expected:
            break
    if len(result) != expected:
        raise ValueError(f"incomplete pagination: {len(result)} != {expected}")
    return result


def collect_day(day):
    query = {"created": f"{day}T00:00:00Z..{day}T23:59:59Z"}
    runs = pages(f"{REPO}/actions/workflows/ci.yml/runs", "workflow_runs", query)
    if any(r["created_at"][:10] != day for r in runs):
        raise ValueError("API returned a run outside the requested day")
    return runs


def collect_jobs(run):
    attempts = []
    for attempt in range(1, run["run_attempt"] + 1):
        path = f"{REPO}/actions/runs/{run['id']}/attempts/{attempt}/jobs"
        jobs = pages(path, "jobs")
        attempts.append({
            "attempt": attempt,
            "api_path": path,
            "all_job_names": [j["name"] for j in jobs],
            "all_job_conclusions": dict(Counter(j["conclusion"] for j in jobs)),
            "jobs": [{
                **{k: j.get(k) for k in ("id", "name", "status", "conclusion", "created_at",
                                       "started_at", "completed_at", "labels", "html_url")},
                "build_steps": [
                    {k: s.get(k) for k in ("name", "status", "conclusion", "started_at", "completed_at")}
                    for s in j.get("steps", []) if s["name"] == "run the build"],
            } for j in jobs if "aarch64-msvc" in j["name"] or
                any("windows" in label and "arm" in label for label in j.get("labels", []))],
        })
    channel = None
    if run["event"] == "push":
        response = api(f"{REPO}/contents/src/ci/channel?ref={run['head_sha']}")
        channel = base64.b64decode(response["content"]).decode().strip()
    return {"run_id": run["id"], "channel": channel, "attempts": attempts}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2026-09-25")
    parser.add_argument("--end", default="2026-10-02", help="exclusive UTC date")
    args = parser.parse_args()
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    if not 0 < (end - start).days <= 35:
        raise ValueError("choose a positive sampling interval of at most 35 days")
    days = [(start + timedelta(days=i)).isoformat() for i in range((end - start).days)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        batches = list(pool.map(collect_day, days))
    runs = sorted((r for batch in batches for r in batch), key=lambda r: r["created_at"])
    if len({r["id"] for r in runs}) != len(runs):
        raise ValueError("duplicate workflow runs")
    selected = [r for r in runs if r["event"] == "push"]
    for day in days:
        for conclusion in ("success", "cancelled"):
            candidates = [r for r in runs if r["event"] == "pull_request" and
                          r["created_at"].startswith(day) and r["conclusion"] == conclusion]
            if candidates:
                selected.append(candidates[0])
    print(f"Collected {len(runs)} CI invocations; inspecting all {len(selected)} selected run job histories",
          flush=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        details = list(pool.map(collect_jobs, selected))
    evidence = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "start_inclusive": str(start), "end_exclusive": str(end),
        "repository": "rust-lang/rust", "workflow": ".github/workflows/ci.yml",
        "selection": "All CI invocations; every push job/attempt; first successful and cancelled PR per UTC day",
        "source_pin": PIN,
        "daily_counts": {day: len(batch) for day, batch in zip(days, batches)},
        "raw_runs_sha256": hashlib.sha256(json.dumps(runs, sort_keys=True).encode()).hexdigest(),
        "runs": [{
            **{k: r.get(k) for k in ("id", "created_at", "run_started_at", "updated_at", "event",
                                   "head_branch", "head_sha", "status", "conclusion", "run_attempt",
                                   "html_url")},
            "commit_subject": (r.get("head_commit") or {}).get("message", "").split("\n")[0],
        } for r in runs],
        "details": details,
    }
    target = ROOT / "data" / f"annual-history-{start}-{end}.json"
    target.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {target.name}: {len(details)} job histories", flush=True)


if __name__ == "__main__":
    main()
