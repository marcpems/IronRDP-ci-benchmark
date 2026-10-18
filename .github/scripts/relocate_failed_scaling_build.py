"""Preserve the inspected failed build on another volume before reclaiming its cache."""

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess

from build_arm_compilers import digest, save

CASES = {
    "arm64": ("MARCPE-D4-Arm64", Path(r"D:\m16997224t16r1"), 16, "38716997224", None),
    "x64": ("MARCPE-TEST01-X64", Path(r"E:\m16997224t4r1"), 4, "38716997224", "116693884027"),
    "arm64-highcore": ("GB300-Arm64", Path(r"D:\m03042998t32r1"), 32, "38903042998", "116979807783"),
}


def is_junction(path):
    return getattr(path.lstat(), "st_reparse_tag", None) == stat.IO_REPARSE_TAG_MOUNT_POINT


def physical_directory(path):
    if not path.is_dir() or path.resolve() != path.absolute() or (
            getattr(path.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
        raise RuntimeError(f"Expected physical directory: {path}")


def symlink_record(path, directory, allow_missing_targets=False):
    target = path.resolve()
    if (not target.is_relative_to(directory) or target == directory
            or not (target.is_file() or target.is_dir() or allow_missing_targets)):
        raise RuntimeError(f"Symlink leaves retained tree or has no target: {path}")
    return {"path": str(path.relative_to(directory)), "symlink": str(target.relative_to(directory)),
            "directory": (bool(getattr(path.lstat(), "st_file_attributes", 0)
                               & stat.FILE_ATTRIBUTE_DIRECTORY) if not target.exists()
                          else target.is_dir())}


def manifest(directory, source_root=None, allow_missing_targets=False):
    physical_directory(directory)
    rows = []
    def fail(error):
        raise error
    for parent, folders, names in os.walk(directory, onerror=fail, followlinks=False):
        for name in folders[:]:
            path = Path(parent) / name
            if path.is_symlink():
                rows.append(symlink_record(path, directory, allow_missing_targets))
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
                rows.append(symlink_record(path, directory, allow_missing_targets))
                continue
            if (not path.is_file()
                    or getattr(path.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
                raise RuntimeError(f"Unexpected redirected or non-file build entry: {path}")
            rows.append({"path": str(path.relative_to(directory)),
                         "bytes": path.stat().st_size, "sha256": digest(path)})
    return sorted(rows, key=lambda row: row["path"])


def retry_readonly(function, name, error_info):
    error = error_info[1]
    info = Path(name).lstat()
    if (os.name != "nt" or not isinstance(error, PermissionError)
            or getattr(error, "winerror", None) != 5 or function is not os.unlink
            or not stat.S_ISREG(info.st_mode)
            or not info.st_file_attributes & stat.FILE_ATTRIBUTE_READONLY
            or info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT):
        raise error
    os.chmod(name, info.st_mode | stat.S_IWRITE)
    function(name)


def finish_relocation(build, destination, record):
    physical_directory(build.parent)
    record["copy_verified"] = True
    save(destination.parent / "relocation.json", record)
    if build.exists() or build.is_symlink():
        physical_directory(build)
        shutil.rmtree(build, onerror=retry_readonly)
    record["complete"] = True
    record["source_volume_free_bytes"] = shutil.disk_usage(build.parent).free
    save(destination.parent / "relocation.json", record)
    print(json.dumps({key: value for key, value in record.items() if key != "files"}), flush=True)


def resume_relocation(build, destination):
    physical_directory(build.parent)
    physical_directory(destination.parent)
    record = json.loads((destination.parent / "relocation.json").read_text())
    if (record.get("source") != str(build) or record.get("destination") != str(destination)
            or not record.get("files")
            or record.get("bytes") != sum(row.get("bytes", 0) for row in record["files"])):
        raise RuntimeError("Relocation receipt identity mismatch; source preserved")
    if manifest(destination, source_root=build.parent) != record["files"]:
        raise RuntimeError("Verified retained copy no longer matches receipt; source preserved")
    if build.exists() or build.is_symlink():
        expected = {row["path"]: row for row in record["files"]}
        remaining = manifest(build, source_root=build.parent, allow_missing_targets=True)
        if record.get("complete") or any(expected.get(row["path"]) != row for row in remaining):
            raise RuntimeError("Remaining source changed after preservation; source preserved")
    finish_relocation(build, destination, record)


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
    finish_relocation(build, destination, record)


def verify_reconnection(report, runner, root, job, run_id):
    if (report.get("Runner") != runner or report.get("FailedRoot") != str(root)
            or report.get("FailedJob") != job or report.get("RecoveryRun") != run_id
            or report.get("Processes") != []):
        raise RuntimeError("Expected current-run successful reconnection evidence without surviving work")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--machine", choices=CASES, default="arm64")
    parser.add_argument("--reconnection-report", type=Path)
    args = parser.parse_args()
    runner, root, cores, failed_run, failed_job = CASES[args.machine]
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
            raise RuntimeError("Interrupted recovery requires a fresh reconnection report")
        report = json.loads(args.reconnection_report.read_text(encoding="utf-8-sig"))
        verify_reconnection(report, runner, root, failed_job, os.environ["GITHUB_RUN_ID"])
        stage = json.loads((root / "e/active-stage.json").read_text())
        if measurement.exists() or stage.get("stage") != "fresh-pgo-full-dist":
            raise RuntimeError("Expected the interrupted, unfinished production measurement")
    if (provenance.get("run_id") != failed_run
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
