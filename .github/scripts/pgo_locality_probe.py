import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time

ROOT = Path.cwd()
OUT = ROOT / "locality-evidence"
OUT.mkdir(exist_ok=True)
HOST = os.environ["EXPERIMENT_HOST"]
TOOLCHAIN = "1.94.1-" + HOST
record = {"host": HOST, "runner": os.environ["EXPERIMENT_RUNNER"],
          "platform": platform.platform(), "logical_cpus": os.cpu_count(),
          "image_version": os.environ.get("ImageVersion"), "samples": [],
          "scope": "stock pinned compiler; not a baseline-vs-PGO experiment",
          "cache": "fresh targets; dependency sources fetched before runs; OS cache uncontrolled warm",
          "disk": dict(zip(("total", "used", "free"), shutil.disk_usage(ROOT))),
          "lock_sha256": hashlib.sha256((ROOT / "Cargo.lock").read_bytes()).hexdigest()}


def save():
    (OUT / "result.json").write_text(json.dumps(record, indent=2) + "\n")


def run(args, name, env=None, timeout=300):
    with (OUT / f"{name}.stdout").open("wb") as stdout, \
            (OUT / f"{name}.stderr").open("wb") as stderr:
        start = time.perf_counter()
        p = subprocess.run(args, stdout=stdout, stderr=stderr, env=env, timeout=timeout)
    result = {"command": args, "exit_code": p.returncode,
              "wall_seconds": time.perf_counter() - start}
    return result


def main():
    save()
    if record["disk"]["free"] < 2 * 1024**3:
        raise RuntimeError("Less than 2 GiB free")
    if os.name == "nt":
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        kernel.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        if not kernel.SetProcessAffinityMask(kernel.GetCurrentProcess(), 15):
            raise ctypes.WinError(ctypes.get_last_error())
        record["affinity"] = [0, 1, 2, 3]
        run(["pwsh", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json"],
            "hardware")
    else:
        allowed = sorted(os.sched_getaffinity(0))[:4]
        os.sched_setaffinity(0, allowed)
        record["affinity"] = allowed
        run(["lscpu", "--json"], "hardware")
        for path in ("/proc/sys/kernel/perf_event_paranoid", "/proc/sys/kernel/kptr_restrict"):
            record[path] = Path(path).read_text().strip()
    check = run(["rustup", "run", TOOLCHAIN, "rustc", "-vV"], "toolchain-before")
    if check["exit_code"]:
        setup = run(["rustup", "toolchain", "install", TOOLCHAIN, "--profile", "minimal"],
                    "toolchain-install")
        if setup["exit_code"]:
            record["blocked"] = "Pinned compiler installation unavailable"
            save()
            return
    run(["rustup", "run", TOOLCHAIN, "rustc", "-vV"], "compiler")
    run(["rustup", "run", TOOLCHAIN, "rustc", "--print", "cfg"], "compiler-cfg")
    run(["rustup", "run", TOOLCHAIN, "rustc", "--print", "cfg", "-C", "target-cpu=native"],
        "native-cfg")
    fetch = run(["rustup", "run", TOOLCHAIN, "cargo", "fetch", "--locked", "--target", HOST],
                "fetch")
    if fetch["exit_code"]:
        record["blocked"] = "Locked dependency acquisition failed"
        save()
        return
    xperf = shutil.which("xperf")
    if not xperf and os.name == "nt":
        candidate = Path(r"C:\Program Files (x86)\Windows Kits\10\Windows Performance Toolkit\xperf.exe")
        if candidate.exists():
            xperf = str(candidate)
    perf = shutil.which("perf")
    record["xperf"] = xperf
    record["perf"] = perf
    can_trace = False
    if xperf:
        run(["logman", "query", "-ets"], "sessions-before")
        sessions = (OUT / "sessions-before.stdout").read_text(errors="replace")
        can_trace = "NT Kernel Logger" not in sessions
        run([xperf, "-pmcsources"], "pmu-sources")
    elif perf:
        probe = run([perf, "stat", "-e", "task-clock,minor-faults,major-faults", "--", "true"],
                    "perf-permission")
        can_trace = probe["exit_code"] == 0
    record["trace_preflight"] = can_trace
    save()
    for index in range(5 if can_trace else 4):
        traced = index == 4
        target = ROOT / f"locality-target-{index}"
        env = {**os.environ, "CARGO_TARGET_DIR": str(target), "CARGO_INCREMENTAL": "0",
               "CARGO_PROFILE_DEV_DEBUG": "0", "CARGO_BUILD_JOBS": "4", "CARGO_NET_OFFLINE": "true"}
        args = ["rustup", "run", TOOLCHAIN, "cargo", "build", "-p", "ironrdp-pdu", "--lib",
                "--frozen", "--timings", "--message-format=json"]
        started = False
        if traced and xperf:
            start = run([xperf, "-on", "PROC_THREAD+LOADER+PROFILE+ALL_FAULTS+HARD_FAULTS+DISK_IO",
                         "-BufferSize", "1024", "-MinBuffers", "32", "-MaxBuffers", "64",
                         "-MaxFile", "128", "-FileMode", "Circular", "-f", str(OUT / "raw.etl")],
                        "trace-start")
            started = start["exit_code"] == 0
            if not started:
                record["trace_blocked"] = start
                save()
                break
        elif traced:
            args = [perf, "stat", "-x", ",", "-o", str(OUT / "perf-stat.csv"),
                    "-e", "task-clock,minor-faults,major-faults,page-faults", "--",
                    perf, "record", "-e", "cpu-clock", "-g", "--call-graph", "dwarf,8192",
                    "-o", str(OUT / "perf.data"), "--", *args]
        try:
            row = run(args, f"sample-{index}", env, timeout=180)
            row.update({"warmup": index == 0, "traced": traced, "index": index})
            record["samples"].append(row)
            save()
        finally:
            if started:
                run([xperf, "-stop", "NT Kernel Logger"], "trace-stop")
                run([xperf, "-merge", str(OUT / "raw.etl"), str(OUT / "capture.etl")], "trace-merge")
                run([xperf, "-i", str(OUT / "capture.etl"), "-a", "tracestats"],
                    "trace-loss", timeout=60)
        shutil.rmtree(target)
        if row["exit_code"]:
            record["blocked"] = "Compile or trace wrapper failed; exclude failed sample"
            break
    if perf and (OUT / "perf.data").exists():
        run([perf, "report", "--stdio", "--header", "-i", str(OUT / "perf.data")], "perf-report")
    save()
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
