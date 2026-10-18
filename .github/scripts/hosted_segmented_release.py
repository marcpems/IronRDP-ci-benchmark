"""Explicit two-host continuation of fresh PGO production, never a continuous timing."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time

from build_arm_compilers import digest, save
from hosted_x64_baseline import timer_sections
import matched_release as release
from msvc_experiment import environment, equivalent_tools, execute, tool_identity
from relocate_failed_scaling_build import manifest, physical_directory

HOST = "x86_64-pc-windows-msvc"
STUDY = "public-x64-segmented-msvc-rust-thin-v1"
PROFILE_NAMES = ("rustc", "rustdoc", "clippy", "cranelift", "llvm")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_flags(flags, source):
    expected = {}
    for component in (*PROFILE_NAMES, "cargo"):
        profile = "rustc" if component == "cargo" else component
        expected[f"pgo.{component}.use"] = (source / "opt-artifacts" / f"{profile}-pgo.profdata").resolve()
    actual = {}
    index = 0
    while index < len(flags):
        pair = flags[index:index + 2]
        if len(pair) != 2:
            raise RuntimeError("Incomplete final-build flags")
        option, value = pair
        if option == "--keep-stage" and value == "0" and "keep-stage" not in actual:
            actual["keep-stage"] = "0"
        elif option == "--set" and "=" in value:
            key, path = value.split("=", 1)
            if key not in expected or key in actual:
                raise RuntimeError("Unexpected or repeated final-build setting")
            actual[key] = Path(path.strip('"')).resolve()
        else:
            raise RuntimeError("Unexpected final-build flags")
        index += 2
    if actual != {**expected, "keep-stage": "0"}:
        raise RuntimeError("Final-build profile flags do not match the complete recipe")


def checkpoint_final(root, flags):
    if root != Path(r"D:\mhx") or Path.cwd() != root / "r":
        raise RuntimeError("Checkpoint callback must use the fixed public build root")
    validate_flags(flags, root / "r")
    receipt = root / "e/final-command.json"
    if receipt.exists():
        raise RuntimeError("Final-build checkpoint already exists")
    profiles = {name: digest(root / "r/opt-artifacts" / f"{name}-pgo.profdata")
                for name in PROFILE_NAMES}
    save(receipt, {"study": STUDY, "flags": flags, "profiles": profiles,
                   "python": sys.executable, "unix": time.time(), "exit_code": 75})
    print("Final distribution explicitly deferred to the continuation job; exit 75.", flush=True)
    return 75


def verify_training(output):
    receipt = read(output / "final-command.json")
    if receipt.get("study") != STUDY or receipt.get("exit_code") != 75:
        raise RuntimeError("Missing explicit final-build checkpoint")
    sections = timer_sections(output / "fresh-pgo-full-dist.stderr")["completed"]
    required = {"Stage 1 (Rustc + rustdoc + cargo + clippy PGO)", "Stage 2 (LLVM PGO)"}
    if not required.issubset({row["name"] for row in sections if row["status"] == "OK"}):
        raise RuntimeError("Both complete PGO stages are required before continuation")
    failed = [row["name"] for row in sections if row["status"] != "OK"]
    if failed != ["Stage 5 (final build)"]:
        raise RuntimeError("Expected only the explicitly deferred final-build section")
    return receipt


def train(root):
    source, output = root / "r", root / "e"
    env, clang, _, _, provenance = release.prepare(
        source, root / "l", output, HOST, release.SCALING_VARIANT)
    start = time.time()
    helper = release.prepare_opt_dist(source, output, HOST, env)
    command = [helper, "local", "--target-triple", HOST, "--checkout-dir", source,
               "--llvm-dir", clang.parent, "--python", sys.executable, "--llvm-shared", "false",
               "--", sys.executable, Path(__file__).resolve(), "--checkpoint-final", root]
    remaining = float(os.environ["RELEASE_JOB_STARTED"]) + 320 * 60 - time.time()
    if remaining <= 0:
        raise TimeoutError("No training budget remains before checkpoint transfer")
    result = execute(command, source, env, output, "fresh-pgo-full-dist",
                     timeout=remaining, expected_success=False, cores=4)
    if result["exit_code"] != 1:
        raise RuntimeError("Unexpected opt-dist checkpoint exit code")
    verify_training(output)
    save(output / "training-production.json", {
        "study": STUDY, "wall_seconds": time.time() - start,
        "complete_training": True, "complete_release": False, "provenance": provenance,
    })
    shutil.copy2(output / "hardware.json", output / "training-hardware.json")


def pack(root, transfer):
    physical_directory(root)
    transfer.mkdir(parents=True, exist_ok=False)
    rows = manifest(root, source_root=root / "r")
    directories = []
    for parent, folders, _ in os.walk(root, followlinks=False):
        folders[:] = [name for name in folders
                      if (Path(parent) / name).resolve() == Path(parent) / name]
        directories.extend(str((Path(parent) / name).relative_to(root)) for name in folders)
    paths = directories + [row["path"] for row in rows if "bytes" in row]
    if any("\n" in name or "\r" in name or name.startswith("-") for name in paths):
        raise RuntimeError("Unexpected archive member name")
    archive = transfer / "workspace.7z"
    # Enumerate regular files explicitly; links are recreated from the verified manifest.
    mtimes = {name: (root / name).stat().st_mtime_ns for name in paths}
    with (transfer / "compress.stdout").open("wb") as stdout, \
            (transfer / "compress.stderr").open("wb") as stderr:
        compressor = subprocess.Popen(
            ["7z", "a", "-t7z", "-mx=1", "-mmt=4", "-siworkspace.tar", str(archive)],
            stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
        try:
            with tarfile.open(fileobj=compressor.stdin, mode="w|", format=tarfile.PAX_FORMAT) as archive_tar:
                for name in paths:
                    archive_tar.add(root / name, arcname=Path(name).as_posix(), recursive=False)
        finally:
            compressor.stdin.close()
            code = compressor.wait()
    if code:
        raise RuntimeError(
            f"Workspace checkpoint archive failed: 7z={code}; "
            + (transfer / "compress.stderr").read_text(errors="replace")[-2000:])
    save(transfer / "manifest.json", {
        "study": STUDY, "root": str(root), "run_id": os.environ["GITHUB_RUN_ID"],
        "attempt": os.environ["GITHUB_RUN_ATTEMPT"], "harness_sha": os.environ["GITHUB_SHA"],
        "archive_sha256": digest(archive), "files": rows,
        "directories": directories,
        "mtime_ns": mtimes,
        "bytes": sum(row.get("bytes", 0) for row in rows),
    })


def validate_members(record, root):
    for relative in [*record["directories"], *(row["path"] for row in record["files"])]:
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or not (root / path).is_relative_to(root):
            raise RuntimeError("Checkpoint contains an unsafe member path")
    expected_times = set(record["directories"]) | {
        row["path"] for row in record["files"] if "bytes" in row}
    if set(record["mtime_ns"]) != expected_times:
        raise RuntimeError("Checkpoint timestamp members do not match regular files and directories")
    for row in record["files"]:
        for kind in ("symlink", "junction"):
            if kind in row:
                path = Path(row[kind])
                if path.is_absolute() or ".." in path.parts or not (root / path).is_relative_to(root):
                    raise RuntimeError("Checkpoint link leaves the restored workspace")
        if "source_junction" in row and Path(row["source_junction"]) != root / "r":
            raise RuntimeError("Checkpoint source junction has an unexpected target")


def unpack(root, transfer):
    record = read(transfer / "manifest.json")
    archive = transfer / "workspace.7z"
    if (record.get("study") != STUDY or record.get("root") != str(root)
            or record.get("run_id") != os.environ["GITHUB_RUN_ID"]
            or record.get("attempt") != os.environ["GITHUB_RUN_ATTEMPT"]
            or record.get("harness_sha") != os.environ["GITHUB_SHA"]
            or digest(archive) != record.get("archive_sha256")):
        raise RuntimeError("Continuation checkpoint identity or archive hash mismatch")
    validate_members(record, root)
    if root.exists() and list(root.iterdir()):
        raise RuntimeError("Continuation requires an empty destination")
    root.mkdir(exist_ok=True)
    physical_directory(root)
    if shutil.disk_usage(root).free < record["bytes"] + 20 * 1024 ** 3:
        raise RuntimeError("Insufficient space to restore the verified checkpoint")
    with (transfer / "extract.stderr").open("wb") as errors:
        extract = subprocess.Popen(["7z", "e", "-so", str(archive)], stdout=subprocess.PIPE, stderr=errors)
        try:
            with tarfile.open(fileobj=extract.stdout, mode="r|") as archive_tar:
                archive_tar.extractall(root, filter="data")
            # Drain archive padding before collecting the decompressor's exit status.
            while extract.stdout.read(1024 * 1024):
                pass
        finally:
            extract.stdout.close()
            code = extract.wait()
    if code:
        raise RuntimeError(
            f"Checkpoint extraction failed: 7z={code}; "
            + (transfer / "extract.stderr").read_text(errors="replace")[-2000:])
    for row in record["files"]:
        target = root / row["path"]
        if "symlink" in row:
            target.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(root / row["symlink"], target, target_is_directory=row["directory"])
        elif "junction" in row or "source_junction" in row:
            link_to = root / row["junction"] if "junction" in row else Path(row["source_junction"])
            target.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run([os.environ["COMSPEC"], "/c", "mklink", "/J", str(target), str(link_to)],
                           check=True, capture_output=True)
    if manifest(root, source_root=root / "r") != record["files"]:
        raise RuntimeError("Restored workspace differs from the training checkpoint")
    if any(not (root / name).is_dir() for name in record["directories"]):
        raise RuntimeError("Restored workspace is missing a checkpoint directory")
    for name, mtime in record["mtime_ns"].items():
        path = root / name
        os.utime(path, ns=(path.stat().st_atime_ns, mtime))
    save(root / "e/continuation-restore.json", {
        "study": STUDY, "verified": True, "archive_sha256": record["archive_sha256"],
        "files": len(record["files"]), "bytes": record["bytes"],
    })
    archive.unlink()


def finish(root):
    source, output = root / "r", root / "e"
    receipt = verify_training(output)
    validate_flags(receipt["flags"], source)
    if sys.executable != receipt["python"]:
        raise RuntimeError("Continuation Python installation differs from the training host")
    if read(output / "continuation-restore.json").get("verified") is not True:
        raise RuntimeError("Workspace restoration has not been verified")
    for name, expected in receipt["profiles"].items():
        if digest(source / "opt-artifacts" / f"{name}-pgo.profdata") != expected:
            raise RuntimeError("Training profile changed during transfer")
    provenance = read(output / "provenance.json")
    clang = source / "citools/clang-rust/bin"
    identity = tool_identity(clang)
    if (not equivalent_tools(identity, provenance["tools"])
            or {name: row["path"] for name, row in identity["files"].items()}
            != {name: row["path"] for name, row in provenance["tools"]["files"].items()}):
        raise RuntimeError("Continuation native tool identity differs from the training host")
    env = environment(output, clang)
    env.update({"WIX": str(source / "wix"), "PGO_HOST": HOST, "DIST_REQUIRE_ALL_TOOLS": "1",
                "DIST_TRY_BUILD": "0", "MATCHED_BUILD_CORES": "4", "CARGO_BUILD_JOBS": "4",
                "CMAKE_BUILD_PARALLEL_LEVEL": "4", "CMAKE_TOOLCHAIN_FILE": str(output / "native-tools.cmake")})
    command = [sys.executable, "x.py", "dist", "bootstrap", "--include-default-paths", *receipt["flags"]]
    final = release.run(command, source, env, output, "continuation-final-dist")
    for suffix in ("stdout", "stderr"):
        with (output / f"fresh-pgo-full-dist.{suffix}").open("ab") as stream, \
                (output / f"continuation-final-dist.{suffix}").open("rb") as continuation:
            shutil.copyfileobj(continuation, stream)
    training = read(output / "training-production.json")
    save(output / "segmented-production.json", {
        "study": STUDY, "training_seconds": training["wall_seconds"],
        "final_build_seconds": final["wall_seconds"],
        "aggregate_active_production_seconds": training["wall_seconds"] + final["wall_seconds"],
        "continuous_full_release_seconds": None,
        "excludes": "setup, archive/transfer/restore, verification, uploads, inter-job wait",
    })
    result = release.validate_distribution(
        source, output, HOST, env, clang, identity, Path(identity["files"]["lib.exe"]["path"]), provenance)
    result.pop("hosted_baseline")
    result.update(segmented_study=STUDY, continuous_full_release_seconds=None,
                  production=read(output / "segmented-production.json"),
                  hardware=[read(output / "training-hardware.json"),
                            read(output / "continuation-hardware.json")])
    save(output / "segmented-result.json", result)


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--checkpoint-final":
        return checkpoint_final(Path(sys.argv[2]), sys.argv[3:])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("train", "pack", "unpack", "finish"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--transfer", type=Path)
    args = parser.parse_args()
    release.validate_runner(HOST)
    if not release.hosted_baseline() or args.root != Path(r"D:\mhx"):
        raise RuntimeError("Segmented production is restricted to the explicit public-hosted baseline")
    try:
        if args.phase == "train":
            train(args.root)
        elif args.phase == "finish":
            finish(args.root)
        elif args.transfer is None:
            parser.error("--transfer is required for checkpoint transfer")
        elif args.phase == "pack":
            pack(args.root, args.transfer)
        else:
            unpack(args.root, args.transfer)
    except Exception as error:
        save(args.root / "e/segmented-failure.json", {
            "phase": args.phase, "error": str(error), "error_type": type(error).__name__,
            "complete": False,
        })
        raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
