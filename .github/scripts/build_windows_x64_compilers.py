"""Build native x64 PGO controls and ThinLTO treatments on standard Windows runners."""

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
import zipfile

from build_arm_compilers import RUST_SHA, LLVM_SHA, PERF_SHA, digest, excluded_sysroot_entries, save

HOST = "x86_64-pc-windows-msvc"
VARIANTS = ("pgo-control", "optimized")


def configuration(clang, variant):
    if variant not in VARIANTS:
        raise ValueError(f"Unknown compiler variant: {variant}")
    lto = variant == "optimized"
    linker_setting = "" if lto else 'use-linker = "lld"\n'
    return f"""profile = "dist"
[build]
build = "{HOST}"
host = ["{HOST}"]
target = ["{HOST}"]
build-dir = "build"
jobs = 4
extended = false
docs = false
locked-deps = true
profiler = true
optimized-compiler-builtins = true
metrics = true
print-step-timings = true
verbose = 2
[llvm]
download-ci-llvm = false
clang-cl = '{clang / "bin" / "clang-cl.exe"}'
optimize = true
assertions = false
ninja = true
link-jobs = 1
thin-lto = {str(lto).lower()}
link-shared = false
static-libstdcpp = true
{linker_setting}[rust]
channel = "stable"
download-rustc = false
optimize = true
debug-assertions = false
overflow-checks = false
codegen-units = 1
debuginfo-level-std = 1
codegen-units-std = 1
remap-debuginfo = true
codegen-backends = ["llvm"]
lld = true
llvm-tools = true
llvm-bitcode-linker = false
lto = "{'thin' if lto else 'thin-local'}"
[target.{HOST}]
linker = '{clang / "bin" / "lld-link.exe"}'
ar = '{clang / "bin" / "llvm-lib.exe"}'
"""


def build_environment(root, clang):
    # opt-dist prints its complete environment: pass build inputs, never Actions credentials.
    keys = (
        "PATH", "SystemRoot", "SystemDrive", "WINDIR", "COMSPEC", "PATHEXT",
        "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE", "ProgramFiles", "ProgramFiles(x86)",
        "ProgramW6432", "INCLUDE", "LIB", "LIBPATH", "VCToolsInstallDir", "VCINSTALLDIR",
        "VSINSTALLDIR", "WindowsSdkDir", "WindowsSDKVersion", "UCRTVersion",
        "UniversalCRTSdkDir", "VSCMD_ARG_HOST_ARCH", "VSCMD_ARG_TGT_ARCH",
        "TEMP", "TMP", "USERPROFILE", "APPDATA", "LOCALAPPDATA",
    )
    env = {k: os.environ[k] for k in keys if k in os.environ}
    env.update({
        "PATH": str(clang / "bin") + os.pathsep + env["PATH"],
        "CARGO_HOME": str(root / "cargo-home"), "CARGO_INCREMENTAL": "0",
        "PYTHONDONTWRITEBYTECODE": "1", "RUST_BACKTRACE": "1",
        "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.longpaths",
        "GIT_CONFIG_VALUE_0": "true", "MSBUILDDISABLENODEREUSE": "1",
    })
    return env


def execute(command, source, env, log, timings):
    started = time.monotonic()
    print(f"START {log.name}: {subprocess.list2cmdline(command)}", flush=True)
    with log.open("wb") as output:
        result = subprocess.run(command, cwd=source, env=env, stdout=output, stderr=subprocess.STDOUT)
    timings.append({"stage": log.stem, "wall_seconds": time.monotonic() - started,
                    "exit_code": result.returncode})
    save(log.parent / "stage-times.json", timings)
    if result.returncode:
        print(log.read_text(encoding="utf-8", errors="replace")[-16000:], flush=True)
        result.check_returncode()
    print(f"DONE {log.name}: {timings[-1]['wall_seconds']:.1f}s", flush=True)


def profile_coverage(profdata, profile, env):
    coverage = {}
    for component in ("X86TargetLowering", "InstCombine"):
        text = subprocess.check_output(
            [str(profdata), "show", f"--function={component}", "--counts", str(profile)],
            env=env, text=True,
        )
        rows = [json.loads(line.split(":", 1)[1]) for line in text.splitlines()
                if line.startswith("    Block counts:")]
        active = sum(any(row) for row in rows)
        if active == 0:
            raise RuntimeError(f"No executed {component} functions in LLVM PGO profile")
        coverage[component] = {"functions": len(rows), "nonzero_functions": active,
                               "max_block_count": max(max(row, default=0) for row in rows)}
    return coverage


