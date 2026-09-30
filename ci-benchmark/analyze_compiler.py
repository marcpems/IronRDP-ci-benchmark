"""Aggregate validated compiler measurements; CPU is user plus kernel process time."""

import argparse
import json
from pathlib import Path
import statistics


PLATFORMS = ("linux-x64", "windows-x64", "linux-arm64", "windows-arm64")
WORKLOADS = ("graphics-project", "yuv-native-metadata", "yuv-native-codegen",
             "yuv-wasm-metadata", "yuv-wasm-codegen")


def analyze(root):
    results = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(root.rglob("results.json"))]
    expected = {(platform, str(rep)) for platform in PLATFORMS for rep in (1, 2, 3)}
    actual = [(r["metadata"]["environment"]["BENCHMARK_PLATFORM"],
               r["metadata"]["environment"]["BENCHMARK_REPLICATE"]) for r in results]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("expected exactly three complete samples for each of four platforms")
    identities = {(r["metadata"]["source_sha"], r["metadata"]["lock_lf_sha256"],
                   json.dumps(r["metadata"]["profile"], sort_keys=True)) for r in results}
    if len(identities) != 1:
        raise ValueError("mixed source, lockfile or profile settings")
    samples = {}
    for result in results:
        platform = result["metadata"]["environment"]["BENCHMARK_PLATFORM"]
        seen = set()
        for row in result["measurements"]:
            key = row["workload"], row["cores"]
            if key in seen or row["exit_code"] or row["cpu_seconds"] < 0:
                raise ValueError("duplicate, failed or invalid measurement")
            seen.add(key)
            if len(row["affinity"]) != row["cores"]:
                raise ValueError("incorrect recorded CPU affinity")
            if abs(row["user_seconds"] + row["kernel_seconds"] - row["cpu_seconds"]) > 1e-6:
                raise ValueError("CPU accounting mismatch")
            if row["effective_cores"] > row["cores"] * 1.05:
                raise ValueError("CPU accounting exceeds the affinity budget")
            if row["workload"] == "graphics-project":
                own = row["rustc_user_seconds"] + row["rustc_kernel_seconds"]
                if own > row["cpu_seconds"] + 0.03 * row["rustc_processes"]:
                    raise ValueError("compiler CPU exceeds process-tree CPU")
            samples.setdefault((platform, *key), []).append(row)
        if seen != {(workload, cores) for workload in WORKLOADS for cores in (1, 4)}:
            raise ValueError("missing workload or parallelism level")
    summaries = []
    for (platform, workload, cores), rows in samples.items():
        row = {"platform": platform, "workload": workload, "cores": cores, "n": len(rows)}
        for metric in ("wall_seconds", "cpu_seconds", "user_seconds", "kernel_seconds", "effective_cores"):
            values = [r[metric] for r in rows]
            row[metric] = {
                "median": statistics.median(values), "min": min(values), "max": max(values),
                "samples": values,
            }
        if workload == "graphics-project":
            own = [r["rustc_user_seconds"] + r["rustc_kernel_seconds"] for r in rows]
            row["compiler_own_cpu_median"] = statistics.median(own)
            row["compiler_fraction_pooled"] = sum(own) / sum(r["cpu_seconds"] for r in rows)
        summaries.append(row)
    return {"samples": results, "summary": summaries}


def markdown(data):
    lookup = {(r["platform"], r["workload"], r["cores"]): r for r in data["summary"]}
    lines = [
        "# Compiler validation measurements", "",
        "Cells: median wall seconds / median CPU seconds (user + kernel). n=3 per cell.",
        "CPU time sums concurrent threads/processes and is not wall time.", "",
        "| Workload | Logical CPUs | Linux x64 | Windows x64 | Linux Arm64 | Windows Arm64 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for workload in WORKLOADS:
        for cores in (1, 4):
            cells = []
            for platform in PLATFORMS:
                r = lookup[(platform, workload, cores)]
                cells.append(f"{r['wall_seconds']['median']:.2f} / {r['cpu_seconds']['median']:.2f}")
            lines.append(f"| {workload} | {cores} | " + " | ".join(cells) + " |")
    lines.extend(["", "## Windows/Linux ratios", "",
                  "| Workload | CPUs | x64 wall | x64 CPU | Arm64 wall | Arm64 CPU |",
                  "|---|---:|---:|---:|---:|---:|"])
    for workload in WORKLOADS:
        for cores in (1, 4):
            cells = []
            for architecture in ("x64", "arm64"):
                linux = lookup[(f"linux-{architecture}", workload, cores)]
                windows = lookup[(f"windows-{architecture}", workload, cores)]
                cells.extend(f"{windows[m]['median'] / linux[m]['median']:.3f}x"
                             for m in ("wall_seconds", "cpu_seconds"))
            lines.append(f"| {workload} | {cores} | " + " | ".join(cells) + " |")
    lines.extend(["", "## Single-to-four CPU wall speedup", "",
                  "Median of the three within-run speedups (same runner for each pair).", "",
                  "| Workload | Linux x64 | Windows x64 | Linux Arm64 | Windows Arm64 |",
                  "|---|---:|---:|---:|---:|"])
    for workload in WORKLOADS:
        cells = []
        for platform in PLATFORMS:
            speedups = []
            for result in data["samples"]:
                if result["metadata"]["environment"]["BENCHMARK_PLATFORM"] != platform:
                    continue
                pair = {r["cores"]: r["wall_seconds"] for r in result["measurements"]
                        if r["workload"] == workload}
                speedups.append(pair[1] / pair[4])
            cells.append(f"{statistics.median(speedups):.3f}x")
        lines.append(f"| {workload} | " + " | ".join(cells) + " |")
    lines.extend(["", "## Compiler-own CPU share in project builds", "",
                  "| Platform | CPUs | Compiler CPU median | Share of all process-tree CPU |",
                  "|---|---:|---:|---:|"])
    for platform in PLATFORMS:
        for cores in (1, 4):
            r = lookup[(platform, "graphics-project", cores)]
            lines.append(f"| {platform} | {cores} | {r['compiler_own_cpu_median']:.2f} | "
                         f"{100*r['compiler_fraction_pooled']:.2f}% |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifacts", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    data = analyze(args.artifacts)
    args.output.with_suffix(".json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown(data), encoding="utf-8")
    print(markdown(data))
