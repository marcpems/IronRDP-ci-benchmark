"""Replay each qualified distribution without replacing its compiler, Cargo, or stdlib."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tomllib

from build_arm_compilers import digest, save
from combined_pgo_validation import protocol
from compiler_probe import validate_meter
from msvc_experiment import equivalent_tools
from native_ci_probe import paired_order, run_block
from x64_pgo_release import HOST


def verify_pair(left, right):
    plan = protocol()
    for variant, result in zip(plan["variants"], (left, right)):
        if (result.get("complete") is not True or result["variant"] != variant
                or result["protocol"] != plan or result["base_sha"] != plan["base_sha"]
                or result["run_id"] != os.environ["GITHUB_RUN_ID"]
                or result["attempt"] != "1" or not result.get("qualification")
                or result["patch_sha256"] != plan["patch_sha256"]):
            raise RuntimeError(f"Unqualified release identity: {variant}")
    if right["applied_patch_sha256"] != plan["patch_sha256"]:
        raise RuntimeError("Candidate did not use the exact reviewed patch")
    if left["applied_patch_sha256"] != hashlib.sha256(b"").hexdigest():
        raise RuntimeError("Control source was modified")
    for key in ("clang_installer_sha256", "wix_archive_sha256", "sccache_sha256", "runner", "harness_sha"):
        if left[key] != right[key]:
            raise RuntimeError(f"Release input mismatch: {key}")
    if not equivalent_tools(left["tools"], right["tools"]):
        raise RuntimeError("Release tools changed between arms")
    configs = [tomllib.loads(row["configuration"]) for row in (left, right)]
    for config in configs:
        config["build"]["ccache"] = Path(config["build"]["ccache"]).name
        config["llvm"]["clang-cl"] = Path(config["llvm"]["clang-cl"]).name
        config["target"][HOST]["ar"] = Path(config["target"][HOST]["ar"]).name
    if configs[0] != configs[1]:
        raise RuntimeError("Release settings differ beyond per-arm tool paths")


def extract_distribution(artifacts, output, variant):
    evidence = artifacts / f"combined-{variant}-evidence"
    result = json.loads((evidence / "result.json").read_text())
    manifest = json.loads((evidence / "dist-manifest.json").read_text())
    manifest = {row["name"]: row for row in manifest}
    folder = output / variant
    folder.mkdir()
    installed = folder / "installed"
    installed.mkdir()
    hashes = {}
    for component in ("rustc", "cargo", "rust-std"):
        name = f"{component}-nightly-{HOST}"
        archive = artifacts / f"combined-{variant}-dist" / f"{name}.tar.xz"
        row = manifest[archive.name]
        if digest(archive) != row["sha256"] or archive.stat().st_size != row["bytes"]:
            raise RuntimeError(f"Archive integrity failure: {archive}")
        hashes[archive.name] = row["sha256"]
        with tarfile.open(archive, "r:xz") as bundle:
            bundle.extractall(folder, filter="data")
        payload = folder / name / (f"rust-std-{HOST}" if component == "rust-std" else component)
        shutil.copytree(payload, installed, dirs_exist_ok=True)
    identities = {
        str(path.relative_to(installed)): digest(path)
        for path in installed.rglob("*") if path.is_file()
    }
    return installed, result, {"archives": hashes, "installed_files": identities}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    plan = protocol()
    source, output = args.source.resolve(), args.output.resolve()
    if (os.name != "nt" or os.cpu_count() != plan["cores"]
            or os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted"):
        raise RuntimeError("Expected standard four-LP hosted Windows")
    if subprocess.check_output(
        ["git", "-C", source, "rev-parse", "HEAD"], text=True,
    ).strip() != plan["source_sha"]:
        raise RuntimeError("Wrong workload source")
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    output.mkdir()
    toolchains, results, evidence = {}, {}, {}
    for variant in plan["variants"]:
        toolchains[variant], results[variant], evidence[variant] = extract_distribution(
            args.artifacts.resolve(), output, variant,
        )
    verify_pair(results["control"], results["candidate"])
    original_path = os.environ["PATH"]
    for key in ("GH_TOKEN", "GITHUB_TOKEN"):
        os.environ.pop(key, None)
    for variant, toolchain in toolchains.items():
        binary = toolchain / "bin"
        env = {**os.environ, "PATH": str(binary) + os.pathsep + original_path,
               "RUSTC": str(binary / "rustc.exe")}
        subprocess.run(
            [binary / "cargo.exe", "fetch", "--locked", "--target", HOST],
            cwd=source, env=env, check=True,
        )
    validate_meter(output / "meter-validation")
    workload = {**plan, "rust_sha": plan["base_sha"]}
    index = {
        "complete": False, "protocol": plan, "releases": results, "evidence": evidence,
        "run_id": os.environ["GITHUB_RUN_ID"], "runs": [],
        "contrast": "Full distribution effect; each arm retains its own Cargo and native stdlib",
    }
    save(output / "index.json", index)
    for round_index in range(plan["warmup_rounds"] + plan["measured_rounds"]):
        for position, variant in enumerate(paired_order(plan["variants"], 1, round_index)):
            binary = toolchains[variant] / "bin"
            os.environ["PATH"] = str(binary) + os.pathsep + original_path
            os.environ["RUSTDOC"] = str(binary / "rustdoc.exe")
            name = f"round-{round_index}-{variant}"
            run_block(
                source, output / name, binary / "rustc.exe", workload,
                {"variant": variant, "round": round_index}, round_index == 0,
                correctness_env={"RUST_TEST_THREADS": "1"}, native_only=True,
            )
            index["runs"].append({
                "variant": variant, "round": round_index, "position": position,
                "warmup": round_index < plan["warmup_rounds"], "path": f"{name}/results.json",
            })
            save(output / "index.json", index)
    for variant, toolchain in toolchains.items():
        actual = {
            str(path.relative_to(toolchain)): digest(path)
            for path in toolchain.rglob("*") if path.is_file()
        }
        if actual != evidence[variant]["installed_files"]:
            raise RuntimeError(f"Distribution files changed during replay: {variant}")
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    index["complete"] = True
    save(output / "index.json", index)


if __name__ == "__main__":
    main()
