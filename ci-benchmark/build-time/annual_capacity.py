"""Offline annual demand/cost and one-runner FCFS capacity sensitivities."""
from collections import Counter
from datetime import datetime
import json
import math
from pathlib import Path
import re
import statistics

from balanced_model import build as balanced_build

ROOT = Path(__file__).resolve().parent
HISTORIES = [ROOT / "data" / f"annual-history-{start}-{end}.json"
             for start, end in (("2026-09-18", "2026-09-25"), ("2026-09-25", "2026-10-02"))]
YEAR_MINUTES = 365 * 24 * 60


def stamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() / 60


def kind(run):
    if run["event"] == "pull_request":
        return "pr"
    return run["head_branch"].rsplit("/", 1)[-1]


def job_kind(name):
    if name.endswith("dist-aarch64-msvc"):
        return "dist"
    if name.endswith(("aarch64-msvc-1", "aarch64-msvc-2")):
        return "test"
    if name.endswith("dist-aarch64-llvm-mingw"):
        return "gnullvm_dist"
    return "other"


def elapsed(job):
    if not job["started_at"] or not job["completed_at"]:
        return 0
    return max(0, stamp(job["completed_at"]) - stamp(job["started_at"]))


def summarize_history(history):
    runs = {r["id"]: r for r in history["runs"]}
    groups = {}
    for name in sorted({kind(r) for r in runs.values()}):
        selected = [r for r in runs.values() if kind(r) == name]
        groups[name] = {
            "runs": len(selected),
            "conclusions": dict(Counter(r["conclusion"] for r in selected)),
            "additional_run_attempts": sum(r["run_attempt"] - 1 for r in selected),
        }
    jobs = []
    inspected_pr = 0
    for detail in history["details"]:
        run = runs[detail["run_id"]]
        inspected_pr += run["event"] == "pull_request"
        for attempt in detail["attempts"]:
            for job in attempt["jobs"]:
                jobs.append({
                    "run_id": run["id"], "attempt": attempt["attempt"], "job_id": job["id"],
                    "job_name": job["name"], "kind": job_kind(job["name"]), "run_kind": kind(run),
                    "source_sha": run["head_sha"], "channel": detail["channel"],
                    "run_created_at": run["created_at"],
                    "arrival": job.get("created_at") or run["created_at"],
                    "completed_at": job["completed_at"],
                    "conclusion": job["conclusion"], "wall_minutes": elapsed(job),
                    "build_started": any(s["started_at"] and s["conclusion"] != "skipped"
                                         for s in job["build_steps"]),
                    "url": job["html_url"],
                })
    if len({j["job_id"] for j in jobs}) != len(jobs):
        raise ValueError("duplicate jobs would double-count retries")
    result = {
        "start_inclusive": history["start_inclusive"], "end_exclusive": history["end_exclusive"],
        "days": (stamp(history["end_exclusive"] + "T00:00:00Z") -
                 stamp(history["start_inclusive"] + "T00:00:00Z")) / 1440,
        "workflow_groups": groups, "inspected_pr_runs": inspected_pr, "jobs": jobs,
        "repeated_auto_pr_subjects": dict(Counter(
            match.group(1) for run in runs.values() if kind(run) == "auto"
            if (match := re.search(r"Auto merge of #(\d+)", run.get("commit_subject", ""))))),
    }
    result["repeated_auto_pr_subjects"] = {
        key: count for key, count in result["repeated_auto_pr_subjects"].items() if count > 1}
    for name in ("dist", "test", "gnullvm_dist", "other"):
        selected = [j for j in jobs if j["kind"] == name]
        successes = [j["wall_minutes"] for j in selected if j["conclusion"] == "success"]
        result[name] = {
            "scheduled_job_attempts": len(selected),
            "build_started": sum(j["build_started"] for j in selected),
            "conclusions": dict(Counter(j["conclusion"] for j in selected)),
            "by_run_kind": dict(Counter(j["run_kind"] for j in selected)),
            "by_channel": dict(Counter(j["channel"] for j in selected)),
            "distinct_source_shas": len({j["source_sha"] for j in selected}),
            "rerun_job_attempts": sum(j["attempt"] > 1 for j in selected),
            "daily_by_run_cohort": {
                day: sum(j["run_created_at"].startswith(day) for j in selected)
                for day in history["daily_counts"]},
            "observed_runner_wall_minutes": sum(j["wall_minutes"] for j in selected),
            "successful_job_median_minutes": statistics.median(successes) if successes else None,
            "successes_by_channel": dict(Counter(j["channel"] for j in selected
                                                if j["conclusion"] == "success")),
            "cancelled_runner_wall_minutes": sum(j["wall_minutes"] for j in selected
                                                if j["conclusion"] == "cancelled"),
        }
    return result


