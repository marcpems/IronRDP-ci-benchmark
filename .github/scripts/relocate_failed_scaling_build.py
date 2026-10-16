"""Preserve the inspected failed build on another volume before reclaiming its cache."""

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess

from build_arm_compilers import digest, save


def is_junction(path):
    return getattr(path.lstat(), "st_reparse_tag", None) == stat.IO_REPARSE_TAG_MOUNT_POINT


def physical_directory(path):
    if not path.is_dir() or path.resolve() != path.absolute() or (
            getattr(path.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
        raise RuntimeError(f"Expected physical directory: {path}")


def symlink_record(path, directory):
    target = path.resolve()
    if (not target.is_relative_to(directory) or target == directory
            or not (target.is_file() or target.is_dir())):
        raise RuntimeError(f"Symlink leaves retained tree or has no target: {path}")
    return {"path": str(path.relative_to(directory)), "symlink": str(target.relative_to(directory)),
            "directory": target.is_dir()}


def manifest(directory, source_root=None):
    physical_directory(directory)
    rows = []
    def fail(error):
        raise error
    for parent, folders, names in os.walk(directory, onerror=fail, followlinks=False):
        for name in folders[:]:
            path = Path(parent) / name
            if path.is_symlink():
                rows.append(symlink_record(path, directory))
                folders.remove(name)
            elif is_junction(path):
                target = path.resolve()
                if target == source_root:
                    rows.append({"path": str(path.relative_to(directory)),
                                 "source_junction": str(target)})
                elif target.is_relative_to(directory) and target != directory:
                    rows.append({"path": str(path.relative_to(directory)),
                                 "junction": str(target.relative_to(directory))})
                else:
                    raise RuntimeError(f"Build junction leaves retained tree: {path} -> {target}")
                folders.remove(name)
            else:
                physical_directory(path)
        for name in sorted(names):
            path = Path(parent) / name
            if path.is_symlink():
                rows.append(symlink_record(path, directory))
                continue
            if (not path.is_file()
                    or getattr(path.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
                raise RuntimeError(f"Unexpected redirected or non-file build entry: {path}")
            rows.append({"path": str(path.relative_to(directory)),
                         "bytes": path.stat().st_size, "sha256": digest(path)})
    return sorted(rows, key=lambda row: row["path"])


def relocate(build, destination):
    physical_directory(build.parent)
    physical_directory(destination.parent)
    if destination.exists() or destination.is_symlink():
        raise RuntimeError("Expected a fresh retained-build destination")
    before = manifest(build, source_root=build.parent)
    if not before:
        raise RuntimeError("Refusing an empty build relocation")
    size = sum(row.get("bytes", 0) for row in before)
    if shutil.disk_usage(destination.parent).free < size + 50 * 1024 ** 3:
        raise RuntimeError("Retained volume needs build size plus 50 GiB free")
    record = {"source": str(build), "destination": str(destination),
              "files": before, "bytes": size, "complete": False}
    accounting = destination.parent / "relocation.json"
    save(accounting, record)
    def ignore_links(parent, names):
        return [name for name in names
                if (Path(parent) / name).is_symlink() or is_junction(Path(parent) / name)]
    shutil.copytree(build, destination, ignore=ignore_links)
    for row in before:
        if "symlink" in row:
            os.symlink(destination / row["symlink"], destination / row["path"],
                       target_is_directory=row["directory"])
        elif "junction" in row or "source_junction" in row:
            target = (destination / row["junction"] if "junction" in row
                      else Path(row["source_junction"]))
            subprocess.run([os.environ["COMSPEC"], "/c", "mklink", "/J",
                            str(destination / row["path"]), str(target)],
                           check=True, capture_output=True)
    if (manifest(destination, source_root=build.parent) != before
            or manifest(build, source_root=build.parent) != before):
        raise RuntimeError("Build changed or retained copy failed checksum verification; source preserved")
    physical_directory(build.parent)
    physical_directory(build)
    shutil.rmtree(build)
    record["complete"] = True
    record["source_volume_free_bytes"] = shutil.disk_usage(build.parent).free
    save(accounting, record)
    print(json.dumps({key: value for key, value in record.items() if key != "files"}), flush=True)


def verify_reconnection(report, runner, root, job, run_id):
    if (report.get("Runner") != runner or report.get("FailedRoot") != str(root)
            or report.get("FailedJob") != job or report.get("RecoveryRun") != run_id
            or report.get("Processes") != []):
        raise RuntimeError("Expected current-run successful reconnection evidence without surviving work")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--machine", choices=("arm64", "x64"), default="arm64")
    parser.add_argument("--reconnection-report", type=Path)
    args = parser.parse_args()
    runner, root, cores = {
        "arm64": ("MARCPE-D4-Arm64", Path(r"D:\m16997224t16r1"), 16),
        "x64": ("MARCPE-TEST01-X64", Path(r"E:\m16997224t4r1"), 4),
    }[args.machine]
    if (os.name != "nt" or os.environ.get("RUNNER_NAME") != runner
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted"):
        raise RuntimeError("Expected the exact recovery runner")
    for path in (root, root / "r", root / "e", root / "r/build"):
        physical_directory(path)
    provenance = json.loads((root / "e/provenance.json").read_text())
    measurement = root / "e/fresh-pgo-full-dist.json"
    if args.machine == "arm64":
        if json.loads(measurement.read_text()).get("exit_code") != 1:
            raise RuntimeError("Expected the failed Arm64 documentation build")
    else:
        if args.reconnection_report is None:
            raise RuntimeError("Interrupted x64 recovery requires a fresh reconnection report")
        report = json.loads(args.reconnection_report.read_text(encoding="utf-8-sig"))
        verify_reconnection(report, runner, root, "116693884027", os.environ["GITHUB_RUN_ID"])
        stage = json.loads((root / "e/active-stage.json").read_text())
        if measurement.exists() or stage.get("stage") != "fresh-pgo-full-dist":
            raise RuntimeError("Expected the interrupted, unfinished x64 production measurement")
    if (provenance.get("run_id") != "38716997224"
            or provenance.get("runner_name") != runner
            or provenance.get("variant") != "msvc-pgo-rust-thin"
            or provenance.get("build_affinity_count") != cores
            or provenance.get("paths", {}).get("source") != str(root / "r")
            or (root / "e/result.json").exists()
            or (root / "r/build/dist").exists()):
        raise RuntimeError("Expected the inspected failed, unqualified build without distribution")
    retained = Path(r"C:\matched-retained")
    if retained.exists():
        physical_directory(retained)
    else:
        retained.mkdir()
    destination = retained / (root.name + "-" + os.environ["GITHUB_RUN_ID"])
    destination.mkdir(exist_ok=False)
    relocate(root / "r/build", destination / "build")


if __name__ == "__main__":
    main()
