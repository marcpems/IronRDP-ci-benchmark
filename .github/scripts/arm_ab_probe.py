"""Paired Arm64 A/B blocks, using the original compiler CPU validation suite."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

from compiler_probe import run, save


def variant_order(variants, vm, round_index):
    offset = (vm - 1 + round_index) % len(variants)
    ordered = variants[offset:] + variants[:offset]
    return list(reversed(ordered)) if round_index % 2 else ordered


def verify_custom(root, variant, protocol):
    metadata = json.loads((root / f"{variant}.json").read_text(encoding="utf-8"))
    if metadata["variant"] != variant or metadata["rust_sha"] != protocol["rust_sha"]:
        raise RuntimeError(f"Wrong compiler provenance: {variant}")
    if metadata["evaluation_stdlib_sha256"] != protocol["evaluation_stdlib_sha256"]:
        raise RuntimeError(f"Wrong evaluation standard libraries: {variant}")
    sysroot = root / variant
    for relative, expected in metadata["files"].items():
        path = sysroot / relative
        if not path.is_file():
            raise RuntimeError(f"Missing compiler file: {path}")
        with path.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != expected:
            raise RuntimeError(f"Compiler file checksum mismatch: {path}")
    return sysroot / "bin" / "rustc.exe"


def download_compilers(root, variants, tag):
    root.mkdir(parents=True, exist_ok=True)
    for variant in variants:
        if variant == "official":
            continue
        subprocess.run([
            "gh", "release", "download", tag, "--repo", os.environ["GITHUB_REPOSITORY"],
            "--pattern", f"{variant}.zip", "--pattern", f"{variant}.json",
            "--dir", str(root),
        ], check=True)
        metadata = json.loads((root / f"{variant}.json").read_text(encoding="utf-8"))
        archive = root / f"{variant}.zip"
        with archive.open("rb") as stream:
            checksum = hashlib.file_digest(stream, "sha256").hexdigest()
        if checksum != metadata["archive_sha256"]:
            raise RuntimeError(f"Archive checksum mismatch: {variant}")
        destination = root / variant
        destination.mkdir(exist_ok=False)
        with zipfile.ZipFile(archive) as package:
            for entry in package.infolist():
                if not (destination / entry.filename).resolve().is_relative_to(destination):
                    raise RuntimeError("Compiler archive contains an unsafe path")
            package.extractall(destination)
        archive.unlink()


def correctness(source, compiler, output, temporary):
    env = {
        **os.environ, "RUSTC": str(compiler), "CARGO_NET_OFFLINE": "true",
        "CARGO_INCREMENTAL": "0", "CARGO_PROFILE_DEV_DEBUG": "0",
        "CARGO_PROFILE_DEV_OPT_LEVEL": "1", "CARGO_PROFILE_DEV_CODEGEN_UNITS": "16",
        "CARGO_BUILD_JOBS": "4", "CARGO_TARGET_DIR": str(temporary),
    }
    command = ["cargo", "test", "-p", "ironrdp-graphics", "--lib", "--frozen"]
    with output.open("wb") as log:
        subprocess.run(command, cwd=source, env=env, stdout=log,
                       stderr=subprocess.STDOUT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wrapper", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--compilers", type=Path)
    parser.add_argument("--official-only", action="store_true")
    parser.add_argument("--baseline-only", action="store_true")
    parser.add_argument("--release-tag")
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    actual_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    if actual_sha != protocol["source_sha"]:
        raise RuntimeError(f"Wrong workload source: {actual_sha}")
    vm = int(os.environ["BENCHMARK_REPLICATE"])
    if vm not in range(1, protocol["independent_vms_per_os"] + 1):
        raise RuntimeError(f"Unexpected VM index: {vm}")
    official = Path(subprocess.check_output(
        ["rustup", "which", "rustc"], cwd=source, text=True,
    ).strip())
    variants = protocol["windows_variants"] if os.name == "nt" else protocol["linux_variants"]
    if args.official_only:
        variants = ["official"]
    elif args.baseline_only and os.name == "nt":
        variants = ["official", "baseline-msvc"]
    if args.release_tag and os.name == "nt" and len(variants) > 1:
        if args.compilers is None:
            parser.error("--compilers is required for downloads")
        download_compilers(args.compilers.resolve(), variants, args.release_tag)
    compilers = {"official": official}
    for variant in variants:
        if variant != "official":
            if args.compilers is None:
                parser.error("--compilers is required for the Windows A/B")
            compilers[variant] = verify_custom(args.compilers.resolve(), variant, protocol)
        version = subprocess.check_output([str(compilers[variant]), "-vV"], text=True)
        if f"release: {protocol['rust_version']}\n" not in version or protocol["rust_sha"] not in version:
            raise RuntimeError(f"Incorrect compiler identity for {variant}: {version}")
    save(output / "protocol.json", protocol)
    index = {
        "protocol": protocol, "vm": vm, "platform": os.environ["BENCHMARK_PLATFORM"],
        "pilot": args.pilot, "variants": variants, "runs": [],
        "compiler_archive_sha256": {},
    }
    for variant in variants:
        if variant != "official":
            metadata = json.loads((args.compilers / f"{variant}.json").read_text(encoding="utf-8"))
            save(output / f"{variant}-compiler.json", metadata)
            index["compiler_archive_sha256"][variant] = metadata["archive_sha256"]
    for variant in variants:
        with tempfile.TemporaryDirectory(prefix="arm-ab-tests-", dir=os.environ["RUNNER_TEMP"]) as tmp:
            correctness(source, compilers[variant], output / f"{variant}-correctness.log", Path(tmp))
    warmups = 0 if args.pilot else protocol["warmup_rounds"]
    rounds = 1 if args.pilot else protocol["measured_rounds"]
    for round_index in range(warmups + rounds):
        for position, variant in enumerate(variant_order(variants, vm, round_index)):
            name = f"round-{round_index}-{variant}"
            print(f"BEGIN {name} (VM {vm}, position {position})", flush=True)
            with tempfile.TemporaryDirectory(prefix="arm-ab-measure-", dir=os.environ["RUNNER_TEMP"]) as tmp:
                run(source, output / name, args.wrapper, compiler=compilers[variant],
                    temporary=Path(tmp) / "targets")
            index["runs"].append({
                "variant": variant, "round": round_index, "position": position,
                "warmup": round_index < warmups, "path": f"{name}/results.json",
            })
            save(output / "index.partial.json", index)
    save(output / "index.json", index)


if __name__ == "__main__":
    main()
