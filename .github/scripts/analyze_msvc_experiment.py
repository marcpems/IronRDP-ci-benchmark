"""Strict paired analysis of the complete same-tools IronRDP experiment."""

import argparse
import json
from pathlib import Path
import random
import statistics

from build_arm_compilers import save
from msvc_experiment import VARIANTS
from msvc_ironrdp_probe import validate_metadata
from native_ci_probe import COMMANDS, NATIVE_COMMANDS, paired_order

HOSTS = ("x86_64-pc-windows-msvc", "aarch64-pc-windows-msvc")


def contrast(control, treatment):
    if len(control) != len(treatment) or not control or min(control + treatment) <= 0:
        raise ValueError("Expected positive paired VM means")
    estimate = 100 * (1 - statistics.mean(treatment) / statistics.mean(control))
    rng = random.Random(20261009)
    draws = []
    for _ in range(10000):
        indices = rng.choices(range(len(control)), k=len(control))
        draws.append(100 * (1 - sum(treatment[i] for i in indices) / sum(control[i] for i in indices)))
    draws.sort()
    return {"reduction_percent": estimate, "ci95_percent": [draws[249], draws[9749]]}


def analyze(root, protocol):
    cells, identity, benchmark_runs, build_runs = {}, {}, set(), set()
    n = protocol["independent_vms_per_arch"]
    rounds = protocol["warmup_rounds"] + protocol["measured_rounds"]
    for path in root.rglob("index.json"):
        index = json.loads(path.read_text())
        if index.get("pilot"):
            raise ValueError("Pilot data must not be mixed into the full study")
        if not index.get("complete") or index["protocol"] != protocol:
            raise ValueError(f"Incomplete or mismatched protocol: {path}")
        host, vm = index["host"], index["vm"]
        if host not in HOSTS or vm not in range(1, n + 1) or (host, vm) in cells:
            raise ValueError("Unexpected or duplicate VM")
        validate_metadata(index["compiler_metadata"], protocol, host, index["build_run"])
        if index["variants"] != list(VARIANTS):
            raise ValueError("Wrong compiler variants")
        benchmark_runs.add((index["benchmark_run"], index["benchmark_attempt"]))
        build_runs.add(index["build_run"])
        fingerprint = {
            "metadata": index["compiler_metadata"], "stdlibs": index["stdlibs"],
            "cargo": index["cargo_sha256"], "rustdoc": index["rustdoc_sha256"],
        }
        if host in identity and identity[host] != fingerprint:
            raise ValueError("Compiler artifacts, profiles, Cargo or stdlibs differ across VMs")
        identity[host] = fingerprint
        expected = {(variant, r) for variant in VARIANTS for r in range(rounds)}
        seen, values = set(), {variant: {} for variant in VARIANTS}
        for run in index["runs"]:
            variant, round_index = run["variant"], run["round"]
            key = (variant, round_index)
            if key not in expected or key in seen:
                raise ValueError("Duplicate or unexpected measurement block")
            seen.add(key)
            warmup = round_index < protocol["warmup_rounds"]
            if run["warmup"] != warmup:
                raise ValueError("Warmup labels differ from protocol")
            order = paired_order(list(VARIANTS), vm, round_index)
            if run["position"] != order.index(variant):
                raise ValueError("Compiler order differs from protocol")
            block = json.loads((path.parent / run["path"]).read_text())
            rows = block["measurements"]
            if [row["name"] for row in rows] != [name for name, _ in COMMANDS]:
                raise ValueError("Missing or reordered Cargo measurements")
            if block["metadata"]["variant"] != variant or block["metadata"]["round"] != round_index:
                raise ValueError("Block identity mismatch")
            if block["metadata"]["source_sha"] != protocol["source_sha"]:
                raise ValueError("Wrong workload source")
            for row in rows:
                if (row["exit_code"] or row["wall_seconds"] <= 0 or row["cpu_seconds"] <= 0
                        or row["compiled_artifacts"] <= 0 or len(row["affinity"]) != protocol["cores"]):
                    raise ValueError("Failed, empty, or invalid measurement")
            if round_index == 0:
                checks = block["correctness"]
                if ([row["name"] for row in checks] != [name for name, _ in NATIVE_COMMANDS[1:]]
                        or any(row["exit_code"] for row in checks)):
                    raise ValueError("Missing or failed original native correctness checks")
            if not warmup:
                for metric in ("wall_seconds", "cpu_seconds"):
                    values[variant].setdefault(f"native-total/{metric}", []).append(
                        sum(row[metric] for row in rows[:len(NATIVE_COMMANDS)]))
                    for row in rows:
                        values[variant].setdefault(f"{row['name']}/{metric}", []).append(row[metric])
        if seen != expected:
            raise ValueError("Incomplete paired measurement matrix")
        cells[host, vm] = {
            variant: {metric: statistics.mean(samples) for metric, samples in metrics.items()}
            for variant, metrics in values.items()
        }
    if set(cells) != {(host, vm) for host in HOSTS for vm in range(1, n + 1)}:
        raise ValueError("Incomplete architecture/VM matrix")
    if len(benchmark_runs) != 1 or len(build_runs) != 1:
        raise ValueError("Mixed workflow runs or benchmark attempts")
    result = {"protocol": protocol, "benchmark_run": list(benchmark_runs)[0],
              "build_run": list(build_runs)[0], "architectures": {}}
    for host in HOSTS:
        metrics = cells[host, 1]["baseline"].keys()
        host_result = {}
        for metric in metrics:
            samples = {variant: [cells[host, vm][variant][metric] for vm in range(1, n + 1)]
                       for variant in VARIANTS}
            host_result[metric] = {
                "vm_means": samples,
                "means": {variant: statistics.mean(rows) for variant, rows in samples.items()},
                "contrasts": {f"{control}->{treatment}": contrast(samples[control], samples[treatment])
                              for control, treatment in [("baseline", "pgo"), ("pgo", "pgo-rust-thin"),
                                                         ("baseline", "pgo-rust-thin")]},
            }
        result["architectures"][host] = host_result
    return result


