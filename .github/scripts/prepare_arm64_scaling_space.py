"""Preserve completed release caches on C: if another Arm64 scaling cell needs space."""

import json
import os
from pathlib import Path
import shutil

from build_arm_compilers import digest, save
from matched_release import RUST, SCALING_STUDY, SCALING_VARIANT
from recover_matched_build import verify_archives
from relocate_failed_scaling_build import physical_directory, relocate


def verify_cell(root, run_id, cores):
    for path in (root, root / "r", root / "e", root / "retained-dist"):
        physical_directory(path)
    result = json.loads((root / "e/result.json").read_text())
    expected = {
        "run_id": run_id, "variant": SCALING_VARIANT, "scaling_study": SCALING_STUDY,
        "build_jobs": cores, "build_affinity_count": cores, "complete": True,
        "full_distribution": True, "rust_sha": RUST, "attempt": "1",
        "runner_name": "MARCPE-D4-Arm64", "runner_class": "self-hosted-arm64",
    }
    if (root.name != f"m{run_id[-8:]}t{cores}r1"
            or any(result.get(key) != value for key, value in expected.items())
            or result.get("paths", {}).get("source") != str(root / "r")
            or (root / "r/build").exists()):
        raise RuntimeError("Expected the exact completed and already reclaimed release")
    verify_archives(root / "retained-dist", json.loads((root / "e/dist-manifest.json").read_text()))
    profiles = json.loads((root / "e/profiles.json").read_text())
    if set(profiles) != {"rustc-pgo.profdata", "rustdoc-pgo.profdata",
                         "clippy-pgo.profdata", "llvm-pgo.profdata"}:
        raise RuntimeError("Missing qualified profile manifest entries")
    for name, checksum in profiles.items():
        if Path(name).name != name or digest(root / "r/opt-artifacts" / name) != checksum:
            raise RuntimeError("Qualified profile identity mismatch")
    return digest(root / "e/result.json")


def main():
    if (os.name != "nt" or os.environ.get("RUNNER_NAME") != "MARCPE-D4-Arm64"
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted"):
        raise RuntimeError("Expected the ordinary Arm64 self-hosted runner")
    output = Path(os.environ["RUNNER_TEMP"]) / f"arm64-eight-space-{os.environ['GITHUB_RUN_ID']}.json"
    report = {"free_bytes_before": shutil.disk_usage("D:\\").free, "relocations": [], "complete": False}
    save(output, report)
    for run_id, cores in (("38728610658", 16), ("38756702383", 4)):
        if shutil.disk_usage("D:\\").free >= 180 * 1024 ** 3:
            break
        root = Path(f"D:\\m{run_id[-8:]}t{cores}r1")
        identity = verify_cell(root, run_id, cores)
        retained = Path(r"C:\matched-retained")
        physical_directory(retained)
        for label, relative in (("cargo", "e/cargo-home"), ("training", "r/opt-artifacts/rustc-perf")):
            if shutil.disk_usage("D:\\").free >= 180 * 1024 ** 3:
                break
            cache = root / relative
            for ancestor in (cache, *cache.parents):
                if ancestor == root.parent:
                    break
                physical_directory(ancestor)
            destination = retained / f"{root.name}-{label}-{os.environ['GITHUB_RUN_ID']}"
            destination.mkdir(exist_ok=False)
            relocate(cache, destination / "cache")
            receipt = json.loads((destination / "relocation.json").read_text())
            after_identity = verify_cell(root, run_id, cores)
            if after_identity != identity or receipt["complete"] is not True:
                raise RuntimeError("Completed release identity changed during cache relocation")
            report["relocations"].append({
                "source": str(cache), "retained": str(destination / "cache"),
                "receipt": str(destination / "relocation.json"), "result_sha256": identity,
                "bytes": receipt["bytes"],
            })
            save(output, report)
    report["free_bytes_after"] = shutil.disk_usage("D:\\").free
    report["complete"] = report["free_bytes_after"] >= 180 * 1024 ** 3
    save(output, report)
    print(json.dumps(report), flush=True)
    if not report["complete"]:
        raise RuntimeError("Preserved caches but still below the unchanged 180 GiB build guard")


if __name__ == "__main__":
    main()
