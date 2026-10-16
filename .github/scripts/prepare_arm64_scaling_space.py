"""Preserve selected completed release caches on C: if another scaling cell needs space."""

import argparse
import json
import os
from pathlib import Path
import shutil

from build_arm_compilers import digest, save
from matched_release import RUST, SCALING_STUDY, SCALING_VARIANT
from recover_matched_build import RUNNERS, verify_archives
from relocate_failed_scaling_build import physical_directory, relocate, resume_relocation

CACHE_PATHS = {"cargo": Path("e") / "cargo-home",
               "training": Path("r") / "opt-artifacts" / "rustc-perf"}


def cache_disposal_complete(root, label):
    receipt = root / "e" / f"obsolete-{label}-cache.json"
    if not receipt.exists():
        return False
    record = json.loads(receipt.read_text())
    cache = root / CACHE_PATHS[label]
    if (record.get("complete") is not True or record.get("source") != str(cache)
            or record.get("result_sha256") != digest(root / "e/result.json")
            or os.path.lexists(cache)):
        raise RuntimeError("Cache disposal receipt is incomplete or no longer matches the release")
    return True


def verify_cell(root, run_id, cores, variant=SCALING_VARIANT, *, machine="self-hosted-arm64"):
    if machine not in ("self-hosted-arm64", "self-hosted-x64"):
        raise RuntimeError("Unsupported completed-cache machine")
    if variant not in (SCALING_VARIANT, "msvc-pgo", "llvm-pgo-thin"):
        raise RuntimeError("Unsupported completed-cache recipe")
    suffix = (f"t{cores}r1" if variant == SCALING_VARIANT
              else ("m1" if variant == "msvc-pgo" else "l1"))
    for path in (root, root / "r", root / "e", root / "retained-dist"):
        physical_directory(path)
    result = json.loads((root / "e/result.json").read_text())
    expected = {
        "run_id": run_id, "variant": variant,
        "build_jobs": cores, "build_affinity_count": cores, "complete": True,
        "full_distribution": True, "rust_sha": RUST, "attempt": "1",
        "runner_name": RUNNERS[machine], "runner_class": machine,
    }
    if variant == SCALING_VARIANT:
        expected["scaling_study"] = SCALING_STUDY
    else:
        expected["vm"] = 1
    if (root.name != f"m{run_id[-8:]}{suffix}"
            or any(result.get(key) != value for key, value in expected.items())
            or result.get("paths", {}).get("source") != str(root / "r")
            or (root / "r/build").exists()):
        raise RuntimeError("Expected the exact completed and already reclaimed release")
    verify_archives(root / "retained-dist", json.loads((root / "e/dist-manifest.json").read_text()))
    profiles = json.loads((root / "e/profiles.json").read_text())
    expected_profiles = {"rustc-pgo.profdata", "rustdoc-pgo.profdata",
                         "clippy-pgo.profdata", "llvm-pgo.profdata"}
    if set(profiles) != expected_profiles:
        raise RuntimeError("Missing qualified profile manifest entries")
    for name, checksum in profiles.items():
        if Path(name).name != name or digest(root / "r/opt-artifacts" / name) != checksum:
            raise RuntimeError("Qualified profile identity mismatch")
    return digest(root / "e/result.json")


def preserve_cache(cache, retained, stem, run_id):
    physical_directory(retained)
    previous = []
    for directory in retained.glob(f"{stem}-*"):
        if not directory.name.removeprefix(f"{stem}-").isdigit():
            raise RuntimeError("Unexpected retained cache directory identity")
        physical_directory(directory)
        if (directory / "relocation.json").exists():
            previous.append(directory)
    if len(previous) > 1:
        raise RuntimeError("Ambiguous previous cache relocation receipts")
    if previous:
        destination = previous[0]
        resume_relocation(cache, destination / "cache")
    else:
        destination = retained / f"{stem}-{run_id}"
        destination.mkdir(exist_ok=False)
        relocate(cache, destination / "cache")
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--machine", choices=("arm64", "x64"), default="arm64")
    args = parser.parse_args()
    machine = f"self-hosted-{args.machine}"
    if (os.name != "nt" or os.environ.get("RUNNER_NAME") != RUNNERS[machine]
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted"):
        raise RuntimeError("Expected the selected self-hosted scaling runner")
    volume = "E:\\" if args.machine == "x64" else "D:\\"
    prefix = "x64-repeat-space" if args.machine == "x64" else "arm64-eight-space"
    output = Path(os.environ["RUNNER_TEMP"]) / f"{prefix}-{os.environ['GITHUB_RUN_ID']}.json"
    report = {"free_bytes_before": shutil.disk_usage(volume).free, "relocations": [], "complete": False}
    save(output, report)
    cases = ([
        ("m69758791t4r1", "38869758791", 4, SCALING_VARIANT),
        ("m16997224t16r1", "38716997224", 16, SCALING_VARIANT),
        ("m06317769l1", "38406317769", 4, "llvm-pgo-thin"),
        ("m06317769m1", "38406317769", 4, "msvc-pgo"),
    ] if args.machine == "x64" else [
        ("m28610658t16r1", "38728610658", 16, SCALING_VARIANT),
        ("m56702383t4r1", "38756702383", 4, SCALING_VARIANT),
    ])
    for name, run_id, cores, variant in cases:
        if shutil.disk_usage(volume).free >= 180 * 1024 ** 3:
            break
        root = Path(volume) / name
        identity = verify_cell(root, run_id, cores, variant, machine=machine)
        retained = Path(r"C:\matched-retained")
        physical_directory(retained)
        for label, relative in CACHE_PATHS.items():
            if shutil.disk_usage(volume).free >= 180 * 1024 ** 3:
                break
            if cache_disposal_complete(root, label):
                report.setdefault("already_disposed", []).append(str(root / relative))
                save(output, report)
                continue
            cache = root / relative
            for ancestor in cache.parents:
                if ancestor == root.parent:
                    break
                physical_directory(ancestor)
            destination = preserve_cache(cache, retained, f"{root.name}-{label}",
                                         os.environ["GITHUB_RUN_ID"])
            receipt = json.loads((destination / "relocation.json").read_text())
            after_identity = verify_cell(root, run_id, cores, variant, machine=machine)
            if after_identity != identity or receipt["complete"] is not True:
                raise RuntimeError("Completed release identity changed during cache relocation")
            report["relocations"].append({
                "source": str(cache), "retained": str(destination / "cache"),
                "receipt": str(destination / "relocation.json"), "result_sha256": identity,
                "bytes": receipt["bytes"],
            })
            save(output, report)
    report["free_bytes_after"] = shutil.disk_usage(volume).free
    report["complete"] = report["free_bytes_after"] >= 180 * 1024 ** 3
    save(output, report)
    print(json.dumps(report), flush=True)
    if not report["complete"]:
        raise RuntimeError("Preserved caches but still below the unchanged 180 GiB build guard")


if __name__ == "__main__":
    main()
