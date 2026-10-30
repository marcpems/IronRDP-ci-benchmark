"""Bounded hosted pilot isolating Rust compiler ThinLTO above repaired fixed PGO."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import tomllib
import zipfile

from build_arm_compilers import digest, excluded_sysroot_entries, save
from compiler_probe import validate_meter
from msvc_experiment import (
    cmake_toolchain, configuration as compiler_configuration, coverage, environment,
    equivalent_tools, execute, tool_identity,
)
from native_ci_probe import build_environment, paired_order, telemetry_executables
from offline_benchmark import NATIVE_COMMANDS
from process_metrics import measure, measurement_session
from stdlib_runtime_identity import compare_stdlib
from x64_pgo_release import preserve_literal_release_batch
from x64_profile_only import audit_profile_use

PROTOCOL = Path(__file__).resolve().parents[2] / "ci-benchmark/x64-rust-thin-incremental.json"
HOST = "x86_64-pc-windows-msvc"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def configuration(clang, tools, variant, profiles):
    if variant not in ("baseline", "rust-thin"):
        raise ValueError("Unknown compiler arm")
    config = compiler_configuration(
        HOST, clang, Path(tools["files"]["link.exe"]["path"]),
        Path(tools["files"]["lib.exe"]["path"]),
        "pgo" if variant == "baseline" else "pgo-rust-thin", profiles,
    )
    return config.replace("lld = true", "lld = false").replace(
        "llvm-tools = true", "llvm-tools = false")


def validate_configs(left, right):
    left, right = (tomllib.loads(text) for text in (left, right))
    if left["rust"]["lto"] != "thin-local" or right["rust"]["lto"] != "thin":
        raise RuntimeError("The pair is not thin-local versus cross-crate thin")
    for config in (left, right):
        if config["llvm"]["thin-lto"] or config["target"][HOST]["linker"] != "link.exe":
            raise RuntimeError("LLVM ThinLTO or a non-Microsoft linker invalidates this study")
    right["rust"]["lto"] = "thin-local"
    if left != right:
        raise RuntimeError("Configuration differs beyond Rust ThinLTO")


def verify_profiles(directory, protocol):
    for name, key in (("result", "training_result_sha256"),
                      ("provenance", "training_provenance_sha256")):
        if digest(directory / f"{name}.json") != protocol[key]:
            raise RuntimeError(f"Frozen training {name} changed")
    training = read(directory / "result.json")
    if (training.get("complete") is not True or training["run_id"] != protocol["profile_run"]
            or training["attempt"] != protocol["profile_attempt"]):
        raise RuntimeError("Wrong or unqualified training run")
    for key in ("rust_sha", "llvm_sha", "rustc_perf_sha", "fixed_helper_git_blob",
                "clang_installer_sha256"):
        if training[key] != protocol[key]:
            raise RuntimeError(f"Training identity differs: {key}")
    for name, expected in protocol["profiles"].items():
        if (digest(directory / f"{name}-pgo.profdata") != expected
                or training["profiles"][name]["sha256"] != expected):
            raise RuntimeError(f"Frozen profile changed: {name}")
    if not all(training["llvm_training_coverage"][name]["active_functions"] > 0
               for name in ("X86TargetLowering", "InstCombine")):
        raise RuntimeError("Training lacks active LLVM backend coverage")
    return training


def verify_pair(left, right, packages=None):
    if (left.get("build_complete") is not True or right.get("build_complete") is not True
            or left["variant"] != "baseline" or right["variant"] != "rust-thin"):
        raise RuntimeError("Both successfully built pilot arms are required")
    for key in ("protocol", "run_id", "attempt", "harness_sha", "source_patch_sha256",
                "native_inputs", "stage0_cargo_sha256", "image"):
        if left[key] != right[key]:
            raise RuntimeError(f"Paired input mismatch: {key}")
    if not equivalent_tools(left["tools"], right["tools"]):
        raise RuntimeError("Paired native tool binaries differ")
    validate_configs(left["configuration"], right["configuration"])
    if packages is not None:
        return compare_stdlib(packages, {"baseline": left, "rust-thin": right})
    if left["stdlib"] != right["stdlib"]:
        raise RuntimeError("Paired input mismatch: stdlib")


def native_inputs():
    result = {}
    for key in ("INCLUDE", "LIB"):
        for index, value in enumerate(os.environ[key].split(os.pathsep)):
            if not value:
                continue
            root = Path(value)
            if not root.is_dir():
                raise RuntimeError(f"Native input root is missing: {root}")
            result[f"{key}-{index}"] = {
                "path": str(root),
                "files": {p.relative_to(root).as_posix(): digest(p)
                          for p in sorted(root.rglob("*")) if p.is_file()},
            }
    binaries = Path(shutil.which("link.exe")).parent
    result["msvc-binaries"] = {
        "path": str(binaries),
        "files": {p.name: digest(p) for p in sorted(binaries.iterdir())
                  if p.suffix.lower() in (".dll", ".exe") and p.is_file()},
    }
    return result


def hosted_only():
    if (os.name != "nt" or os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted"
            or os.environ.get("RUNNER_ARCH") != "X64" or os.cpu_count() != 4):
        raise RuntimeError("Only standard four-LP GitHub-hosted Windows x64 is authorized")


def verify_source(source, protocol, patched=False):
    for relative, key in ((".", "rust_sha"), ("src/llvm-project", "llvm_sha"),
                          ("src/tools/rustc-perf", "rustc_perf_sha")):
        if subprocess.check_output(
            ["git", "-C", source / relative, "rev-parse", "HEAD"], text=True
        ).strip() != protocol[key]:
            raise RuntimeError(f"Wrong source: {relative}")
    expected = "1\t0\tsrc/bootstrap/src/utils/helpers.rs" if patched else ""
    changes = subprocess.check_output(
        ["git", "-C", source, "diff", "--numstat", "--ignore-submodules=dirty", "HEAD"], text=True
    ).strip()
    if changes != expected:
        raise RuntimeError(f"Unexpected Rust source modifications: {changes}")
    for relative in ("src/llvm-project", "src/tools/rustc-perf"):
        subprocess.run(["git", "-C", source / relative, "diff", "--exit-code", "HEAD"], check=True)
    if patched and subprocess.check_output(
        ["git", "-C", source, "hash-object", "src/bootstrap/src/utils/helpers.rs"], text=True
    ).strip() != protocol["fixed_helper_git_blob"]:
        raise RuntimeError("Bootstrap prerequisite differs from the qualified exact blob")


def build(root, variant):
    hosted_only()
    protocol = read(PROTOCOL)
    source, output, profiles = root / "r", root / "e", root / "profiles"
    if root != Path(r"D:\ri") or (source / "build").exists():
        raise RuntimeError("Build requires the same clean, short hosted path in both arms")
    if shutil.disk_usage(root).free < 90 * 2**30:
        raise RuntimeError("Less than 90 GiB free: do not start a resource-constrained build")
    training = verify_profiles(profiles, protocol)
    save(output / "checkout.json", preserve_literal_release_batch(source / "src/llvm-project"))
    verify_source(source, protocol)
    patch = PROTOCOL.parent / "bootstrap-clang-runtime.patch"
    subprocess.run(["git", "-C", source, "apply", "--check", "--ignore-space-change", patch], check=True)
    subprocess.run(["git", "-C", source, "apply", "--ignore-space-change", patch], check=True)
    verify_source(source, protocol, patched=True)
    (output / "source.patch").write_bytes(
        subprocess.check_output(["git", "-C", source, "diff", "--binary", "HEAD"]))
    clang = root / "clang/bin"
    if digest(root / "LLVM-20.1.3-win64.exe") != protocol["clang_installer_sha256"]:
        raise RuntimeError("Wrong CI Clang installer")
    tools = tool_identity(clang)
    for name in ("clang-cl.exe", "llvm-profdata.exe"):
        if tools["files"][name]["sha256"] != training["tools"]["files"][name]["sha256"]:
            raise RuntimeError("Clang differs from the profile producer")
    config = configuration(clang, tools, variant, profiles)
    validate_configs(configuration(clang, tools, "baseline", profiles),
                     configuration(clang, tools, "rust-thin", profiles))
    (source / "bootstrap.toml").write_text(config, encoding="utf-8")
    (output / "bootstrap.toml").write_text(config, encoding="utf-8")
    env = environment(output, clang)
    env.update(MATCHED_BUILD_CORES="4", CMAKE_TOOLCHAIN_FILE=str(cmake_toolchain(output, tools)))
    record = {
        "complete": False, "build_complete": False, "variant": variant, "protocol": protocol,
        "run_id": os.environ["GITHUB_RUN_ID"], "attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "harness_sha": os.environ["GITHUB_SHA"], "image": os.environ["ImageVersion"],
        "tools": tools, "native_inputs": native_inputs(), "configuration": config,
        "source_patch_sha256": digest(output / "source.patch"), "training_tools": training["tools"],
        "stack_policy": "Unmodified compiler default; no RUST_MIN_STACK override",
        "qualification": "Pending compiler smoke; no full extracted-distribution qualification",
        "cache": {"enabled": False, "hit_rate": None},
    }
    save(output / "result.json", record)
    deadline = float(os.environ["THIN_JOB_STARTED"]) + protocol["build_budget_minutes"] * 60
    remaining = deadline - time.time()
    if remaining <= 0:
        raise TimeoutError("Build preparation exhausted the production deadline")
    save(output / "active-stage.json", {
        "phase": "fixed-profile-compiler", "started_unix": time.time(),
        "deadline_unix": deadline, "timeout_seconds": remaining,
        "command": [sys.executable, "x.py", "build", "--stage", "2", "library/std", "compiler/rustc"],
    })
    record["production"] = execute(
        [sys.executable, "x.py", "build", "--stage", "2", "library/std", "compiler/rustc"],
        source, env, output, "fixed-profile-dist", timeout=remaining, cores=4,
    )
    shutil.copy2(source / "build/metrics.json", output / "production-metrics.json")
    save(output / "coverage.json", coverage(
        source / "build" / HOST / "llvm/bin/llvm-profdata.exe", profiles / "llvm-pgo.profdata",
        ("X86TargetLowering", "InstCombine"), env, output))
    caches = list((source / "build" / HOST / "llvm").rglob("CMakeCache.txt"))
    if len(caches) != 1:
        raise RuntimeError("Expected one native LLVM CMake cache")
    cache = {}
    for line in caches[0].read_text().splitlines():
        if line and not line.startswith(("#", "//")) and ":" in line and "=" in line:
            key, value = line.split("=", 1)
            cache[key.split(":", 1)[0]] = value
    for key, name in (("CMAKE_LINKER", "link.exe"), ("CMAKE_AR", "lib.exe")):
        if digest(Path(cache[key])) != tools["files"][name]["sha256"]:
            raise RuntimeError("Native LLVM did not use Microsoft linking tools")
    if (cache.get("LLVM_ENABLE_LTO", "OFF").upper() not in ("OFF", "")
            or cache.get("LLVM_BUILD_INSTRUMENTED", "OFF") not in ("OFF", "")
            or digest(Path(cache["LLVM_PROFDATA_FILE"])) != protocol["profiles"]["llvm"]):
        raise RuntimeError("Native LLVM LTO/instrumentation/profile mismatch")
    if any(value for key, value in cache.items() if "COMPILER_LAUNCHER" in key):
        raise RuntimeError("Unexpected native compiler cache launcher")
    shutil.copy2(caches[0], output / "LLVM-CMakeCache.txt")
    audit = audit_profile_use(source, output, profiles / "rustc-pgo.profdata")
    log = "\n".join((output / f"fixed-profile-dist.{ext}").read_text(errors="replace")
                    for ext in ("stdout", "stderr"))
    thin = re.compile(r"-Clto=thin(?:[\s'\"`]|$)")
    audit["driver_thin_flag"] = any(
        "rustc_driver" in line and thin.search(line) for line in log.splitlines())
    save(output / "profile-use-audit.json", audit)
    if (not audit["rustc_profile_use"] or audit["rejected_profile_mismatch_warnings"]
            or audit["driver_thin_flag"] != (variant == "rust-thin")):
        raise RuntimeError("Compiler profile or cross-crate ThinLTO evidence failed")
    verify_source(source, protocol, patched=True)
    verify_profiles(profiles, protocol)
    stage = source / "build" / HOST / "stage2"
    package = root / "package"
    shutil.copytree(stage, package, ignore=lambda p, names: excluded_sysroot_entries(stage, p, names))
    cargo = source / "build" / HOST / "stage0/bin/cargo.exe"
    shutil.copy2(cargo, package / "bin/cargo.exe")
    for name in ("COPYRIGHT", "LICENSE-APACHE", "LICENSE-MIT"):
        shutil.copy2(source / name, package / name)
    record["stage0_cargo_sha256"] = digest(cargo)
    std = package / "lib/rustlib" / HOST / "lib"
    record["stdlib"] = {p.name: digest(p) for p in sorted(std.iterdir()) if p.is_file()}
    if not any(name.startswith("libstd-") and name.endswith(".rlib") for name in record["stdlib"]):
        raise RuntimeError("Package lacks its own native standard library")
    compiler = package / "bin/rustc.exe"
    record["version"] = subprocess.check_output([compiler, "-vV"], text=True, env=env)
    for expected in (f"host: {HOST}", f"commit-hash: {protocol['rust_sha']}",
                     f"release: {protocol['rust_version']}"):
        if expected not in record["version"].splitlines():
            raise RuntimeError(f"Unexpected compiler version: {expected}")
    smoke = output / "smoke.rs"
    smoke.write_text("fn main() { assert_eq!((0..10).sum::<u32>(), 45); }\n", encoding="utf-8")
    smoke_env = {**env, "LLVM_PROFILE_FILE": str(output / "unexpected-%m-%p.profraw")}
    execute([compiler, smoke, "-o", output / "smoke.exe"], output, smoke_env, output,
            "smoke-compile", timeout=120, cores=4)
    execute([output / "smoke.exe"], output, smoke_env, output, "smoke-run", timeout=30, cores=4)
    if list(output.glob("*.profraw")):
        raise RuntimeError("Compiler is unexpectedly instrumented")
    record["files"] = {p.relative_to(package).as_posix(): digest(p)
                       for p in sorted(package.rglob("*")) if p.is_file()}
    archive = root / "package.zip"
    packaging_started = time.monotonic()
    save(output / "active-stage.json", {"phase": "package", "started_unix": time.time()})
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED, compresslevel=1) as bundle:
        for name in record["files"]:
            bundle.write(package / name, name)
    record.update(build_complete=True, archive_sha256=digest(archive),
                  archive_bytes=archive.stat().st_size,
                  packaging_seconds=time.monotonic() - packaging_started,
                  qualification="Compiler smoke passed; IronRDP correctness still pending; NOT a full release")
    save(output / "result.json", record)


def unpack(artifact, destination):
    record = read(artifact / "result.json")
    archive = artifact / "package.zip"
    if record.get("build_complete") is not True or digest(archive) != record["archive_sha256"]:
        raise RuntimeError("Package is incomplete or its checksum changed")
    with zipfile.ZipFile(archive) as bundle:
        for item in bundle.infolist():
            path = Path(item.filename)
            if (path.is_absolute() or ".." in path.parts or ":" in item.filename
                    or "\\" in item.filename):
                raise RuntimeError("Unsafe package member")
        bundle.extractall(destination)
    actual = {p.relative_to(destination).as_posix(): digest(p)
              for p in sorted(destination.rglob("*")) if p.is_file()}
    if actual != record["files"]:
        raise RuntimeError("Extracted package differs from the file manifest")
    return record


def block(source, output, compiler, cargo, protocol, env, correctness=False, correctness_env=None):
    output.mkdir()
    target = output / "target"
    target.mkdir()
    child_env = build_environment(env, compiler, protocol["cores"])
    child_env["CARGO_TARGET_DIR"] = str(target)
    if correctness:
        child_env.update(correctness_env or {})
    rows = []
    with measurement_session(telemetry_executables()) as session:
        for name, arguments in NATIVE_COMMANDS:
            args = [arg for arg in arguments if not (correctness and arg == "--no-run")]
            if correctness and name == "workspace-tests":
                args += ["--tests"]
            command = [str(cargo), *args, "--frozen"]
            if not correctness:
                command += ["--timings", "--message-format=json"]
            row = measure(command, source, child_env, protocol["cores"],
                          output / name, session=session, timeout=3600)
            row["name"] = name
            row["correctness_environment"] = (correctness_env or {}) if correctness else {}
            rows.append(row)
            save(output / f"{name}.json", row)
            save(output / "results.json", {"complete": False, "correctness": correctness, "rows": rows})
            if row["exit_code"] != 0:
                print(json.dumps(row), flush=True)
                for suffix in ("stdout", "stderr"):
                    log = output / f"{name}.{suffix}"
                    if log.is_file():
                        print(f"{log}:\n{log.read_text(errors='replace')[-16000:]}", flush=True)
                raise RuntimeError(f"Consumer command failed: {output / name}")
            if not correctness:
                messages = [json.loads(line) for line in (output / f"{name}.stdout").read_text().splitlines()]
                row["compiled_artifacts"] = sum(
                    item.get("reason") == "compiler-artifact" and not item["fresh"] for item in messages)
                if not row["compiled_artifacts"]:
                    raise RuntimeError(f"No compilation observed for {name}")
                shutil.copy2(target / "cargo-timings/cargo-timing.html", output / f"{name}.timings.html")
                save(output / f"{name}.json", row)
    result = {
        "complete": True, "correctness": correctness, "rows": rows,
        "wall_seconds": sum(row["wall_seconds"] for row in rows),
        "cpu_seconds": sum(row["cpu_seconds"] for row in rows),
    }
    save(output / "results.json", result)
    shutil.rmtree(target)
    return result


def benchmark(root, source, continuation=False):
    hosted_only()
    protocol = read(PROTOCOL)
    output = root / "e"
    output.mkdir(exist_ok=True)
    if subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip() != protocol["source_sha"]:
        raise RuntimeError("Wrong IronRDP source")
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    producer = read(PROTOCOL.with_name("x64-rust-thin-continuation.json")) if continuation else None
    records = {}
    for arm in protocol["variants"]:
        artifact = root / "artifacts" / arm
        if producer and (digest(artifact / "result.json") != producer["metadata_sha256"][arm]
                         or digest(artifact / "package.zip") != producer["archive_sha256"][arm]):
            raise RuntimeError("Continuation differs from the exact frozen original package")
        records[arm] = unpack(artifact, root / arm)
    stdlib_identity = verify_pair(
        records["baseline"], records["rust-thin"],
        {arm: root / arm for arm in protocol["variants"]} if continuation else None)
    if stdlib_identity:
        save(output / "stdlib-identity.json", stdlib_identity)
    for record in records.values():
        expected = producer or {"run_id": os.environ["GITHUB_RUN_ID"],
                                "attempt": os.environ["GITHUB_RUN_ATTEMPT"],
                                "head_sha": os.environ["GITHUB_SHA"]}
        if (record["protocol"] != protocol or record["run_id"] != expected["run_id"]
                or record["attempt"] != expected["attempt"]
                or record["harness_sha"] != expected["head_sha"]):
            raise RuntimeError("Only exact same-run owned compiler packages are accepted")
    tools = tool_identity(root / "clang/bin")
    if (not equivalent_tools(records["baseline"]["tools"], tools)
            or native_inputs() != records["baseline"]["native_inputs"]
            or os.environ["ImageVersion"] != records["baseline"]["image"]):
        raise RuntimeError("Consumer native environment differs from compiler production")
    env = environment(output, root / "clang/bin")
    env.pop("RUSTC_BOOTSTRAP", None)
    cargo = root / "baseline/bin/cargo.exe"
    env["PATH"] = str(cargo.parent) + os.pathsep + env["PATH"]
    compiler = root / "baseline/bin/rustc.exe"
    execute([cargo, "fetch", "--locked", "--target", HOST], source,
            {**env, "RUSTC": str(compiler)}, output, "fetch-outside-measurement", timeout=1200, cores=4)
    lock = digest(source / "Cargo.lock")
    validate_meter(output / "meter-validation")
    correctness_env = {"PUBLIC": os.environ["PUBLIC"]}
    if not Path(correctness_env["PUBLIC"]).is_dir():
        raise RuntimeError("The native correctness suite requires the actual Windows public-user directory")
    index = {
        "complete": False, "pilot": True, "full_release_qualified": False, "protocol": protocol,
        "run_id": os.environ["GITHUB_RUN_ID"], "attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "compilers": records, "tools": tools, "cargo_sha256": digest(cargo),
        "workload_lock_sha256": lock, "runs": [],
        "harness_sha": os.environ["GITHUB_SHA"], "producer": producer,
        "stdlib_identity": stdlib_identity,
        "correctness_environment": correctness_env,
    }
    save(output / "index.json", index)
    for arm in protocol["variants"]:
        block(source, output / f"correctness-{arm}", root / arm / "bin/rustc.exe",
              cargo, protocol, env, correctness=True, correctness_env=correctness_env)
    rounds = protocol["warmup_rounds"] + protocol["measured_rounds"]
    for round_index in range(rounds):
        for position, arm in enumerate(paired_order(protocol["variants"], 1, round_index)):
            name = f"round-{round_index}-{arm}"
            result = block(source, output / name, root / arm / "bin/rustc.exe",
                           cargo, protocol, env)
            index["runs"].append({
                "variant": arm, "round": round_index, "position": position,
                "warmup": round_index < protocol["warmup_rounds"],
                "path": f"{name}/results.json", "wall_seconds": result["wall_seconds"],
                "cpu_seconds": result["cpu_seconds"],
            })
            save(output / "index.json", index)
    if digest(source / "Cargo.lock") != lock:
        raise RuntimeError("IronRDP lockfile changed")
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    index["complete"] = True
    index["interpretation"] = "Descriptive one-build-pair, one-consumer-VM pilot; no population CI"
    save(output / "index.json", index)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("build", "benchmark"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--variant", choices=("baseline", "rust-thin"))
    parser.add_argument("--source", type=Path)
    parser.add_argument("--continuation", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.phase == "build":
            build(root, args.variant)
        else:
            benchmark(root, args.source.resolve(), continuation=args.continuation)
    except Exception as error:
        (root / "e").mkdir(parents=True, exist_ok=True)
        save(root / "e/failure.json", {
            "complete": False, "phase": args.phase, "variant": args.variant,
            "error": str(error), "unix": time.time(),
            "censored": isinstance(error, subprocess.TimeoutExpired),
            "timeout_cpu_receipt": "Unavailable when the process-meter raises a timeout",
        })
        raise
