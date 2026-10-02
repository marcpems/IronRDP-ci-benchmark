"""Offline conditional production model; no downloads, builds, or runner calls."""
from datetime import datetime
from html import escape
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / "pgo-lto-inputs.json"
COLORS = {
    "Stock": "#64748b", "Setup/support": "#94a3b8", "Seed LLVM": "#eab308",
    "FE instrumentation": "#2563eb", "FE training": "#db2777",
    "FE profile-use": "#1e40af", "LLVM instrumentation": "#f97316",
    "Static relink": "#a16207", "LLVM training": "#be123c",
    "Final compiler": "#7c3aed", "Full dist remainder": "#0891b2",
    "Qualification": "#16a34a", "Handoff/setup": "#64748b", "Waiting": "#e2e8f0",
    "Plain FE + static link": "#0284c7",
    "Instrumented LLVM restore": "#ca8a04",
}


def stamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_baselines(config):
    summaries = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
    result = []
    for run in summaries:
        if run["run"]["id"] not in config["baseline_runs"]:
            continue
        job = next(j for j in run["jobs"] if j["name"] == config["baseline_job"])
        categories = job["build_categories_seconds"]
        llvm = categories["LLVM/LLD"] / 60
        compiler = categories["Compiler"] / 60
        stock = job["elapsed_seconds"] / 60
        tail = sum(categories[k] for k in ("Tools", "Libraries", "Docs", "Packaging")) / 60
        residual = stock - llvm - compiler
        jobs = json.loads((ROOT / "data" / str(run["run"]["id"]) / "jobs.json").read_text())
        actual = next(j for j in jobs if j["id"] == job["id"])
        matrix = [j for j in jobs if j["name"].startswith("auto - ")]
        origin = stamp(run["run"]["run_started_at"])
        finish = lambda j: (stamp(j["completed_at"]) - origin).total_seconds() / 60
        old_matrix_finish = max(finish(j) for j in matrix)
        result.append({
            "run_id": run["run"]["id"], "job_id": job["id"],
            "source_sha": run["run"]["head_sha"],
            "stock_minutes": stock, "stock_llvm_minutes": llvm,
            "stock_compiler_minutes": compiler,
            "retained_minutes": residual, "retained_tail_minutes": tail,
            "retained_prefix_minutes": residual - tail,
            "eligible_stage2_tools_minutes": sum(
                i["seconds"] for i in job["intervals"]
                if i["category"] == "Tools" and i["name"].startswith("Building stage2")) / 60,
            "arm_start_minutes": (stamp(actual["started_at"]) - origin).total_seconds() / 60,
            "other_matrix_finish_minutes": max(finish(j) for j in matrix if j["id"] != job["id"]),
            "workflow_suffix_minutes": run["makespan_seconds"] / 60 - old_matrix_finish,
            "stock_workflow_minutes": run["makespan_seconds"] / 60,
            "stock_runner_minutes": run["runner_seconds"] / 60,
        })
    assert len(result) == len(config["baseline_runs"])
    return result


def job(name, start, phases):
    assert all(value >= 0 for _, value in phases)
    elapsed = sum(value for _, value in phases)
    return {"name": name, "start_minutes": start, "duration_minutes": elapsed,
            "finish_minutes": start + elapsed,
            "phases": [{"name": name, "minutes": value} for name, value in phases]}


def serial_jobs(base, budget, variant):
    phases = [("Setup/support", base["retained_prefix_minutes"])]
    if variant == "stock":
        return [job("Stock full dist", 0, [("Stock", base["stock_minutes"])])]
    if variant not in ("thinlto_only", "exact_profile_consumer_only"):
        phases.append(("Setup/support", budget["profile_support"]))
    if variant == "exact_profile_consumer_only":
        phases.append(("Handoff/setup", budget["handoff"]))
    if variant == "frontend_pgo_only":
        phases += [("Seed LLVM", base["stock_llvm_minutes"]),
                   ("FE instrumentation", budget["frontend_instrument"]),
                   ("FE training", budget["frontend_training"]),
                   ("FE profile-use", budget["frontend_profile_use"])]
    elif variant in ("fresh_dual_pgo_thinlto", "fresh_dual_pgo_no_lto"):
        phases += [
            ("Seed LLVM", budget["seed_llvm"]),
            ("FE instrumentation", budget["frontend_instrument"]),
            ("FE training", budget["frontend_training"]),
            ("FE profile-use", budget["frontend_profile_use"]),
            ("LLVM instrumentation", budget["llvm_instrument"]),
            ("Static relink", budget["static_relink"]),
            ("LLVM training", budget["llvm_training"]),
            ("Final compiler", budget["final_thinlto"] if variant.endswith("thinlto")
             else budget["final_without_lto"]),
        ]
    else:
        phases.append(("Final compiler", budget["standalone_thinlto"] if variant == "thinlto_only"
                       else budget["final_thinlto"]))
    phases += [("Full dist remainder", base["retained_tail_minutes"]),
               ("Qualification", budget["extra_qualification"])]
    return [job(variant, 0, phases)]


