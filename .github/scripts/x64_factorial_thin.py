"""Matched 2x2 Rust/LLVM ThinLTO pilot with a fixed LLD tool stack."""

import argparse
import json
import os
from pathlib import Path
import random
import shutil
import statistics
import subprocess
import time
import tomllib

from build_arm_compilers import digest, save
from compiler_probe import validate_meter
from msvc_experiment import environment, equivalent_tools, execute, tool_identity
from x64_rust_thin_incremental import (
    HOST, block, build, hosted_only, native_inputs, read, unpack,
)

PROTOCOL = Path(__file__).resolve().parents[2] / "ci-benchmark/x64-factorial-thin.json"
ARMS = ("baseline", "rust-thin", "llvm-thin", "both-thin")
SEQUENCES = ((0, 1, 3, 2), (1, 2, 0, 3), (2, 3, 1, 0), (3, 0, 2, 1))


def order(vm, round_index):
    if vm not in range(1, 5) or round_index not in range(4):
        raise ValueError("Four predeclared VMs and four rounds are required")
    return [ARMS[i] for i in SEQUENCES[(vm - 1 + round_index) % 4]]


def verify_records(records, protocol):
    if set(records) != set(ARMS):
        raise RuntimeError("A complete four-arm producer matrix is required")
    baseline = records["baseline"]
    expected_config = None
    for arm in ARMS:
        record = records[arm]
        if (record.get("build_complete") is not True or record["variant"] != arm
                or record["protocol"] != protocol
                or record["cache"] != {"enabled": False, "hit_rate": None}):
            raise RuntimeError("Wrong or incomplete factorial producer")
        for key in ("run_id", "attempt", "harness_sha", "source_patch_sha256",
                    "native_inputs", "stage0_cargo_sha256", "image"):
            if record[key] != baseline[key]:
                raise RuntimeError(f"Unmatched producer identity: {key}")
        if not equivalent_tools(record["tools"], baseline["tools"]):
            raise RuntimeError("Unmatched native tools")
        rust_thin, llvm_thin = protocol["lto_factors"][arm]
        config = tomllib.loads(record["configuration"])
        if (config["rust"]["lto"] != ("thin" if rust_thin else "thin-local")
                or config["llvm"]["thin-lto"] is not llvm_thin
                or config["llvm"].get("use-linker") is not None
                or config["target"][HOST]["linker"] != "lld-link.exe"):
            raise RuntimeError("Wrong factorial intervention")
        config["rust"]["lto"], config["llvm"]["thin-lto"] = "thin-local", False
        if expected_config is None:
            expected_config = config
        elif config != expected_config:
            raise RuntimeError("Configuration differs beyond the two LTO factors")
        audit = record["profile_use_audit"]
        if (audit["rustc_profile_use"] is not True or audit["rejected_profile_mismatch_warnings"]
                or any(audit[key] is not rust_thin for key in
                       ("driver_thin_flag", "driver_dylib_lto_flag", "driver_embedded_bitcode"))
                or audit["llvm_native_lto"].upper() not in (("THIN",) if llvm_thin else ("OFF", ""))):
            raise RuntimeError("Actual compiler intervention audit failed")
        if record["driver"] != f"bin/rustc_driver{audit['driver_suffix']}.dll":
            raise RuntimeError("Final driver and package identity disagree")


def file_manifest(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(root.rglob("*")) if p.is_file()}


def share_stdlib(root, records):
    relative = Path("lib") / "rustlib" / HOST / "lib"
    original = root / "baseline" / relative
    canonical = file_manifest(original)
    if canonical != records["baseline"]["stdlib"]:
        raise RuntimeError("Baseline stdlib was modified")
    receipts = {}
    for arm in ARMS:
        package = root / arm
        if file_manifest(package) != records[arm]["files"]:
            raise RuntimeError("Original package changed before controlled stdlib replacement")
        if arm != "baseline":
            shutil.rmtree(package / relative)
            shutil.copytree(original, package / relative)
        expected = {name: value for name, value in records[arm]["files"].items()
                    if not name.startswith(relative.as_posix() + "/")}
        expected.update({f"{relative.as_posix()}/{name}": value for name, value in canonical.items()})
        actual = file_manifest(package)
        if actual != expected:
            raise RuntimeError("Controlled library replacement changed unexpected files")
        receipts[arm] = {"original_archive_sha256": records[arm]["archive_sha256"],
                         "evaluated_files": actual}
    return receipts


