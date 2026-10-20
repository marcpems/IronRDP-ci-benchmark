"""Replay shipping and fresh full-release PGO compilers using the established native meter."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile

from build_arm_compilers import digest, save
from compiler_probe import validate_meter
from native_ci_probe import paired_order, run_block
from x64_pgo_release import validate_reference


def checked_release(artifacts, variant, protocol):
    evidence = artifacts / f"x64-pgo-{variant}-evidence"
    result_path = evidence / "result.json"
    result = json.loads(result_path.read_text())
    expected = {"complete": True, "variant": variant, "run_id": protocol["release_run"],
                "attempt": protocol["release_attempt"], "rust_sha": protocol["rust_sha"]}
    if any(result.get(key) != value for key, value in expected.items()):
        raise RuntimeError(f"Unqualified or wrong full-release artifact: {variant}")
    if digest(result_path) != protocol["compiler_metadata_sha256"][variant]:
        raise RuntimeError(f"Release metadata differs from preregistered evidence: {variant}")
    name = f"rustc-{protocol['rust_version']}-{protocol['host']}.tar.xz"
    manifest = json.loads((evidence / "dist-manifest.json").read_text())
    entries = [row for row in manifest if row["name"] == name]
    if len(entries) != 1:
        raise RuntimeError(f"Missing or duplicate compiler manifest entry: {variant}")
    archive = artifacts / f"x64-pgo-{variant}-dist" / name
    expected_sha = protocol["compiler_archive_sha256"][variant]
    if (entries[0]["sha256"] != expected_sha or digest(archive) != expected_sha
            or archive.stat().st_size != entries[0]["bytes"]):
        raise RuntimeError(f"Compiler archive differs from preregistered full release: {variant}")
    return result, archive, {"result_sha256": digest(result_path), "archive_sha256": expected_sha}


def share_native_libraries(official, compiler, host):
    source = official.parent.parent / "lib/rustlib" / host / "lib"
    expected = {path.name: digest(path) for path in source.iterdir() if path.is_file()}
    if not any(name.startswith("libstd-") for name in expected):
        raise RuntimeError("Official native standard library is missing")
    target = compiler.parent.parent / "lib/rustlib" / host / "lib"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    actual = {path.name: digest(path) for path in target.iterdir() if path.is_file()}
    if actual != expected:
        raise RuntimeError("Native standard-library identity check failed")
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    protocol = json.loads(args.protocol.read_text())
    vm = int(os.environ["BENCHMARK_REPLICATE"])
    if (os.name != "nt" or os.cpu_count() != protocol["cores"]
            or os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted"
            or os.environ["BENCHMARK_HOST"] != protocol["host"]
            or vm not in range(1, protocol["independent_vms"] + 1)):
        raise RuntimeError("Expected an independent standard four-CPU Windows x64 VM")
    if subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip() != protocol["source_sha"]:
        raise RuntimeError("Wrong IronRDP source revision")
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    output.mkdir(exist_ok=False)
    official = Path(subprocess.check_output(
        ["rustup", "which", "--toolchain", protocol["rust_version"], "rustc"], text=True,
    ).strip())
    compilers = {"official": official}
    metadata, evidence, standard = {}, {}, None
    for variant in ("upstream", "local"):
        metadata[variant], archive, evidence[variant] = checked_release(args.artifacts, variant, protocol)
        folder = output / "compilers" / variant
        folder.mkdir(parents=True)
        with tarfile.open(archive, "r:xz") as bundle:
            bundle.extractall(folder, filter="data")
        compiler = folder / archive.name.removesuffix(".tar.xz") / "rustc/bin/rustc.exe"
        if not compiler.is_file():
            raise RuntimeError(f"Missing extracted compiler: {variant}")
        libraries = share_native_libraries(official, compiler, protocol["host"])
        if standard is not None and libraries != standard:
            raise RuntimeError("Official libraries changed during preparation")
        standard = libraries
        compilers[variant] = compiler
    validate_reference(metadata["upstream"], metadata["local"])
    cargo = official.parent / "cargo.exe"
    os.environ["PATH"] = str(official.parent) + os.pathsep + os.environ["PATH"]
    os.environ["RUSTDOC"] = str(official.parent / "rustdoc.exe")
    for name in ("GH_TOKEN", "GITHUB_TOKEN"):
        os.environ.pop(name, None)
    versions = {}
    for variant, compiler in compilers.items():
        version = subprocess.check_output([compiler, "-vV"], text=True)
        if any(value not in version for value in (
                f"host: {protocol['host']}\n", protocol["rust_sha"],
                f"release: {protocol['rust_version']}\n")):
            raise RuntimeError(f"Wrong compiler binary identity: {variant}")
        versions[variant] = version
        evidence.setdefault(variant, {})["rustc_sha256"] = digest(compiler)
        evidence[variant]["driver_sha256"] = {
            path.name: digest(path) for path in compiler.parent.glob("rustc_driver-*.dll")}
        if not evidence[variant]["driver_sha256"]:
            raise RuntimeError(f"Missing compiler driver: {variant}")
    subprocess.run([cargo, "fetch", "--locked", "--target", protocol["host"]], cwd=source,
                   env={**os.environ, "RUSTC": str(official)}, check=True)
    validate_meter(output / "meter-validation")
    index = {
        "protocol": protocol, "vm": vm, "complete": False, "variants": protocol["variants"],
        "benchmark_run": os.environ["GITHUB_RUN_ID"], "attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "versions": versions, "compiler_metadata": metadata, "artifact_evidence": evidence,
        "stdlib": standard, "cargo_sha256": digest(cargo), "runs": [],
    }
    save(output / "index.json", index)
    for round_index in range(protocol["warmup_rounds"] + protocol["measured_rounds"]):
        for position, variant in enumerate(paired_order(protocol["variants"], vm, round_index)):
            name = f"round-{round_index}-{variant}"
            print(f"BEGIN {name} (VM {vm}, position {position})", flush=True)
            run_block(source, output / name, compilers[variant], protocol,
                      {"variant": variant, "round": round_index}, round_index == 0, native_only=True)
            index["runs"].append({"variant": variant, "round": round_index, "position": position,
                                  "warmup": round_index < protocol["warmup_rounds"],
                                  "path": f"{name}/results.json"})
            save(output / "index.json", index)
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    index["complete"] = True
    save(output / "index.json", index)


if __name__ == "__main__":
    main()