def parallel_jobs(base, budget, independent):
    prefix = base["retained_prefix_minutes"] + budget["profile_support"]
    frontend = [("Setup/support", prefix), ("Seed LLVM", budget["seed_llvm"]),
                ("FE instrumentation", budget["frontend_instrument"]),
                ("FE training", budget["frontend_training"])]
    if not independent:
        frontend.append(("FE profile-use", budget["frontend_profile_use"]))
    fe = job("Frontend producer", 0, frontend)
    backend = [("Setup/support", prefix), ("LLVM instrumentation", budget["llvm_instrument"])]
    if independent:
        backend += [("Plain FE + static link", budget["plain_frontend_for_backend"]),
                    ("LLVM training", budget["llvm_training"] *
                     (1 + budget["backend_training_penalty"]))]
    else:
        ready = prefix + budget["llvm_instrument"]
        backend += [("Waiting", max(0, fe["finish_minutes"] - ready)),
                    ("Handoff/setup", budget["handoff"]),
                    ("Static relink", budget["static_relink"]),
                    ("LLVM training", budget["llvm_training"])]
    be = job("LLVM profile producer", 0, backend)
    final = job("Final compiler + full dist + qualification",
                max(fe["finish_minutes"], be["finish_minutes"]), [
                    ("Handoff/setup", budget["consumer_setup"] + budget["handoff"]),
                    ("Final compiler", budget["final_thinlto"]),
                    ("Full dist remainder", base["retained_tail_minutes"]),
                    ("Qualification", budget["extra_qualification"]),
                ])
    return [fe, be, final]


def native_dependency_jobs(base, budget):
    """Four jobs express the dependency barrier with ordinary job-level needs."""
    prefix = base["retained_prefix_minutes"] + budget["profile_support"]
    fe = job("Frontend producer", 0, [
        ("Setup/support", prefix), ("Seed LLVM", budget["seed_llvm"]),
        ("FE instrumentation", budget["frontend_instrument"]),
        ("FE training", budget["frontend_training"]),
        ("FE profile-use", budget["frontend_profile_use"]),
    ])
    llvm = job("Instrumented LLVM build", 0, [
        ("Setup/support", prefix), ("LLVM instrumentation", budget["llvm_instrument"]),
    ])
    backend = job("Backend relink + training", max(fe["finish_minutes"], llvm["finish_minutes"]), [
        ("Handoff/setup", budget["consumer_setup"] + 2 * budget["handoff"]),
        ("Static relink", budget["static_relink"]), ("LLVM training", budget["llvm_training"]),
    ])
    final = job("Final compiler + full dist + qualification", backend["finish_minutes"], [
        ("Handoff/setup", budget["consumer_setup"] + budget["handoff"]),
        ("Final compiler", budget["final_thinlto"]),
        ("Full dist remainder", base["retained_tail_minutes"]),
        ("Qualification", budget["extra_qualification"]),
    ])
    return [fe, llvm, backend, final]


def metrics(base, jobs, config, external_profiles=False):
    elapsed = max(j["finish_minutes"] for j in jobs)
    runners = sum(j["duration_minutes"] for j in jobs)
    largest = max(j["duration_minutes"] for j in jobs)
    limit = config["limits_minutes"]["rust_ci_job"]
    result = {
        "jobs": jobs, "artifact_and_extra_qualification_minutes": elapsed,
        "arm_runner_minutes": runners, "longest_job_minutes": largest,
        "fits_360_minute_job_limit": largest <= limit,
        "fits_350_minute_practical_budget": largest <= config["limits_minutes"]["practical_job_budget"],
        "fresh_profiles_included": not external_profiles,
        "all_results_assume_extra_tool_pgo_E_zero": True,
        "all_results_assume_extra_retained_work_U_zero": True,
    }
    if not external_profiles:
        workflow = max(base["other_matrix_finish_minutes"], base["arm_start_minutes"] + elapsed)
        workflow += base["workflow_suffix_minutes"]
        result.update({
            "arm_elapsed_increase_minutes": elapsed - base["stock_minutes"],
            "arm_runner_increase_minutes": runners - base["stock_minutes"],
            "projected_workflow_minutes": workflow,
            "workflow_increase_minutes": workflow - base["stock_workflow_minutes"],
            "projected_workflow_runner_minutes": base["stock_runner_minutes"] +
                                                runners - base["stock_minutes"],
        })
    return result


