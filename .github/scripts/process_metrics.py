"""Exact completed-process-tree CPU accounting and inherited CPU affinity."""

import os
from pathlib import Path
import shutil
import subprocess
import time


def measure(command, cwd, env, cores, prefix):
    prefix = Path(prefix)
    with prefix.with_suffix(".stdout").open("wb") as stdout, \
            prefix.with_suffix(".stderr").open("wb") as stderr:
        if os.name == "nt":
            result = windows_measure(command, cwd, env, cores, stdout, stderr)
        else:
            allowed = sorted(os.sched_getaffinity(0))
            if cores > len(allowed):
                raise RuntimeError("requested CPU affinity exceeds available CPUs")
            start = time.perf_counter()
            process = subprocess.Popen(
                command, cwd=cwd, env=env, stdout=stdout, stderr=stderr,
                preexec_fn=lambda: os.sched_setaffinity(0, allowed[:cores]),
                close_fds=False,
            )
            _, status, usage = os.wait4(process.pid, 0)
            elapsed = time.perf_counter() - start
            process.returncode = os.waitstatus_to_exitcode(status)
            result = {
                "wall_seconds": elapsed, "user_seconds": usage.ru_utime,
                "kernel_seconds": usage.ru_stime, "exit_code": process.returncode,
                "affinity": allowed[:cores], "accounting": "wait4 process plus waited descendants",
            }
    result["cpu_seconds"] = result["user_seconds"] + result["kernel_seconds"]
    result["effective_cores"] = result["cpu_seconds"] / result["wall_seconds"]
    result["command"] = command
    return result