def compiler_identity(package, record):
    paths = ("bin/rustc.exe", record["driver"])
    hashes = {name: digest(package / name) for name in paths}
    if any(hashes[name] != record["files"][name] for name in paths):
        raise RuntimeError("Compiler executable or driver changed")
    return {"RUSTC": str(package / "bin/rustc.exe"), "files": hashes,
            "driver_path": str(package / record["driver"])}


def prove_loaded_driver(package, record, env, output):
    """Keep rustc waiting for stdin so its actual loaded driver can be inspected."""
    identity = compiler_identity(package, record)
    output.mkdir()
    command = [identity["RUSTC"], "--crate-name", "identity_probe", "--crate-type=lib",
               "--emit=metadata", "-o", str(output / "identity.rmeta"), "-"]
    process = subprocess.Popen(command, cwd=output, env=env, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 30
        loaded = []
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("Compiler exited before loaded-driver inspection")
            query = (
                "$ErrorActionPreference='Stop'; "
                f"@(Get-Process -Id {process.pid}).Modules | "
                "Where-Object { $_.ModuleName -like 'rustc_driver-*.dll' } | "
                "Select-Object -ExpandProperty FileName | ConvertTo-Json -Compress"
            )
            text = subprocess.check_output(
                ["powershell.exe", "-NoProfile", "-Command", query],
                text=True, timeout=30, env=env).strip()
            if text:
                value = json.loads(text)
                loaded = [value] if isinstance(value, str) else value
                break
            time.sleep(0.1)
        if len(loaded) != 1 or Path(loaded[0]).resolve() != Path(identity["driver_path"]).resolve():
            raise RuntimeError(f"Wrong or unobserved loaded compiler driver: {loaded}")
        stdout, stderr = process.communicate(b"pub fn identity_probe() -> u32 { 42 }\n", timeout=120)
        (output / "compile.stdout").write_bytes(stdout)
        (output / "compile.stderr").write_bytes(stderr)
        if process.returncode != 0:
            raise RuntimeError(f"Identity smoke failed: {stderr.decode(errors='replace')}")
        save(output / "identity.json", {**identity, "loaded_driver": loaded[0],
                                       "pid": process.pid, "exit_code": process.returncode})
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=30)


