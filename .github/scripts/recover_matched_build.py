"""Retain verified qualified distributions before removing their disposable build directory."""

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import time

from build_arm_compilers import digest, save
from matched_release import RUST, SCALING_ALLOCATIONS, SCALING_STUDY, SCALING_VARIANT

RUNNERS = {
    "self-hosted-arm64-highcore": "GB300-Arm64",
    "self-hosted-x64": "MARCPE-TEST01-X64",
    "self-hosted-arm64": "MARCPE-D4-Arm64",
}
CODES = {"baseline": "b", "msvc-pgo": "m", "llvm-pgo-thin": "l", SCALING_VARIANT: "t"}


def verify_archives(directory, manifest):
    names = [row["name"] for row in manifest]
    if not names or len(set(names)) != len(names):
        raise RuntimeError("empty or duplicate distribution manifest")
    if set(p.name for p in directory.iterdir()) != set(names):
        raise RuntimeError("retained distribution does not match its complete manifest")
    for row in manifest:
        path = directory / row["name"]
        if (Path(row["name"]).name != row["name"] or not path.is_file()
                or path.is_symlink() or path.stat().st_size != row["bytes"]
                or digest(path) != row["sha256"]):
            raise RuntimeError(f"distribution checksum or size mismatch: {path}")


def recover(root, machine, run_id, variant, vm, scaling_cores=None):
    root = root.absolute()
    if (variant == SCALING_VARIANT) != (scaling_cores is not None):
        raise RuntimeError("scaling recovery requires explicit CPU allocation and recipe")
    expected_name = f"m{run_id[-8:]}{CODES[variant]}{vm}"
    if scaling_cores is not None:
        allowed = SCALING_ALLOCATIONS[machine]
        if scaling_cores not in allowed:
            raise RuntimeError("unexpected scaling CPU allocation")
        expected_name = f"m{run_id[-8:]}t{scaling_cores}r{vm}"
    if root.name != expected_name:
        raise RuntimeError("unexpected experiment directory name")
    build, evidence = root / "r" / "build", root / "e"
    retained = root / "retained-dist"
    for path in (root, root / "r", evidence, build, retained):
        if path.exists() and (path.resolve() != path or
                              getattr(path.stat(), "st_file_attributes", 0)
                              & stat.FILE_ATTRIBUTE_REPARSE_POINT):
            raise RuntimeError(f"refusing redirected experiment directory: {path}")
    result = json.loads((evidence / "result.json").read_text())
    if scaling_cores is not None and (
            result.get("scaling_study") != SCALING_STUDY
            or result.get("build_jobs") != scaling_cores
            or result.get("build_affinity_count") != scaling_cores):
        raise RuntimeError("scaling result resource provenance mismatch")
    if (result.get("complete") is not True or result.get("full_distribution") is not True
            or result.get("rust_sha") != RUST or result.get("runner_class") != machine
            or result.get("runner_name") != RUNNERS[machine]
            or result.get("run_id") != run_id or result.get("variant") != variant
            or result.get("vm") != vm or result.get("attempt") != "1"
            or Path(result["paths"]["source"]).resolve() != root / "r"):
        raise RuntimeError("only the exact qualified experiment can be reclaimed")
    manifest = json.loads((evidence / "dist-manifest.json").read_text())
    dist = build / "dist"
    if dist.exists() and retained.exists():
        raise RuntimeError("both original and retained distributions exist")
    verify_archives(dist if dist.exists() else retained, manifest)
    record = {
        "started_unix": time.time(), "build_directory": str(build),
        "retained_distribution": str(retained), "result_sha256": digest(evidence / "result.json"),
        "free_bytes_before": shutil.disk_usage(root).free, "complete": False,
    }
    save(evidence / "space-recovery.json", record)
    if (build / "metrics.json").is_file():
        shutil.copy2(build / "metrics.json", evidence / "build-metrics-before-cleanup.json")
    if dist.exists():
        dist.rename(retained)
    verify_archives(retained, manifest)
    if build.exists():
        # Only this checked build subdirectory is disposable; profiles and sources remain.
        shutil.rmtree(build)
    verify_archives(retained, manifest)
    record.update(complete=True, finished_unix=time.time(),
                  free_bytes_after=shutil.disk_usage(root).free)
    save(evidence / "space-recovery.json", record)
    print(json.dumps(record), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--machine", choices=RUNNERS, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--variant", choices=CODES, required=True)
    parser.add_argument("--vm", type=int, default=1)
    parser.add_argument("--scaling-cores", type=int)
    args = parser.parse_args()
    root = args.root.absolute()
    if (os.name != "nt" or root.parent != Path(root.anchor)
            or os.environ.get("RUNNER_NAME") != RUNNERS[args.machine]
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted"):
        raise RuntimeError("expected the exact self-hosted runner and direct-volume experiment root")
    recover(root, args.machine, args.run_id, args.variant, args.vm, args.scaling_cores)


if __name__ == "__main__":
    main()
