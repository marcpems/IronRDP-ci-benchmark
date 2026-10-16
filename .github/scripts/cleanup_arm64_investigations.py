"""Remove only disposable caches from the two qualified Arm64 scaling controls."""

import json
import os
from pathlib import Path
import shutil
import time

from build_arm_compilers import save
from prepare_arm64_scaling_space import CACHE_PATHS, cache_disposal_complete, verify_cell
from relocate_failed_scaling_build import manifest, physical_directory, retry_readonly


def cleanup_cell(root, run_id, cores, retained):
    identity = verify_cell(root, run_id, cores)
    physical_directory(retained)
    results = []
    plans = []
    for label, relative in CACHE_PATHS.items():
        cache = root / relative
        if cache_disposal_complete(root, label):
            results.append({"source": str(cache), "status": "already-disposed"})
            continue
        for ancestor in cache.parents:
            if ancestor == root.parent:
                break
            physical_directory(ancestor)
        targets = []
        if os.path.lexists(cache):
            targets.append((cache, manifest(cache, source_root=cache.parent)))
        for directory in retained.glob(f"{root.name}-{label}-*"):
            physical_directory(directory)
            if not directory.name.removeprefix(f"{root.name}-{label}-").isdigit():
                raise RuntimeError("Unexpected retained cache directory identity")
            receipt = directory / "relocation.json"
            if not receipt.exists():
                continue
            record = json.loads(receipt.read_text())
            destination = directory / "cache"
            if (record.get("complete") is not True or record.get("source") != str(cache)
                    or record.get("destination") != str(destination) or os.path.lexists(cache)):
                raise RuntimeError("Only completely relocated, unused qualified caches may be removed")
            files = manifest(destination, source_root=cache.parent)
            if files != record.get("files"):
                raise RuntimeError("Retained cache no longer matches its relocation receipt")
            targets.append((destination, files))
        if not targets:
            results.append({"source": str(cache), "status": "absent"})
            continue
        plans.append((label, cache, targets))

    for label, cache, targets in plans:
        receipt = root / "e" / f"obsolete-{label}-cache.json"
        record = {"source": str(cache), "result_sha256": identity, "complete": False,
                  "started_unix": time.time(), "targets": []}
        save(receipt, record)
        for target, files in targets:
            physical_directory(target.parent)
            physical_directory(target)
            if manifest(target, source_root=cache.parent) != files:
                raise RuntimeError("Disposable cache changed during inventory; no further removal")
            entry = {"path": str(target), "bytes": sum(row.get("bytes", 0) for row in files),
                     "free_bytes_before": shutil.disk_usage(target).free, "removed": False}
            record["targets"].append(entry)
            save(receipt, record)
            shutil.rmtree(target, onerror=retry_readonly)
            if os.path.lexists(target):
                raise RuntimeError("Disposable cache remains after removal")
            entry.update(removed=True, free_bytes_after=shutil.disk_usage(target.parent).free)
            save(receipt, record)
        if verify_cell(root, run_id, cores) != identity:
            raise RuntimeError("Qualified release identity changed during cache cleanup")
        record.update(complete=True, finished_unix=time.time())
        save(receipt, record)
        results.append(record)
        print(json.dumps(record), flush=True)
    return results


def main():
    if (os.name != "nt" or os.environ.get("RUNNER_NAME") != "MARCPE-D4-Arm64"
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted"):
        raise RuntimeError("Expected the ordinary Arm64 self-hosted runner")
    output = Path(os.environ["RUNNER_TEMP"]) / f"obsolete-arm64-caches-{os.environ['GITHUB_RUN_ID']}.json"
    report = {"complete": False, "cells": [],
              "free_bytes_before": {drive: shutil.disk_usage(drive).free for drive in ("C:\\", "D:\\")},
              "preserved": "All sources, profiles, results, archives, failed-build diagnostics and active cells"}
    save(output, report)
    for run_id, cores in (("38728610658", 16), ("38756702383", 4)):
        root = Path(f"D:\\m{run_id[-8:]}t{cores}r1")
        report["cells"].append({"root": str(root), "caches": cleanup_cell(
            root, run_id, cores, Path(r"C:\matched-retained"))})
        save(output, report)
    report.update(complete=True, free_bytes_after={
        drive: shutil.disk_usage(drive).free for drive in ("C:\\", "D:\\")})
    save(output, report)
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
