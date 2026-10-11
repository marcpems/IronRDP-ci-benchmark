"""Paired, cold-artifact replay of the original seven offline Cargo measurements."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

from compiler_probe import save, validate_meter
from arm_ab_probe import download_compilers, verify_custom, verify_shared_stdlib
from install_optimized_rust import verify_installation
from offline_benchmark import NATIVE_COMMANDS, COMMON_COMMAND, WASM_COMMAND
from process_metrics import measure, measurement_session

COMMANDS = [*NATIVE_COMMANDS, ("common", COMMON_COMMAND), ("wasm", WASM_COMMAND)]
PROFILE_ENV = {"CARGO_INCREMENTAL": "0", "CARGO_PROFILE_DEV_DEBUG": "0",
               "CARGO_BUILD_JOBS": "4", "CARGO_NET_OFFLINE": "true",
               "MSBUILDDISABLENODEREUSE": "1"}


def paired_order(variants, vm, round_index):
    if len(variants) > 2:
        from arm_ab_probe import variant_order
        return variant_order(variants, vm, round_index)
    return variants.copy() if (vm + round_index) % 2 else list(reversed(variants))


def build_environment(env, compiler):
    for key in env:
        if key.startswith("CARGO_PROFILE_") and key != "CARGO_PROFILE_DEV_DEBUG" and env[key]:
            raise RuntimeError(f"Unexpected profile override: {key}")
    for key in ("RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER",
                "CARGO_BUILD_TARGET", "CARGO_BUILD_RUSTC", "RUSTC", "RUSTDOCFLAGS", "CARGO_ENCODED_RUSTDOCFLAGS"):
        if env.get(key):
            raise RuntimeError(f"Unexpected compiler override: {key}")
    return {**{k: v for k, v in env.items() if k not in ("GH_TOKEN", "GITHUB_TOKEN")},
            **PROFILE_ENV, "RUSTC": str(compiler)}


def telemetry_executables():
    if os.name != "nt":
        return []
    vswhere = Path(os.environ["ProgramFiles(x86)"]) / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
    machine = platform.machine().lower()
    if machine not in ("arm64", "aarch64", "amd64", "x86_64"):
        raise RuntimeError(f"Unsupported Windows build architecture: {machine}")
    arch = "arm64" if machine in ("arm64", "aarch64") else "x64"
    found = subprocess.check_output([
        str(vswhere), "-latest", "-products", "*", "-find",
        rf"VC\Tools\MSVC\*\bin\Host{arch}\{arch}\vctip.exe",
    ], text=True).splitlines()
    return [str(Path(p).resolve()) for p in found if p]


def run_block(source, output, compiler, protocol, identity, verify_tests, correctness_env=None):
    output.mkdir()
    env = build_environment(os.environ, compiler)
    version = subprocess.check_output([str(compiler), "-vV"], text=True, env=env)
    host = os.environ["BENCHMARK_HOST"]
    if (f"host: {host}\n" not in version or protocol["rust_sha"] not in version
            or f"release: {protocol['rust_version']}\n" not in version):
        raise RuntimeError("Wrong compiler identity")
    lock = (source / "Cargo.lock").read_bytes().replace(b"\r\n", b"\n")
    metadata = {
        **identity, "source_sha": protocol["source_sha"], "rustc": version,
        "compiler_executable": str(compiler), "profile_environment": PROFILE_ENV,
        "lock_lf_sha256": hashlib.sha256(lock).hexdigest(),
        "cargo": subprocess.check_output(["cargo", "-V"], env=env, text=True).strip(),
        "platform": platform.platform(), "logical_cpus": os.cpu_count(),
        "environment": {k: os.environ.get(k) for k in (
            "BENCHMARK_PLATFORM", "BENCHMARK_REPLICATE", "BENCHMARK_HOST",
            "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "ImageOS", "ImageVersion",
        )},
    }
    hardware = (["pwsh", "-NoProfile", "-Command",
                 "Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,"
                 "NumberOfLogicalProcessors | ConvertTo-Json"]
                if os.name == "nt" else ["lscpu", "--json"])
    metadata["hardware"] = subprocess.check_output(hardware, text=True)
    background = telemetry_executables()
    metadata["approved_background_executables"] = background
    rows, checks = [], []
    with tempfile.TemporaryDirectory(prefix="native-ci-", dir=os.environ["RUNNER_TEMP"]) as tmp, \
            measurement_session(background) as session:
        targets = {name: Path(tmp) / name for name in ("native", "common", "wasm")}
        metadata["cold_target_directories"] = {k: str(p) for k, p in targets.items()}
        save(output / "environment.json", metadata)
        for name, args in COMMANDS:
            target = targets[name if name in targets else "native"]
            child_env = {**env, "CARGO_TARGET_DIR": str(target)}
            command = ["cargo", *args, "--frozen", "--timings", "--message-format=json"]
            row = measure(command, source, child_env, protocol["cores"], output / name, session=session)
            row.update({"name": name, "seconds": row["wall_seconds"],
                        "target_directory": str(target), "fresh_artifacts": 0, "compiled_artifacts": 0})
            for line in (output / f"{name}.stdout").read_text(encoding="utf-8").splitlines():
                item = json.loads(line)
                if item.get("reason") == "compiler-artifact":
                    row["fresh_artifacts" if item["fresh"] else "compiled_artifacts"] += 1
            save(output / f"{name}.measurement.json", row)
            if row["exit_code"]:
                raise RuntimeError(f"{name} failed; inspect {output / (name + '.stderr')}")
            if not row["compiled_artifacts"]:
                raise RuntimeError(f"{name} did not compile any new artifacts")
            shutil.copyfile(target / "cargo-timings" / "cargo-timing.html",
                            output / f"{name}.timings.html")
            rows.append(row)
            print(f"{name}: wall={row['wall_seconds']:.3f}s CPU={row['cpu_seconds']:.3f}s", flush=True)
        if verify_tests:
            for name, args in NATIVE_COMMANDS[1:]:
                command = ["cargo", *(a for a in args if a != "--no-run"), "--frozen"]
                result = measure(
                    command, source, {**env, **(correctness_env or {}),
                                      "CARGO_TARGET_DIR": str(targets["native"])},
                    protocol["cores"], output / f"{name}-correctness", session=session, timeout=1200,
                )
                check = {"name": name, "command": command, "exit_code": result["exit_code"],
                         "environment_overrides": correctness_env or {},
                         "seconds_outside_measurement": result["wall_seconds"],
                         "cpu_seconds_outside_measurement": result["cpu_seconds"]}
                checks.append(check)
                save(output / "correctness.json", checks)
                if result["exit_code"]:
                    raise RuntimeError(f"Original native tests failed: {name}; see correctness stdout/stderr")
    if (source / "Cargo.lock").read_bytes().replace(b"\r\n", b"\n") != lock:
        raise RuntimeError("Workload lockfile changed")
    save(output / "results.json", {"metadata": metadata, "measurements": rows, "correctness": checks})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--installation", type=Path)
    parser.add_argument("--compilers", type=Path)
    parser.add_argument("--release-tag")
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if os.cpu_count() != protocol["cores"]:
        raise RuntimeError("Expected a standard four-CPU runner")
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    if actual != protocol["source_sha"]:
        raise RuntimeError("Wrong workload revision")
    subprocess.run(["git", "diff", "--exit-code"], cwd=source, check=True)
    output.mkdir(exist_ok=False)
    validate_meter(output / "meter-validation")
    official = Path(subprocess.check_output(["rustup", "which", "rustc"], cwd=source, text=True).strip())
    compilers = {"official": official}
    variants = protocol["windows_variants"] if os.name == "nt" else protocol["linux_variants"]
    if args.release_tag and os.name == "nt":
        if args.compilers is None:
            parser.error("--compilers is required for release downloads")
        download_compilers(args.compilers.resolve(), variants, args.release_tag, protocol)
    for name in ("GH_TOKEN", "GITHUB_TOKEN"):
        os.environ.pop(name, None)
    if os.name == "nt":
        if args.compilers is not None:
            root = args.compilers.resolve()
            for variant in variants:
                if variant == "official":
                    continue
                provenance = root / f"{variant}.json"
                if hashlib.sha256(provenance.read_bytes()).hexdigest() != protocol["compiler_metadata_sha256"][variant]:
                    raise RuntimeError(f"Wrong compiler metadata: {variant}")
                compilers[variant] = verify_custom(root, variant, protocol)
                metadata = json.loads(provenance.read_text(encoding="utf-8"))
                verify_shared_stdlib(official, metadata, os.environ["BENCHMARK_HOST"])
                shutil.copyfile(provenance, output / f"{variant}-compiler.json")
        elif args.installation is None:
            parser.error("--installation is required on Windows")
        else:
            root = args.installation.resolve()
            record = json.loads((root / "installation.json").read_text(encoding="utf-8"))
            manifest = record["manifest"]
            if (manifest["compiler_archive_sha256"]["optimized"] != protocol["optimized_archive_sha256"]
                    or manifest["metadata_sha256"] != protocol["optimized_metadata_sha256"]):
                raise RuntimeError("Installer used the wrong preregistered compiler")
            compilers["optimized"] = verify_installation(root, manifest, official)
            shutil.copyfile(root / "installation.json", output / "installation.json")
            shutil.copyfile(root / "optimized.json", output / "optimized-compiler.json")
    vm = int(os.environ["BENCHMARK_REPLICATE"])
    if vm not in range(1, protocol["independent_vms_per_os"] + 1):
        raise RuntimeError("Unexpected VM index")
    index = {"protocol": protocol, "platform": os.environ["BENCHMARK_PLATFORM"],
             "vm": vm, "pilot": args.pilot, "variants": variants, "runs": []}
    if args.compilers is not None:
        index["identical_windows_stdlibs_verified"] = True
    save(output / "index.json", index)
    warmups = 0 if args.pilot else protocol["warmup_rounds"]
    rounds = 1 if args.pilot else warmups + protocol["measured_rounds"]
    for round_index in range(rounds):
        for position, variant in enumerate(paired_order(variants, vm, round_index)):
            name = f"round-{round_index}-{variant}"
            print(f"BEGIN {name} (VM {vm}, position {position})", flush=True)
            run_block(source, output / name, compilers[variant], protocol,
                      {"variant": variant, "round": round_index}, round_index == 0)
            index["runs"].append({
                "variant": variant, "round": round_index, "position": position,
                "warmup": round_index < warmups, "path": f"{name}/results.json",
            })
            save(output / "index.json", index)
    subprocess.run(["git", "diff", "--exit-code"], cwd=source, check=True)


if __name__ == "__main__":
    main()