def render_svg(rows, path, title, subtitle, maximum, limit=None):
    left, plot, width, height = 320, 840, 1250, 125 + 34 * len(rows)
    output = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<g font-family="Arial,sans-serif" font-size="12" fill="#0f172a">',
        f'<text x="14" y="24" font-size="19">{escape(title)}</text>',
        f'<text x="14" y="46">{escape(subtitle)}</text>',
    ]
    for minute in range(0, int(maximum) + 1, 60):
        x = left + plot * minute / maximum
        output += [f'<path d="M{x:.2f},72 V{height-22}" stroke="#e2e8f0"/>',
                   f'<text x="{x:.2f}" y="66">{minute}m</text>']
    if limit is not None:
        x = left + plot * limit / maximum
        output += [f'<path d="M{x:.2f},72 V{height-22}" stroke="#dc2626" stroke-dasharray="5 4"/>',
                   f'<text x="{x+4:.2f}" y="{height-5}" fill="#dc2626">360m single-job limit</text>']
    for number, (name, item) in enumerate(rows):
        y = 84 + number * 34
        output.append(f'<text x="14" y="{y+14}">{escape(name)}</text>')
        x = left + plot * item["start_minutes"] / maximum
        for phase in item["phases"]:
            w = plot * phase["minutes"] / maximum
            color = COLORS[phase["name"]]
            output.append(f'<rect x="{x:.3f}" y="{y}" width="{w:.3f}" height="20" fill="{color}"><title>{escape(phase["name"])}: {phase["minutes"]:.2f} assumed/accounted minutes</title></rect>')
            x += w
        output.append(f'<text x="{x+4:.2f}" y="{y+14}">~{item["duration_minutes"]:.0f}m job</text>')
    output += ["</g>", "</svg>"]
    text = "\n".join(output) + "\n"
    ET.fromstring(text)
    path.write_text(text, encoding="utf-8")


