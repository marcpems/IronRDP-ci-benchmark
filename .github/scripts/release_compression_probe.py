"""Compare existing installer compression profiles without changing release artifacts."""

import argparse
import hashlib
import lzma
import os
from pathlib import Path
import statistics
import subprocess

from build_arm_compilers import digest, save
from matched_release import RUST
from msvc_experiment import execute


def tar_digest(path):
    checksum = hashlib.sha256()
    with lzma.open(path, "rb") as stream:
        while block := stream.read(1024 * 1024):
            checksum.update(block)
    return checksum.hexdigest()


def summarize(rows):
    result = {}
    for package in sorted({row["package"] for row in rows}):
        selected = [row for row in rows if row["package"] == package]
        profiles = {}
        for profile in ("balanced", "fast"):
            samples = [row for row in selected if row["profile"] == profile]
            if len(samples) != 2 or {row["round"] for row in samples} != {0, 1}:
                raise RuntimeError(f"incomplete paired compression samples: {package}/{profile}")
            if any(row["exit_code"] or not row["identical_tar_stream"] for row in samples):
                raise RuntimeError(f"invalid compression sample: {package}/{profile}")
            if len({row["archive_bytes"] for row in samples}) != 1:
                raise RuntimeError(f"non-deterministic archive size: {package}/{profile}")
            profiles[profile] = {
                "median_seconds": statistics.median(row["wall_seconds"] for row in samples),
                "archive_bytes": samples[0]["archive_bytes"],
            }
        result[package] = {
            **profiles,
            "seconds_saved": profiles["balanced"]["median_seconds"] - profiles["fast"]["median_seconds"],
            "compression_saving_percent": 100 * (
                1 - profiles["fast"]["median_seconds"] / profiles["balanced"]["median_seconds"]),
            "archive_growth_percent": 100 * (
                profiles["fast"]["archive_bytes"] / profiles["balanced"]["archive_bytes"] - 1),
        }
    if not result:
        raise RuntimeError("no compression samples")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--installer", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--mtime", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cores", type=int, required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    if os.environ.get("RUNNER_ENVIRONMENT") == "self-hosted" or os.environ.get("COMPUTERNAME") in (
        "MARCPE-D4-Arm64", "MARCPE-TEST01-X64",
    ):
        raise RuntimeError("throughput experiments must not run on the custom timing runners")
    if args.cores < 1 or args.cores > (os.cpu_count() or 0):
        raise RuntimeError("invalid compression CPU allowance")
    output.mkdir(exist_ok=False)
    revision = subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip()
    if revision != RUST:
        raise RuntimeError("installer source must match the pinned release source")
    installer = args.installer.resolve()
    if not installer.is_file():
        raise RuntimeError(f"missing built release installer: {installer}")
    timestamp = args.mtime
    rows = []
    provenance = {
        "rust_sha": RUST, "installer_sha256": digest(installer),
        "machine": os.environ["COMPUTERNAME"], "cpu_allowance": args.cores,
        "logical_cpus": os.cpu_count(),
        "scope": "paired packaging-only replay; not a cold full-release timing",
        "cache_policy": "OS cache not flushed; balanced/fast then fast/balanced order",
        "excludes": "source verification, archive decompression/hash verification, cleanup, uploads",
        "packages": {},
    }
    save(output / "provenance.json", provenance)
    for package_path in (args.package.resolve(),):
        package = package_path.name
        work = package_path.parent
        original = args.reference.resolve()
        if not (work / package).is_dir() or not original.is_file():
            raise RuntimeError(f"missing original packaging input or archive: {package}")
        expected_tar = tar_digest(original)
        provenance["packages"][package] = {
            "original_archive_sha256": digest(original), "tar_stream_sha256": expected_tar,
        }
        save(output / "provenance.json", provenance)
        for round_index, order in enumerate((("balanced", "fast"), ("fast", "balanced"))):
            for profile in order:
                name = f"package-{round_index}-{profile}"
                prefix = output / name
                result = execute(
                    [installer, "tarball", "--input", package, "--work-dir", work,
                     "--output", prefix, "--compression-formats", "xz",
                     "--compression-profile", profile, "--override-file-mtime", timestamp],
                    source, dict(os.environ), output, name, timeout=1800, cores=args.cores)
                archive = prefix.with_suffix(".tar.xz")
                actual_tar = tar_digest(archive)
                row = {
                    **result, "package": package, "profile": profile, "round": round_index,
                    "archive_bytes": archive.stat().st_size, "tar_stream_sha256": actual_tar,
                    "identical_tar_stream": actual_tar == expected_tar,
                }
                rows.append(row)
                save(output / "samples.json", rows)
                if not row["identical_tar_stream"]:
                    raise RuntimeError(f"packaging replay changed the decompressed tar stream: {name}")
                archive.unlink()
    save(output / "comparison.json", {
        "complete": True, "provenance": provenance, "packages": summarize(rows),
        "scope": "packaging-only; do not extrapolate savings to entire dist assembly or MSI",
    })


if __name__ == "__main__":
    main()
