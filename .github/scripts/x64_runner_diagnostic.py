"""Bounded CPU-accounting and filesystem diagnostics; not a Rust release benchmark."""

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

from build_arm_compilers import save
from process_metrics import measure


def topology():
    class Relation(ctypes.Structure):
        _fields_ = [("mask", ctypes.c_size_t), ("relationship", wintypes.DWORD),
                    ("data", ctypes.c_ulonglong * 2)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    function = kernel.GetLogicalProcessorInformation
    function.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD)]
    function.restype = wintypes.BOOL
    length = wintypes.DWORD()
    if function(None, ctypes.byref(length)) or ctypes.get_last_error() != 122:
        raise RuntimeError("Unexpected topology buffer query")
    buffer = ctypes.create_string_buffer(length.value)
    if not function(buffer, ctypes.byref(length)):
        raise ctypes.WinError(ctypes.get_last_error())
    if length.value % ctypes.sizeof(Relation):
        raise RuntimeError("Unexpected processor topology layout")
    rows = (Relation * (length.value // ctypes.sizeof(Relation))).from_buffer(buffer)
    return [[bit for bit in range(64) if row.mask & (1 << bit)]
            for row in rows if row.relationship == 0]


def worker(barrier, queue, seconds):
    barrier.wait(timeout=60)
    start, cpu = time.perf_counter(), time.process_time()
    work = 0
    while time.perf_counter() - start < seconds:
        hashlib.pbkdf2_hmac("sha256", b"matched-cpu-calibration", b"fixed-salt", 50000)
        work += 1
    queue.put({"work_units": work, "wall_seconds": time.perf_counter() - start,
               "cpu_seconds": time.process_time() - cpu})


def cpu_load(cores, seconds):
    barrier, queue = mp.Barrier(cores + 1), mp.Queue()
    children = [mp.Process(target=worker, args=(barrier, queue, seconds)) for _ in range(cores)]
    for process in children:
        process.start()
    barrier.wait(timeout=60)
    start = time.perf_counter()
    rows = [queue.get(timeout=seconds + 60) for _ in children]
    for process in children:
        process.join(timeout=20)
        if process.exitcode != 0:
            raise RuntimeError("CPU calibration child did not complete successfully")
    elapsed = time.perf_counter() - start
    print(json.dumps({"workers": rows, "work_units": sum(row["work_units"] for row in rows),
                      "compute_wall_seconds": elapsed, "cores": cores}), flush=True)


def filesystem_probe(volume, output):
    if not Path(volume).is_dir():
        raise RuntimeError(f"Expected local volume {volume}")
    if shutil.disk_usage(volume).free < 2 * 1024 ** 3:
        raise RuntimeError("Filesystem diagnostic requires 2 GiB free")
    records = []
    for file_count, size, durable in ((1024, 4096, False), (1024, 4096, True),
                                      (16, 4 * 1024 * 1024, False), (16, 4 * 1024 * 1024, True)):
        payload = os.urandom(size)
        with tempfile.TemporaryDirectory(prefix="matched-x64-diagnostic-", dir=volume) as name:
            root = Path(name)
            start = time.perf_counter()
            for index in range(file_count):
                with (root / str(index)).open("xb") as stream:
                    stream.write(payload)
                    stream.flush()
                    if durable:
                        os.fsync(stream.fileno())
            written = time.perf_counter()
            total = sum(path.stat().st_size for path in root.iterdir())
            stat_end = time.perf_counter()
            for path in root.iterdir():
                if path.read_bytes() != payload:
                    raise RuntimeError("Filesystem diagnostic payload mismatch")
            read_end = time.perf_counter()
            records.append({"volume": volume, "files": file_count, "bytes": total,
                            "fsync_per_file": durable, "create_write_close_seconds": written - start,
                            "stat_seconds": stat_end - written, "warm_read_verify_seconds": read_end - stat_end})
    save(output, records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--load", type=int, choices=(4, 16))
    parser.add_argument("--seconds", type=int, default=20)
    parser.add_argument("--compiler-probe", action="store_true")
    args = parser.parse_args()
    if not 0 < args.seconds <= 60:
        raise ValueError("Diagnostic CPU duration must be between 1 and 60 seconds")
    if args.load:
        cpu_load(args.load, args.seconds)
        return
    if (os.name != "nt" or os.environ.get("RUNNER_NAME") != "MARCPE-TEST01-X64"
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted" or args.output is None):
        raise RuntimeError("Expected the exact self-hosted x64 diagnostic runner")
    args.output.mkdir(exist_ok=False, parents=True)
    save(args.output / "topology.json", {"physical_core_logical_cpu_masks": topology(),
                                       "logical_cpu_count": os.cpu_count(),
                                       "run_id": os.environ["GITHUB_RUN_ID"]})
    with (args.output / "telemetry.stdout").open("wb") as stdout, (
            args.output / "telemetry.stderr").open("wb") as stderr:
        sampler = subprocess.Popen([
            "powershell.exe", "-NoProfile", "-File", str(Path(__file__).with_name("x64_runner_telemetry.ps1")),
            "-OutputDirectory", str(args.output)], stdout=stdout, stderr=stderr)
        try:
            deadline = time.monotonic() + 120
            while not (args.output / "telemetry-ready").exists():
                if sampler.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("Telemetry sampler did not become ready; inspect telemetry.stderr")
                time.sleep(1)
            time.sleep(15)
            phases = []
            for index, cores in enumerate((4, 16, 16, 4)):
                if sampler.poll() is not None:
                    raise RuntimeError("Telemetry sampler exited before CPU calibration")
                prefix = args.output / f"cpu-{index}-{cores}"
                phase = {"phase": prefix.name, "started_unix": time.time()}
                phases.append(phase)
                save(args.output / "phase-timeline.json", phases)
                result = measure([sys.executable, str(Path(__file__).resolve()), "--load", str(cores),
                                  "--seconds", str(args.seconds)], Path.cwd(), os.environ.copy(),
                                 cores, prefix, timeout=120)
                save(prefix.with_suffix(".json"), result)
                phase["finished_unix"] = time.time()
                save(args.output / "phase-timeline.json", phases)
                if result["exit_code"]:
                    raise RuntimeError("CPU calibration failed")
            for index, volume in enumerate(("C:\\", "E:\\", "E:\\", "C:\\")):
                if sampler.poll() is not None:
                    raise RuntimeError("Telemetry sampler exited before filesystem probe")
                name = f"filesystem-{index}-{volume[0]}"
                phase = {"phase": name, "started_unix": time.time()}
                phases.append(phase)
                save(args.output / "phase-timeline.json", phases)
                filesystem_probe(volume, args.output / f"{name}.json")
                phase["finished_unix"] = time.time()
                save(args.output / "phase-timeline.json", phases)
            if args.compiler_probe:
                if sampler.poll() is not None:
                    raise RuntimeError("Telemetry sampler exited before instrumented compiler probe")
                from x64_instrumented_compiler_probe import run_probe
                phase = {"phase": "instrumented-rustc", "started_unix": time.time()}
                phases.append(phase)
                save(args.output / "phase-timeline.json", phases)
                run_probe(args.output)
                phase["finished_unix"] = time.time()
                save(args.output / "phase-timeline.json", phases)
        finally:
            (args.output / "telemetry-stop").touch()
            try:
                sampler.wait(timeout=30)
            except subprocess.TimeoutExpired:
                sampler.kill()
                sampler.wait()
                raise
        if sampler.returncode:
            raise RuntimeError("Telemetry sampler failed; inspect telemetry.stderr")
    save(args.output / "complete.json", {"complete": True, "run_id": os.environ["GITHUB_RUN_ID"],
         "boundary": "Bounded CPU/filesystem and optional tiny instrumented-compiler diagnostics; not a full release",
         "system_settings_changed": False})


if __name__ == "__main__":
    main()
