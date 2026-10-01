"""Predeclared paired/cluster analysis of the Windows Arm64 compiler experiment."""

import argparse
import json
import math
from pathlib import Path
import random
import statistics

from analyze_compiler import WORKLOADS

ENDPOINTS = {(workload, cores) for workload in WORKLOADS for cores in (1, 4)}
PLATFORMS = ("windows-arm64", "linux-arm64")
METRICS = ("cpu_seconds", "wall_seconds")
SEED = 9412026


def quantile(values, probability):
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def interval(values, coverage=0.95):
    tail = (1 - coverage) / 2
    return [quantile(values, tail), quantile(values, 1 - tail)]


def load_matrix(root, protocol):
    indexes = sorted(root.rglob("index.json"))
    wanted = {(p, vm) for p in PLATFORMS
              for vm in range(1, protocol["independent_vms_per_os"] + 1)}
    seen = set()
    identities, hashes = set(), set()
    matrix = {endpoint: {p: {} for p in PLATFORMS} for endpoint in ENDPOINTS}
    for path in indexes:
        index = json.loads(path.read_text(encoding="utf-8"))
        key = index["platform"], index["vm"]
        if key not in wanted or key in seen or index["pilot"] or index["protocol"] != protocol:
            raise ValueError("Unexpected/duplicate VM, pilot data or changed protocol")
        seen.add(key)
        platform, vm = key
        variants = protocol["windows_variants"] if platform == "windows-arm64" else ["official"]
        if index["variants"] != variants:
            raise ValueError("Missing or unexpected compiler variant")
        if platform == "windows-arm64":
            if not index.get("identical_windows_stdlibs_verified"):
                raise ValueError("Official/custom standard-library identity was not verified")
            if protocol.get("llvm_profile_coverage_required") and not index.get("llvm_profile_coverage_verified"):
                raise ValueError("Meaningful LLVM PGO training coverage was not verified")
            manifests = index["compiler_archive_sha256"]
            if set(manifests) != set(variants) - {"official"}:
                raise ValueError("Incomplete compiler provenance")
            if manifests != protocol["compiler_archive_sha256"]:
                raise ValueError("Compiler artifacts differ from the preregistered hashes")
            hashes.add(json.dumps(manifests, sort_keys=True))
        total_rounds = protocol["warmup_rounds"] + protocol["measured_rounds"]
        expected_runs = {(v, r) for v in variants for r in range(total_rounds)}
        found_runs = set()
        observations = {e: {v: {m: [] for m in METRICS} for v in variants} for e in ENDPOINTS}
        for entry in index["runs"]:
            run_key = entry["variant"], entry["round"]
            if run_key not in expected_runs or run_key in found_runs:
                raise ValueError("Missing/duplicate/unexpected trial")
            found_runs.add(run_key)
            warmup = entry["round"] < protocol["warmup_rounds"]
            if entry["warmup"] != warmup:
                raise ValueError("Incorrect warmup classification")
            result_path = (path.parent / entry["path"]).resolve()
            if not result_path.is_relative_to(path.parent.resolve()):
                raise ValueError("Result path escapes the evidence directory")
            result = json.loads(result_path.read_text(encoding="utf-8"))
            metadata = result["metadata"]
            if metadata["source_sha"] != protocol["source_sha"] or protocol["rust_sha"] not in metadata["rustc"]:
                raise ValueError("Wrong source/compiler revision")
            compiler = metadata["compiler_executable"]
            if entry["variant"] != "official":
                if compiler.replace("\\", "/").split("/")[-3:] != [entry["variant"], "bin", "rustc.exe"]:
                    raise ValueError("Trial used the wrong custom compiler")
            environment = metadata["environment"]
            if (environment["BENCHMARK_PLATFORM"], int(environment["BENCHMARK_REPLICATE"])) != key:
                raise ValueError("Trial does not belong to its declared VM")
            identities.add((metadata["source_sha"], metadata["lock_lf_sha256"],
                            json.dumps(metadata["profile"], sort_keys=True)))
            if metadata["profile"] != {"opt_level": 1, "codegen_units": 16, "debug": 0, "incremental": False}:
                raise ValueError("Wrong workload compilation profile")
            found_endpoints = set()
            for row in result["measurements"]:
                endpoint = row["workload"], row["cores"]
                if endpoint not in ENDPOINTS or endpoint in found_endpoints or row["exit_code"]:
                    raise ValueError("Missing/duplicate/failed endpoint")
                found_endpoints.add(endpoint)
                if len(row["affinity"]) != row["cores"]:
                    raise ValueError("Wrong CPU affinity")
                for metric in METRICS:
                    if not math.isfinite(row[metric]) or row[metric] <= 0:
                        raise ValueError("Invalid measured time")
                if abs(row["cpu_seconds"] - row["user_seconds"] - row["kernel_seconds"]) > 1e-6:
                    raise ValueError("CPU accounting mismatch")
                if row["cpu_seconds"] / row["wall_seconds"] > row["cores"] * 1.05:
                    raise ValueError("CPU use exceeds affinity budget")
                if platform == "windows-arm64" and endpoint[0].startswith("yuv-") and row["processes"] != 1:
                    raise ValueError("Direct replay spawned unexpected child processes")
                if endpoint[0].startswith("yuv-") and row["command"][0] != compiler:
                    raise ValueError("Direct replay did not use the declared compiler")
                if not warmup:
                    for metric in METRICS:
                        observations[endpoint][entry["variant"]][metric].append(row[metric])
            if found_endpoints != ENDPOINTS:
                raise ValueError("Incomplete trial")
        if found_runs != expected_runs:
            raise ValueError("Incomplete VM")
        for endpoint, variants_data in observations.items():
            matrix[endpoint][platform][vm] = {}
            for variant, metrics in variants_data.items():
                if any(len(values) != protocol["measured_rounds"] for values in metrics.values()):
                    raise ValueError("Incorrect measured trial count")
                matrix[endpoint][platform][vm][variant] = {
                    metric: statistics.mean(values) for metric, values in metrics.items()
                }
    if seen != wanted or len(identities) != 1 or len(hashes) != 1:
        raise ValueError("Expected complete matrix with identical inputs and compiler artifacts")
    return matrix


