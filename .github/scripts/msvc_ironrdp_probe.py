"""Replay the original IronRDP measurements with matched native-linker toolchains."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

from arm_ab_probe import extract_compiler
from build_arm_compilers import digest, save
from compiler_probe import validate_meter
from msvc_experiment import VARIANTS, equivalent_tools, tool_identity
from native_ci_probe import paired_order, run_block


def validate_metadata(metadata, protocol, host, run_id):
    baseline = metadata["baseline"]
    for variant in VARIANTS:
        item = metadata[variant]
        if (item["phase"] != variant or item["rust_sha"] != protocol["rust_sha"]
                or item["host"] != host or item["run_id"] != run_id):
            raise RuntimeError(f"Wrong compiler provenance for {variant}")
        if not equivalent_tools(baseline["tools"], item["tools"]):
            raise RuntimeError("Build tools differ between compiler variants")
        if item["llvm_sha"] != baseline["llvm_sha"] or item["perf_sha"] != baseline["perf_sha"]:
            raise RuntimeError("Source submodules differ between variants")
        if (not item.get("profiling_runtime_sources")
                or item["profiling_runtime_sources"] != baseline.get("profiling_runtime_sources")):
            raise RuntimeError("Profiling runtime sources are missing or differ between variants")
    for variant in ("pgo", "pgo-rust-thin"):
        if set(metadata[variant]["profiles"]) != {"rustc-pgo.profdata", "llvm-pgo.profdata"}:
            raise RuntimeError("Missing PGO profiles")
        training = metadata[variant]["training"]
        for phase in ("rustc-profile", "llvm-profile"):
            counts = training[phase]["coverage"]
            if not counts or any(value["active_functions"] <= 0 for value in counts.values()):
                raise RuntimeError("Missing meaningful PGO coverage")
    if (metadata["pgo"]["profiles"] != metadata["pgo-rust-thin"]["profiles"]
            or metadata["pgo"]["profile_parent_sha256"] != metadata["pgo-rust-thin"]["profile_parent_sha256"]):
        raise RuntimeError("PGO variants do not share byte-identical training profiles")
    if baseline["profiles"]:
        raise RuntimeError("Baseline must not use PGO")


def install(root, protocol, host, run_id):
    metadata = {variant: json.loads((root / variant / "metadata.json").read_text()) for variant in VARIANTS}
    validate_metadata(metadata, protocol, host, run_id)
    compilers = {}
    for variant, item in metadata.items():
        directory = root / variant
        archive = directory / "compiler.zip"
        if digest(archive) != item["archive_sha256"]:
            raise RuntimeError(f"Archive checksum mismatch: {variant}")
        sysroot = directory / "sysroot"
        extract_compiler(archive, sysroot)
        actual_files = {p.relative_to(sysroot).as_posix(): digest(p)
                        for p in sysroot.rglob("*") if p.is_file()}
        if actual_files != item["files"]:
            raise RuntimeError(f"Extracted file manifest mismatch: {variant}")
        compilers[variant] = sysroot / "bin/rustc.exe"
    baseline_root = compilers["baseline"].parent.parent
    shared = {}
    for target in (host, "wasm32-unknown-unknown"):
        relative = Path("lib/rustlib") / target / "lib"
        original = baseline_root / relative
        if not list(original.glob("libstd-*.rlib")):
            raise RuntimeError(f"Missing baseline standard libraries: {target}")
        for variant in ("pgo", "pgo-rust-thin"):
            destination = compilers[variant].parent.parent / relative
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(original, destination)
        shared[target] = {p.name: digest(p) for p in original.iterdir() if p.is_file()}
        for compiler in compilers.values():
            candidate = compiler.parent.parent / relative
            if {p.name: digest(p) for p in candidate.iterdir() if p.is_file()} != shared[target]:
                raise RuntimeError("Standard libraries are not identical")
    return compilers, metadata, shared


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--compilers", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--clang", type=Path, required=True)
    parser.add_argument("--build-run", required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    source, root, output = args.source.resolve(), args.compilers.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    protocol = json.loads(args.protocol.read_text())
    host, vm = os.environ["BENCHMARK_HOST"], int(os.environ["BENCHMARK_REPLICATE"])
    if os.cpu_count() != protocol["cores"] or vm not in range(1, protocol["independent_vms_per_arch"] + 1):
        raise RuntimeError("Unexpected standard runner or replicate")
    source_sha = subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip()
    if source_sha != protocol["source_sha"]:
        raise RuntimeError("Wrong IronRDP revision")
    subprocess.run(["git", "-C", source, "diff", "--exit-code"], check=True)
    compilers, metadata, stdlibs = install(root, protocol, host, args.build_run)
    tools = tool_identity(args.clang.resolve())
    if not equivalent_tools(tools, metadata["baseline"]["tools"]):
        raise RuntimeError("Native toolchain or SDK changed since compiler construction")
    common_bin = compilers["baseline"].parent
    os.environ["PATH"] = str(common_bin) + os.pathsep + str(args.clang.resolve()) + os.pathsep + os.environ["PATH"]
    os.environ["RUSTDOC"] = str(common_bin / "rustdoc.exe")
    for key in ("GH_TOKEN", "GITHUB_TOKEN"):
        os.environ.pop(key, None)
    # Fetch once with the baseline compiler before any measured command.
    subprocess.run([str(common_bin / "cargo.exe"), "fetch", "--locked"], cwd=source,
                   env={**os.environ, "RUSTC": str(compilers["baseline"])}, check=True)
    validate_meter(output / "meter-validation")
    index = {
        "protocol": protocol, "host": host, "vm": vm, "pilot": args.pilot,
        "build_run": args.build_run, "benchmark_run": os.environ["GITHUB_RUN_ID"],
        "benchmark_attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "variants": list(VARIANTS), "tools": tools, "stdlibs": stdlibs,
        "cargo_sha256": digest(common_bin / "cargo.exe"),
        "rustdoc_sha256": digest(common_bin / "rustdoc.exe"),
        "compiler_metadata": metadata, "runs": [],
    }
    save(output / "index.json", index)
    warmups = 0 if args.pilot else protocol["warmup_rounds"]
    rounds = 1 if args.pilot else warmups + protocol["measured_rounds"]
    for round_index in range(rounds):
        for position, variant in enumerate(paired_order(list(VARIANTS), vm, round_index)):
            name = f"round-{round_index}-{variant}"
            print(f"BEGIN VM {vm} {name}", flush=True)
            run_block(source, output / name, compilers[variant], protocol,
                      {"variant": variant, "round": round_index}, round_index == 0,
                      correctness_env={"RUST_TEST_THREADS": str(protocol["correctness_test_threads"])})
            index["runs"].append({
                "variant": variant, "round": round_index, "position": position,
                "warmup": round_index < warmups, "path": f"{name}/results.json",
            })
            save(output / "index.json", index)
    subprocess.run(["git", "-C", source, "diff", "--exit-code"], check=True)
    index["complete"] = True
    save(output / "index.json", index)


if __name__ == "__main__":
    main()
