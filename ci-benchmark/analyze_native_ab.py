"""Predeclared paired analysis of the original IronRDP offline CI replay."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".github" / "scripts"))
from native_ci_probe import COMMANDS, NATIVE_COMMANDS, PROFILE_ENV, paired_order
from analyze_arm_ab import interval
from analyze_native import analyze_units, js_json

METRICS = ("wall_seconds", "cpu_seconds")
PLATFORMS = ("windows-arm64", "linux-arm64")
NAMES = [name for name, _ in COMMANDS]
NATIVE_NAMES = [name for name, _ in NATIVE_COMMANDS]
SEED = 1012026


def load_matrix(root, protocol):
    matrix = {name: {p: {} for p in PLATFORMS} for name in [*NAMES, "native-total"]}
    expected = {(p, vm) for p in PLATFORMS for vm in range(1, protocol["independent_vms_per_os"] + 1)}
    seen, identities, run_ids, partitions = set(), set(), set(), []
    for index_path in sorted(root.rglob("index.json")):
        index = json.loads(index_path.read_text(encoding="utf-8"))
        key = index["platform"], index["vm"]
        if key not in expected or key in seen or index["pilot"] or index["protocol"] != protocol:
            raise ValueError("Unexpected/duplicate VM, pilot or changed protocol")
        seen.add(key)
        platform, vm = key
        variants = protocol["windows_variants"] if platform == "windows-arm64" else protocol["linux_variants"]
        if index["variants"] != variants:
            raise ValueError("Wrong compiler variants")
        if platform == "windows-arm64":
            provenance_path = index_path.parent / "optimized-compiler.json"
            if hashlib.sha256(provenance_path.read_bytes()).hexdigest() != protocol["optimized_metadata_sha256"]:
                raise ValueError("Wrong optimized compiler provenance")
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            installation = json.loads((index_path.parent / "installation.json").read_text(encoding="utf-8"))
            if (provenance["archive_sha256"] != protocol["optimized_archive_sha256"]
                    or not installation["stdlib_identity_verified"]
                    or not installation["native_and_wasm_smoke_passed"]):
                raise ValueError("Unverified optimized compiler installation")
        rounds = protocol["warmup_rounds"] + protocol["measured_rounds"]
        wanted_runs = [(v, r, pos) for r in range(rounds)
                       for pos, v in enumerate(paired_order(variants, vm, r))]
        actual_runs = [(r["variant"], r["round"], r["position"]) for r in index["runs"]]
        if actual_runs != wanted_runs:
            raise ValueError("Incomplete or incorrectly ordered paired blocks")
        observations = {name: {v: {m: [] for m in METRICS} for v in variants} for name in matrix}
        used_targets = set()
        for entry in index["runs"]:
            warmup = entry["round"] < protocol["warmup_rounds"]
            if entry["warmup"] != warmup:
                raise ValueError("Wrong warmup classification")
            result_path = (index_path.parent / entry["path"]).resolve()
            if not result_path.is_relative_to(index_path.parent.resolve()):
                raise ValueError("Result path escapes evidence directory")
            result = json.loads(result_path.read_text(encoding="utf-8"))
            meta = result["metadata"]
            if (meta["source_sha"] != protocol["source_sha"] or protocol["rust_sha"] not in meta["rustc"]
                    or f"release: {protocol['rust_version']}\n" not in meta["rustc"]
                    or meta["profile_environment"] != PROFILE_ENV or meta["logical_cpus"] != protocol["cores"]
                    or (meta["variant"], meta["round"]) != (entry["variant"], entry["round"])):
                raise ValueError("Changed source, compiler, profile or trial identity")
            env = meta["environment"]
            if (env["BENCHMARK_PLATFORM"], int(env["BENCHMARK_REPLICATE"])) != key:
                raise ValueError("Trial assigned to wrong VM")
            if entry["variant"] == "optimized" and not meta["compiler_executable"].replace("\\", "/").endswith("/optimized/bin/rustc.exe"):
                raise ValueError("Wrong optimized compiler executable")
            run_ids.add((env["GITHUB_RUN_ID"], env["GITHUB_RUN_ATTEMPT"]))
            identities.add((meta["lock_lf_sha256"], meta["cargo"]))
            targets = meta["cold_target_directories"]
            if set(targets) != {"native", "common", "wasm"} or len(set(targets.values())) != 3 or used_targets.intersection(targets.values()):
                raise ValueError("Target directories reused across compiler/round blocks")
            used_targets.update(targets.values())
            rows = result["measurements"]
            if [r["name"] for r in rows] != NAMES:
                raise ValueError("Wrong or incomplete original command sequence")
            block_partitions = {}
            for row, (name, args) in zip(rows, COMMANDS):
                command = ["cargo", *args, "--frozen", "--timings", "--message-format=json"]
                if row["command"] != command or row["exit_code"] or row["compiled_artifacts"] <= 0:
                    raise ValueError("Changed, failed or unexpectedly cached build command")
                if row["target_directory"] != targets[name if name in targets else "native"]:
                    raise ValueError("Wrong target directory")
                if len(set(row["affinity"])) != protocol["cores"]:
                    raise ValueError("Wrong CPU affinity")
                if any(not math.isfinite(row[m]) or row[m] <= 0 for m in METRICS):
                    raise ValueError("Invalid measured duration")
                if abs(row["cpu_seconds"] - row["user_seconds"] - row["kernel_seconds"]) > 1e-6:
                    raise ValueError("CPU accounting mismatch")
                if row["cpu_seconds"] > row["wall_seconds"] * protocol["cores"] * 1.05:
                    raise ValueError("CPU use exceeds affinity budget")
                if not warmup:
                    for metric in METRICS:
                        observations[name][entry["variant"]][metric].append(row[metric])
                    if name in NATIVE_NAMES:
                        html = (result_path.parent / f"{name}.timings.html").read_text(encoding="utf-8")
                        units = js_json(html, "UNIT_DATA")
                        parts = analyze_units(units, row["wall_seconds"], set())["wall_partition"]
                        for part, seconds in parts.items():
                            block_partitions[part] = block_partitions.get(part, 0) + seconds
            checks = result["correctness"]
            expected_checks = NATIVE_COMMANDS[1:] if entry["round"] == 0 else []
            if len(checks) != len(expected_checks):
                raise ValueError("Missing original native correctness checks")
            for check, (name, args) in zip(checks, expected_checks):
                command = ["cargo", *(a for a in args if a != "--no-run"), "--frozen"]
                if check["name"] != name or check["command"] != command or check["exit_code"]:
                    raise ValueError("Original native correctness checks failed or changed")
            if not warmup:
                for metric in METRICS:
                    observations["native-total"][entry["variant"]][metric].append(
                        sum(row[metric] for row in rows if row["name"] in NATIVE_NAMES))
                partitions.append({"platform": platform, "vm": vm, "variant": entry["variant"],
                                   "round": entry["round"], **block_partitions})
        for name in matrix:
            matrix[name][platform][vm] = {}
            for variant in variants:
                metrics = observations[name][variant]
                if any(len(v) != protocol["measured_rounds"] for v in metrics.values()):
                    raise ValueError("Incorrect measured trial count")
                matrix[name][platform][vm][variant] = {m: statistics.mean(v) for m, v in metrics.items()}
    if seen != expected or len(identities) != 1 or len(run_ids) != 1:
        raise ValueError("Expected complete matrix with identical Cargo/lock inputs and one workflow attempt")
    return matrix, partitions, next(iter(run_ids))


def analyze(matrix, protocol, draws=10000):
    rng = random.Random(SEED)
    ids = list(range(1, protocol["independent_vms_per_os"] + 1))
    samples = [(rng.choices(ids, k=len(ids)), rng.choices(ids, k=len(ids))) for _ in range(draws)]
    rows = []
    for name, platforms in matrix.items():
        for metric in METRICS:
            def calculate(win_ids, linux_ids):
                win = {v: statistics.mean(platforms["windows-arm64"][i][v][metric] for i in win_ids)
                       for v in protocol["windows_variants"]}
                linux = statistics.mean(platforms["linux-arm64"][i]["official"][metric] for i in linux_ids)
                saved = win["official"] - win["optimized"]
                gap = win["official"] - linux
                return {"official_windows": win["official"], "optimized_windows": win["optimized"],
                        "official_linux": linux, "saved_seconds": saved,
                        "reduction_fraction": saved / win["official"],
                        "windows_linux_gap_seconds": gap, "gap_closed_fraction": saved / gap if gap > 0 else None}
            point = calculate(ids, ids)
            bootstrap = [calculate(w, l) for w, l in samples]
            intervals = {}
            for key in ("saved_seconds", "reduction_fraction", "windows_linux_gap_seconds", "gap_closed_fraction"):
                values = [b[key] for b in bootstrap]
                intervals[key] = None if any(v is None for v in values) else interval(values)
            rows.append({"component": name, "metric": metric, **point, "ci95": intervals})
    return {"protocol": protocol, "bootstrap_draws": draws, "bootstrap_seed": SEED, "results": rows}


def markdown(data):
    lines = ["# Original IronRDP CI: optimized Windows Arm64 compiler", "",
             "Paired stock-to-optimized toolchain replacement; cold artifacts, original Cargo profiles.",
             "Equal-weight VM means after averaging rounds; 95% paired VM-cluster bootstrap intervals.",
             "CPU = user + kernel process-tree seconds; setup and correctness checks are excluded.", "",
             "| Component | Metric | Linux stock | Windows stock | Windows optimized | Reduction (95% interval) |",
             "|---|---|---:|---:|---:|---|"]
    for row in data["results"]:
        lo, hi = row["ci95"]["reduction_fraction"]
        lines.append(f"| {row['component']} | {row['metric']} | {row['official_linux']:.2f} | "
                     f"{row['official_windows']:.2f} | {row['optimized_windows']:.2f} | "
                     f"{row['reduction_fraction']:.1%} ({lo:.1%} to {hi:.1%}) |")
    lines += ["", "Prior graphics-workload reference: 18.0% CPU / 18.8% wall reduction versus an LLD control.",
              "This experiment measures the practical official-to-optimized replacement instead.",
              "Interval overlap is not proof of equal effects. Native, common and WASM are separate workloads,",
              "not stages to add into one CI total. Cargo activity intervals do not uniquely attribute CPU costs.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(Path(__file__).with_name("native-ab-protocol.json").read_text())
    matrix, partitions, run = load_matrix(args.evidence, protocol)
    result = analyze(matrix, protocol)
    result.update({"github_run_id": run[0], "github_run_attempt": run[1], "native_wall_partitions": partitions})
    args.output.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown(result), encoding="utf-8")
