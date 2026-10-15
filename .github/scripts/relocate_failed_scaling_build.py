"""Preserve the inspected failed build on another volume before reclaiming its cache."""

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


def manifest(directory):
    physical_directory(directory)
    rows = []
    def fail(error):
        raise error
    for parent, folders, names in os.walk(directory, onerror=fail, followlinks=False):
        for name in folders[:]:
            path = Path(parent) / name
            if is_junction(path):
                target = path.resolve()
                if not target.is_relative_to(directory) or target == directory:
                    raise RuntimeError(f"Build junction leaves retained tree: {path}")
                rows.append({"path": str(path.relative_to(directory)),
                             "junction": str(target.relative_to(directory))})
                folders.remove(name)
            else:
                physical_directory(path)
        for name in sorted(names):
            path = Path(parent) / name
            if (path.is_symlink() or not path.is_file()
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
    before = manifest(build)
    if not before:
        raise RuntimeError("Refusing an empty build relocation")
    size = sum(row.get("bytes", 0) for row in before)
    if shutil.disk_usage(destination.parent).free < size + 50 * 1024 ** 3:
        raise RuntimeError("Retained volume needs build size plus 50 GiB free")
    record = {"source": str(build), "destination": str(destination),
              "files": before, "bytes": size, "complete": False}
    accounting = destination.parent / "relocation.json"
    save(accounting, record)
    def ignore_junctions(parent, names):
        return [name for name in names
                if is_junction(Path(parent) / name)]
    shutil.copytree(build, destination, ignore=ignore_junctions)
    for row in before:
        if "junction" in row:
            subprocess.run([os.environ["COMSPEC"], "/c", "mklink", "/J",
                            str(destination / row["path"]), str(destination / row["junction"])],
                           check=True, capture_output=True)
    if manifest(destination) != before or manifest(build) != before:
        raise RuntimeError("Build changed or retained copy failed checksum verification; source preserved")
    physical_directory(build.parent)
    physical_directory(build)
    shutil.rmtree(build)
    record["complete"] = True
    record["source_volume_free_bytes"] = shutil.disk_usage(build.parent).free
    save(accounting, record)
    print(json.dumps({key: value for key, value in record.items() if key != "files"}), flush=True)


def main():
    if (os.name != "nt" or os.environ.get("RUNNER_NAME") != "MARCPE-D4-Arm64"
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted"):
        raise RuntimeError("Expected the exact ordinary Arm64 runner")
    root = Path(r"D:\m16997224t16r1")
    for path in (root, root / "r", root / "e", root / "r/build"):
        physical_directory(path)
    provenance = json.loads((root / "e/provenance.json").read_text())
    failure = json.loads((root / "e/fresh-pgo-full-dist.json").read_text())
    if (provenance.get("run_id") != "38716997224"
            or provenance.get("runner_name") != "MARCPE-D4-Arm64"
            or provenance.get("variant") != "msvc-pgo-rust-thin"
            or provenance.get("build_affinity_count") != 16
            or provenance.get("paths", {}).get("source") != str(root / "r")
            or failure.get("exit_code") != 1 or (root / "e/result.json").exists()
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