def benchmark(root, source, vm):
    hosted_only()
    protocol = read(PROTOCOL)
    order(vm, 0)
    output = root / "e"
    if subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip() != protocol["source_sha"]:
        raise RuntimeError("Wrong IronRDP source")
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    records = {arm: unpack(root / "artifacts" / f"factorial-{arm}-package", root / arm) for arm in ARMS}
    verify_records(records, protocol)
    baseline = records["baseline"]
    if (baseline["run_id"] != os.environ["GITHUB_RUN_ID"]
            or baseline["attempt"] != os.environ["GITHUB_RUN_ATTEMPT"]
            or baseline["harness_sha"] != os.environ["GITHUB_SHA"]):
        raise RuntimeError("Producer run/head/attempt differs from the consumer")
    tools = tool_identity(root / "clang/bin")
    for name in ("lld-link.exe", "llvm-lib.exe"):
        tools["files"][name] = {"path": str(root / "clang/bin" / name),
                               "sha256": digest(root / "clang/bin" / name)}
    if (not equivalent_tools(baseline["tools"], tools) or native_inputs() != baseline["native_inputs"]
            or os.environ["ImageVersion"] != baseline["image"]):
        raise RuntimeError("Consumer tool/SDK/image inputs differ from producers")
    evaluated = share_stdlib(root, records)
    env = environment(output, root / "clang/bin")
    env.pop("RUSTC_BOOTSTRAP", None)
    cargo = root / "baseline/bin/cargo.exe"
    env["PATH"] = str(cargo.parent) + os.pathsep + env["PATH"]
    index = {
        "complete": False, "pilot": True, "full_release_qualified": False,
        "protocol": protocol, "vm": vm, "run_id": os.environ["GITHUB_RUN_ID"],
        "attempt": os.environ["GITHUB_RUN_ATTEMPT"], "harness_sha": os.environ["GITHUB_SHA"],
        "compilers": records, "evaluated_packages": evaluated, "tools": tools,
        "cargo_sha256": digest(cargo), "runs": [],
    }
    save(output / "index.json", index)
    for arm in ARMS:
        prove_loaded_driver(root / arm, records[arm], env, output / f"identity-{arm}")
    execute([cargo, "fetch", "--locked", "--target", HOST], source,
            {**env, "RUSTC": str(root / "baseline/bin/rustc.exe")}, output,
            "fetch-outside-measurement", timeout=1200, cores=4)
    lock = digest(source / "Cargo.lock")
    index["workload_lock_sha256"] = lock
    validate_meter(output / "meter-validation")
    correctness_env = {"PUBLIC": os.environ["PUBLIC"]}
    if not Path(correctness_env["PUBLIC"]).is_dir():
        raise RuntimeError("Correctness requires the actual Windows public-user directory")
    for arm in order(vm, 0):
        block(source, output / f"correctness-{arm}", root / arm / "bin/rustc.exe",
              cargo, protocol, env, correctness=True, correctness_env=correctness_env)
    for round_index in range(4):
        for position, arm in enumerate(order(vm, round_index)):
            before = compiler_identity(root / arm, records[arm])
            name = f"round-{round_index}-{arm}"
            result = block(source, output / name, root / arm / "bin/rustc.exe", cargo, protocol, env)
            after = compiler_identity(root / arm, records[arm])
            if before != after:
                raise RuntimeError("Compiler changed during a measured block")
            save(output / name / "compiler-identity.json", before)
            index["runs"].append({
                "variant": arm, "round": round_index, "position": position,
                "warmup": round_index == 0, "path": f"{name}/results.json",
                "wall_seconds": result["wall_seconds"], "cpu_seconds": result["cpu_seconds"],
            })
            save(output / "index.json", index)
    if digest(source / "Cargo.lock") != lock:
        raise RuntimeError("Workload lockfile changed")
    for arm in ARMS:
        if file_manifest(root / arm) != evaluated[arm]["evaluated_files"]:
            raise RuntimeError("Evaluated compiler/sysroot changed")
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    index["complete"] = True
    save(output / "index.json", index)


def effects(means):
    pairs = {"rust_without_llvm": ("baseline", "rust-thin"),
             "llvm_without_rust": ("baseline", "llvm-thin"),
             "llvm_with_rust": ("rust-thin", "both-thin"),
             "rust_with_llvm": ("llvm-thin", "both-thin"),
             "combined": ("baseline", "both-thin")}
    if set(means) != set(ARMS) or any(value <= 0 for value in means.values()):
        raise ValueError("Positive four-arm means are required")
    values = {name: 100 * (1 - means[t] / means[b]) for name, (b, t) in pairs.items()}
    values["multiplicative_interaction"] = 100 * (
        means["both-thin"] * means["baseline"] / (means["rust-thin"] * means["llvm-thin"]) - 1)
    return values


def summarize(vm_means):
    if len(vm_means) != 4:
        raise ValueError("All four independent consumers must qualify")
    result = {}
    for metric in ("wall_seconds", "cpu_seconds"):
        means = {arm: statistics.mean(vm[metric][arm] for vm in vm_means) for arm in ARMS}
        point = effects(means)
        rng = random.Random(20261030)
        samples = {key: [] for key in point}
        for _ in range(10000):
            picked = rng.choices(vm_means, k=4)
            draw = effects({arm: statistics.mean(vm[metric][arm] for vm in picked) for arm in ARMS})
            for key, value in draw.items():
                samples[key].append(value)
        intervals = {key: sorted(values) for key, values in samples.items()}
        result[metric] = {
            "means": means,
            "effects": {key: {"percent": value,
                              "paired_vm_bootstrap_95": [intervals[key][250],
                                                        intervals[key][9749]]}
                        for key, value in point.items()},
        }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("build", "benchmark"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--variant", choices=ARMS)
    parser.add_argument("--vm", type=int)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.phase == "build":
            build(root, args.variant, PROTOCOL)
        else:
            benchmark(root, args.source.resolve(), args.vm)
    except Exception as error:
        save(root / "e/failure.json", {"phase": args.phase, "type": type(error).__name__,
                                     "message": str(error)})
        raise