def windows_measure(command, cwd, env, cores, stdout, stderr):
    import ctypes as c
    from ctypes import wintypes as w
    import msvcrt

    size = c.c_size_t
    handle = w.HANDLE

    class BasicLimits(c.Structure):
        _fields_ = [
            ("process_time", c.c_int64), ("job_time", c.c_int64),
            ("flags", w.DWORD), ("min_working", size), ("max_working", size),
            ("active_limit", w.DWORD), ("affinity", size),
            ("priority", w.DWORD), ("scheduling", w.DWORD),
        ]

    class IoCounters(c.Structure):
        _fields_ = [(name, c.c_uint64) for name in
                    ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]

    class Limits(c.Structure):
        _fields_ = [("basic", BasicLimits), ("io", IoCounters),
                    ("process_memory", size), ("job_memory", size),
                    ("peak_process_memory", size), ("peak_job_memory", size)]

    class Accounting(c.Structure):
        _fields_ = [
            ("user", c.c_int64), ("kernel", c.c_int64),
            ("period_user", c.c_int64), ("period_kernel", c.c_int64),
            ("faults", w.DWORD), ("processes", w.DWORD),
            ("active", w.DWORD), ("terminated", w.DWORD),
        ]

    class Startup(c.Structure):
        _fields_ = [
            ("cb", w.DWORD), ("reserved", w.LPWSTR), ("desktop", w.LPWSTR),
            ("title", w.LPWSTR), ("x", w.DWORD), ("y", w.DWORD),
            ("x_size", w.DWORD), ("y_size", w.DWORD), ("x_chars", w.DWORD),
            ("y_chars", w.DWORD), ("fill", w.DWORD), ("flags", w.DWORD),
            ("show", w.WORD), ("reserved_size", w.WORD),
            ("reserved_data", c.c_void_p), ("stdin", handle),
            ("stdout", handle), ("stderr", handle),
        ]

    class ProcessInfo(c.Structure):
        _fields_ = [("process", handle), ("thread", handle),
                    ("pid", w.DWORD), ("tid", w.DWORD)]

    kernel = c.WinDLL("kernel32", use_last_error=True)
    signatures = {
        "CreateJobObjectW": ([c.c_void_p, w.LPCWSTR], handle),
        "SetInformationJobObject": ([handle, c.c_int, c.c_void_p, w.DWORD], w.BOOL),
        "QueryInformationJobObject": ([handle, c.c_int, c.c_void_p, w.DWORD, c.c_void_p], w.BOOL),
        "AssignProcessToJobObject": ([handle, handle], w.BOOL),
        "GetCurrentProcess": ([], handle),
        "GetProcessAffinityMask": ([handle, c.POINTER(size), c.POINTER(size)], w.BOOL),
        "SetHandleInformation": ([handle, w.DWORD, w.DWORD], w.BOOL),
        "CreateProcessW": ([w.LPCWSTR, w.LPWSTR, c.c_void_p, c.c_void_p, w.BOOL,
                            w.DWORD, c.c_void_p, w.LPCWSTR,
                            c.POINTER(Startup), c.POINTER(ProcessInfo)], w.BOOL),
        "ResumeThread": ([handle], w.DWORD),
        "WaitForSingleObject": ([handle, w.DWORD], w.DWORD),
        "GetExitCodeProcess": ([handle, c.POINTER(w.DWORD)], w.BOOL),
        "OpenProcess": ([w.DWORD, w.BOOL, w.DWORD], handle),
        "QueryFullProcessImageNameW": ([handle, w.DWORD, w.LPWSTR, c.POINTER(w.DWORD)], w.BOOL),
        "TerminateProcess": ([handle, w.UINT], w.BOOL),
        "CloseHandle": ([handle], w.BOOL),
    }
    for name, (args, result_type) in signatures.items():
        function = getattr(kernel, name)
        function.argtypes, function.restype = args, result_type

    def check(result):
        if not result:
            raise c.WinError(c.get_last_error())

    own_mask, system_mask = size(), size()
    check(kernel.GetProcessAffinityMask(
        kernel.GetCurrentProcess(), c.byref(own_mask), c.byref(system_mask),
    ))
    allowed = [i for i in range(c.sizeof(size) * 8) if own_mask.value & (1 << i)]
    if cores > len(allowed):
        raise RuntimeError("requested CPU affinity exceeds available CPUs")
    job = kernel.CreateJobObjectW(None, None)
    check(job)
    info = ProcessInfo()
    completed = False
    try:
        limits = Limits()
        limits.basic.flags = 0x2000 | 0x10  # Kill on close and job-wide affinity.
        limits.basic.affinity = sum(1 << i for i in allowed[:cores])
        check(kernel.SetInformationJobObject(job, 9, c.byref(limits), c.sizeof(limits)))
        startup = Startup()
        startup.cb, startup.flags = c.sizeof(startup), 0x100
        with open(os.devnull, "rb") as stdin:
            for field, stream in (("stdin", stdin), ("stdout", stdout), ("stderr", stderr)):
                value = msvcrt.get_osfhandle(stream.fileno())
                check(kernel.SetHandleInformation(value, 1, 1))
                setattr(startup, field, value)
            executable = shutil.which(str(command[0]), path=env.get("PATH"))
            if not executable:
                raise FileNotFoundError(command[0])
            cmdline = c.create_unicode_buffer(subprocess.list2cmdline(command))
            environment = c.create_unicode_buffer(
                "\0".join(f"{k}={v}" for k, v in sorted(env.items(), key=lambda p: p[0].upper()))
                + "\0\0"
            )
            start = time.perf_counter()
            check(kernel.CreateProcessW(
                executable, cmdline, None, None, True, 0x4 | 0x400,
                environment, str(cwd), c.byref(startup), c.byref(info),
            ))
            # Assignment before resuming prevents any child escaping CPU accounting.
            check(kernel.AssignProcessToJobObject(job, info.process))
            if kernel.ResumeThread(info.thread) == 0xFFFFFFFF:
                raise c.WinError(c.get_last_error())
            if kernel.WaitForSingleObject(info.process, 0xFFFFFFFF) != 0:
                raise c.WinError(c.get_last_error())
            elapsed = time.perf_counter() - start
        code = w.DWORD()
        check(kernel.GetExitCodeProcess(info.process, c.byref(code)))
        accounting = Accounting()
        deadline = time.perf_counter() + 2
        while True:
            check(kernel.QueryInformationJobObject(
                job, 1, c.byref(accounting), c.sizeof(accounting), None,
            ))
            if not accounting.active or time.perf_counter() >= deadline:
                break
            time.sleep(0.01)
        if accounting.active:
            class ProcessIds(c.Structure):
                _fields_ = [("assigned", w.DWORD), ("count", w.DWORD),
                            ("ids", size * max(64, accounting.active * 2))]
            ids = ProcessIds()
            check(kernel.QueryInformationJobObject(job, 3, c.byref(ids), c.sizeof(ids), None))
            active = []
            for pid in ids.ids[:ids.count]:
                process = kernel.OpenProcess(0x1000, False, pid)
                image = c.create_unicode_buffer(32768)
                length = w.DWORD(len(image))
                if process:
                    try:
                        found = kernel.QueryFullProcessImageNameW(process, 0, image, c.byref(length))
                        active.append({"pid": pid, "image": image.value if found else "unavailable"})
                    finally:
                        kernel.CloseHandle(process)
                else:
                    active.append({"pid": pid, "image": "exited or inaccessible"})
            raise RuntimeError(f"measured command left running descendants: {active}")
        completed = True
        return {
            "wall_seconds": time.perf_counter() - start, "root_process_wall_seconds": elapsed,
            "user_seconds": accounting.user / 10_000_000,
            "kernel_seconds": accounting.kernel / 10_000_000,
            "exit_code": code.value, "processes": accounting.processes,
            "affinity": allowed[:cores], "accounting": "Windows Job Object process tree",
        }
    finally:
        if info.process and not completed:
            kernel.TerminateProcess(info.process, 1)
        for value in (info.thread, info.process, job):
            if value:
                kernel.CloseHandle(value)
