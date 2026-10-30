"""Validate PR 164707 with fresh training, a full distribution, and upstream tests."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import tomllib

from build_arm_compilers import digest, save
from hosted_x64_baseline import timer_sections
from msvc_experiment import cmake_toolchain, coverage, environment, execute, tool_identity
from x64_pgo_release import (
    CORES, HOST, check_distribution, configuration, preserve_literal_release_batch, telemetry,
)
from x64_profile_only import audit_native_cache
from x64_runner_diagnostic import topology

RUST_SHA = "4da678aada4683607acbd67a8da37a320c791f93"
LLVM_SHA = "aab11ee0ea5ea9a1d462ad0bc1fae9d9bb643019"
PERF_SHA = "208d929efe770996eb02cd3d2712623ea48b7646"
FIXED_HELPER_BLOB = "6aa5fc0bf36a9de34e4ae88ec7da4aef333273f6"
TEST_MODULE_BLOB = "e0e2c487db4c5445f033409de4e774b41c22a26e"
CLANG_SHA256 = "0a18ea761147a7de69d6dd60ef81b70496e5255aec6caff22d45da85188614af"


def release_configuration(clang, workers):
    if workers not in (4, 8, 16):
        raise ValueError("Expected 4, 8, or 16 logical processors")
    config = configuration(clang, "upstream").replace('channel = "stable"', 'channel = "nightly"')
    if config.count(f"\njobs = {CORES}\n") != 1:
        raise RuntimeError("Cannot identify the release worker setting")
    return config.replace(f"\njobs = {CORES}\n", f"\njobs = {workers}\n")


def comparison_identity(config, tools, wix_hash, hardware):
    normalized = tomllib.loads(config)
    normalized["build"]["jobs"] = "allocation"
    normalized["llvm"]["clang-cl"] = "<isolated-clang-cl>"
    return {
        "rust_sha": RUST_SHA, "llvm_sha": LLVM_SHA, "rustc_perf_sha": PERF_SHA,
        "fixed_helper_blob": FIXED_HELPER_BLOB, "configuration": normalized,
        "native_tool_sha256": {name: row["sha256"] for name, row in tools["files"].items()},
        "msvc": tools["msvc"], "sdk": tools["sdk"], "wix_sha256": wix_hash,
        "clang_installer_sha256": CLANG_SHA256, "hardware": hardware,
    }


def verify_reference(reference, identity, run_id):
    if (reference.get("complete") is not True or reference.get("build_workers") != 16
            or reference.get("run_id") != run_id or reference.get("attempt") != os.environ["GITHUB_RUN_ATTEMPT"]
            or reference.get("comparison_identity") != identity):
        raise RuntimeError("Scaling reference changed source, tools, recipe, hardware, or run")


def verify_no_compiler_cache(output):
    findings = {}
    for component in ("llvm", "lld"):
        text = (output / f"{component}-CMakeCache.txt").read_text()
        values = {}
        for line in text.splitlines():
            if line and not line.startswith(("#", "//")) and ":" in line and "=" in line:
                key, value = line.split("=", 1)
                values[key.split(":", 1)[0]] = value
        launchers = {key: values.get(key, "") for key in (
            "CMAKE_C_COMPILER_LAUNCHER", "CMAKE_CXX_COMPILER_LAUNCHER", "RULE_LAUNCH_COMPILE",
        )}
        if any(launchers.values()):
            raise RuntimeError(f"Unexpected {component} compiler-cache launcher: {launchers}")
        findings[component] = launchers
    return {"compiler_cache": "not enabled", "hit_rate": None, "native_launchers": findings,
            "note": "Fresh initial objects; normal within-pipeline bootstrap reuse remains."}


def verify_sections(sections):
    required = {
        "Stage 1 (Rustc + rustdoc + cargo + clippy PGO)",
        "Stage 2 (LLVM PGO)",
        "Stage 5 (final build)",
        "Run tests",
    }
    successful = {row["name"] for row in sections["completed"] if row["status"] == "OK"}
    if sections["unfinished"] or any(row["status"] != "OK" for row in sections["completed"]):
        raise RuntimeError("Optimization pipeline contains unfinished or failed sections")
    if not required <= successful:
        raise RuntimeError(f"Missing successful pipeline sections: {sorted(required - successful)}")


def verify_patch(source):
    changes = subprocess.check_output(
        ["git", "-C", source, "diff", "--numstat", "--ignore-submodules=dirty", "HEAD"], text=True,
    ).strip()
    if changes != "1\t0\tsrc/bootstrap/src/utils/helpers.rs":
        raise RuntimeError(f"Unexpected Rust source changes: {changes}")
    for relative, expected in (
        ("src/bootstrap/src/utils/helpers.rs", FIXED_HELPER_BLOB),
        ("src/tools/opt-dist/src/tests.rs", TEST_MODULE_BLOB),
    ):
        actual = subprocess.check_output(
            ["git", "-C", source, "hash-object", relative], text=True,
        ).strip()
        if actual != expected:
            raise RuntimeError(f"Source does not match the locally tested input: {relative}")


def run(root, correctness_temp, workers=CORES, reference=None, scaling=False):
    source, output = root / "r", root / "e"
    if (os.name != "nt" or os.cpu_count() != CORES
            or os.environ.get("RUNNER_NAME") != "MARCPE-TEST01-X64"
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted"):
        raise RuntimeError("Expected the dedicated 16-LP Windows x64 runner")
    owner = f'{os.environ["GITHUB_RUN_ID"]}/{os.environ["GITHUB_RUN_ATTEMPT"]}'
    if (root / "owner-run.txt").read_text().strip() != owner:
        raise RuntimeError("Run directory ownership mismatch")
    if source.drive.upper() != "D:" or len(str(source)) > 24:
        raise RuntimeError("Expected the reserved short ReFS build path")
    if correctness_temp.drive.upper() != "C:" or not correctness_temp.is_dir():
        raise RuntimeError("Expected the reserved NTFS correctness scratch directory")
    if shutil.disk_usage(root).free < 250 * 2**30:
        raise RuntimeError("Fresh release validation requires 250 GiB free")
    if (source / "build").exists() or (source / "bootstrap.toml").exists():
        raise RuntimeError("Release validation requires fresh compiler objects and configuration")
    for path, revision in (
        (source, RUST_SHA), (source / "src/llvm-project", LLVM_SHA),
        (source / "src/tools/rustc-perf", PERF_SHA),
    ):
        actual = subprocess.check_output(["git", "-C", path, "rev-parse", "HEAD"], text=True).strip()
        if actual != revision:
            raise RuntimeError(f"Unexpected source revision: {path}")
    save(output / "checkout-validation.json", preserve_literal_release_batch(source / "src/llvm-project"))
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    patch = Path(__file__).resolve().parents[2] / "ci-benchmark/bootstrap-clang-runtime.patch"
    for arguments in (["--check"], []):
        subprocess.run(
            ["git", "-C", source, "apply", *arguments, "--ignore-space-change", patch], check=True,
        )
    verify_patch(source)
    (output / "tested-source.patch").write_bytes(
        subprocess.check_output(["git", "-C", source, "diff", "--binary", "HEAD"])
    )
    clang = source / "citools/clang-rust/bin"
    if digest(source / "citools/LLVM-20.1.3-win64.exe") != CLANG_SHA256:
        raise RuntimeError("CI Clang installer checksum mismatch")
    tools = tool_identity(clang)
    readiness = json.loads((output / "readiness.json").read_bytes())
    masks = topology()
    hardware = {
        "runner": os.environ["RUNNER_NAME"], "cpu": readiness["CPU"],
        "memory_bytes": readiness["PhysicalMemoryBytes"], "os": readiness["OS"],
        "power_scheme": readiness["PowerScheme"], "physical_core_masks": masks,
        "build_disk": [row for row in readiness["DiskMapping"] if row["Drive"] == "D:"],
    }
    if len(masks) != 8 or sorted(bit for mask in masks for bit in mask) != list(range(16)):
        raise RuntimeError("Expected eight physical cores and sixteen logical processors")
    config = release_configuration(clang, workers)
    wix_hash = digest(source / "citools/wix311-binaries.zip")
    identity = comparison_identity(config, tools, wix_hash, hardware)
    if scaling and workers != 16 and reference is None:
        raise RuntimeError("Lower-worker scaling builds require the qualified 16-LP reference")
    if reference is not None:
        verify_reference(json.loads((reference / "result.json").read_bytes()), identity, os.environ["GITHUB_RUN_ID"])
    save(output / "topology.json", {"physical_core_masks": masks, "selected_logical_processors": list(range(workers)),
                                  "selected_physical_cores": sum(any(bit < workers for bit in mask) for mask in masks)})
    env = environment(output, clang)
    env.update({
        "WIX": str(source / "wix"), "PGO_HOST": HOST,
        "DIST_REQUIRE_ALL_TOOLS": "1", "DIST_TRY_BUILD": "0",
        "COMPILETEST_REQUIRE_ALL_LLVM_COMPONENTS": "1", "MATCHED_BUILD_CORES": str(workers),
        "TEMP": str(correctness_temp), "TMP": str(correctness_temp),
        "CMAKE_TOOLCHAIN_FILE": str(cmake_toolchain(output, tools)),
    })
    (source / "bootstrap.toml").write_text(config, encoding="utf-8")
    (output / "production-bootstrap.toml").write_text(config, encoding="utf-8")
    provenance = {
        "complete": False, "rust_sha": RUST_SHA, "llvm_sha": LLVM_SHA, "rustc_perf_sha": PERF_SHA,
        "fixed_helper_git_blob": FIXED_HELPER_BLOB, "test_module_git_blob": TEST_MODULE_BLOB,
        "patch_sha256": digest(patch), "configuration": config, "tools": tools,
        "clang_installer_sha256": CLANG_SHA256,
        "wix_archive_sha256": wix_hash,
        "runner": os.environ["RUNNER_NAME"], "logical_processors": CORES,
        "build_workers": workers, "comparison_identity": identity,
        "run_id": os.environ["GITHUB_RUN_ID"], "attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "scope": ("Single-pass 16/8/4-LP fresh full release scaling; same Microsoft tools, no added LTO or compiler cache"
                  if scaling else "Current PR plus exact local prerequisite; full fresh windows-ci pipeline, not a timing comparison"),
    }
    save(output / "provenance.json", provenance)
    deadline = time.monotonic() + 23 * 3600

    def measured(arguments, cwd, name):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Release validation reached its evidence-preservation deadline")
        save(output / "active-stage.json", {"stage": name, "unix": time.time()})
        result = execute(arguments, cwd, env, output, name, timeout=remaining, cores=workers)
        if result["affinity"] != list(range(workers)):
            raise RuntimeError("Measured process affinity does not match the selected allocation")
        return result

    x = [sys.executable, "x.py"]
    started = time.monotonic()
    measured(x + ["build", "--set", "rust.debug=true", "opt-dist"], source, "build-opt-dist")
    fixture = source / "src/tools/rustc-perf/collector/compile-benchmarks/token-stream-stress"
    lockfile = fixture / "Cargo.lock"
    before = tomllib.loads(lockfile.read_text())
    if before.get("version", 1) < 3:
        original_hash = digest(lockfile)
        measured(
            [source / "build" / HOST / "stage0/bin/cargo.exe", "generate-lockfile", "--offline"],
            fixture, "training-lockfile",
        )
        if tomllib.loads(lockfile.read_text())["package"] != before["package"]:
            raise RuntimeError("Training lockfile migration changed dependencies")
        save(output / "training-lockfile-migration.json", {
            "before_sha256": original_hash, "after_sha256": digest(lockfile),
            "package_graph_unchanged": True,
        })
    perf = source / "src/tools/rustc-perf"
    perf_diff = subprocess.check_output(["git", "-C", perf, "diff", "--binary", "HEAD"])
    (output / "training-fixture.patch").write_bytes(perf_diff)
    helper = source / "build" / HOST / "stage1-tools-bin/opt-dist.exe"
    measured(
        [helper, "windows-ci", "--", *x, "dist", "bootstrap", "--include-default-paths"],
        source, "full-release",
    )
    duration = time.monotonic() - started
    sections = timer_sections(output / "full-release.stderr")
    save(output / "pipeline-sections.json", sections)
    verify_sections(sections)
    profiles = {}
    for name in ("rustc", "rustdoc", "clippy", "cranelift", "llvm"):
        path = source / "opt-artifacts" / f"{name}-pgo.profdata"
        if not path.is_file() or not path.stat().st_size:
            raise RuntimeError(f"Missing freshly trained profile: {name}")
        profiles[name] = {"sha256": digest(path), "bytes": path.stat().st_size}
        shutil.copy2(path, output / path.name)
    reader = source / "build" / HOST / "llvm/bin/llvm-profdata.exe"
    counts = coverage(
        reader, output / "llvm-pgo.profdata", ("X86TargetLowering", "InstCombine"), env, output,
    )
    audit_native_cache(source, output, {"llvm": output / "llvm-pgo.profdata"}, tools)
    cache_status = verify_no_compiler_cache(output)
    save(output / "compiler-cache-status.json", cache_status)
    verify_patch(source)
    if subprocess.check_output(["git", "-C", perf, "diff", "--binary", "HEAD"]) != perf_diff:
        raise RuntimeError("The original rustc-perf inputs changed during the optimization pipeline")
    subprocess.run(
        ["git", "-C", source / "src/llvm-project", "diff", "--exit-code", "HEAD"], check=True,
    )
    files = sorted(path for path in (source / "build/dist").iterdir() if path.is_file())
    check_distribution(files, version="nightly")
    save(output / "dist-manifest.json", [
        {"name": path.name, "bytes": path.stat().st_size, "sha256": digest(path)} for path in files
    ])
    shutil.copy2(source / "build/metrics.json", output / "metrics.json")
    test_seconds = next(row["wall_seconds"] for row in sections["completed"] if row["name"] == "Run tests")
    save(output / "result.json", {
        **provenance, "complete": True, "production_and_tests_seconds": duration,
        "production_seconds": duration - test_seconds, "qualification_seconds": test_seconds,
        "compiler_cache_status": cache_status,
        "profiles": profiles, "llvm_training_coverage": counts,
        "profile_reader_sha256": digest(reader),
        "qualification": "Unmodified upstream extracted-distribution tests passed in the full pipeline",
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--correctness-temp", type=Path, required=True)
    parser.add_argument("--workers", type=int, choices=(4, 8, 16), default=16)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--scaling", action="store_true")
    args = parser.parse_args()
    output = args.root / "e"
    try:
        with telemetry(output, build_drive="D:"):
            run(args.root.resolve(), args.correctness_temp.resolve(), args.workers, args.reference, args.scaling)
    except Exception as error:
        save(output / "failure.json", {"complete": False, "error": str(error), "unix": time.time()})
        if (output / "result.json").exists():
            result = json.loads((output / "result.json").read_text())
            save(output / "result.json", {**result, "complete": False, "rejection": str(error)})
        raise