def package(source, output, official, variant, metadata, env):
    stage = source / "build" / HOST / "stage2"
    with tempfile.TemporaryDirectory(prefix="package-", dir=output) as tmp:
        sysroot = Path(tmp) / "sysroot"
        shutil.copytree(stage, sysroot, ignore=lambda p, names: excluded_sysroot_entries(stage, p, names))
        for target in (HOST, "wasm32-unknown-unknown"):
            relative = Path("lib") / "rustlib" / target / "lib"
            original = official.parent.parent / relative
            if not list(original.glob("libstd-*.rlib")):
                raise RuntimeError(f"Missing official target libraries: {target}")
            destination = sysroot / relative
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(original, destination)
        for name in ("COPYRIGHT", "LICENSE-MIT", "LICENSE-APACHE"):
            shutil.copy2(source / name, sysroot / name)
        notices = official.parent.parent / "share" / "doc" / "rust"
        if not (notices / "COPYRIGHT.html").is_file():
            raise RuntimeError("Missing Rust third-party license notices")
        shutil.copytree(notices, sysroot / "share" / "doc" / "rust", dirs_exist_ok=True)
        compiler = sysroot / "bin" / "rustc.exe"
        version = subprocess.check_output([str(compiler), "-vV"], env=env, text=True)
        for expected in (f"host: {HOST}", f"commit-hash: {RUST_SHA}", "LLVM version: 21.1.8",
                         "release: 1.94.1"):
            if expected not in version.splitlines():
                raise RuntimeError(f"Unexpected compiler identity: {expected}")
        probe = Path(tmp) / "smoke.rs"
        probe.write_text("pub fn sum(xs: &[u64]) -> u64 { xs.iter().copied().sum() }\n")
        for target in (HOST, "wasm32-unknown-unknown"):
            artifact = Path(tmp) / f"{target}.rlib"
            subprocess.run([str(compiler), "--crate-type=rlib", "-O", "--target", target,
                            str(probe), "-o", str(artifact)],
                           env={**env, "LLVM_PROFILE_FILE": str(Path(tmp) / "unexpected-%m-%p.profraw")},
                           check=True)
            if artifact.stat().st_size == 0:
                raise RuntimeError("Empty compiler smoke-test artifact")
        if list(Path(tmp).glob("*.profraw")):
            raise RuntimeError("Packaged compiler still emits PGO instrumentation")
        metadata["rustc_version"] = version
        metadata["files"] = {str(p.relative_to(sysroot)): digest(p)
                             for p in sorted(sysroot.rglob("*")) if p.is_file()}
        archive = output / f"{variant}.zip"
        with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED, compresslevel=1) as z:
            for p in sorted(sysroot.rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(sysroot))
        metadata["archive_sha256"] = digest(archive)
        metadata["archive_bytes"] = archive.stat().st_size
    save(output / f"{variant}.json", metadata)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--clang", type=Path, required=True)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    args = parser.parse_args()
    if os.name != "nt" or platform.machine().lower() not in ("amd64", "x86_64"):
        parser.error("Build on native Windows x64, not the local Arm64 machine")
    source, output, clang = args.source.resolve(), args.output.resolve(), args.clang.resolve()
    output.mkdir(parents=True, exist_ok=True)
    logs = output / "logs"
    logs.mkdir(exist_ok=True)
    env = build_environment(output, clang)
    official = Path(subprocess.check_output(
        ["rustup", "which", "--toolchain", f"1.94.1-{HOST}", "rustc"], text=True,
    ).strip())
    for relative, expected in ((".", RUST_SHA), ("src/llvm-project", LLVM_SHA),
                               ("src/tools/rustc-perf", PERF_SHA)):
        actual = subprocess.check_output(["git", "-C", str(source / relative), "rev-parse", "HEAD"],
                                         env=env, text=True).strip()
        if actual != expected:
            raise RuntimeError(f"Unexpected revision: {relative}")
    for tool in ("cl.exe", "cmake", "ninja", "git", "perl", "bash"):
        if shutil.which(tool, path=env["PATH"]) is None:
            raise RuntimeError(f"Missing native build dependency: {tool}")
    patches = Path(__file__).resolve().parents[2] / "ci-benchmark"
    patch_names = ("bootstrap-clang-runtime.patch", "static-llvm-pgo.patch")
    for name in patch_names:
        subprocess.run(["git", "-C", str(source), "apply", "--check", "--ignore-space-change",
                        str(patches / name)], check=True)
        subprocess.run(["git", "-C", str(source), "apply", "--ignore-space-change",
                        str(patches / name)], check=True)
    config = configuration(clang, args.variant)
    (source / "bootstrap.toml").write_text(config, encoding="utf-8")
    (output / "bootstrap.toml").write_text(config, encoding="utf-8")
    timings = []
    x = [sys.executable, "x.py"]
    execute(x + ["build", "--set", "rust.debug=true", "opt-dist"], source, env,
            logs / "build-opt-dist.log", timings)
    stage0 = source / "build" / HOST / "stage0" / "bin"
    fixture = source / "src" / "tools" / "rustc-perf" / "collector" / "compile-benchmarks" / "token-stream-stress"
    before = tomllib.loads((fixture / "Cargo.lock").read_text())
    execute([str(stage0 / "cargo.exe"), "generate-lockfile", "--offline"], fixture, env,
            logs / "training-lockfile.log", timings)
    if tomllib.loads((fixture / "Cargo.lock").read_text())["package"] != before["package"]:
        raise RuntimeError("Training fixture dependency graph changed")
    helper = source / "build" / HOST / "stage1-tools-bin" / "opt-dist.exe"
    execute([str(helper), "local", "--target-triple", HOST, "--checkout-dir", str(source),
             "--llvm-dir", str(clang), "--python", sys.executable, "--llvm-shared", "false",
             "--", *x, "build", "--stage", "2", "library/std"],
            source, env, logs / "pgo-pipeline.log", timings)
    profiles = {}
    for name in ("rustc-pgo.profdata", "llvm-pgo.profdata"):
        path = source / "opt-artifacts" / name
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Missing profile: {name}")
        shutil.copy2(path, output / name)
        profiles[name] = {"sha256": digest(path), "bytes": path.stat().st_size}
    coverage = profile_coverage(clang / "bin" / "llvm-profdata.exe",
                                output / "llvm-pgo.profdata", env)
    cache_path = source / "build" / HOST / "llvm" / "build" / "CMakeCache.txt"
    cache = {}
    for line in cache_path.read_text().splitlines():
        if line and not line.startswith(("#", "//")) and ":" in line and "=" in line:
            key, value = line.split("=", 1)
            cache[key.split(":", 1)[0]] = value
    expected_lto = "Thin" if args.variant == "optimized" else "OFF"
    if cache.get("LLVM_ENABLE_LTO", "OFF").lower() != expected_lto.lower():
        raise RuntimeError("LLVM LTO configuration does not match variant")
    if cache.get("LLVM_BUILD_INSTRUMENTED", "OFF") not in ("", "OFF"):
        raise RuntimeError("Final LLVM is still instrumented")
    if digest(Path(cache["LLVM_PROFDATA_FILE"])) != profiles["llvm-pgo.profdata"]["sha256"]:
        raise RuntimeError("Final LLVM did not use the validated profile")
    log = (logs / "pgo-pipeline.log").read_text(encoding="utf-8", errors="replace")
    for flag in (["-Cprofile-use="] + (["-Clto=thin", "-Zdylib-lto"] if args.variant == "optimized" else [])):
        if flag not in log:
            raise RuntimeError(f"Missing compiler flag evidence: {flag}")
    shutil.copy2(cache_path, output / "CMakeCache.txt")
    metadata = {
        "variant": args.variant, "host": HOST, "rust_sha": RUST_SHA, "llvm_sha": LLVM_SHA,
        "rustc_perf_sha": PERF_SHA, "configuration": config, "profiles": profiles,
        "llvm_training_coverage": coverage, "llvm_profile_sha256": profiles["llvm-pgo.profdata"]["sha256"],
        "patches": {name: digest(patches / name) for name in patch_names},
        "clang": subprocess.check_output([str(clang / "bin" / "clang-cl.exe"), "--version"], env=env, text=True),
        "clang_installer_sha256": digest(clang.parent / "LLVM-20.1.3-win64.exe"),
        "msvc": env.get("VCToolsInstallDir"), "sdk": env.get("WindowsSDKVersion"),
        "github_run_id": os.environ["GITHUB_RUN_ID"], "github_sha": os.environ["GITHUB_SHA"],
        "runner": "windows-2025", "stage_times": timings,
        "intervention": {"rust_pgo": True, "llvm_pgo": True, "rust_codegen_units": 1,
                         "rust_lto": "thin" if args.variant == "optimized" else "thin-local",
                         "llvm_thin_lto": args.variant == "optimized", "rust_linker": "lld-20.1.3"},
        "scope": "Compiler-only package, official native/WASM target libraries; not full rustup distribution",
    }
    package(source, output, official, args.variant, metadata, env)


if __name__ == "__main__":
    main()
