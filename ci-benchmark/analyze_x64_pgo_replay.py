"""Validate and analyze the fresh full-release three-compiler native replay."""

import argparse
import json
import math
from pathlib import Path
import random
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".github/scripts"))
from native_ci_probe import NATIVE_COMMANDS, PROFILE_ENV, paired_order
from analyze_arm_ab import interval

METRICS = ("wall_seconds", "cpu_seconds")
NAMES = [name for name, _ in NATIVE_COMMANDS]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_matrix(root, protocol):
    matrix, identities, attempts, shared, targets = {}, set(), set(), set(), set()
    for path in sorted(root.rglob("index.json")):
        index = json.loads(path.read_text())
        vm = index["vm"]
        require(index["complete"] and index["protocol"] == protocol, "Incomplete VM or changed protocol")
        require(vm not in matrix and vm in range(1, protocol["independent_vms"] + 1), "Unexpected or duplicate VM")
        require(index["variants"] == protocol["variants"], "Changed compiler variants")
        require(any(name.startswith("libstd-") for name in index["stdlib"]), "Missing shared standard libraries")
        shared.add(json.dumps([index["stdlib"], index["cargo_sha256"], index["artifact_evidence"]], sort_keys=True))
        attempts.add((index["benchmark_run"], index["attempt"]))
        for variant in ("upstream", "local"):
            evidence = index["artifact_evidence"][variant]
            require(evidence["archive_sha256"] == protocol["compiler_archive_sha256"][variant]
                    and evidence["result_sha256"] == protocol["compiler_metadata_sha256"][variant],
                    "Changed compiler artifact or provenance")
            release = index["compiler_metadata"][variant]
            require(release["complete"] and release["variant"] == variant
                    and release["run_id"] == protocol["release_run"]
                    and release["attempt"] == protocol["release_attempt"]
                    and release["rust_sha"] == protocol["rust_sha"], "Wrong compiler release")
        expected = [(variant, r, p)
                    for r in range(protocol["warmup_rounds"] + protocol["measured_rounds"])
                    for p, variant in enumerate(paired_order(protocol["variants"], vm, r))]
        require([(r["variant"], r["round"], r["position"]) for r in index["runs"]] == expected,
                "Incomplete or incorrectly ordered matrix")
        observations = {variant: {name: {metric: [] for metric in METRICS}
                                  for name in [*NAMES, "native-total"]} for variant in protocol["variants"]}
        for entry in index["runs"]:
            warmup = entry["round"] < protocol["warmup_rounds"]
            require(entry["warmup"] == warmup, "Changed warmup exclusion")
            result_path = (path.parent / entry["path"]).resolve()
            require(result_path.is_relative_to(path.parent.resolve()), "Escaping evidence path")
            result = json.loads(result_path.read_text())
            meta, rows = result["metadata"], result["measurements"]
            variant = entry["variant"]
            require(meta["source_sha"] == protocol["source_sha"]
                    and meta["profile_environment"] == PROFILE_ENV
                    and meta["logical_cpus"] == protocol["cores"]
                    and (meta["variant"], meta["round"]) == (variant, entry["round"])
                    and meta["rustc"] == index["versions"][variant]
                    and protocol["rust_sha"] in meta["rustc"]
                    and f"release: {protocol['rust_version']}\n" in meta["rustc"]
                    and f"host: {protocol['host']}\n" in meta["rustc"], "Changed trial or compiler inputs")
            executable = meta["compiler_executable"].replace("\\", "/")
            suffix = (f"/rustup/toolchains/{protocol['rust_version']}-{protocol['host']}/bin/rustc.exe"
                      if variant == "official" else
                      f"/compilers/{variant}/rustc-{protocol['rust_version']}-{protocol['host']}/rustc/bin/rustc.exe")
            require(executable.endswith(suffix), "Wrong compiler executable")
            env = meta["environment"]
            require(env["BENCHMARK_PLATFORM"] == "windows-x64"
                    and env["BENCHMARK_REPLICATE"] == str(vm)
                    and env["BENCHMARK_HOST"] == protocol["host"]
                    and (env["GITHUB_RUN_ID"], env["GITHUB_RUN_ATTEMPT"]) ==
                    (index["benchmark_run"], index["attempt"]), "Mixed workflow or VM identity")
            identities.add((meta["lock_lf_sha256"], meta["cargo"]))
            target = meta["cold_target_directories"]["native"]
            require((vm, target) not in targets, "Reused native target")
            targets.add((vm, target))
            approved = {name.replace("\\", "/").lower() for name in meta["approved_background_executables"]}
            require(all("/vc/tools/msvc/" in name and name.endswith("/bin/hostx64/x64/vctip.exe")
                        for name in approved), "Unexpected approved background process")
            require([row["name"] for row in rows] == NAMES, "Changed native command sequence")
            for row, (name, args) in zip(rows, NATIVE_COMMANDS):
                require(row["command"] == ["cargo", *args, "--frozen", "--timings", "--message-format=json"]
                        and row["exit_code"] == 0 and row["compiled_artifacts"] > 0
                        and row["target_directory"] == target, "Changed, failed or cached native command")
                require(len(set(row["affinity"])) == protocol["cores"], "Wrong CPU affinity")
                require(all(math.isfinite(row[m]) and row[m] > 0 for m in METRICS)
                        and abs(row["cpu_seconds"] - row["user_seconds"] - row["kernel_seconds"]) < 1e-6
                        and row["cpu_seconds"] <= row["wall_seconds"] * protocol["cores"] * 1.05,
                        "Invalid duration or CPU accounting")
                require(all(p["image"].replace("\\", "/").lower() in approved
                            for p in row.get("background_processes_at_completion", [])),
                        "Unexpected surviving process")
                if not warmup:
                    for metric in METRICS:
                        observations[variant][name][metric].append(row[metric])
            checks = result["correctness"]
            expected_checks = NATIVE_COMMANDS[1:] if entry["round"] == 0 else []
            require(len(checks) == len(expected_checks), "Missing correctness checks")
            for check, (name, args) in zip(checks, expected_checks):
                require(check["name"] == name and check["exit_code"] == 0
                        and check["command"] == ["cargo", *(a for a in args if a != "--no-run"), "--frozen"],
                        "Changed or failed correctness checks")
            if not warmup:
                for metric in METRICS:
                    observations[variant]["native-total"][metric].append(sum(row[metric] for row in rows))
        require(all(len(values) == protocol["measured_rounds"] for commands in observations.values()
                    for metrics in commands.values() for values in metrics.values()), "Missing measured rounds")
        matrix[vm] = {variant: {name: {metric: statistics.mean(values) for metric, values in metrics.items()}
                               for name, metrics in commands.items()} for variant, commands in observations.items()}
    require(set(matrix) == set(range(1, protocol["independent_vms"] + 1))
            and len(identities) == len(attempts) == len(shared) == 1,
            "Expected complete matrix, identical common inputs and one workflow attempt")
    return matrix, next(iter(attempts))


