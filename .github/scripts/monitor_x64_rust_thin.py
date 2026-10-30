"""One bounded, attached, read-only completion monitor for the hosted ThinLTO pilot."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def identity(run, run_id, head, attempt, branch="experiment/x64-rust-thin-incremental",
             workflow=".github/workflows/x64-rust-thin-incremental.yml"):
    if (str(run["id"]) != run_id or run["head_sha"] != head
            or run["run_attempt"] != attempt
            or run["head_branch"] != branch or run["path"] != workflow):
        raise RuntimeError("Run/head/attempt/workflow identity changed; refusing to follow it")


def command(gh, arguments, deadline, events, timeout=180):
    last_error = None
    for retry in range(8):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("The bounded completion monitor reached its deadline")
        try:
            result = subprocess.run(
                [str(gh), *arguments], capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=min(timeout, remaining),
            )
            if result.returncode == 0:
                return result.stdout
            last_error = result.stderr[-4000:] or result.stdout[-4000:]
        except subprocess.TimeoutExpired as error:
            last_error = str(error)
        with events.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"unix": time.time(), "retry": retry + 1,
                                     "command": arguments, "error": last_error}) + "\n")
        if retry != 7:
            time.sleep(min(2 ** retry, max(0, deadline - time.monotonic())))
    raise RuntimeError(f"GitHub command failed after eight attempts: {last_error}")


def monitor(args):
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    deadline = time.monotonic() + args.hours * 3600
    events = output / "network-retries.jsonl"
    expected = {
        "run_id": args.run_id, "head_sha": args.head, "attempt": args.attempt,
        "repository": args.repository, "started_unix": time.time(),
        "maximum_hours": args.hours, "interval_seconds": args.interval,
        "attached": True, "read_only": True, "complete": False,
        "branch": args.branch, "workflow": args.workflow, "producer_run": args.producer_run,
    }
    save(output / "monitor.json", expected)

    def gh(arguments, timeout=180):
        return command(args.gh, arguments, deadline, events, timeout)

    try:
        while True:
            run = json.loads(gh(["api", f"repos/{args.repository}/actions/runs/{args.run_id}"]))
            identity(run, args.run_id, args.head, args.attempt, args.branch, args.workflow)
            jobs = json.loads(gh([
                "api", f"repos/{args.repository}/actions/runs/{args.run_id}/attempts/{args.attempt}/jobs",
                "-f", "per_page=100", "--method", "GET",
            ]))
            for job in jobs["jobs"]:
                if (job["labels"] != ["windows-2022"]
                        and not (job["conclusion"] == "skipped" and not job["labels"])):
                    raise RuntimeError("Unexpected runner label; monitor never permits self-hosted work")
            save(output / "run.json", run)
            save(output / "jobs.json", jobs)
            status = {
                "unix": time.time(), "status": run["status"], "conclusion": run["conclusion"],
                "jobs": [{key: job.get(key) for key in
                          ("id", "name", "status", "conclusion", "runner_name", "labels")}
                         for job in jobs["jobs"]],
            }
            with (output / "status.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(status) + "\n")
            if run["status"] == "completed":
                break
            time.sleep(min(args.interval, max(0, deadline - time.monotonic())))

        inventory = json.loads(gh([
            "api", f"repos/{args.repository}/actions/runs/{args.run_id}/artifacts",
            "-f", "per_page=100", "--method", "GET",
        ]))
        save(output / "artifact-inventory.json", inventory)
        downloaded = []
        for artifact in inventory["artifacts"]:
            name = artifact["name"]
            if not name.startswith("thin-"):
                raise RuntimeError(f"Unexpected study artifact: {name}")
            if artifact["expired"]:
                raise RuntimeError(f"Required terminal evidence expired: {name}")
            destination = output / "artifacts" / name
            destination.mkdir(parents=True, exist_ok=True)
            gh(["run", "download", args.run_id, "--repo", args.repository,
                "--name", name, "--dir", str(destination)], timeout=900)
            files = {}
            for file in sorted(destination.rglob("*")):
                if file.is_file():
                    with file.open("rb") as stream:
                        sha = hashlib.file_digest(stream, "sha256").hexdigest()
                    files[file.relative_to(destination).as_posix()] = {
                        "sha256": sha, "bytes": file.stat().st_size,
                    }
            downloaded.append({"id": artifact["id"], "name": name, "files": files})
            save(output / "download-manifest.json", downloaded)
        if run["conclusion"] != "success":
            failed_log = gh(["run", "view", args.run_id, "--repo", args.repository,
                             "--log-failed"], timeout=300)
            (output / "failed-job-logs.txt").write_text(failed_log, encoding="utf-8")
            raise RuntimeError(f"Remote run concluded {run['conclusion']}; original evidence retained")
        identity(json.loads(gh(["api", f"repos/{args.repository}/actions/runs/{args.run_id}"])),
                 args.run_id, args.head, args.attempt, args.branch, args.workflow)
        if args.producer_run:
            producer = json.loads(gh(["api", f"repos/{args.repository}/actions/runs/{args.producer_run}"]))
            identity(producer, args.producer_run, args.producer_head, 1)
            save(output / "producer-run.json", producer)
            for arm in ("baseline", "rust-thin"):
                for kind in ("evidence", "package"):
                    name = f"thin-{arm}-{kind}"
                    destination = output / "artifacts" / name
                    destination.mkdir(parents=True, exist_ok=True)
                    gh(["run", "download", args.producer_run, "--repo", args.repository,
                        "--name", name, "--dir", str(destination)], timeout=900)
        verifier = Path(__file__).with_name("verify_x64_rust_thin.py")
        result = subprocess.run(
            [sys.executable, str(verifier), "--artifacts", str(output / "artifacts"),
             "--run-id", args.run_id, "--head", args.head, "--attempt", str(args.attempt),
             "--output", str(output / "verified-results.json")],
            capture_output=True, text=True, timeout=min(1800, max(1, deadline - time.monotonic())),
        )
        (output / "verification.stdout").write_text(result.stdout, encoding="utf-8")
        (output / "verification.stderr").write_text(result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(f"Independent verification failed: {result.stderr[-3000:]}")
        save(output / "monitor.json", {**expected, "complete": True, "finished_unix": time.time(),
                                      "remote_conclusion": run["conclusion"],
                                      "verified_results": "verified-results.json"})
        print((output / "verified-results.json").read_text(encoding="utf-8"), flush=True)
    except Exception as error:
        save(output / "monitor-failure.json", {
            **expected, "error": str(error), "finished_unix": time.time(),
            "performance_accepted": False,
        })
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gh", type=Path, required=True)
    parser.add_argument("--repository", default="marcpems/IronRDP-ci-benchmark")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--hours", type=float, default=12)
    parser.add_argument("--interval", type=int, default=120)
    parser.add_argument("--branch", default="experiment/x64-rust-thin-incremental")
    parser.add_argument("--workflow", default=".github/workflows/x64-rust-thin-incremental.yml")
    parser.add_argument("--producer-run")
    parser.add_argument("--producer-head")
    options = parser.parse_args()
    if not 0 < options.hours <= 12 or options.interval < 30:
        parser.error("Use a positive bound of at most twelve hours and intervals of at least thirty seconds")
    if bool(options.producer_run) != bool(options.producer_head):
        parser.error("Producer run and head must be supplied together")
    monitor(options)
