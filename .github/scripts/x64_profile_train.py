"""Generate a repaired LLVM profile, then freeze inputs for a fresh matched pair."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time
import tomllib

from build_arm_compilers import digest, save
from hosted_x64_baseline import timer_sections
from msvc_experiment import cmake_toolchain, coverage, environment, execute, tool_identity
from x64_pgo_release import HOST, configuration, preserve_literal_release_batch, telemetry


def stop_after_training(source):
    main = source / "src/tools/opt-dist/src/main.rs"
    text = main.read_text(encoding="utf-8")
    marker = "    let bolt_profiles = if env.use_bolt() {"
    if text.count(marker) != 1 or "X64_PROFILE_TRAIN_ONLY" in text:
        raise RuntimeError("Pinned training boundary changed")
    text = text.replace(marker, '''    if std::env::var_os("X64_PROFILE_TRAIN_ONLY").as_deref()
        == Some(std::ffi::OsStr::new("1"))
    {
        return Ok(());
    }

''' + marker)
    main.write_text(text, encoding="utf-8")
    return digest(main)


def train(root, protocol_path):
    protocol = json.loads(protocol_path.read_text())
    source, output = root / "r", root / "e/train"
    if (os.name != "nt" or os.cpu_count() != protocol["build_cores"]
            or os.environ.get("RUNNER_NAME") != protocol["runner"]
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted"
            or source.drive != protocol["build_drive"] or len(str(source)) > 24):
        raise RuntimeError("Wrong training runner or source path")
    if shutil.disk_usage(root).free < 250 * 2**30:
        raise RuntimeError("Fresh training requires 250 GiB free")
    if (source / "build").exists() or (source / "bootstrap.toml").exists():
        raise RuntimeError("Training requires fresh source/build objects")
    for directory, revision in (
            (source, protocol["rust_sha"]), (source / "src/llvm-project", protocol["llvm_sha"]),
            (source / "src/tools/rustc-perf", protocol["rustc_perf_sha"])):
        if subprocess.check_output(["git", "-C", directory, "rev-parse", "HEAD"], text=True).strip() != revision:
            raise RuntimeError(f"Wrong pinned training input: {directory}")
    save(output / "checkout-validation.json", preserve_literal_release_batch(source / "src/llvm-project"))
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    clang = source / "citools/clang-rust/bin"
    if digest(source / "citools/LLVM-20.1.3-win64.exe") != protocol["clang_installer_sha256"]:
        raise RuntimeError("Wrong pinned upstream native compiler")
    tools = tool_identity(clang)
    env = environment(output, clang)
    env.update({"PGO_HOST": HOST, "WIX": str(source / "wix"), "DIST_TRY_BUILD": "0",
                "X64_PROFILE_TRAIN_ONLY": "1", "MATCHED_BUILD_CORES": str(protocol["build_cores"])})
    patches = Path(__file__).resolve().parents[2] / "ci-benchmark"
    selected = ("bootstrap-clang-runtime.patch", "static-llvm-pgo.patch")
    for name in selected:
        subprocess.run(["git", "-C", source, "apply", "--check", "--ignore-space-change", patches / name], check=True)
        subprocess.run(["git", "-C", source, "apply", "--ignore-space-change", patches / name], check=True)
    config = configuration(clang, "upstream")
    (source / "bootstrap.toml").write_text(config, encoding="utf-8")
    (output / "training-bootstrap.toml").write_text(config, encoding="utf-8")
    provenance = {
        "complete": False, "protocol": protocol, "configuration": config, "tools": tools,
        "run_id": os.environ["GITHUB_RUN_ID"], "attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "patches": {name: digest(patches / name) for name in selected},
        "training_boundary_main_sha256": stop_after_training(source),
        "training_module_sha256": digest(source / "src/tools/opt-dist/src/training.rs"),
    }
    save(output / "provenance.json", provenance)
    env["CMAKE_TOOLCHAIN_FILE"] = str(cmake_toolchain(output, tools))
    started = time.monotonic()
    execute([sys.executable, "x.py", "build", "--set", "rust.debug=true", "opt-dist"],
            source, env, output, "build-training-helper", timeout=3600, cores=protocol["build_cores"])
    fixture = source / "src/tools/rustc-perf/collector/compile-benchmarks/token-stream-stress"
    lock = fixture / "Cargo.lock"
    before = tomllib.loads(lock.read_text())
    if before.get("version", 1) < 3:
        execute([source / "build" / HOST / "stage0/bin/cargo.exe", "generate-lockfile", "--offline"],
                fixture, env, output, "training-lockfile", timeout=120, cores=protocol["build_cores"])
        if tomllib.loads(lock.read_text())["package"] != before["package"]:
            raise RuntimeError("Training lockfile migration changed dependencies")
    execute([source / "build" / HOST / "stage1-tools-bin/opt-dist.exe", "windows-ci"],
            source, env, output, "train-profile", timeout=10 * 3600, cores=protocol["build_cores"])
    sections = timer_sections(output / "train-profile.stderr")
    successful = {row["name"] for row in sections["completed"] if row["status"] == "OK"}
    if not {"Stage 1 (Rustc + rustdoc PGO)", "Stage 2 (LLVM PGO)"} <= successful:
        raise RuntimeError("Training did not complete both upstream phases")
    save(output / "training-sections.json", sections)
    profiles = {}
    for name in ("rustc", "rustdoc", "llvm"):
        destination = output / f"{name}-pgo.profdata"
        shutil.copy2(source / "opt-artifacts" / destination.name, destination)
        profiles[name] = {"sha256": digest(destination), "bytes": destination.stat().st_size}
    tools_archive = root / "inputs/llvm-tools.tar.xz"
    if digest(tools_archive) != protocol["official_tools_sha256"]:
        raise RuntimeError("Wrong release profile reader archive")
    with tarfile.open(tools_archive, "r:xz") as archive:
        archive.extractall(root / "inputs/reader", filter="data")
    readers = list((root / "inputs/reader").rglob("llvm-profdata.exe"))
    if len(readers) != 1 or digest(readers[0]) != protocol["reader_sha256"]:
        raise RuntimeError("Wrong release profile reader")
    counts = coverage(readers[0], output / "llvm-pgo.profdata",
                      ("X86TargetLowering", "InstCombine"), env, output)
    if digest(source / "src/tools/opt-dist/src/training.rs") != provenance["training_module_sha256"]:
        raise RuntimeError("Upstream training implementation changed")
    frozen = json.loads(json.dumps(protocol))
    if frozen["llvm_profile_sha256"]["repaired"] is not None:
        raise RuntimeError("Template unexpectedly contains a previously trained profile")
    frozen["llvm_profile_sha256"]["repaired"] = profiles["llvm"]["sha256"]
    frozen["training_identity"] = {
        "run_id": provenance["run_id"], "attempt": provenance["attempt"],
        "provenance_sha256": digest(output / "provenance.json"),
    }
    save(output / "protocol.json", frozen)
    save(output / "result.json", {
        **provenance, "complete": True, "profiles": profiles, "llvm_coverage": counts,
        "training_seconds": time.monotonic() - started,
        "scope": "Standalone repaired training, not the incremental cost versus upstream training",
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    args = parser.parse_args()
    output = args.root / "e/train"
    try:
        with telemetry(output, build_drive="D:"):
            train(args.root.resolve(), args.protocol)
    except Exception as error:
        save(output / "failure.json", {"complete": False, "error": str(error)})
        raise
