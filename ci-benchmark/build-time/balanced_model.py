"""Offline hardware, dependency, billing and failure sensitivities."""
import json
import math
from pathlib import Path

from project_pgo_lto import job, native_dependency_jobs, serial_jobs

ROOT = Path(__file__).resolve().parent


def scale(minutes, vcpus, serial_fraction, efficiency, memory_multiplier=1):
    if minutes < 0 or vcpus < 4 or not 0 <= serial_fraction <= 1:
        raise ValueError("invalid stage scaling input")
    if not 0 < efficiency <= 1 or memory_multiplier < 1:
        raise ValueError("invalid efficiency or memory multiplier")
    parallel_capacity = 1 + (vcpus / 4 - 1) * efficiency
    return minutes * (serial_fraction + (1 - serial_fraction) / parallel_capacity) * memory_multiplier


def rounded_minutes(jobs, fraction=1):
    if not 0 <= fraction <= 1:
        raise ValueError("invalid attempt fraction")
    return sum(math.ceil(round(j["duration_minutes"] * fraction, 9)) for j in jobs)


def completed_cost(success_cost, failed_cost, probability):
    if not 0 < probability <= 1 or min(success_cost, failed_cost) < 0:
        raise ValueError("invalid qualification cost input")
    return success_cost + (1 - probability) / probability * failed_cost


def four_jobs(base, budget):
    fe, llvm, backend, final = native_dependency_jobs(base, budget)
    handoff = budget["handoff"]
    phases = lambda item: [(p["name"], p["minutes"]) for p in item["phases"]]
    # Charge compression/upload on producers and download/extraction on consumers.
    fe = job(fe["name"], 0, phases(fe) + [("Handoff/setup", handoff / 2)])
    llvm = job(llvm["name"], 0, phases(llvm) + [("Handoff/setup", handoff / 2)])
    backend = job(backend["name"], max(fe["finish_minutes"], llvm["finish_minutes"]), [
        ("Handoff/setup", budget["consumer_setup"] + handoff),
        ("Static relink", budget["static_relink"]),
        ("LLVM training", budget["llvm_training"]),
        ("Handoff/setup", handoff / 2),
    ])
    final = job(final["name"], backend["finish_minutes"], [
        ("Handoff/setup", budget["consumer_setup"] + handoff / 2),
        *phases(final)[1:],
    ])
    return [fe, llvm, backend, final]


def two_jobs(base, budget):
    phases = serial_jobs(base, budget, "fresh_dual_pgo_thinlto")[0]["phases"]
    split = next(i for i, phase in enumerate(phases) if phase["name"] == "Final compiler")
    producer = job("Fresh profile producer", 0, [
        *((p["name"], p["minutes"]) for p in phases[:split]),
        ("Handoff/setup", budget["handoff"] / 2),
    ])
    consumer = job("Final compiler + full dist + qualification", producer["finish_minutes"], [
        ("Handoff/setup", budget["consumer_setup"] + budget["handoff"] / 2),
        *((p["name"], p["minutes"]) for p in phases[split:]),
    ])
    return [producer, consumer]


def summarize(jobs, hardware, assumptions, layout):
    longest = max(j["duration_minutes"] for j in jobs)
    elapsed = max(j["finish_minutes"] for j in jobs)
    rounded = rounded_minutes(jobs)
    rate = hardware["usd_per_minute"]
    success = rounded * rate
    failure = rounded_minutes(jobs, assumptions["failed_attempt_fraction"]) * rate
    feasible = longest <= assumptions["operational_job_minutes"]
    queue = assumptions["queue_minutes_per_job"] * {"serial": 1, "two_job": 2, "four_job": 3}[layout]
    return {
        "jobs": jobs,
        "elapsed_minutes": elapsed,
        "elapsed_with_assumed_queue_minutes": elapsed + queue,
        "sum_runner_wall_minutes": sum(j["duration_minutes"] for j in jobs),
        "sum_job_rounded_minutes": rounded,
        "billed_compute_minutes": rounded if rate else 0,
        "longest_job_minutes": longest,
        "headroom_to_360_minutes": 360 - longest,
        "fits_350": feasible,
        "fits_300_acceptance_target": longest <= assumptions["acceptance_job_minutes"],
        "complete_uncapped_attempt_usd": success,
        "expected_compute_usd_per_qualified_build": (
            completed_cost(success, failure, assumptions["qualification_success_probability"])
            if feasible else None),
        "failure_probability_sensitivity_usd": {
            str(p): completed_cost(success, failure, p) if feasible else None
            for p in (0.8, 0.95, 0.99)
        },
    }