def annual_cost(attempts, job_minutes, rate, availability=0.95, target_utilization=0.70):
    if attempts < 0 or not job_minutes or any(t <= 0 for t in job_minutes) or rate < 0:
        raise ValueError("invalid annual work input")
    if not 0 < availability <= 1 or not 0 < target_utilization <= 1:
        raise ValueError("invalid capacity fraction")
    minutes = attempts * sum(job_minutes)
    billed = attempts * sum(math.ceil(round(t, 9)) for t in job_minutes)
    capacity = YEAR_MINUTES * availability
    return {
        "attempts_per_year": attempts, "runner_wall_minutes": minutes,
        "billed_runner_minutes": billed, "compute_usd": billed * rate,
        "availability_assumed": availability,
        "utilization_of_available_time": minutes / capacity,
        "required_runners_at_70_percent": math.ceil(minutes / (capacity * target_utilization)),
        "fits_aggregate_one_runner": minutes <= capacity,
        "fits_job_limit": max(job_minutes) <= 360,
        "annual_attempt_capacity_at_70_percent": capacity * target_utilization / sum(job_minutes),
    }


def queue_replay(arrivals, service_minutes):
    """One nonpreemptive runner, empty initial queue; cancelled requests not removed."""
    if service_minutes <= 0:
        raise ValueError("service time must be positive")
    arrivals = sorted(arrivals)
    if not arrivals:
        return {"requests": 0, "max_wait_minutes": 0, "p95_wait_minutes": 0,
                "median_wait_minutes": 0, "last_completion_after_last_arrival_minutes": 0}
    free = arrivals[0]
    waits = []
    for arrival in arrivals:
        start = max(free, arrival)
        waits.append(start - arrival)
        free = start + service_minutes
    ordered = sorted(waits)
    return {
        "requests": len(arrivals), "max_wait_minutes": max(waits),
        "p95_wait_minutes": ordered[math.ceil(0.95 * len(ordered)) - 1],
        "median_wait_minutes": statistics.median(waits),
        "last_completion_after_last_arrival_minutes": free - arrivals[-1],
        "note": "Conditional FCFS replay, full duration for every scheduled attempt; no observed cancellation cutoffs, maintenance, extra retries or preexisting backlog.",
    }


def cancellation_replay(jobs, stage_minutes):
    """Keep original external cancellation deadlines; not a future failure forecast."""
    free = 0
    wall = billed = skipped = 0
    waits = []
    for job in sorted(jobs, key=lambda j: stamp(j["arrival"])):
        arrival = stamp(job["arrival"])
        start = max(free, arrival)
        deadline = (stamp(job["completed_at"]) if job["conclusion"] == "cancelled"
                    else math.inf)
        if start >= deadline:
            skipped += 1
            continue
        duration = min(sum(stage_minutes), deadline - start)
        waits.append(start - arrival)
        wall += duration
        remaining = duration
        for stage in stage_minutes:
            used = min(stage, remaining)
            billed += math.ceil(round(used, 9))
            remaining -= used
        free = start + duration
    return {
        "runner_wall_minutes": wall, "rounded_job_minutes": billed,
        "cancelled_before_service": skipped,
        "max_wait_minutes": max(waits, default=0),
        "median_wait_minutes": statistics.median(waits) if waits else 0,
        "note": "Counterfactual only: original cancellation timestamps fixed, one runner, no maintenance or additional retries; successful original requests complete the modeled build.",
    }


