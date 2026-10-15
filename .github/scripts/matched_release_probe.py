"""Measure the actual full-release compilers with common Cargo and native std."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tomllib

from build_arm_compilers import digest, save
from compiler_probe import validate_meter
from matched_release import RUST, VARIANTS, build_cores, check_build_paths, runner_class, validate_runner
from msvc_experiment import equivalent_tools, tool_identity
from native_ci_probe import paired_order, run_block


def one_file(root, name):
    files = list(root.rglob(name))
    if len(files) != 1:
        raise RuntimeError(f"expected exactly one {name} under {root}, found {files}")
    return files[0]


def release_runs(run_id, runner):
    if runner is None:
        if not isinstance(run_id, str):
            raise RuntimeError("hosted benchmarks require one release run")
        return dict.fromkeys(VARIANTS, run_id)
    if (not isinstance(run_id, dict) or set(run_id) != set(VARIANTS)
            or any(not isinstance(value, str) or not value.isdecimal() for value in run_id.values())):
        raise RuntimeError("self-hosted benchmarks require explicit per-variant numeric release IDs")
    return run_id


def runner_configuration(directory, item, runner):
    if (not item.get("full_distribution")
            or any(item.get(key) != value for key, value in runner.items() if key != "build_jobs")
            or ("build_jobs" in item and item["build_jobs"] != runner["build_jobs"])):
        raise RuntimeError("release machine or resource-class mismatch")
    path = one_file(directory, "bootstrap.toml")
    jobs = tomllib.loads(path.read_text())["build"]["jobs"]
    if jobs != runner["build_jobs"]:
        raise RuntimeError("recorded bootstrap worker count differs from the runner protocol")
    return {"bootstrap_sha256": digest(path), "build_jobs": jobs,
            "build_jobs_source": "metadata-and-bootstrap.toml" if "build_jobs" in item else "bootstrap.toml"}


def install(root, destination, arch, host, vm, run_id, pilot, protocol, runner=None):
    runs = release_runs(run_id, runner)
    destination.mkdir(exist_ok=False)
    compilers, metadata = {}, {}
    evidence = {}
    for variant in VARIANTS:
        directory = root / f"release-{arch}-{variant}-{vm}-evidence"
        path = one_file(directory, "result.json")
        item = json.loads(path.read_text())
        if (not item["complete"] or item["rust_sha"] != RUST or item["host"] != host
                or item["variant"] != variant or item["run_id"] != runs[variant]
                or item["vm"] != vm or item["pilot"] != pilot or item["attempt"] != "1"):
            raise RuntimeError("release identity, qualification, or attempt mismatch")
        if runner is None:
            if item.get("runner_class", "github-hosted") != "github-hosted":
                raise RuntimeError("self-hosted releases cannot enter the hosted comparison")
        if item["llvm_sha"] != protocol["llvm_sha"] or item["perf_sha"] != protocol["perf_sha"]:
            raise RuntimeError("release submodule mismatch")
        manifest = json.loads(one_file(directory, "dist-manifest.json").read_text())
        checksums = {row["name"]: row["sha256"] for row in manifest}
        metadata[variant] = item
        evidence[variant] = {"result_sha256": digest(path), "archives": {}}
        if runner is not None:
            evidence[variant]["runner_configuration"] = runner_configuration(directory, item, runner)
        dist = root / f"release-{arch}-{variant}-{vm}-dist"
        folder = destination / variant
        folder.mkdir()
        components = [f"rustc-nightly-{host}"]
        if variant == "baseline":
            components.extend([f"rust-std-nightly-{host}", f"cargo-nightly-{host}"])
        for component in components:
            archive = one_file(dist, component + ".tar.xz")
            checksum = digest(archive)
            if checksum != checksums[archive.name]:
                raise RuntimeError(f"distribution archive checksum mismatch: {archive}")
            evidence[variant]["archives"][archive.name] = checksum
            with tarfile.open(archive, "r:xz") as bundle:
                bundle.extractall(folder, filter="data")
        compilers[variant] = folder / f"rustc-nightly-{host}/rustc/bin/rustc.exe"
        if not compilers[variant].is_file():
            raise RuntimeError("distribution is missing its compiler executable")
        if not equivalent_tools(metadata["baseline"]["tools"], item["tools"]):
            raise RuntimeError("release builders used different native tool binaries")
    library = destination / "baseline" / f"rust-std-nightly-{host}/rust-std-{host}/lib/rustlib" / host / "lib"
    standard = {p.name: digest(p) for p in library.iterdir() if p.is_file()}
    if not standard:
        raise RuntimeError("empty native standard library")
    for compiler in compilers.values():
        target = compiler.parent.parent / "lib/rustlib" / host / "lib"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(library, target)
        if {p.name: digest(p) for p in target.iterdir() if p.is_file()} != standard:
            raise RuntimeError("native standard libraries are not identical")
    cargo = destination / "baseline" / f"cargo-nightly-{host}/cargo/bin/cargo.exe"
    if not cargo.is_file():
        raise RuntimeError("baseline distribution is missing Cargo")
    return compilers, cargo, metadata, evidence, standard


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--clang", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--release-run")
    selection.add_argument("--release-runs", type=Path,
                           help="Self-hosted only: JSON mapping variant to qualified release run ID")
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--correctness-temp", type=Path)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    check_build_paths(source, output)
    protocol = json.loads(args.protocol.read_text())
    host, vm = os.environ["BENCHMARK_HOST"], int(os.environ["BENCHMARK_REPLICATE"])
    arch = "arm64" if host.startswith("aarch64") else "x64"
    validate_runner(host)
    runner = None
    correctness_env = {"RUST_TEST_THREADS": "1"}
    if args.correctness_temp is not None:
        if (runner_class() not in ("self-hosted-x64", "self-hosted-arm64")
                or not args.correctness_temp.is_dir()):
            raise RuntimeError("correctness temporary directory requires an ordinary self-hosted runner")
        correctness_env.update(TEMP=str(args.correctness_temp.resolve()),
                               TMP=str(args.correctness_temp.resolve()))
    run_ids = args.release_run
    if runner_class() != "github-hosted":
        if args.release_runs is None:
            raise RuntimeError("self-hosted benchmarks require explicit per-variant release provenance")
        run_ids = json.loads(args.release_runs.read_text())
        runner = {"runner_class": runner_class(), "runner_name": os.environ["RUNNER_NAME"],
                  "build_affinity_count": build_cores(), "build_jobs": build_cores(),
                  "logical_cpus": os.cpu_count()}
        protocol = {**protocol, "cores": build_cores(), "resource_class": runner_class()}
    elif args.release_runs is not None:
        raise RuntimeError("per-variant release runs are not permitted in the hosted protocol")
    elif os.cpu_count() != protocol["cores"]:
        raise RuntimeError("hosted protocol capacity mismatch")
    if vm not in range(1, protocol["release_repetitions_per_cell"] + 1):
        raise RuntimeError("unexpected native runner capacity or replicate")
    actual = subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip()
    if actual != protocol["source_sha"]:
        raise RuntimeError("IronRDP source revision mismatch")
    subprocess.run(["git", "-C", source, "diff", "--exit-code"], check=True)
    output.mkdir(exist_ok=False)
    compilers, cargo, metadata, evidence, standard = install(
        args.artifacts.resolve(), output / "compilers", arch, host, vm,
        run_ids, args.pilot, protocol, runner)
    tools = tool_identity(args.clang.resolve())
    if not equivalent_tools(tools, metadata["baseline"]["tools"]):
        raise RuntimeError("benchmark native tools differ from release construction")
    os.environ["PATH"] = os.pathsep.join([str(cargo.parent), str(compilers["baseline"].parent),
                                       str(args.clang.resolve()), os.environ["PATH"]])
    os.environ["RUSTDOC"] = str(compilers["baseline"].parent / "rustdoc.exe")
    for key in ("GH_TOKEN", "GITHUB_TOKEN"):
        os.environ.pop(key, None)
    subprocess.run([cargo, "fetch", "--locked", "--target", host], cwd=source,
                   env={**os.environ, "RUSTC": str(compilers["baseline"])}, check=True)
    validate_meter(output / "meter-validation")
    index = {
        "protocol": protocol, "host": host, "vm": vm, "pilot": args.pilot,
        "release_run": args.release_run, "benchmark_run": os.environ["GITHUB_RUN_ID"],
        "benchmark_attempt": os.environ["GITHUB_RUN_ATTEMPT"], "tools": tools,
        "compiler_metadata": metadata, "artifact_evidence": evidence, "stdlib": standard,
        "cargo_sha256": digest(cargo), "runs": [], "complete": False,
    }
    if runner is not None:
        index.update(selfhost_schema=1, runner=runner, release_runs=run_ids)
        index["correctness_environment"] = correctness_env
    save(output / "index.json", index)
    warmups = 0 if args.pilot else protocol["warmup_rounds"]
    rounds = 1 if args.pilot else warmups + protocol["measured_rounds"]
    for round_index in range(rounds):
        for position, variant in enumerate(paired_order(list(VARIANTS), vm, round_index)):
            name = f"round-{round_index}-{variant}"
            run_block(source, output / name, compilers[variant], protocol,
                      {"variant": variant, "round": round_index}, round_index == 0,
                      correctness_env=correctness_env, native_only=True)
            index["runs"].append({"variant": variant, "round": round_index, "position": position,
                                  "warmup": round_index < warmups, "path": f"{name}/results.json"})
            save(output / "index.json", index)
    subprocess.run(["git", "-C", source, "diff", "--exit-code"], check=True)
    index["complete"] = True
    save(output / "index.json", index)


if __name__ == "__main__":
    main()
