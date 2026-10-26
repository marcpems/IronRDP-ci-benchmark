"""Lightweight paired IronRDP replay of a Rust try build and its exact upstream parent."""

import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tarfile

from build_arm_compilers import digest, save
from compiler_probe import validate_meter
from native_ci_probe import PROFILE_ENV, paired_order, run_block
from offline_benchmark import NATIVE_COMMANDS

HOST = "x86_64-pc-windows-msvc"
SOURCE_SHA = "0c5419eca6bf53563056ed252f537bca67862705"
REVISIONS = {
    "parent": "dc44e7f2c436b6041742e138b9c2176f093196d5",
    "try": "51dae83933ec0602516d385a07cea7c692d15261",
}
ARCHIVE_BYTES = {"parent": 263227696, "try": 263146960}
VARIANTS = list(REVISIONS)
ROUNDS = 2
SCOPE = (
    "Two alternating cold native-build pairs on one 16-LP Windows host, constrained to four CPUs; "
    "no excluded warmup or statistical qualification. Each compiler retains its own bundled stdlib; "
    "Cargo is held fixed to the parent build. Setup, downloads, extraction and correctness are untimed."
)


def install(root, variant):
    revision = REVISIONS[variant]
    url = f"https://ci-artifacts.rust-lang.org/rustc-builds/{revision}/rust-nightly-{HOST}.tar.xz"
    destination = root / "compilers" / variant
    destination.mkdir(parents=True)
    archive = destination / "toolchain.tar.xz"
    subprocess.run(
        ["curl.exe", "--fail", "--location", "--retry", "3", "--silent", "--show-error",
         "--max-time", "600", url, "--output", archive], check=True,
    )
    if archive.stat().st_size != ARCHIVE_BYTES[variant]:
        raise RuntimeError(f"Unexpected CI archive size for {variant}")
    with tarfile.open(archive, "r:xz") as bundle:
        bundle.extractall(destination, filter="data")
    unpacked = destination / f"rust-nightly-{HOST}"
    compiler = unpacked / "rustc/bin/rustc.exe"
    cargo = unpacked / "cargo/bin/cargo.exe"
    shutil.copytree(
        unpacked / f"rust-std-{HOST}/lib", compiler.parent.parent / "lib", dirs_exist_ok=True,
    )
    version = subprocess.check_output([compiler, "-vV"], text=True)
    if f"commit-hash: {revision}\n" not in version or f"host: {HOST}\n" not in version:
        raise RuntimeError(f"CI compiler does not match the requested revision: {variant}")
    drivers = {path.name: digest(path) for path in compiler.parent.glob("rustc_driver-*.dll")}
    if not drivers or not cargo.is_file():
        raise RuntimeError("The downloaded compiler bundle is incomplete")
    return compiler, cargo, {
        "url": url, "sha": revision, "rustc_version": version,
        "archive_bytes": archive.stat().st_size, "archive_sha256": digest(archive),
        "rustc_sha256": digest(compiler), "driver_sha256": drivers, "cargo_sha256": digest(cargo),
        "checksum_note": "Archive SHA-256 recorded locally; this CI endpoint has no .sha256 sidecar.",
    }


def summarize(output, runs):
    expected = {(variant, round_index) for variant in VARIANTS for round_index in range(ROUNDS)}
    actual = [(row["variant"], row["round"]) for row in runs]
    if len(actual) != len(expected) or set(actual) != expected:
        raise RuntimeError("Incomplete or duplicate paired measurements")
    totals = {variant: {} for variant in VARIANTS}
    common, affinity, targets = None, None, set()
    for row in runs:
        result = json.loads((output / row["path"]).read_text())
        meta, measurements = result["metadata"], result["measurements"]
        if (meta["variant"] != row["variant"] or meta["round"] != row["round"]
                or meta["source_sha"] != SOURCE_SHA or meta["profile_environment"] != PROFILE_ENV
                or f"commit-hash: {REVISIONS[row['variant']]}\n" not in meta["rustc"]):
            raise RuntimeError("Measured compiler or workload identity mismatch")
        identity = (meta["lock_lf_sha256"], meta["cargo"])
        if common is not None and common != identity:
            raise RuntimeError("Cargo or workload lockfile changed between compilers")
        common = identity
        target = meta["cold_target_directories"]["native"]
        if target in targets:
            raise RuntimeError("A supposedly cold target directory was reused")
        targets.add(target)
        if [item["name"] for item in measurements] != [name for name, _ in NATIVE_COMMANDS]:
            raise RuntimeError("Missing or changed native Cargo commands")
        for item, (_, args) in zip(measurements, NATIVE_COMMANDS):
            if (item["exit_code"] or not item["compiled_artifacts"]
                    or item["command"] != ["cargo", *args, "--frozen", "--timings", "--message-format=json"]
                    or any(not math.isfinite(item[key]) or item[key] <= 0
                           for key in ("wall_seconds", "cpu_seconds"))):
                raise RuntimeError("Failed, empty, or invalid native compilation")
            current_affinity = tuple(item["affinity"])
            if len(current_affinity) != 4 or affinity is not None and current_affinity != affinity:
                raise RuntimeError("CPU affinity changed between compilations")
            affinity = current_affinity
        totals[row["variant"]][row["round"]] = {
            **{key: sum(item[key] for item in measurements) for key in ("wall_seconds", "cpu_seconds")},
            "workspace_seconds": measurements[1]["wall_seconds"],
        }
    means = {
        variant: {key: sum(row[key] for row in values.values()) / ROUNDS
                  for key in ("wall_seconds", "cpu_seconds", "workspace_seconds")}
        for variant, values in totals.items()
    }
    return {
        "scope": SCOPE, "means": means,
        "paired_rounds": [
            {"round": round_index,
             "parent_seconds": totals["parent"][round_index]["wall_seconds"],
             "try_seconds": totals["try"][round_index]["wall_seconds"],
             "wall_reduction_percent": 100 * (
                 1 - totals["try"][round_index]["wall_seconds"] / totals["parent"][round_index]["wall_seconds"]
             )}
            for round_index in range(ROUNDS)
        ],
        "wall_reduction_percent": 100 * (1 - means["try"]["wall_seconds"] / means["parent"]["wall_seconds"]),
        "cpu_reduction_percent": 100 * (1 - means["try"]["cpu_seconds"] / means["parent"]["cpu_seconds"]),
        "workspace_reduction_percent": 100 * (
            1 - means["try"]["workspace_seconds"] / means["parent"]["workspace_seconds"]
        ),
    }


