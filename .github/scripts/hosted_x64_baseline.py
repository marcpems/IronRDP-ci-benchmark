"""Bounded public Windows production attempt; partial phases are never a full release.

Uses matched_release unchanged for configuration, fresh PGO and qualification.
An outer four-CPU Windows Job Object bounds preparation and verification as well
as production to 350 minutes from the first workflow step, reserving upload time.
"""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time

from build_arm_compilers import save
import matched_release as release
from msvc_experiment import execute


def timer_sections(path):
    active, completed = {}, []
    pattern = re.compile(
        r"^\[([^ ]+) INFO\s+opt_dist::timer\] Section `(.+)` "
        r"(starts|ended: (OK|ERROR) \(([0-9.]+)s\))")
    if path.is_file():
        with path.open(encoding="utf-8", errors="replace") as lines:
            for number, line in enumerate(lines, 1):
                match = pattern.search(line)
                if not match:
                    continue
                timestamp, name, event, status, seconds = match.groups()
                if event == "starts":
                    active[name] = {"name": name, "started_utc": timestamp, "start_line": number}
                else:
                    row = active.pop(name, {"name": name, "started_utc": None})
                    completed.append({
                        **row, "finished_utc": timestamp, "wall_seconds": float(seconds),
                        "status": status, "end_line": number,
                    })
    return {"completed": completed, "unfinished": list(active.values()),
            "source": path.name, "note": "Nested inclusive sections; do not sum parents and children."}


def summarize(source, output):
    unreadable = []

    def read(name):
        path = output / name
        try:
            return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
        except (OSError, ValueError) as error:
            unreadable.append({"file": name, "error": str(error)})
            return None

    attempt, result, failure = read("hosted-attempt.json"), read("result.json"), read("failure.json")
    complete = bool(
        result and result.get("complete") and result.get("qualification")
        and result.get("hosted_baseline") == release.HOSTED_BASELINE
        and result.get("variant") == release.SCALING_VARIANT
        and result.get("rust_sha") == release.RUST
        and result.get("runner_class") == "github-hosted"
        and result.get("full_distribution")
    )
    reason = (attempt or {}).get("stop_reason")
    if failure and failure.get("error_type") in ("TimeoutExpired", "TimeoutError"):
        reason = "deadline"
    status = "qualified-full-release" if complete else (
        "censored-deadline" if reason == "deadline" else "failed")
    production = read("distribution-timing.json")
    production_start = read("production-start.json")
    active = read("active-stage.json")
    summary = {
        "schema": 1, "study": release.HOSTED_BASELINE, "status": status,
        "complete": complete, "full_release_wall_seconds": (
            production["wall_seconds"] if complete and production else None),
        "production_finished_before_qualification": production,
        "censored_production_elapsed_seconds": (
            max(0, min(attempt["finished_unix"], attempt.get("deadline_unix", float("inf")))
                - production_start["started_unix"])
            if status == "censored-deadline" and not production and production_start and attempt
            and "finished_unix" in attempt else None),
        "attempt": attempt, "failure": failure, "active_stage": active,
        "hardware": read("hardware.json"), "provenance": read("provenance.json"),
        "unreadable_evidence": unreadable,
        "completed_commands": [
            {"evidence": path.name, "wall_seconds": row["wall_seconds"], "exit_code": row["exit_code"],
             "affinity": row.get("affinity"), "cpu_seconds": row.get("cpu_seconds")}
            for path in sorted(output.glob("*.json"))
            if isinstance(row := read(path.name), dict)
            and "wall_seconds" in row and "exit_code" in row
        ],
        "production_sections": timer_sections(output / "fresh-pgo-full-dist.stderr"),
        "bootstrap_metrics_available": (source / "build" / "metrics.json").is_file(),
        "boundaries": {
            "deadline_minutes_from_first_workflow_step": 350,
            "job_limit_minutes": 360,
            "outer_attempt_includes": "runtime preparation, helper, fresh PGO, full distribution, qualification",
            "production_clock_excludes": "source/tool preparation, qualification, uploads",
            "partial_total": "No full-release estimate; unfinished production is right-censored only on deadline.",
            "command_accounting": "Outer bounded-attempt time contains its child commands; do not sum them.",
        },
    }
    save(output / "hosted-summary.json", summary)
    return summary


def sample_storage(output, source, stop):
    with (output / "storage-samples.jsonl").open("a", encoding="utf-8") as stream:
        while True:
            usage = shutil.disk_usage(source)
            row = {"unix": time.time(), "total_bytes": usage.total, "free_bytes": usage.free}
            stream.write(json.dumps(row) + "\n")
            stream.flush()
            print(f"HOSTED STORAGE: {usage.free / 2**30:.2f} GiB free", flush=True)
            if stop.wait(60):
                break


def run(source, runtime_source, output):
    release.validate_runner("x86_64-pc-windows-msvc")
    release.validate_recipe("x86_64-pc-windows-msvc", release.SCALING_VARIANT)
    if not release.hosted_baseline():
        raise RuntimeError("this driver requires the explicit hosted baseline opt-in")
    started = time.time()
    deadline = float(os.environ["RELEASE_JOB_STARTED"]) + 350 * 60
    attempt = {
        "started_unix": started, "deadline_unix": deadline,
        "job_started_unix": float(os.environ["RELEASE_JOB_STARTED"]),
        "logical_cpus": os.cpu_count(), "build_jobs": release.build_cores(),
        "stop_reason": "running",
    }
    save(output / "hosted-attempt.json", attempt)
    stop = threading.Event()
    sampler = threading.Thread(target=sample_storage, args=(output, source, stop), daemon=True)
    sampler.start()
    exit_code = 1
    try:
        remaining = deadline - time.time()
        if remaining <= 0:
            raise TimeoutError("hosted baseline reached the 350-minute safety boundary")
        # The same Job Object measurement primitive kills the entire owned tree on timeout.
        execute(
            [sys.executable, Path(release.__file__), "--source", source, "--runtime-source",
             runtime_source, "--output", output, "--host", "x86_64-pc-windows-msvc",
             "--variant", release.SCALING_VARIANT],
            source, dict(os.environ), output, "hosted-bounded-attempt", timeout=remaining, cores=4,
        )
        attempt["stop_reason"] = "command-completed"
        exit_code = 0
    except (TimeoutError, subprocess.TimeoutExpired) as error:
        attempt.update(stop_reason="deadline", error=str(error))
    except Exception as error:
        attempt.update(stop_reason="error", error=str(error))
    finally:
        stop.set()
        sampler.join(timeout=5)
        attempt.update(finished_unix=time.time(), elapsed_seconds=time.time() - started)
        save(output / "hosted-attempt.json", attempt)
        summary = summarize(source, output)
        print(json.dumps({"status": summary["status"], "complete": summary["complete"]}), flush=True)
    return exit_code if summary["complete"] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--runtime-source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summarize-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if args.summarize_only:
        summarize(args.source.resolve(), output)
        return 0
    if args.runtime_source is None:
        parser.error("--runtime-source is required for a production attempt")
    return run(args.source.resolve(), args.runtime_source.resolve(), output)


if __name__ == "__main__":
    sys.exit(main())