def analyze(matrix, draws=10000):
    ids = sorted(matrix)
    rng = random.Random(1012026)
    samples = [rng.choices(ids, k=len(ids)) for _ in range(draws)]
    output = []
    for component in matrix[ids[0]]["official"]:
        for metric in METRICS:
            for baseline, candidate in (("official", "local"), ("upstream", "local"), ("official", "upstream")):
                def calculate(selected):
                    base = statistics.mean(matrix[i][baseline][component][metric] for i in selected)
                    local = statistics.mean(matrix[i][candidate][component][metric] for i in selected)
                    return {"baseline_seconds": base, "candidate_seconds": local,
                            "saved_seconds": base - local, "reduction_fraction": (base - local) / base}
                point = calculate(ids)
                resampled = [calculate(sample) for sample in samples]
                output.append({"component": component, "metric": metric, "baseline": baseline,
                               "candidate": candidate, **point,
                               "ci95": {key: interval([row[key] for row in resampled]) for key in point}})
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(Path(__file__).with_name("x64-pgo-replay-protocol.json").read_text())
    matrix, attempt = load_matrix(args.evidence, protocol)
    result = {"protocol": protocol, "workflow_attempt": attempt, "vm_means": matrix, "results": analyze(matrix)}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps([row for row in result["results"]
                      if row["component"] == "native-total" and row["metric"] == "wall_seconds"], indent=2))


if __name__ == "__main__":
    main()