def build():
    config = json.loads((ROOT / "balanced-inputs.json").read_text(encoding="utf-8"))
    old = json.loads((ROOT / "pgo-lto-inputs.json").read_text(encoding="utf-8"))
    cold = config["cold_baseline"]
    tail = sum(cold[k] for k in ("tools_minutes", "docs_minutes", "packaging_minutes"))
    retained = cold["job_minutes"] - cold["llvm_minutes"] - cold["rustc_std_minutes"]
    base = {
        "stock_minutes": cold["job_minutes"],
        "stock_llvm_minutes": cold["llvm_minutes"],
        "retained_prefix_minutes": retained - tail,
        "retained_tail_minutes": tail,
    }
    results = []
    for budget_name in ("planning", "stress"):
        for scaling_name, scaling in config["scaling"].items():
            for hardware_name, hardware in config["hardware"].items():
                cores = hardware["vcpus"]
                # Four-CPU anchors are not slowed again by a larger-host sensitivity.
                memory = scaling["memory_multiplier"] if cores > 4 else 1

                def scaled(value, category):
                    return scale(value, cores, scaling[f"{category}_serial_fraction"],
                                 scaling["efficiency"], memory)

                budget = dict(old["scenarios"][budget_name])
                budget["seed_llvm"] = cold["llvm_minutes"]
                for stage in ("seed_llvm", "frontend_instrument", "frontend_profile_use",
                              "llvm_instrument", "static_relink", "final_thinlto"):
                    budget[stage] = scaled(budget[stage], "compile")
                for stage in ("frontend_training", "llvm_training", "extra_qualification"):
                    budget[stage] = scaled(budget[stage], "training")
                scaled_base = dict(base)
                scaled_base["retained_tail_minutes"] = sum(
                    scaled(cold[f"{category}_minutes"], category)
                    for category in ("tools", "docs", "packaging"))
                for layout in ("serial", "two_job", "four_job"):
                    def producer(b):
                        if layout == "serial":
                            return serial_jobs(scaled_base, b, "fresh_dual_pgo_thinlto")
                        if layout == "two_job":
                            return two_jobs(scaled_base, b)
                        return four_jobs(scaled_base, b)
                    value = summarize(producer(budget), hardware, config["assumptions"], layout)
                    warm = dict(budget)
                    warm["llvm_instrument"] = config["assumptions"]["instrument_restore_minutes"]
                    warm_value = summarize(producer(warm), hardware, config["assumptions"], layout)
                    hit = config["assumptions"]["instrument_cache_hit_probability"]
                    value["cache_sensitivity"] = {
                        "hit_probability_assumed": hit,
                        "cold_elapsed_minutes": value["elapsed_minutes"],
                        "hit_elapsed_minutes": warm_value["elapsed_minutes"],
                        "expected_elapsed_minutes": (1 - hit) * value["elapsed_minutes"] +
                                                    hit * warm_value["elapsed_minutes"],
                        "expected_uncapped_attempt_usd": (1 - hit) * value["complete_uncapped_attempt_usd"] +
                                                        hit * warm_value["complete_uncapped_attempt_usd"],
                        "note": "Fresh profiles and static relinks retained; cold path controls acceptance.",
                    }
                    if layout != "serial":
                        slow_transfer = dict(budget, handoff=20, consumer_setup=15)
                        slower = summarize(producer(slow_transfer), hardware,
                                           config["assumptions"], layout)
                        value["large_handoff_sensitivity"] = {
                            key: slower[key] for key in (
                                "elapsed_minutes", "sum_runner_wall_minutes",
                                "longest_job_minutes", "expected_compute_usd_per_qualified_build")
                        }
                    results.append({"budget": budget_name, "scaling": scaling_name,
                                    "hardware": hardware_name, "layout": layout, **value})
    return config, {
        "classification": config["classification"],
        "cold_accounting": {"retained_minutes": retained, **base},
        "results": results,
    }


def main():
    config, output = build()
    (ROOT / "balanced-results.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Conditional hardware/cost comparison",
        "",
        "Generated by `python balanced_model.py`; assumptions in [inputs](balanced-inputs.json).",
        "Not measured timings or confidence bounds. All rows retain fresh dual PGO, final",
        "Rust/LLVM ThinLTO, full distribution and added qualification. Standard public compute",
        "is free; larger-runner compute uses the verified native Arm64 rates.",
        "Rounded = SUM(ceil(job wall minutes)); not ceil(makespan), not vCPU-minutes.",
        "Cost/qualified assumes 95% success and failed attempts consuming half of each job.",
        "A dash means the modeled cold job exceeds the operational 350-minute cap;",
        "uncapped work is not a purchasable successful build. Queue is excluded here;",
        "JSON also adds an assumed 5 minutes per dependency level.",
        "",
        "| Budget / scaling | Runner / layout | Elapsed | SUM wall | Rounded | Longest | $ attempt / qualified |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in output["results"]:
        qualified = row["expected_compute_usd_per_qualified_build"]
        price = f"${qualified:.2f}" if qualified is not None else "—"
        lines.append(
            f'| {row["budget"]} / {row["scaling"]} | {row["hardware"]} / {row["layout"]} | '
            f'{row["elapsed_minutes"]:.1f} | {row["sum_runner_wall_minutes"]:.1f} | '
            f'{row["sum_job_rounded_minutes"]} | {row["longest_job_minutes"]:.1f} | '
            f'${row["complete_uncapped_attempt_usd"]:.2f} / {price} |')
    lines += [
        "",
        "Prices exclude plans, storage, taxes and operations. Retry sensitivity, cache-hit/miss",
        "mixtures, headroom and complete stage/job arithmetic: [balanced-results.json](balanced-results.json).",
        "Catalog specs and rates were checked on " + config["as_of"] + "; account capacity is unverified.",
        "",
    ]
    (ROOT / "BALANCED-TABLES.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
