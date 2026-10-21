"""Replay the qualified profile-only pair on one self-hosted x64 machine."""

import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
from urllib.request import urlopen

from build_arm_compilers import digest, save
from compiler_probe import validate_meter
from native_ci_probe import PROFILE_ENV, paired_order, run_block
from offline_benchmark import NATIVE_COMMANDS
from x64_pgo_replay import share_native_libraries
from x64_profile_only import PROTOCOL, verify_pair


def install_official(output, protocol):
    unpacked = output / "official"
    unpacked.mkdir()
    for component in ("rustc", "cargo", "rust-std"):
        name = f"{component}-{protocol['rust_version']}-{protocol['host']}"
        url = f"https://static.rust-lang.org/dist/{name}.tar.xz"
        with urlopen(url + ".sha256", timeout=60) as response:
            expected = response.read().decode().split()[0]
        archive = unpacked / f"{name}.tar.xz"
        with urlopen(url, timeout=120) as response, archive.open("wb") as destination:
            shutil.copyfileobj(response, destination)
        if digest(archive) != expected:
            raise RuntimeError(f"Official {component} archive checksum mismatch")
        save(unpacked / f"{name}.json", {"url": url, "sha256": expected})
        with tarfile.open(archive, "r:xz") as bundle:
            bundle.extractall(unpacked, filter="data")
    suffix = f"{protocol['rust_version']}-{protocol['host']}"
    compiler = unpacked / f"rustc-{suffix}/rustc/bin/rustc.exe"
    cargo = unpacked / f"cargo-{suffix}/cargo/bin/cargo.exe"
    libraries = unpacked / f"rust-std-{suffix}/rust-std-{protocol['host']}/lib/rustlib"
    shutil.copytree(libraries, compiler.parent.parent / "lib/rustlib", dirs_exist_ok=True)
    return compiler, cargo


def checked_compiler(root, output, variant, protocol):
    evidence = root / "a" / f"x64-profile-{variant}-evidence"
    result = json.loads((evidence / "result.json").read_text())
    if (not result.get("complete") or result["protocol"] != protocol
            or result["variant"] != variant or result["run_id"] != os.environ["GITHUB_RUN_ID"]
            or result["attempt"] != os.environ["GITHUB_RUN_ATTEMPT"]
            or result["llvm_profile_sha256"] != protocol["llvm_profile_sha256"][variant]):
        raise RuntimeError(f"Unqualified or wrong build artifact: {variant}")
    name = f"rustc-{protocol['rust_version']}-{protocol['host']}.tar.xz"
    manifest = json.loads((evidence / "dist-manifest.json").read_text())
    rows = [row for row in manifest if row["name"] == name]
    archive = root / "a" / f"x64-profile-{variant}-dist" / name
    if len(rows) != 1 or digest(archive) != rows[0]["sha256"] or archive.stat().st_size != rows[0]["bytes"]:
        raise RuntimeError(f"Compiler archive does not match its qualified manifest: {variant}")
    folder = output / "compilers" / variant
    folder.mkdir(parents=True)
    with tarfile.open(archive, "r:xz") as bundle:
        bundle.extractall(folder, filter="data")
    return result, folder / name.removesuffix(".tar.xz") / "rustc/bin/rustc.exe", {
        "archive_sha256": digest(archive), "result_sha256": digest(evidence / "result.json")}