def build():
    config = json.loads(INPUTS.read_text(encoding="utf-8"))
    baselines = load_baselines(config)
    results = []
    for base in baselines:
        for name, budget in config["scenarios"].items():
            variants = {}
            for variant in ("stock", "frontend_pgo_only", "thinlto_only",
                            "fresh_dual_pgo_no_lto", "fresh_dual_pgo_thinlto",
                            "exact_profile_consumer_only"):
                variants[variant] = metrics(base, serial_jobs(base, budget, variant), config,
                                            external_profiles=variant == "exact_profile_consumer_only")
            for variant, independent in (("overlap_llvm_build", False), ("independent_profiles", True)):
                variants[variant] = metrics(base, parallel_jobs(base, budget, independent), config)
            variants["native_four_job_dag"] = metrics(base, native_dependency_jobs(base, budget), config)
            warm_budget = dict(budget)
            warm_budget["seed_llvm"] = base["stock_llvm_minutes"]
            warm_budget["llvm_instrument"] = budget["instrument_cache_restore"]
            warm_jobs = serial_jobs(base, warm_budget, "fresh_dual_pgo_thinlto")
            for phase in warm_jobs[0]["phases"]:
                if phase["name"] == "LLVM instrumentation":
                    phase["name"] = "Instrumented LLVM restore"
            variants["warm_exact_instrumented_llvm"] = metrics(base, warm_jobs, config)
            variants["warm_exact_instrumented_llvm"]["qualification"] = (
                "conditional exact instrumented-LLVM hit; fresh frontend/backend training, static relink "
                "and final profile-use build retained; not part of the cold-optimized-stage headline")
            serial = variants["fresh_dual_pgo_thinlto"]["artifact_and_extra_qualification_minutes"]
            fixed_before_final = serial - budget["final_thinlto"]
            thresholds = {
                "final_build_allowance_at_360_minutes": 360 - fixed_before_final,
                "final_build_allowance_at_350_minutes": 350 - fixed_before_final,
                "split_final_consumer_allowance_at_360_minutes": 360 -
                    budget["consumer_setup"] - budget["handoff"] -
                    base["retained_tail_minutes"] - budget["extra_qualification"],
                "split_final_consumer_allowance_at_350_minutes": 350 -
                    budget["consumer_setup"] - budget["handoff"] -
                    base["retained_tail_minutes"] - budget["extra_qualification"],
                "other_extra_cost_allowance_at_360_minutes": 360 - serial,
                "tool_savings": [
                    {"assumed_rate": rate,
                     "saved_minutes_if_toolchain_lineage_qualifies": rate * base["eligible_stage2_tools_minutes"]}
                    for rate in config["tool_saving_sensitivity_rates"]],
            }
            results.append({"baseline_run": base["run_id"], "scenario": name,
                            "variants": variants, "thresholds": thresholds})
    hist = config["historical_x64"]
    control, reuse, attempt = (hist["control"], hist["profile_reuse_thinlto"],
                               hist["initial_thinlto_attempt"])
    context = {
        "classification": "same-x64 arithmetic sensitivity, NOT a measured fresh ThinLTO production run or Arm64 scaling factor",
        "final_stage_ratio": reuse["profile_use_build_minutes"] / control["final_build_minutes"],
        "initial_stage_ratio": attempt["initial_instrument_minutes"] / control["initial_instrument_minutes"],
        "substituted_fresh_pipeline_minutes": control["pipeline_minutes"] -
                                              control["final_build_minutes"] +
                                              reuse["profile_use_build_minutes"],
    }
    primary = baselines[0]
    planning = next(r for r in results if r["baseline_run"] == primary["run_id"] and r["scenario"] == "planning")
    serial_planning = planning["variants"]["fresh_dual_pgo_thinlto"]["artifact_and_extra_qualification_minutes"]
    budget = config["scenarios"]["planning"]
    context["arm_planning_final_stage_sensitivity"] = {
        "assumed_final_minutes": reuse["profile_use_build_minutes"],
        "conditional_arm_job_minutes": serial_planning - budget["final_thinlto"] +
                                       reuse["profile_use_build_minutes"],
        "interpretation": "If Arm64 final stage happened to take this long; not a prediction from x64"
    }
    context["early_lto_sensitivity"] = [
        {"assumed_initial_stage_multiplier": m,
         "conditional_arm_job_minutes": serial_planning +
              (m - 1) * (budget["seed_llvm"] + budget["frontend_instrument"])}
        for m in (1, 1.5, 2, context["initial_stage_ratio"])]
    output = {"inputs": INPUTS.name, "baselines": baselines, "results": results,
              "historical_sensitivity": context,
              "promotion": "240-minute limit belongs to publishing existing artifacts, not to any modeled compiler job"}
    (ROOT / "pgo-lto-results.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    return config, output


def document(config, output):
    primary = output["baselines"][0]
    cases = [r for r in output["results"] if r["baseline_run"] == primary["run_id"]]
    lines = ["# Generated PGO/ThinLTO planning arithmetic", "",
             "**Hypothetical budgets, not measurements, forecasts with probabilities, or confidence intervals.**",
             "Read [scope, evidence and dependencies](PGO-LTO-PROJECTION.md). Values below are rounded to",
             "five minutes unless showing observed baseline accounting or a conditional threshold.", "",
             f"Representative stock run: **{primary['run_id']}**; observed job **{primary['stock_minutes']:.2f} min**.",
             f"Remove stock compiler {primary['stock_compiler_minutes']:.2f} + cached LLVM/LLD {primary['stock_llvm_minutes']:.2f} min.",
             f"Keep **{primary['retained_minutes']:.2f} min**, including **{primary['retained_tail_minutes']:.2f} min** full tools/docs/libraries/packaging.",
             "", "| Scenario | Fresh PGO + final ThinLTO job | Added Arm64 elapsed/runner-min | Final-build allowance to fit360 | Single job fits360? |",
             "|---|---:|---:|---:|---|"]
    rounded = lambda value: f"~{round(value/5)*5:.0f}"
    for case in cases:
        value = case["variants"]["fresh_dual_pgo_thinlto"]
        lines.append(f"| {case['scenario']} | {rounded(value['artifact_and_extra_qualification_minutes'])} | {rounded(value['arm_elapsed_increase_minutes'])} | {case['thresholds']['final_build_allowance_at_360_minutes']:.0f} min | {'yes under these assumptions' if value['fits_360_minute_job_limit'] else 'no'} |")
    lines += ["", "## Subsets and scheduling", "",
              "| Scenario / variant | Arm path elapsed min | Arm runner-min | Longest job min | Whole-merge increase min (Sep4 AM) |",
              "|---|---:|---:|---:|---:|"]
    for case in cases:
        for variant, value in case["variants"].items():
            if variant == "stock":
                continue
            delta = value.get("workflow_increase_minutes")
            lines.append(f"| {case['scenario']} / {variant} | {rounded(value['artifact_and_extra_qualification_minutes'])} | {rounded(value['arm_runner_minutes'])} | {rounded(value['longest_job_minutes'])} | {rounded(delta) if delta is not None else 'unknown: external profile cost'} |")
    lines += ["", "Serial fresh variants count all runner time in one job. Parallel variants count",
              "duplicate producer setup, reserved-runner waiting and consumer handoff/setup.",
              "Profile-consumer-only is **not** an end-to-end fresh production scenario.", "",
              "## Assumed component budgets", "",
              "| Budget (minutes, except slowdown fraction) | Efficient | Planning | Stress |",
              "|---|---:|---:|---:|"]
    for key in config["scenarios"]["planning"]:
        values = [str(config["scenarios"][name][key]) for name in config["scenarios"]]
        lines.append(f"| {key} | {' | '.join(values)} |")
    lines += ["", "Definitions and rationale are in [pgo-lto-inputs.json](pgo-lto-inputs.json).",
              "The numbers are exposed assumptions, not per-stage measurements transferred across hardware.", "",
              "## Whole-merge replay across all three samples", "",
              "| Baseline merge run | Original makespan | Efficient fresh serial increase | Planning increase | Stress increase |",
              "|---|---:|---:|---:|---:|"]
    for base in output["baselines"]:
        delta = []
        for scenario in config["scenarios"]:
            row = next(r for r in output["results"] if r["baseline_run"] == base["run_id"] and r["scenario"] == scenario)
            delta.append(rounded(row["variants"]["fresh_dual_pgo_thinlto"]["workflow_increase_minutes"]))
        lines.append(f"| {base['run_id']} | {base['stock_workflow_minutes']:.2f} | {' | '.join(delta)} |")
    lines += ["", "Other platform/test jobs are held unchanged, as are measured Arm start offsets and",
              "the final workflow suffix. This is dependency replay, not a queue/concurrency forecast.",
              "In particular, adding a long Arm job can make Arm the new critical path even though",
              "making the old117-minute Arm job faster had no effect on the original merge makespan.", "",
              "## Tool compilation benefit sensitivity", "",
              "| Baseline run | Eligible observed stage2-tool minutes | 10% conditional saving | 20% conditional saving |",
              "|---|---:|---:|---:|"]
    for base in output["baselines"]:
        eligible = base["eligible_stage2_tools_minutes"]
        lines.append(f"| {base['run_id']} | {eligible:.1f} | {eligible*.1:.1f} | {eligible*.2:.1f} |")
    lines += ["", "Base scenarios deduct **zero**. These are rate sensitivities only, not transferred",
              "IronRDP speedups. Prove which bootstrap compiler actually builds these tools before",
              "using any saving; packaging and documentation are not multiplied by this factor.",
              "", "Reproduce offline: `python project_pgo_lto.py`. Full precision in JSON is arithmetic",
              "traceability, not measurement precision for hypothetical stages."]
    (ROOT / "PGO-LTO-TABLES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    serial_rows = [("Observed stock full dist", cases[0]["variants"]["stock"]["jobs"][0])]
    serial_rows += [(f"Assumed {r['scenario']}: fresh PGO + ThinLTO",
                     r["variants"]["fresh_dual_pgo_thinlto"]["jobs"][0]) for r in cases]
    render_svg(serial_rows, ROOT / "optimized-arm64-projection.svg",
               "Adding optimizations: conditional Arm64 single-job projection",
               "NOT measured: cold optimized stages; unchanged full output budget retained | phase details in hover/table",
               maximum=max(720, 60 * math.ceil(
                   (max(item["finish_minutes"] for _, item in serial_rows) + 30) / 60)),
               limit=360)
    planning = next(r for r in cases if r["scenario"] == "planning")
    parallel_rows = [("Planning: one serial job", planning["variants"]["fresh_dual_pgo_thinlto"]["jobs"][0])]
    for label, variant in (("Native four-job DAG", "native_four_job_dag"),
                           ("Mid-job handoff", "overlap_llvm_build"),
                           ("Independent profiles", "independent_profiles")):
        parallel_rows += [(f"{label}: {i+1}. {item['name'].split(' ')[0]}", item)
                          for i, item in enumerate(planning["variants"][variant]["jobs"])]
    render_svg(parallel_rows, ROOT / "optimized-arm64-jobs.svg",
               "Planning scenario: serial versus profile-producer jobs",
               "Assumed timelines; pale sections are charged idle time | 360m limit applies to each job length, not absolute finish",
               maximum=max(450, 60 * math.ceil(
                   (max(item["finish_minutes"] for _, item in parallel_rows) + 30) / 60)))


if __name__ == "__main__":
    config, output = build()
    document(config, output)
    print("Generated 9 baseline/scenario combinations, 10 variants each, and 2 projected SVGs")
