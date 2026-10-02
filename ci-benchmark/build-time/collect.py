"""Collect completed public production CI metadata; never stores credentials."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from datetime import datetime

ROOT = Path(__file__).resolve().parent
GH = os.environ.get("GH_EXE", r"D:\copilot\tools\gh\bin\gh.exe")
REPO = "rust-lang/rust"
RUNS = [33865610474, 33916006473, 33961251131]


def api(path):
    return subprocess.check_output([GH, "api", "--allow-escape-sequences", path])


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def seconds(start, end):
    if not start or not end:
        return None
    return (datetime.fromisoformat(end.replace("Z", "+00:00")) -
            datetime.fromisoformat(start.replace("Z", "+00:00"))).total_seconds()


def collect(run_id, logs):
    dest = ROOT / "data" / str(run_id)
    run = json.loads(api(f"repos/{REPO}/actions/runs/{run_id}"))
    assert run["status"] == "completed"
    keys = ["id", "name", "event", "head_sha", "head_branch", "status",
            "conclusion", "created_at", "run_started_at", "updated_at", "html_url"]
    save(dest / "run.json", {k: run.get(k) for k in keys})
    jobs = []
    page = 1
    while True:
        batch = json.loads(api(f"repos/{REPO}/actions/runs/{run_id}/jobs?per_page=100&page={page}"))["jobs"]
        jobs.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    result = []
    for job in jobs:
        keys = ["id", "name", "status", "conclusion", "started_at", "completed_at",
                "runner_name", "runner_group_name", "labels", "html_url", "steps"]
        row = {k: job.get(k) for k in keys}
        row["elapsed_seconds"] = seconds(row["started_at"], row["completed_at"])
        for step in row["steps"]:
            step["elapsed_seconds"] = seconds(step.get("started_at"), step.get("completed_at"))
        result.append(row)
    save(dest / "jobs.json", result)
    if logs:
        selected = {"auto - dist-aarch64-msvc", "auto - aarch64-msvc-1",
                    "auto - aarch64-msvc-2", "auto - dist-x86_64-msvc",
                    "auto - dist-aarch64-linux", "auto - dist-x86_64-linux"}
        selected.add(max(jobs, key=lambda j: j["completed_at"] or "")["name"])
        selected.add(max(jobs, key=lambda j: seconds(j["started_at"], j["completed_at"]) or 0)["name"])
        for job in jobs:
            if job["name"] not in selected:
                continue
            raw_path = ROOT / "raw" / f'{job["id"]}.log'
            raw_path.parent.mkdir(exist_ok=True)
            try:
                raw = raw_path.read_bytes() if raw_path.exists() else api(f'repos/{REPO}/actions/jobs/{job["id"]}/logs')
                raw_path.write_bytes(raw)
            except subprocess.CalledProcessError as error:
                save(dest / f'{job["id"]}-log.json', {"error": str(error)})
                continue
            text = raw.decode("utf-8", errors="replace")
            events = []
            pattern = re.compile(r"(##\[group\]|##\[endgroup\]|finished in|"
                                 r"opt_dist::timer|[Tt]otal time|[Bb]uild completed|"
                                 r"Cache hits|Cache misses|cpu cores|MemTotal|"
                                 r"clang version|Image:|Version:|LLVM_VERSION_SUFFIX|"
                                 r"Dist |building `msi`)")
            for number, line in enumerate(text.splitlines(), 1):
                if pattern.search(line):
                    events.append({"line": number, "text": line})
            save(dest / f'{job["id"]}-log.json', {
                "job_id": job["id"], "name": job["name"],
                "source": f"https://api.github.com/repos/{REPO}/actions/jobs/{job['id']}/logs",
                "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "events": events})
    print(f"{run_id}: {len(jobs)} completed jobs")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", nargs="+", type=int, default=RUNS)
    parser.add_argument("--logs", action="store_true")
    args = parser.parse_args()
    for run_id in args.runs:
        collect(run_id, args.logs)
