"""Bounded stock-runner full Rust distribution experiment; no release publication."""

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import tomllib

RUST = "e408947bfd200af42db322daf0fadfe7e26d3bd1"
LLVM = "00d23d10dc48c6bb9d57ba96d4a748d85d77d0c7"
PERF = "c0301bc44d175b9b2c5442b25049475c39d7700c"
HOST = "aarch64-pc-windows-msvc"
HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent / "arm-evidence"


def save(name, value):
    (EVIDENCE / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def clean_environment(source):
    allowed = {
        "SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "COMSPEC", "PATHEXT", "PATH",
        "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE", "PROGRAMFILES",
        "PROGRAMFILES(X86)", "PROGRAMW6432", "INCLUDE", "LIB", "LIBPATH",
        "VCTOOLSINSTALLDIR", "VCINSTALLDIR", "VSINSTALLDIR", "WINDOWSSDKDIR",
        "WINDOWSSDKVERSION", "WINDOWSSDKBINPATH", "WINDOWSSDKVERBINPATH",
        "UNIVERSALCRTSDKDIR", "UCRTVERSION", "VSCMD_ARG_HOST_ARCH", "VSCMD_ARG_TGT_ARCH",
        "VCTOOLSVERSION", "VISUALSTUDIOVERSION", "WINDOWSLIBPATH",
    }
    env = {k: v for k, v in os.environ.items() if k.upper() in allowed}
    home = source / "experiment-home"
    work = source / "experiment-scratch"
    for directory in (home, work, home / "AppData" / "Local", home / "AppData" / "Roaming"):
        directory.mkdir(parents=True, exist_ok=True)
    env.update({
        "PATH": str(source / "citools" / "clang-rust" / "bin") + os.pathsep + env["PATH"],
        "HOME": str(home), "USERPROFILE": str(home),
        "APPDATA": str(home / "AppData" / "Roaming"),
        "LOCALAPPDATA": str(home / "AppData" / "Local"),
        "TEMP": str(work), "TMP": str(work),
        "CARGO_HOME": str(source / "experiment-cargo"),
        "CARGO_INCREMENTAL": "0", "CARGO_REGISTRIES_CRATES_IO_PROTOCOL": "sparse",
        "RUST_BACKTRACE": "1", "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_CONFIG_COUNT": "2", "GIT_CONFIG_KEY_0": "core.longpaths",
        "GIT_CONFIG_VALUE_0": "true", "GIT_CONFIG_KEY_1": "core.autocrlf",
        "GIT_CONFIG_VALUE_1": "false", "WIX": str(source / "wix"),
        "DIST_REQUIRE_ALL_TOOLS": "1", "PGO_HOST": HOST,
    })
    return env


class MemoryStatus(ctypes.Structure):
    _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
        (name, ctypes.c_ulonglong) for name in (
            "total_physical", "available_physical", "total_pagefile", "available_pagefile",
            "total_virtual", "available_virtual", "available_extended",
        )
    ]


def sample(source):
    memory = MemoryStatus()
    memory.length = ctypes.sizeof(memory)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
        raise ctypes.WinError()
    disk = shutil.disk_usage(source)
    return {
        "unix": time.time(), "physical_total": memory.total_physical,
        "physical_available": memory.available_physical,
        "commit_limit": memory.total_pagefile,
        "commit_available": memory.available_pagefile,
        "disk_total": disk.total, "disk_free": disk.free,
    }