def summarize(output, index):
    protocol = index["protocol"]
    expected = {(variant, round_index) for variant in protocol["variants"]
                for round_index in range(protocol["warmup_rounds"] + protocol["measured_rounds"])}
    actual = [(row["variant"], row["round"]) for row in index["runs"]]
    if len(actual) != len(expected) or set(actual) != expected:
        raise RuntimeError("Incomplete or duplicate replay matrix")
    totals = {variant: {} for variant in protocol["variants"]}
    shared, targets = None, set()
    for row in index["runs"]:
        result = json.loads((output / row["path"]).read_text())
        meta, measurements = result["metadata"], result["measurements"]
        if (meta["variant"] != row["variant"] or meta["round"] != row["round"]
                or meta["source_sha"] != protocol["source_sha"]
                or meta["profile_environment"] != PROFILE_ENV
                or meta["logical_cpus"] != protocol["build_cores"]
                or meta["rustc"] != index["versions"][row["variant"]]
                or meta["environment"]["GITHUB_RUN_ID"] != index["run_id"]
                or meta["environment"]["GITHUB_RUN_ATTEMPT"] != index["attempt"]
                or row["position"] != paired_order(protocol["variants"], 1, row["round"]).index(row["variant"])):
            raise RuntimeError("Replay metadata mismatch")
        identity = (meta["lock_lf_sha256"], meta["cargo"])
        if shared is not None and identity != shared:
            raise RuntimeError("Workload lock or Cargo identity changed")
        shared = identity
        target = meta["cold_target_directories"]["native"]
        if target in targets:
            raise RuntimeError("A target directory was reused")
        targets.add(target)
        approved = {path.replace("\\", "/").lower() for path in meta["approved_background_executables"]}
        if any("/vc/tools/msvc/" not in path or not path.endswith("/bin/hostx64/x64/vctip.exe") for path in approved):
            raise RuntimeError("Unexpected approved background process")
        if ([item["name"] for item in measurements] != [name for name, _ in NATIVE_COMMANDS]
                or any(item["exit_code"] or not item["compiled_artifacts"] for item in measurements)):
            raise RuntimeError("Incomplete or failed native command block")
        for item, (_, args) in zip(measurements, NATIVE_COMMANDS):
            if (item["command"] != ["cargo", *args, "--frozen", "--timings", "--message-format=json"]
                    or item["target_directory"] != target or len(set(item["affinity"])) != protocol["cores"]
                    or any(not math.isfinite(item[key]) or item[key] <= 0 for key in ("wall_seconds", "cpu_seconds"))
                    or abs(item["cpu_seconds"] - item["user_seconds"] - item["kernel_seconds"]) > 1e-6
                    or item["cpu_seconds"] > item["wall_seconds"] * protocol["cores"] * 1.05
                    or any(process["image"].replace("\\", "/").lower() not in approved
                           for process in item.get("background_processes_at_completion", []))):
                raise RuntimeError("Invalid native command, target, affinity or CPU accounting")
        checks = NATIVE_COMMANDS[1:] if row["round"] == 0 else []
        if len(result["correctness"]) != len(checks):
            raise RuntimeError("Missing successful original correctness tests")
        for check, (name, args) in zip(result["correctness"], checks):
            if (check["name"] != name or check["exit_code"]
                    or check["command"] != ["cargo", *(arg for arg in args if arg != "--no-run"), "--frozen"]
                    or check["environment_overrides"] != index["correctness_environment"]):
                raise RuntimeError("Changed or failed correctness tests")
        if row["round"] >= protocol["warmup_rounds"]:
            totals[row["variant"]][row["round"]] = {
                key: sum(item[key] for item in measurements) for key in ("wall_seconds", "cpu_seconds")}
    means = {variant: {key: sum(row[key] for row in values.values()) / protocol["measured_rounds"]
                       for key in ("wall_seconds", "cpu_seconds")} for variant, values in totals.items()}
    paired = []
    for round_index in sorted(totals["official"]):
        left, right = totals["official"][round_index], totals["repaired"][round_index]
        paired.append({"round": round_index, "seconds_saved": left["wall_seconds"] - right["wall_seconds"],
                       "wall_reduction_percent": 100 * (1 - right["wall_seconds"] / left["wall_seconds"])})
    return {"scope": protocol["scope"], "means": means, "paired_rounds": paired,
            "wall_reduction_percent": 100 * (1 - means["repaired"]["wall_seconds"] / means["official"]["wall_seconds"]),
            "seconds_saved": means["official"]["wall_seconds"] - means["repaired"]["wall_seconds"],
            "uncertainty": "Three rounds on one machine; paired-round variation, not a multi-VM confidence interval"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--correctness-temp", type=Path, required=True)
    args = parser.parse_args()
    root, correctness = args.root.resolve(), args.correctness_temp.resolve()
    output, source = root / "e", root / "s"
    protocol = json.loads(PROTOCOL.read_text())
    if (os.name != "nt" or os.cpu_count() != protocol["build_cores"]
            or os.environ.get("RUNNER_NAME") != protocol["runner"]
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted"
            or root.drive != protocol["build_drive"]):
        raise RuntimeError("Expected the qualified ReFS x64 replay host")
    if subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip() != protocol["source_sha"]:
        raise RuntimeError("Wrong pinned IronRDP workload")
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    output.mkdir()
    official, cargo = install_official(output, protocol)
    compilers, metadata, artifacts, standard = {}, {}, {}, None
    for variant in protocol["variants"]:
        metadata[variant], compilers[variant], artifacts[variant] = checked_compiler(root, output, variant, protocol)
        libraries = share_native_libraries(official, compilers[variant], protocol["host"])
        if standard is not None and standard != libraries:
            raise RuntimeError("Official shared libraries changed")
        standard = libraries
    verify_pair(metadata["official"], metadata["repaired"])
    versions = {}
    for variant, compiler in compilers.items():
        versions[variant] = subprocess.check_output([compiler, "-vV"], text=True)
        if any(value not in versions[variant] for value in (
                f"release: {protocol['rust_version']}\n", f"host: {protocol['host']}\n", protocol["rust_sha"])):
            raise RuntimeError("Wrong compiler binary version")
        artifacts[variant]["rustc_sha256"] = digest(compiler)
        artifacts[variant]["driver_sha256"] = {
            path.name: digest(path) for path in compiler.parent.glob("rustc_driver-*.dll")}
        if not artifacts[variant]["driver_sha256"]:
            raise RuntimeError("Missing compiler driver")
    os.environ["PATH"] = str(cargo.parent) + os.pathsep + str(official.parent) + os.pathsep + os.environ["PATH"]
    os.environ["RUSTDOC"] = str(official.parent / "rustdoc.exe")
    subprocess.run([cargo, "fetch", "--locked", "--target", protocol["host"]], cwd=source,
                   env={**os.environ, "RUSTC": str(official)}, check=True)
    validate_meter(output / "meter-validation")
    index = {"complete": False, "protocol": protocol, "compiler_metadata": metadata,
             "artifact_evidence": artifacts, "stdlib": standard, "cargo_sha256": digest(cargo),
             "run_id": os.environ["GITHUB_RUN_ID"], "attempt": os.environ["GITHUB_RUN_ATTEMPT"], "runs": [],
             "versions": versions, "correctness_environment": {"TEMP": str(correctness), "TMP": str(correctness)}}
    save(output / "index.json", index)
    for round_index in range(protocol["warmup_rounds"] + protocol["measured_rounds"]):
        for position, variant in enumerate(paired_order(protocol["variants"], 1, round_index)):
            name = f"round-{round_index}-{variant}"
            print(f"BEGIN {name}, position {position}", flush=True)
            run_block(source, output / name, compilers[variant], protocol,
                      {"variant": variant, "round": round_index}, round_index == 0,
                      correctness_env={"TEMP": str(correctness), "TMP": str(correctness)}, native_only=True)
            index["runs"].append({"variant": variant, "round": round_index, "position": position,
                                  "path": f"{name}/results.json"})
            save(output / "index.json", index)
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    summary = summarize(output, index)
    save(output / "summary.json", summary)
    index["complete"] = True
    save(output / "index.json", index)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
