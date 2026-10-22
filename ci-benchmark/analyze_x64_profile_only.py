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
from x64_profile_only import verify_pair, verify_training_input
from x64_profile_replay import summarize
from audit_official_profiles import coverage


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def analyze(root, rust_version="1.94.1"):
    require(rust_version in ("1.94.1", "1.99.1"), "Unsupported qualified release")
    pins = None
    if rust_version == "1.99.1":
        pins = load(Path(__file__).with_name("x64-profile-1991-replay-input.json"))
        protocol, inputs = pins["protocol"], pins["release_inputs"]
        run_id, attempt = pins["replay_run"], pins["replay_attempt"]
        recorded_inputs = None
    else:
        protocol = load(Path(__file__).with_name("x64-profile-only-protocol.json"))
        inputs = load(Path(__file__).with_name("x64-profile-replay-input.json"))
        run_id, attempt, recorded_inputs = "39635843303", "1", inputs
    replay = root / "replay"
    index = load(replay / "index.json")
    require(index["complete"] and index["protocol"] == protocol and index["release_inputs"] == recorded_inputs,
            "Incomplete replay or changed protocol/input pins")
    require(index["run_id"] == run_id and index["attempt"] == attempt, "Wrong replay attempt")
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
    training = None
    if pins is not None:
        folder = root / "training"
        for name, expected in pins["training_evidence_sha256"].items():
            require(hashlib.sha256((folder / name).read_bytes()).hexdigest() == expected,
                    f"Changed frozen training evidence: {name}")
        verify_training_input(folder, protocol, metadata["official"]["tools"],
                              run_id=run_id, attempt=attempt)
        trained = load(folder / "result.json")
        require(trained["protocol"] == load(Path(__file__).with_name("x64-profile-1991-protocol.json")),
                "Changed preregistered training protocol")
        for variant, result in metadata.items():
            require(result["protocol"] == protocol and result["run_id"] == run_id
                    and result["attempt"] == attempt
                    and result["common_profile_sha256"] == {
                        "rustc": protocol["rustc_profile_sha256"],
                        "cargo": protocol["rustc_profile_sha256"],
                        "rustdoc": protocol["rustdoc_profile_sha256"],
                    }, f"Changed qualified release inputs: {variant}")
            require(result["configuration"] == trained["configuration"],
                    "Training and final-build configuration differ")
        for group, counts in trained["llvm_coverage"].items():
            parsed = coverage((folder / f"coverage-{group}.txt").read_text())
            require(parsed == {"functions": counts["functions"], "active": counts["active_functions"]},
                    f"Training coverage mismatch: {group}")
        stages = load(folder / "training-sections.json")
        require(not stages["unfinished"] and all(row["status"] == "OK" for row in stages["completed"]),
                "Incomplete training timer sections")
        phases = {row["name"]: row["wall_seconds"] for row in stages["completed"] if " > " not in row["name"]}
        require(set(phases) == {"Stage 1 (Rustc + rustdoc PGO)", "Stage 2 (LLVM PGO)"}
                and all(math.isfinite(value) and value > 0 for value in phases.values()),
                "Missing successful upstream training phases")
        executions = {name: load(folder / f"{name}.json")
                      for name in ("build-training-helper", "train-profile")}
        require(all(row["exit_code"] == 0 and row["wall_seconds"] > 0
                    for row in executions.values()), "Failed training execution")
        require(math.isfinite(trained["training_seconds"])
                and trained["training_seconds"] >= sum(phases.values()), "Invalid standalone training duration")
        training = {
            "wall_seconds": trained["training_seconds"],
            "phase_wall_seconds": phases, "llvm_coverage": trained["llvm_coverage"],
            "llvm_profile_sha256": trained["profiles"]["llvm"]["sha256"],
            "scope": trained["scope"],
        }
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
    result = {
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
    if training is not None:
        result["training"] = training
        result["compiler_production"]["limitation"] = (
            "One ordered pair, fixed profiles reused, both distributions qualified in their original jobs. "
            "Standalone repaired training measured separately; no upstream-training control or marginal PR cost.")
        require(run["url"].endswith(f"/actions/runs/{run_id}") and run["headSha"] == pins["harness_sha"],
                "Wrong completed workflow identity")
        expected_jobs = {"train / cell", "official / cell", "repaired / cell", "replay / replay"}
        require({job["name"] for job in run["jobs"]} == expected_jobs
                and all(job["conclusion"] == "success" for job in run["jobs"]),
                "Missing qualified experiment jobs")
        result["workflow_job_seconds"] = {job["name"]: duration(job) for job in run["jobs"]}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rust-version", choices=("1.94.1", "1.99.1"), default="1.94.1")
    args = parser.parse_args()
    result = analyze(args.evidence.resolve(), args.rust_version)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
