"""Strict paired analysis of the complete same-tools IronRDP experiment."""

import argparse
import json
from pathlib import Path
import random
import statistics

from build_arm_compilers import digest, save
from msvc_experiment import VARIANTS, equivalent_tools
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


def analyze(root, protocol, hosts=HOSTS):
    if not hosts or len(set(hosts)) != len(hosts) or not set(hosts) <= set(HOSTS):
        raise ValueError("Select a nonempty, unique subset of the supported architectures")
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
        if host not in hosts or vm not in range(1, n + 1) or (host, vm) in cells:
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
                if "correctness_test_threads" in protocol and any(
                    row.get("environment_overrides") != {
                        "RUST_TEST_THREADS": str(protocol["correctness_test_threads"])}
                    for row in checks
                ):
                    raise ValueError("Correctness concurrency differs from the protocol")
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
    if set(cells) != {(host, vm) for host in hosts for vm in range(1, n + 1)}:
        raise ValueError("Incomplete architecture/VM matrix")
    if len(benchmark_runs) != 1 or len(build_runs) != 1:
        raise ValueError("Mixed workflow runs or benchmark attempts")
    result = {"protocol": protocol, "benchmark_run": list(benchmark_runs)[0],
              "build_run": list(build_runs)[0], "included_hosts": list(hosts), "architectures": {},
              "compiler_metadata": {host: identity[host]["metadata"] for host in hosts}}
    for host in hosts:
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
        "Architecture scope: " + ", ".join(result["included_hosts"]) + ".",
        "No results for omitted architectures are implied.", "",
        f"Compiler build run: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/{result['build_run']}",
        f"Benchmark run: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/{result['benchmark_run'][0]}",
        "", "Native clang-cl, link.exe and lib.exe were held constant. Both PGO variants used",
        "byte-identical profiles. Each architecture has five independent VMs and three",
        "measured rounds per compiler, following one excluded warmup.", "",
        "Correctness commands run outside timing. Protocol amendment: "
        + result["protocol"].get("amendment", "none") + "", "",
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


def build_summary(root, result):
    phases = ("baseline", "rustc-profile", "llvm-profile", "pgo", "pgo-rust-thin")
    hosts = tuple(result.get("included_hosts", HOSTS))
    records, metadata, paths = {}, {}, {}
    for path in root.rglob("metadata.json"):
        item = json.loads(path.read_text())
        key = (item["host"], item["phase"])
        if key in records:
            raise ValueError("Duplicate compiler build artifacts")
        if item["phase"] in VARIANTS and item["run_id"] != result["build_run"]:
            raise ValueError("Final compiler artifacts are from a different build run")
        if item["rust_sha"] != result["protocol"]["rust_sha"]:
            raise ValueError("Wrong compiler source in build report")
        timing = {}
        for stage in ("build", "training-tools", "training", "merge", "training-lockfile", "smoke-compile", "smoke-run"):
            measurement = path.parent / f"{stage}.json"
            if measurement.is_file():
                row = json.loads(measurement.read_text())
                if row["exit_code"] != 0:
                    raise ValueError(f"Failed build stage: {measurement}")
                timing[stage] = {key: row[key] for key in ("wall_seconds", "cpu_seconds")}
        if "build" not in timing:
            raise ValueError("Missing compiler construction timing")
        if item["phase"].endswith("-profile") and not {"training-tools", "training", "merge"} <= timing.keys():
            raise ValueError("Missing profile collection timing")
        records[key] = timing
        metadata[key], paths[key] = item, path
    if set(records) != {(host, phase) for host in hosts for phase in phases}:
        raise ValueError("Incomplete compiler construction artifact matrix")
    for host in hosts:
        final = {variant: metadata[host, variant] for variant in VARIANTS}
        validate_metadata(final, result["protocol"], host, result["build_run"])
        if final != result["compiler_metadata"][host]:
            raise ValueError("Construction artifacts differ from the benchmark's compiler metadata")
        for phase in phases:
            item, path = metadata[host, phase], paths[host, phase]
            if not equivalent_tools(final["baseline"]["tools"], item["tools"]):
                raise ValueError("Construction phases used different native tools")
            if any(item[key] != final["baseline"][key] for key in ("llvm_sha", "perf_sha")):
                raise ValueError("Construction phases used different source submodules")
            expected_profiles = set() if phase == "baseline" else {"rustc-pgo.profdata"}
            if phase not in ("baseline", "rustc-profile"):
                expected_profiles.add("llvm-pgo.profdata")
            if set(item["profiles"]) != expected_profiles:
                raise ValueError("Wrong profiles for construction phase")
            for name, checksum in item["profiles"].items():
                if digest(path.parent / name) != checksum:
                    raise ValueError("Construction profile checksum mismatch")
            if phase in ("llvm-profile", "pgo", "pgo-rust-thin"):
                parent_phase = "rustc-profile" if phase == "llvm-profile" else "llvm-profile"
                parent = metadata[host, parent_phase]
                if item["profile_parent_sha256"] != digest(paths[host, parent_phase]):
                    raise ValueError("Construction profile parent mismatch")
                if any(item["profiles"].get(name) != checksum for name, checksum in parent["profiles"].items()):
                    raise ValueError("Construction phases did not retain identical input profiles")
    lines = ["", "## Toolchain construction", "",
             "| Architecture | Phase | Bootstrap wall (min) | Collector build (min) | Training wall (min) | Bootstrap CPU (min) |",
             "|---|---|---:|---:|---:|---:|"]
    for host in hosts:
        for phase in phases:
            timing = records[host, phase]
            training = timing.get("training", {}).get("wall_seconds", 0) / 60
            tools = timing.get("training-tools", {}).get("wall_seconds", 0) / 60
            lines.append(f"| {host} | {phase} | {timing['build']['wall_seconds']/60:.2f} | "
                         f"{tools:.2f} | {training:.2f} | {timing['build']['cpu_seconds']/60:.2f} |")
    lines += ["", "Bootstrap-command time includes stage0 acquisition, bootstrap compilation, LLVM",
              "and Rust compilation. It is not a pure offline compiler CPU measurement.",
              "Collector construction, training and profile merging are separately recorded. Source/tool setup and",
              "artifact transfers are excluded from this table. Jobs rebuild prerequisites",
              "independently; their summed time is not the workflow critical path.", ""]
    return {
        "stages": {f"{host}/{phase}": timing for (host, phase), timing in records.items()},
        "provenance": {f"{host}/{phase}": {"run_id": item["run_id"], "metadata_sha256": digest(paths[host, phase])}
                       for (host, phase), item in metadata.items()},
    }, "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--build-input", type=Path)
    parser.add_argument("--architecture", choices=("both", "x64", "arm64"), default="both")
    args = parser.parse_args()
    hosts = HOSTS if args.architecture == "both" else (HOSTS[0 if args.architecture == "x64" else 1],)
    result = analyze(args.input, json.loads(args.protocol.read_text()), hosts)
    args.output.mkdir(parents=True, exist_ok=True)
    report = markdown(result)
    if args.build_input:
        result["construction"], appendix = build_summary(args.build_input, result)
        report += appendix
    save(args.output / "results.json", result)
    (args.output / "RESULTS.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