def build():
    histories = [json.loads(path.read_text(encoding="utf-8")) for path in HISTORIES]
    history = {
        "start_inclusive": min(h["start_inclusive"] for h in histories),
        "end_exclusive": max(h["end_exclusive"] for h in histories),
        "runs": [r for h in histories for r in h["runs"]],
        "details": [d for h in histories for d in h["details"]],
        "daily_counts": {k: v for h in histories for k, v in h["daily_counts"].items()},
    }
    summary = summarize_history(history)
    config, balanced = balanced_build()
    def scenario(budget, scaling, layout):
        row = next(r for r in balanced["results"] if r["hardware"] == "native32" and
                   (r["budget"], r["scaling"], r["layout"]) == (budget, scaling, layout))
        return [j["duration_minutes"] for j in row["jobs"]]
    durations = {
        "stock_reference_not_32cpu_measurement": [config["cold_baseline"]["job_minutes"]],
        "central_optimized": scenario("planning", "balanced", "serial"),
        "adverse_optimized": scenario("planning", "constrained", "serial"),
        "stress_two_job": scenario("stress", "constrained", "two_job"),
    }
    factor = 365 / summary["days"]
    scheduled = summary["dist"]["scheduled_job_attempts"]
    started = summary["dist"]["build_started"]
    volumes = {
        "one_daily_release_candidate_only": 365,
        "observed_build_started_annualized": started * factor,
        "observed_scheduled_attempts_annualized": scheduled * factor,
        "scheduled_plus_20_percent_growth": scheduled * factor * 1.2,
    }
    rate = config["hardware"]["native32"]["usd_per_minute"]
    rows = [{"volume": name, "duration": duration,
             **annual_cost(attempts, times, rate)}
            for name, attempts in volumes.items() for duration, times in durations.items()]
    arrivals = [stamp(j["arrival"]) for j in summary["jobs"] if j["kind"] == "dist"]
    queue = {name: queue_replay(arrivals, sum(times)) for name, times in durations.items()}
    cancelled = {}
    for name, times in durations.items():
        replay = cancellation_replay([j for j in summary["jobs"] if j["kind"] == "dist"], times)
        replay.update({
            "annual_runner_wall_minutes": replay["runner_wall_minutes"] * factor,
            "annual_compute_usd": replay["rounded_job_minutes"] * factor * rate,
            "utilization_of_available_time": replay["runner_wall_minutes"] * factor /
                                             (YEAR_MINUTES * 0.95),
        })
        cancelled[name] = replay
    # Existing native test durations are not presumed to scale like optimized dist.
    test_attempts = summary["test"]["scheduled_job_attempts"] * factor
    consolidation = [
        {"assumed_minutes_per_test_job": minutes,
         "tests_only": annual_cost(test_attempts, [minutes], rate),
         "tests_plus_gnullvm": annual_cost(
             test_attempts + summary["gnullvm_dist"]["scheduled_job_attempts"] * factor,
             [minutes], rate)}
        for minutes in (45, 90, 135)]
    return {
        "history": summary,
        "weekly_summaries": [{k: v for k, v in summarize_history(h).items() if k != "jobs"}
                             for h in histories],
        "rate_usd_per_minute": rate,
        "assumptions": {
            "availability": 0.95, "target_utilization": 0.70,
            "concurrency": 1, "year_days": 365,
            "attempt_accounting": "Observed rates already include reruns/cancellations; no additional probability retry multiplier.",
            "stock_reference": "141.82 minutes measured on 4-CPU stock, not optimized or measured 32-vCPU; hypothetical same-duration charge only.",
        },
        "durations_minutes": durations, "annual": rows, "queue_replay": queue,
        "fixed_cancellation_replay": cancelled,
        "additional_test_consolidation": consolidation,
        "dist_service_budget_at_observed_rate": {
            "minutes_per_scheduled_attempt_at_full_available_capacity":
                YEAR_MINUTES * 0.95 / (scheduled * factor),
            "minutes_per_scheduled_attempt_at_70_percent":
                YEAR_MINUTES * 0.95 * 0.70 / (scheduled * factor),
        },
        "full_year_continuous_active_rate_equivalent_usd": YEAR_MINUTES * rate,
    }


def main():
    output = build()
    (ROOT / "annual-results.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Annual one-runner sensitivity tables",
        "",
        "Generated by `annual_capacity.py`. 365-day year; 95% availability; 70% planning",
        "utilization ceiling. Native Windows Arm64 rate $0.098/min. Historical counts",
        "are attempts, including cancellation/retry attempts, not guaranteed qualified builds.",
        "Full-duration budgeting of cancelled/pre-build requests is conservative; no second",
        "retry multiplier is applied. Fractional annual counts are extrapolated rates.",
        "",
        "| Annual volume / duration scenario | Attempts/year | Runner wall min | Billed min | USD/year | Utilization | Runners at 70% |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in output["annual"]:
        lines.append(f'| {row["volume"]} / {row["duration"]} | {row["attempts_per_year"]:.1f} | '
                     f'{row["runner_wall_minutes"]:,.0f} | {row["billed_runner_minutes"]:,.0f} | '
                     f'${row["compute_usd"]:,.0f} | {100*row["utilization_of_available_time"]:.1f}% | '
                     f'{row["required_runners_at_70_percent"]} |')
    lines += ["", "## Conditional single-runner FCFS replay", "",
              "| Duration scenario | Median wait | p95 wait | Max wait |",
              "|---|---:|---:|---:|"]
    for name, queue in output["queue_replay"].items():
        lines.append(f'| {name} | {queue["median_wait_minutes"]:.1f} | '
                     f'{queue["p95_wait_minutes"]:.1f} | {queue["max_wait_minutes"]:.1f} |')
    lines += ["", "Waits are minutes, not measured queue latency. All scheduled requests are",
              "retained at full modeled duration; see JSON for scope/assumptions and source jobs.",
              "The stock reference is measured on four CPUs without PGO, not a 32-vCPU forecast.",
              "A >100% load is required work/cost on sufficient capacity, not achievable one-runner throughput.",
              ""]
    lines += ["## Fixed historical cancellation deadlines (conditional)", "",
              "| Duration | Annual active minutes | Annual compute | Utilization | Skipped before service |",
              "|---|---:|---:|---:|---:|"]
    for name, replay in output["fixed_cancellation_replay"].items():
        lines.append(f'| {name} | {replay["annual_runner_wall_minutes"]:,.0f} | '
                     f'${replay["annual_compute_usd"]:,.0f} | '
                     f'{100*replay["utilization_of_available_time"]:.1f}% | '
                     f'{replay["cancelled_before_service"]} |')
    lines += ["", "This sensitivity retains original external cancellations, not future guaranteed",
              "cancellation rates. It is not a lower confidence bound or a promise of equivalent",
              "release latency. Do not rely on other-platform failures to make capacity fit.", ""]
    (ROOT / "ANNUAL-TABLES.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