def contrasts(windows, linux):
    official = windows["official"]
    gap = official - linux
    optimization = windows["baseline-lld"] - windows["optimized"]
    return {
        "baseline_ratio": windows["baseline-msvc"] / official,
        "optimization_seconds": optimization,
        "optimization_saving_fraction": optimization / windows["baseline-lld"],
        "linker_seconds": windows["baseline-msvc"] - windows["baseline-lld"],
        "build_bridge_seconds": official - windows["baseline-msvc"],
        "official_gap_seconds": gap,
        "gap_equivalent_fraction": optimization / gap if gap > 0 else None,
        "saving_fraction_of_official": optimization / official,
        "total_official_to_optimized_fraction": (official - windows["optimized"]) / official,
    }


def analyze(matrix, protocol, draws=10000):
    rng = random.Random(SEED)
    n = protocol["independent_vms_per_os"]
    vm_ids = list(range(1, n + 1))
    resamples = [
        (rng.choices(vm_ids, k=n), rng.choices(vm_ids, k=n)) for _ in range(draws)
    ]
    records = []
    for (workload, cores), platforms in sorted(matrix.items()):
        for metric in METRICS:
            win = platforms["windows-arm64"]
            lin = platforms["linux-arm64"]

            def summarize(win_ids, linux_ids):
                windows = {v: sum(win[i][v][metric] for i in win_ids) / len(win_ids)
                           for v in protocol["windows_variants"]}
                linux = sum(lin[i]["official"][metric] for i in linux_ids) / len(linux_ids)
                return windows, linux, contrasts(windows, linux)

            windows, linux, point = summarize(vm_ids, vm_ids)
            boot = [summarize(w, l)[2] for w, l in resamples]
            intervals = {}
            for key in point:
                values = [b[key] for b in boot]
                intervals[key] = None if any(v is None for v in values) else interval(values)
            baseline_ci90 = interval([b["baseline_ratio"] for b in boot], coverage=0.90)
            equivalent = baseline_ci90[0] >= 0.95 and baseline_ci90[1] <= 1.05
            gap_identifiable = intervals["official_gap_seconds"][0] > 0
            record = {
                "workload": workload, "cores": cores, "metric": metric,
                "windows_mean_seconds": windows, "linux_mean_seconds": linux,
                "contrasts": point, "ci95": intervals,
                "baseline_ratio_ci90": baseline_ci90,
                "baseline_equivalent": equivalent, "positive_gap": gap_identifiable,
                "vms_per_os": n, "measured_rounds_per_vm": protocol["measured_rounds"],
                "attribution_warning": None if equivalent and gap_identifiable else (
                    "Baseline equivalence or positive-gap gate failed: do not claim official-gap attribution."
                ),
            }
            if workload == "graphics-project" and cores == 4:
                historic = protocol[f"historical_graphics_4_{'cpu' if metric == 'cpu_seconds' else 'wall'}"]
                excess_fraction = 1 - historic["linux_seconds"] / historic["windows_seconds"]
                record["historical_gap_equivalent_fraction"] = point["saving_fraction_of_official"] / excess_fraction
                record["historical_gap_equivalent_ci95"] = [
                    v / excess_fraction for v in intervals["saving_fraction_of_official"]
                ]
            records.append(record)
    primary = next(r for r in records if (r["workload"], r["cores"], r["metric"]) ==
                   ("graphics-project", 4, "cpu_seconds"))
    return {
        "protocol": protocol, "bootstrap_draws": draws, "bootstrap_seed": SEED,
        "primary_attribution_gate_passed": primary["baseline_equivalent"] and primary["positive_gap"],
        "results": records,
    }