def execute(command, source, env, name, deadline):
    start = time.time()
    event = {"stage": name, "started_unix": start, "command": list(map(str, command))}
    save("active-stage.json", event)
    print("STAGE_START " + json.dumps(event), flush=True)
    if start >= deadline:
        raise TimeoutError("350-minute total-job safety budget exhausted before " + name)
    stop = threading.Event()
    proc = subprocess.Popen(list(map(str, command)), cwd=source, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    timed_out = []

    def monitor():
        while not stop.is_set():
            row = {**sample(source), "stage": name, "pid": proc.pid}
            with (EVIDENCE / "resources.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row) + "\n")
            print("RESOURCE " + json.dumps(row), flush=True)
            if time.time() >= deadline and proc.poll() is None:
                timed_out.append(True)
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], check=False)
                return
            stop.wait(min(60, max(1, deadline - time.time())))

    worker = threading.Thread(target=monitor, daemon=True)
    worker.start()
    with (EVIDENCE / (name + ".log")).open("wb") as log:
        for line in proc.stdout:
            log.write(line)
            log.flush()
            print(line.decode("utf-8", errors="replace"), end="", flush=True)
    code = proc.wait()
    stop.set()
    worker.join()
    event.update(completed_unix=time.time(), elapsed_seconds=time.time() - start,
                 returncode=code, safety_deadline_hit=bool(timed_out))
    with (EVIDENCE / "stages.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event) + "\n")
    print("STAGE_END " + json.dumps(event), flush=True)
    if code or timed_out:
        raise RuntimeError(f"{name} failed: return code {code}, deadline={bool(timed_out)}")


def configure_args(source, treatment):
    args = [
        "--build=" + HOST, "--host=" + HOST,
        "--target=" + HOST + ",arm64ec-pc-windows-msvc",
        "--enable-full-tools", "--enable-profiler", "--enable-locked-deps",
        "--disable-manage-submodules", "--enable-cargo-native-static",
        "--disable-dist-src", "--enable-llvm-static-stdcpp", "--release-channel=stable",
        "--debuginfo-level-std=1", "--dist-compression-formats=xz",
        "--set", "build.print-step-timings=true", "--set", "build.metrics=true",
        "--set", "build.optimized-compiler-builtins=true",
        "--set", "rust.codegen-units-std=1", "--set", "rust.remap-debuginfo=true",
        "--set", "dist.compression-profile=balanced",
        "--set", "llvm.download-ci-llvm=false", "--set", "rust.download-rustc=false",
        "--set", "llvm.clang-cl=" + str(source / "citools" / "clang-rust" / "bin" / "clang-cl.exe"),
    ]
    if treatment:
        args += [
            "--set", "rust.lto=thin", "--set", "llvm.thin-lto=true",
            "--set", "target." + HOST + ".linker=" +
            str(source / "citools" / "clang-rust" / "bin" / "lld-link.exe"),
        ]
    return args


def validate_profiles(source, env):
    result = {}
    root = source / "opt-artifacts"
    profile = root / "llvm-pgo.profdata"
    tool = source / "citools" / "clang-rust" / "bin" / "llvm-profdata.exe"
    for part in ("AArch64TargetLowering", "InstCombine"):
        text = subprocess.check_output(
            [str(tool), "show", "--function=" + part, "--counts", str(profile)],
            env=env, text=True,
        )
        (EVIDENCE / (part + ".txt")).write_text(text, encoding="utf-8")
        rows = [json.loads(line.split(":", 1)[1]) for line in text.splitlines()
                if line.startswith("    Block counts:")]
        result[part] = {"functions": len(rows), "nonzero_functions": sum(any(row) for row in rows),
                        "max_count": max((max(row, default=0) for row in rows), default=0)}
        if not result[part]["nonzero_functions"]:
            raise RuntimeError("LLVM PGO did not exercise " + part)
    result["hashes"] = {p.name: sha(p) for p in root.glob("*.profdata")}
    if "rustc-pgo.profdata" not in result["hashes"]:
        raise RuntimeError("Rustc PGO profile is missing")
    save("profile-validation.json", result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--variant", choices=("baseline", "treatment"), required=True)
    parser.add_argument("--phase", choices=("prepare", "build"), required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    EVIDENCE.mkdir(exist_ok=True)
    env = clean_environment(source)
    deadline = int(os.environ["ARM_JOB_STARTED"]) + 350 * 60
    treatment = args.variant == "treatment"
    if args.phase == "prepare":
        pins = {}
        for relative, expected in ((".", RUST), ("src/llvm-project", LLVM),
                                   ("src/tools/rustc-perf", PERF)):
            actual = subprocess.check_output(
                ["git", "-C", str(source / relative), "rev-parse", "HEAD"], text=True).strip()
            if actual != expected:
                raise RuntimeError(f"Wrong {relative} pin: {actual}, expected {expected}")
            pins[relative] = actual
        if treatment:
            for patch in sorted((HERE / "patches").glob("*.patch")):
                subprocess.run(["git", "-C", str(source), "apply", "--ignore-space-change",
                                "--check", str(patch)], check=True)
                subprocess.run(["git", "-C", str(source), "apply", "--ignore-space-change",
                                str(patch)], check=True)
        configure = [sys.executable, str(source / "src" / "bootstrap" / "configure.py"),
                     *configure_args(source, treatment)]
        execute(configure, source, env, "configure", deadline)
        shutil.copy2(source / "bootstrap.toml", EVIDENCE / "bootstrap.toml")
        diff = subprocess.check_output(["git", "-C", str(source), "diff"], text=True)
        (EVIDENCE / "candidate.patch").write_text(diff, encoding="utf-8")
        save("provenance.json", {
            "variant": args.variant, "pins": pins, "configure": configure,
            "llvm_installer_sha256": sha(source / "citools" / "LLVM-20.1.3-woa64.exe"),
            "wix_sha256": sha(source / "wix" / "wix311-binaries.zip"),
            "job_start_unix": int(os.environ["ARM_JOB_STARTED"]),
            "safety_deadline_unix": deadline, "fresh_profiles": treatment,
            "full_tools": True, "arm64ec": True, "native_sdk": True,
            "sccache": False, "release_upload": False,
        })
        return
    save("allowlisted-environment.json", env)
    for tool in ("cmake", "ninja", "git", "perl", "cl", "link", "clang-cl", "lld-link"):
        if not shutil.which(tool, path=env["PATH"]):
            raise FileNotFoundError("Required native runner tool missing: " + tool)
    dist = [sys.executable, "x.py", "dist", "bootstrap", "--include-default-paths"]
    if treatment:
        execute([sys.executable, "x.py", "build", "--set", "rust.debug=true", "opt-dist"],
                source, env, "build-opt-dist", deadline)
        fixture = source / "src" / "tools" / "rustc-perf" / "collector" / "compile-benchmarks" / "token-stream-stress"
        lock = fixture / "Cargo.lock"
        before = tomllib.loads(lock.read_text())
        if before["package"] != [{"name": "token-stream-stress", "version": "0.0.0"}]:
            raise RuntimeError("Training package graph differs from expected fixture")
        cargo = source / "build" / HOST / "stage0" / "bin" / "cargo.exe"
        execute([cargo, "generate-lockfile", "--offline"], fixture, env, "lock-format", deadline)
        after = tomllib.loads(lock.read_text())
        if before["package"] != after["package"]:
            raise RuntimeError("Training package graph changed")
        save("lock-migration.json", {"before": before, "after": after, "sha256": sha(lock)})
        helper = source / "build" / HOST / "stage1-tools-bin" / "opt-dist.exe"
        execute([helper, "windows-ci", "--", *dist], source, env, "fresh-pgo-full-dist-tests", deadline)
        validate_profiles(source, env)
    else:
        execute(dist, source, env, "full-dist", deadline)
    artifacts = [{"name": p.name, "bytes": p.stat().st_size, "sha256": sha(p)}
                 for p in sorted((source / "build" / "dist").iterdir()) if p.is_file()]
    save("dist-manifest.json", artifacts)
    if not any("arm64ec-pc-windows-msvc" in p["name"] for p in artifacts):
        raise RuntimeError("Arm64EC distribution component missing")
    save("result.json", {"success": True, "completed_unix": time.time(),
                         "variant": args.variant, "treatment_dist_tests": treatment})


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        EVIDENCE.mkdir(exist_ok=True)
        save("failure.json", {"error": str(error), "unix": time.time()})
        raise
