"""Explicit processor-group limits for the separate high-core Windows track."""

import ctypes as c
from ctypes import wintypes as w
import json
import sys


class GroupAffinity(c.Structure):
    _fields_ = [("mask", c.c_size_t), ("group", w.WORD), ("reserved", w.WORD * 3)]


def api():
    kernel = c.WinDLL("kernel32", use_last_error=True)
    for name, args, result in (
        ("GetActiveProcessorGroupCount", [], w.WORD),
        ("GetActiveProcessorCount", [w.WORD], w.DWORD),
        ("SetInformationJobObject", [w.HANDLE, c.c_int, c.c_void_p, w.DWORD], w.BOOL),
        ("QueryInformationJobObject", [w.HANDLE, c.c_int, c.c_void_p, w.DWORD, c.c_void_p], w.BOOL),
    ):
        function = getattr(kernel, name)
        function.argtypes, function.restype = args, result
    return kernel


def selected_groups(counts, cores):
    if cores < 1 or cores > sum(counts) or any(count < 1 or count > 64 for count in counts):
        raise ValueError("requested group affinity exceeds active processors")
    selected = []
    for group, count in enumerate(counts):
        take = min(cores, count)
        if take:
            selected.append({"group": group, "cpus": list(range(take))})
        cores -= take
    return selected


def configure_job_groups(job, cores):
    kernel = api()
    counts = [kernel.GetActiveProcessorCount(group)
              for group in range(kernel.GetActiveProcessorGroupCount())]
    selected = selected_groups(counts, cores)
    groups = (w.WORD * len(selected))(*(row["group"] for row in selected))
    affinities = (GroupAffinity * len(selected))()
    for affinity, row in zip(affinities, selected):
        affinity.group = row["group"]
        affinity.mask = sum(1 << cpu for cpu in row["cpus"])
    # Assign the groups first, then constrain each group's processor mask.
    if not kernel.SetInformationJobObject(job, 11, groups, c.sizeof(groups)):
        raise c.WinError(c.get_last_error())
    if not kernel.SetInformationJobObject(job, 14, affinities, c.sizeof(affinities)):
        raise c.WinError(c.get_last_error())
    verify_job_groups(job, selected)
    return selected


def verify_job_groups(job, expected):
    kernel = api()
    actual = (GroupAffinity * kernel.GetActiveProcessorGroupCount())()
    returned = w.DWORD()
    if not kernel.QueryInformationJobObject(job, 14, actual, c.sizeof(actual), c.byref(returned)):
        raise c.WinError(c.get_last_error())
    observed = {row.group: row.mask for row in actual[:returned.value // c.sizeof(GroupAffinity)]}
    wanted = {row["group"]: sum(1 << cpu for cpu in row["cpus"]) for row in expected}
    if observed != wanted:
        raise RuntimeError(f"job group affinity differs: expected={wanted}, actual={observed}")


def probe(cores):
    kernel = api()
    kernel.GetCurrentThread.restype = w.HANDLE
    kernel.SetThreadGroupAffinity.argtypes = [w.HANDLE, c.POINTER(GroupAffinity), c.POINTER(GroupAffinity)]
    kernel.SetThreadGroupAffinity.restype = w.BOOL

    class Processor(c.Structure):
        _fields_ = [("group", w.WORD), ("number", c.c_ubyte), ("reserved", c.c_ubyte)]

    kernel.GetCurrentProcessorNumberEx.argtypes = [c.POINTER(Processor)]
    kernel.GetCurrentProcessorNumberEx.restype = None
    counts = [kernel.GetActiveProcessorCount(group)
              for group in range(kernel.GetActiveProcessorGroupCount())]
    selected = selected_groups(counts, cores)
    wanted = {(row["group"], cpu) for row in selected for cpu in row["cpus"]}
    exercised = []
    rejected = []
    for group, count in enumerate(counts):
        for cpu in range(count):
            request = GroupAffinity()
            request.group, request.mask = group, 1 << cpu
            previous = GroupAffinity()
            success = kernel.SetThreadGroupAffinity(kernel.GetCurrentThread(), c.byref(request), c.byref(previous))
            if (group, cpu) not in wanted:
                if success:
                    raise RuntimeError(f"thread escaped the job affinity onto excluded CPU {group}:{cpu}")
                rejected.append([group, cpu])
                continue
            if not success:
                raise c.WinError(c.get_last_error())
            actual = Processor()
            kernel.GetCurrentProcessorNumberEx(c.byref(actual))
            if (actual.group, actual.number) != (group, cpu):
                raise RuntimeError(f"requested CPU {group}:{cpu} did not execute the probe")
            exercised.append([group, cpu])
            if not kernel.SetThreadGroupAffinity(kernel.GetCurrentThread(), c.byref(previous), None):
                raise c.WinError(c.get_last_error())
    print(json.dumps({"group_counts": counts, "exercised": exercised, "excluded_rejected": rejected}))


if __name__ == "__main__":
    probe(int(sys.argv[1]))
