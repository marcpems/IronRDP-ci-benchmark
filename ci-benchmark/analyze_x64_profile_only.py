"""Reproduce the qualified profile-only result from extracted compact evidence."""

import argparse
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".github/scripts"))
from native_ci_probe import NATIVE_COMMANDS
from x64_profile_only import verify_pair
from x64_profile_replay import summarize


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def analyze(root):
    protocol = load(Path(__file__).with_name("x64-profile-only-protocol.json"))
    inputs = load(Path(__file__).with_name("x64-profile-replay-input.json"))
    replay = root / "replay"
    index = load(replay / "index.json")
    require(index["complete"] and index["protocol"] == protocol and index["release_inputs"] == inputs,
            "Incomplete replay or changed protocol/input pins")
    require(index["run_id"] == "39635843303" and index["attempt"] == "1", "Wrong replay attempt")
    for entry in index["runs"]:
        path = (replay / entry["path"]).resolve()
        require(path.is_relative_to(replay.resolve()), "Escaping result path")
    summary = summarize(replay, index)
    require(summary == load(replay / "summary.json"), "Recorded and recomputed replay summaries differ")
    meter = load(replay / "meter-validation/self-test.json")
    require(all(row["exit_code"] == 0 for row in meter.values())
            and meter["busy_descendant"]["cpu_seconds"] >= 0.25
            and meter["sleep"]["cpu_seconds"] < 0.15
            and (replay / "meter-validation/affinity.stdout").read_text().strip() == "1",
            "CPU meter self-test failed")
    require(any(name.startswith("libstd-") for name in index["stdlib"]), "Missing shared native library manifest")
    metadata, production, qualification, resources = {}, {}, {}, {}
    for variant in protocol["variants"]:
        folder = root / "builds" / variant
        result_path = folder / "result.json"
        metadata[variant] = load(result_path)
        require(hashlib.sha256(result_path.read_bytes()).hexdigest() == inputs["compiler_metadata_sha256"][variant],
                f"Changed qualified compiler metadata: {variant}")
        require(metadata[variant]["complete"] and metadata[variant] == index["compiler_metadata"][variant]
                and metadata[variant]["llvm_profile_sha256"] == protocol["llvm_profile_sha256"][variant]
                and metadata[variant]["rustc_profile_sha256"] == protocol["rustc_profile_sha256"],
                f"Wrong qualified profiles: {variant}")
        identity = index["artifact_evidence"][variant]
        require(identity["result_sha256"] == inputs["compiler_metadata_sha256"][variant]
                and identity["archive_sha256"] == inputs["compiler_archive_sha256"][variant]
                and identity["driver_sha256"], f"Wrong measured compiler identity: {variant}")
        archive_name = f"rustc-{protocol['rust_version']}-{protocol['host']}.tar.xz"
        archives = [row for row in load(folder / "dist-manifest.json") if row["name"] == archive_name]
        require(len(archives) == 1 and archives[0]["sha256"] == inputs["compiler_archive_sha256"][variant]
                and archives[0]["bytes"] == inputs["compiler_archive_bytes"][variant], "Compiler manifest mismatch")
        version = index["versions"][variant]
        require(all(value in version for value in (protocol["rust_sha"], f"host: {protocol['host']}\n",
                                                  f"release: {protocol['rust_version']}\n")), "Compiler version mismatch")
        build = load(folder / "production.json")
        require(build["exit_code"] == 0 and math.isfinite(build["wall_seconds"]) and build["wall_seconds"] > 0
                and metadata[variant]["production_seconds"] == build["wall_seconds"],
                "Invalid compiler-production measurement")
        require(len(set(build["affinity"])) == protocol["build_cores"], "Wrong production CPU allocation")
        audit = load(folder / "profile-use-audit.json")
        require(audit["rustc_profile_use"] and not audit["rejected_profile_mismatch_warnings"],
                "Unqualified profile use")
        checks = [load(folder / name) for name in ("build-test-helper.json", "extracted-dist-tests.json")]
        require(all(row["exit_code"] == 0 for row in checks), "Compiler qualification failed")
        production[variant] = build["wall_seconds"]
        qualification[variant] = {
            "total_seconds": metadata[variant]["qualification_seconds"],
            "helper_seconds": checks[0]["wall_seconds"], "tests_seconds": checks[1]["wall_seconds"],
        }
        telemetry = [json.loads(line) for line in (folder / "telemetry.jsonl").read_text().splitlines()]
        require(telemetry and all(row["BuildDrive"] == "D:" and row["BuildFreeBytes"] > 0
                                 and all(counter["Status"] == 0 for counter in row["Counters"])
                                 for row in telemetry), "Missing or invalid build-volume telemetry")
        available = [counter["CookedValue"] for row in telemetry for counter in row["Counters"]
                     if counter["Path"].lower().endswith("\\memory\\available mbytes")]
        require(available, "Missing memory telemetry")
        resources[variant] = {"samples": len(telemetry),
                              "minimum_build_free_gib": min(row["BuildFreeBytes"] for row in telemetry) / 2**30,
                              "minimum_available_ram_mib": min(available)}
    verify_pair(metadata["official"], metadata["repaired"])
    require(index["artifact_evidence"]["official"]["driver_sha256"]
            != index["artifact_evidence"]["repaired"]["driver_sha256"], "Identical compiler driver treatment")
    observations = {variant: [] for variant in protocol["variants"]}
    correctness = 0
    measured_seconds = warmup_seconds = correctness_seconds = 0
    for entry in index["runs"]:
        block = load(replay / entry["path"])
        meta = block["metadata"]
        suffix = f"/compilers/{entry['variant']}/rustc-{protocol['rust_version']}-{protocol['host']}/rustc/bin/rustc.exe"
        require(meta["compiler_executable"].replace("\\", "/").endswith(suffix), "Wrong measured executable")
        require(meta["environment"]["BENCHMARK_HOST"] == protocol["host"]
                and meta["environment"]["BENCHMARK_PLATFORM"] == "windows-x64-selfhosted-refs",
                "Wrong workload host")
        correctness += len(block["correctness"])
        correctness_seconds += sum(check["seconds_outside_measurement"] for check in block["correctness"])
        block_seconds = sum(row["wall_seconds"] for row in block["measurements"])
        if entry["round"] >= protocol["warmup_rounds"]:
            observations[entry["variant"]].append(block)
            measured_seconds += block_seconds
        else:
            warmup_seconds += block_seconds
    components = []
    for position, (name, _) in enumerate(NATIVE_COMMANDS):
        means = {variant: {
            metric: statistics.mean(block["measurements"][position][metric] for block in blocks)
            for metric in ("wall_seconds", "cpu_seconds")} for variant, blocks in observations.items()}
        components.append({
            "name": name, "means": means,
            "seconds_saved": means["official"]["wall_seconds"] - means["repaired"]["wall_seconds"],
            "wall_reduction_percent": 100 * (1 - means["repaired"]["wall_seconds"] / means["official"]["wall_seconds"]),
        })
    cpu = summary["means"]
    run = load(root / "jobs/replay.json")
    require(run["conclusion"] == "success", "Unsuccessful replay workflow")
    jobs = [job for job in run["jobs"] if job["name"] == "replay / replay"]
    require(len(jobs) == 1 and jobs[0]["conclusion"] == "success", "Missing completed native replay job")
    job = jobs[0]
    steps = [step for step in job["steps"] if step["name"] == "Measure the isolated LLVM profile difference"]
    require(len(steps) == 1 and steps[0]["conclusion"] == "success", "Missing completed benchmark step")
    def duration(row):
        return (datetime.fromisoformat(row["completedAt"]) - datetime.fromisoformat(row["startedAt"])).total_seconds()
    job_seconds, step_seconds = duration(job), duration(steps[0])
    residual = step_seconds - measured_seconds - warmup_seconds - correctness_seconds
    require(residual >= 0 and job_seconds >= step_seconds, "Inconsistent experiment job accounting")
    evidence_hashes = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in sorted(root.rglob("*")) if path.is_file()}
    return {
        "protocol": protocol, "release_inputs": inputs, "replay_run": index["run_id"],
        "summary": summary, "components": components,
        "cpu_reduction_percent": 100 * (1 - cpu["repaired"]["cpu_seconds"] / cpu["official"]["cpu_seconds"]),
        "measured_blocks": sum(len(rows) for rows in observations.values()),
        "measured_commands": sum(len(rows) for rows in observations.values()) * len(NATIVE_COMMANDS),
        "excluded_warmup_blocks": 2, "original_correctness_commands_passed": correctness,
        "experiment_job_accounting": {
            "job_seconds": job_seconds, "benchmark_step_seconds": step_seconds,
            "measured_native_commands_seconds": measured_seconds,
            "excluded_warmup_commands_seconds": warmup_seconds,
            "untimed_correctness_seconds": correctness_seconds,
            "other_inside_benchmark_step_seconds": residual,
            "outside_benchmark_step_seconds": job_seconds - step_seconds,
            "scope": "Eight-block experiment job, not a representative single-toolchain production CI job",
        },
        "compiler_production": {
            "wall_seconds": production,
            "seconds_saved": production["official"] - production["repaired"],
            "wall_reduction_percent": 100 * (1 - production["repaired"] / production["official"]),
            "qualification": qualification, "whole_ci_comparable": False,
            "limitation": "One ordered pair, fixed profiles reused; control qualification recovered separately. No matched fresh whole-CI comparison.",
        },
        "build_resource_checks": resources,
        "evidence_sha256": evidence_hashes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.evidence.resolve())
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