def markdown(result):
    lines = [
        "# Same-tools Windows compiler results", "",
        f"Compiler build run: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/{result['build_run']}",
        f"Benchmark run: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/{result['benchmark_run'][0]}",
        "", "Native clang-cl, link.exe and lib.exe were held constant. Both PGO variants used",
        "byte-identical profiles. Each architecture has five independent VMs and three",
        "measured rounds per compiler, following one excluded warmup.", "",
        "| Architecture | Variant | Native wall (s) | Native CPU (s) |",
        "|---|---|---:|---:|",
    ]
    for host, metrics in result["architectures"].items():
        for variant in VARIANTS:
            wall = metrics["native-total/wall_seconds"]["means"][variant]
            cpu = metrics["native-total/cpu_seconds"]["means"][variant]
            lines.append(f"| {host} | {variant} | {wall:.2f} | {cpu:.2f} |")
    lines += ["", "Positive reductions mean faster compilation; negative values mean slower.",
              "Intervals resample paired whole VMs, not individual Cargo commands.", "",
              "| Architecture | Contrast | Wall reduction | 95% interval |",
              "|---|---|---:|---:|"]
    for host, metrics in result["architectures"].items():
        for name, value in metrics["native-total/wall_seconds"]["contrasts"].items():
            lo, hi = value["ci95_percent"]
            lines.append(f"| {host} | {name} | {value['reduction_percent']:.2f}% | {lo:.2f}% to {hi:.2f}% |")
    lines += ["", "## Native test-compilation breakdown", "",
              "| Architecture | Command | Baseline (s) | PGO (s) | PGO + Rust ThinLTO (s) |",
              "|---|---|---:|---:|---:|"]
    for host, metrics in result["architectures"].items():
        for name, _ in COMMANDS:
            means = metrics[f"{name}/wall_seconds"]["means"]
            cells = " | ".join(f"{means[variant]:.2f}" for variant in VARIANTS)
            lines.append(f"| {host} | {name} | {cells} |")
    lines += ["", "These are offline Cargo compilation measurements, not end-to-end CI times.",
              "Setup, downloads, uploads, and correctness runs are outside the timed totals.",
              "The toolchains are compiler-only experiments, not qualified releases.",
              "This newer source is not a matched comparison against the earlier Rust 1.94.1 study.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.input, json.loads(args.protocol.read_text()))
    args.output.mkdir(parents=True, exist_ok=True)
    save(args.output / "results.json", result)
    (args.output / "RESULTS.md").write_text(markdown(result), encoding="utf-8")


if __name__ == "__main__":
    main()