def markdown(data):
    lines = [
        "# Arm64 compiler optimization A/B", "",
        "Times are equal-weight means across VMs after averaging measured rounds within each VM.",
        "Intervals are paired Windows / independent Linux VM-cluster bootstrap percentiles.",
        "Warmups are excluded; no slow-run trimming. CPU = user + kernel seconds.", "",
        "| Endpoint | CPUs | Metric | Linux official | Windows official | MSVC baseline | LLD control | Optimized |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in data["results"]:
        values = [row["linux_mean_seconds"]] + [
            row["windows_mean_seconds"][v] for v in data["protocol"]["windows_variants"]
        ]
        lines.append(f"| {row['workload']} | {row['cores']} | {row['metric']} | "
                     + " | ".join(f"{v:.3f}" for v in values) + " |")
    lines += ["", "## Primary graphics / four-CPU contrasts", ""]
    for row in data["results"]:
        if row["workload"] != "graphics-project" or row["cores"] != 4:
            continue
        point, ci = row["contrasts"], row["ci95"]
        fraction = point["optimization_saving_fraction"]
        bounds = ci["optimization_saving_fraction"]
        lines += [
            f"**{row['metric']}:** optimization-only saving {fraction:.1%} "
            f"(95% interval {bounds[0]:.1%} to {bounds[1]:.1%}).",
            f"Rebuilt MSVC / official ratio: {point['baseline_ratio']:.3f}; "
            f"90% interval {row['baseline_ratio_ci90']}; equivalence gate: {row['baseline_equivalent']}.",
        ]
        if row["attribution_warning"]:
            lines.append(f"**{row['attribution_warning']}**")
        else:
            fraction, bounds = point["gap_equivalent_fraction"], ci["gap_equivalent_fraction"]
            if bounds is None:
                lines.append("Gap fraction is unstable under bootstrap resampling; no interval reported.")
            else:
                lines.append(f"Optimization contrast closes **{fraction:.1%}** of the contemporary "
                             f"official Windows/Linux gap (95% interval {bounds[0]:.1%} to {bounds[1]:.1%}).")
            historic = row["historical_gap_equivalent_fraction"]
            lines.append(f"Historical-gap equivalent: {historic:.1%}, conditional on the "
                         "measured relative saving transferring to the earlier runner sample.")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(Path(__file__).with_name("arm64-ab-protocol.json").read_text())
    result = analyze(load_matrix(args.evidence, protocol), protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    args.output.with_suffix(".md").write_text(markdown(result), encoding="utf-8")