def main(root, correctness):
    source, output = root / "s", root / "e"
    if (os.name != "nt" or os.cpu_count() != 16
            or os.environ.get("RUNNER_NAME") != "MARCPE-TEST01-X64"
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted" or root.drive.upper() != "D:"):
        raise RuntimeError("Expected the dedicated Windows x64 ReFS benchmark runner")
    if (root / "owner-run.txt").read_text().strip() != (
            f'{os.environ["GITHUB_RUN_ID"]}/{os.environ["GITHUB_RUN_ATTEMPT"]}'):
        raise RuntimeError("Wrong run directory owner")
    if subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip() != SOURCE_SHA:
        raise RuntimeError("Wrong IronRDP revision")
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    compilers, cargos, artifacts = {}, {}, {}
    for variant in VARIANTS:
        compilers[variant], cargos[variant], artifacts[variant] = install(root, variant)
    releases = [
        next(line.removeprefix("release: ") for line in item["rustc_version"].splitlines()
             if line.startswith("release: ")) for item in artifacts.values()
    ]
    if releases[0] != releases[1]:
        raise RuntimeError("Parent and try-build release versions differ")
    cargo = cargos["parent"]
    base_path = os.environ["PATH"]
    os.environ["PATH"] = str(cargo.parent) + os.pathsep + str(compilers["parent"].parent) + os.pathsep + base_path
    subprocess.run(
        [cargo, "fetch", "--locked", "--target", HOST], cwd=source,
        env={**os.environ, "RUSTC": str(compilers["parent"]), "CARGO_NET_OFFLINE": "false"}, check=True,
    )
    validate_meter(output / "meter-validation")
    index = {
        "complete": False, "scope": SCOPE, "source_sha": SOURCE_SHA, "revisions": REVISIONS,
        "artifacts": artifacts, "common_cargo_sha256": digest(cargo), "runs": [],
        "run_id": os.environ["GITHUB_RUN_ID"], "attempt": os.environ["GITHUB_RUN_ATTEMPT"],
    }
    save(output / "index.json", index)
    for round_index in range(ROUNDS):
        for position, variant in enumerate(paired_order(VARIANTS, 1, round_index)):
            os.environ["PATH"] = str(cargo.parent) + os.pathsep + str(compilers[variant].parent) + os.pathsep + base_path
            os.environ["RUSTDOC"] = str(compilers[variant].parent / "rustdoc.exe")
            protocol = {"source_sha": SOURCE_SHA, "rust_sha": REVISIONS[variant],
                        "rust_version": releases[0], "cores": 4}
            name = f"round-{round_index}-{variant}"
            print(f"BEGIN {name}, position {position}", flush=True)
            run_block(
                source, output / name, compilers[variant], protocol,
                {"variant": variant, "round": round_index}, round_index == 0,
                correctness_env={"TEMP": str(correctness), "TMP": str(correctness)}, native_only=True,
            )
            index["runs"].append({"variant": variant, "round": round_index, "position": position,
                                  "path": f"{name}/results.json"})
            save(output / "index.json", index)
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    result = summarize(output, index["runs"])
    save(output / "summary.json", result)
    index["complete"] = True
    save(output / "index.json", index)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--correctness-temp", type=Path, required=True)
    args = parser.parse_args()
    try:
        main(args.root.resolve(), args.correctness_temp.resolve())
    except Exception as error:
        save(args.root / "e/failure.json", {"complete": False, "error": str(error)})
        raise
