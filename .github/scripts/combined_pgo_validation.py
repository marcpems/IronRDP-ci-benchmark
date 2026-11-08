"""Isolated validation of the reviewed PGO and cache patches, not an upstream contribution."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import time
import tomllib

from build_arm_compilers import digest, save
from hosted_x64_baseline import timer_sections
from msvc_experiment import cmake_toolchain, coverage, environment, execute, tool_identity
from x64_pgo_release import (
    HOST, check_distribution, configuration, preserve_literal_release_batch, telemetry,
)
from x64_profile_only import audit_native_cache

INPUTS = Path(__file__).resolve().parents[2] / "ci-benchmark/combined-pgo"


def protocol():
    return json.loads((INPUTS / "protocol.json").read_text())


def source_diff(source):
    return subprocess.check_output(
        ["git", "-C", source, "diff", "--binary", "--ignore-submodules=dirty", "HEAD"],
    )


def prepare(source, variant):
    plan = protocol()
    if variant not in plan["variants"]:
        raise ValueError(f"Unknown variant: {variant}")
    actual = subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip()
    if actual != plan["base_sha"] or source_diff(source):
        raise RuntimeError("Expected the clean pinned upstream source")
    patch = INPUTS / "reviewed.patch"
    if digest(patch) != plan["patch_sha256"]:
        raise RuntimeError("Reviewed patch checksum mismatch")
    if variant == "candidate":
        subprocess.run(["git", "-C", source, "apply", "--check", patch], check=True)
        subprocess.run(["git", "-C", source, "apply", patch], check=True)
        subprocess.run(
            ["git", "-C", source, "add", "-N", "src/tools/opt-dist/src/exec/tests.rs"], check=True,
        )
        if source_diff(source) != patch.read_bytes():
            raise RuntimeError("Applied candidate differs from the reviewed patch")
    return source_diff(source)


def verify_sections(sections):
    required = {
        "Stage 1 (Rustc + rustdoc + cargo + clippy PGO)",
        "Stage 2 (LLVM PGO)", "Stage 5 (final build)", "Run tests",
    }
    if sections["unfinished"] or any(row["status"] != "OK" for row in sections["completed"]):
        raise RuntimeError("Pipeline contains failed or unfinished sections")
    if not required <= {row["name"] for row in sections["completed"]}:
        raise RuntimeError("Missing complete production or qualification sections")


def cache_command(cache, output, arguments):
    output.mkdir()

    def snapshot(label):
        text = subprocess.check_output([cache, "--show-stats"], text=True, timeout=30)
        (output / f"{label}.txt").write_text(text, encoding="utf-8")

    subprocess.run([cache, "--start-server"], check=True, timeout=30)
    try:
        snapshot("start")
        subprocess.run([cache, "--zero-stats"], check=True, timeout=30)
        with subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, encoding="utf-8", errors="replace", bufsize=1) as child:
            def forward(stream, target, collect):
                index = 0
                for line in stream:
                    target.write(line)
                    target.flush()
                    if collect and "opt_dist::timer" in line and "Section `" in line:
                        snapshot(f"phase-{index:03}")
                        (output / f"phase-{index:03}.label").write_text(line, encoding="utf-8")
                        index += 1

            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [
                    pool.submit(forward, child.stdout, sys.stdout, False),
                    pool.submit(forward, child.stderr, sys.stderr, True),
                ]
                for future in futures:
                    future.result()
            status = child.wait()
        snapshot("final")
        if status:
            raise subprocess.CalledProcessError(status, arguments)
    finally:
        subprocess.run([cache, "--stop-server"], check=True, timeout=60)
        with socket.socket() as check:
            check.settimeout(2)
            if check.connect_ex(("127.0.0.1", int(os.environ["SCCACHE_SERVER_PORT"]))) == 0:
                raise RuntimeError("Experiment cache server did not stop")


def run_release(root, scratch, variant):
    plan = protocol()
    source, output = root / "r", root / "e"
    if (os.name != "nt" or os.cpu_count() != 16
            or os.environ.get("RUNNER_NAME") != "MARCPE-TEST01-X64"):
        raise RuntimeError("Expected the dedicated 16-LP Windows runner")
    owner = f'{os.environ["GITHUB_RUN_ID"]}/{os.environ["GITHUB_RUN_ATTEMPT"]}/{variant}'
    if (root / "owner-run.txt").read_text().strip() != owner:
        raise RuntimeError("Build-directory ownership mismatch")
    if source.drive.upper() != "D:" or scratch.drive.upper() != "C:":
        raise RuntimeError("Expected D: build and C: correctness scratch")
    if shutil.disk_usage(root).free < 250 * 2**30:
        raise RuntimeError("Insufficient free build capacity")
    if (source / "build").exists() or (source / "bootstrap.toml").exists():
        raise RuntimeError("Expected fresh build objects and configuration")
    for subdir, revision in (
        ("src/llvm-project", plan["llvm_sha"]), ("src/tools/rustc-perf", plan["perf_sha"]),
    ):
        actual = subprocess.check_output(
            ["git", "-C", source / subdir, "rev-parse", "HEAD"], text=True,
        ).strip()
        if actual != revision:
            raise RuntimeError(f"Unexpected submodule: {subdir}")
    save(output / "llvm-checkout.json", preserve_literal_release_batch(source / "src/llvm-project"))
    expected_diff = prepare(source, variant)
    (output / "tested-source.patch").write_bytes(expected_diff)
    clang, cache = source / "citools/clang-rust/bin", root / "tools/sccache.exe"
    if digest(cache) != plan["sccache_sha256"]:
        raise RuntimeError("Unexpected sccache binary")
    clang_version = subprocess.check_output([clang / "clang-cl.exe", "--version"], text=True)
    if f"clang version {plan['clang_version']} " not in clang_version:
        raise RuntimeError("Unexpected Clang version")
    tools = tool_identity(clang)
    env = environment(output, clang)
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    cache_config = output / "sccache.toml"
    cache_config.write_text("[cache.disk]\nsize = 53687091200\n", encoding="utf-8")
    env.update({
        "WIX": str(source / "wix"), "PGO_HOST": HOST,
        "DIST_REQUIRE_ALL_TOOLS": "1", "DIST_TRY_BUILD": "0",
        "COMPILETEST_REQUIRE_ALL_LLVM_COMPONENTS": "1", "MATCHED_BUILD_CORES": "16",
        "TEMP": str(scratch), "TMP": str(scratch),
        "CMAKE_TOOLCHAIN_FILE": str(cmake_toolchain(output, tools)),
        "SCCACHE_SERVER_PORT": str(port), "SCCACHE_DIR": str(root / "cache"),
        "SCCACHE_CONF": str(cache_config), "SCCACHE_IDLE_TIMEOUT": "0",
        "SCCACHE_C_CUSTOM_CACHE_BUSTER": "1", "SCCACHE_CACHE_SIZE": "50G",
    })
    config = configuration(clang, "upstream").replace('channel = "stable"', 'channel = "nightly"')
    config = config.replace("[build]\n", f'[build]\nccache = "{cache.as_posix()}"\n', 1)
    (source / "bootstrap.toml").write_text(config, encoding="utf-8")
    (output / "production-bootstrap.toml").write_text(config, encoding="utf-8")
    provenance = {
        "complete": False, "variant": variant, "protocol": plan, "tools": tools,
        "base_sha": plan["base_sha"], "patch_sha256": digest(INPUTS / "reviewed.patch"),
        "applied_patch_sha256": digest(output / "tested-source.patch"),
        "run_id": os.environ["GITHUB_RUN_ID"], "attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "harness_sha": os.environ["GITHUB_SHA"], "configuration": config,
        "clang_version": clang_version, "sccache_sha256": digest(cache),
        "clang_installer_sha256": digest(source / "citools/clang.exe"),
        "wix_archive_sha256": digest(source / "citools/wix.zip"),
        "runner": os.environ["RUNNER_NAME"], "job_started_unix": float(os.environ["VALIDATION_STARTED"]),
    }
    save(output / "provenance.json", provenance)
    deadline = provenance["job_started_unix"] + 340 * 60

    def measured(arguments, name, cwd=source):
        remaining = deadline - time.time()
        if remaining <= 0:
            raise TimeoutError("Reached production evidence-preservation deadline")
        save(output / "active-stage.json", {"stage": name, "unix": time.time()})
        command = [
            sys.executable, Path(__file__).resolve(), "cache-command",
            "--cache", cache, "--output", output / f"{name}-cache", "--", *arguments,
        ]
        return execute(command, cwd, env, output, name, timeout=remaining, cores=16)

    x = [sys.executable, "x.py"]
    started = time.monotonic()
    measured(x + ["build", "--set", "rust.debug=true", "opt-dist"], "build-opt-dist")
    fixture = source / "src/tools/rustc-perf/collector/compile-benchmarks/token-stream-stress"
    lockfile = fixture / "Cargo.lock"
    before = tomllib.loads(lockfile.read_text())
    if before.get("version", 1) < 3:
        old_hash = digest(lockfile)
        measured(
            [source / "build" / HOST / "stage0/bin/cargo.exe", "generate-lockfile", "--offline"],
            "training-lockfile", fixture,
        )
        if tomllib.loads(lockfile.read_text())["package"] != before["package"]:
            raise RuntimeError("Training lockfile migration changed dependency graph")
        save(output / "training-lockfile.json", {
            "before": old_hash, "after": digest(lockfile), "package_graph_unchanged": True,
        })
    perf = source / "src/tools/rustc-perf"
    perf_diff = source_diff(perf)
    (output / "training-fixture.patch").write_bytes(perf_diff)
    helper = source / "build" / HOST / "stage1-tools-bin/opt-dist.exe"
    measured([helper, "windows-ci", "--", *x, "dist", "bootstrap", "--include-default-paths"],
             "full-release")
    sections = timer_sections(output / "full-release.stderr")
    save(output / "pipeline-sections.json", sections)
    verify_sections(sections)
    profiles = {}
    for name in ("rustc", "rustdoc", "clippy", "cranelift", "llvm"):
        path = source / "opt-artifacts" / f"{name}-pgo.profdata"
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Missing trained profile: {name}")
        profiles[name] = {"sha256": digest(path), "bytes": path.stat().st_size}
        shutil.copy2(path, output / path.name)
    reader = source / "build" / HOST / "llvm/bin/llvm-profdata.exe"
    counts = None
    if variant == "candidate":
        counts = coverage(reader, output / "llvm-pgo.profdata",
                          ("X86TargetLowering", "InstCombine"), env, output)
    audit_native_cache(source, output, {"llvm": output / "llvm-pgo.profdata"}, tools)
    cache_text = (output / "llvm-CMakeCache.txt").read_text()
    if not re.search(r"^CMAKE_CXX_COMPILER_LAUNCHER:[^=]+=" + re.escape(cache.as_posix())
                     + r"\s*$", cache_text.replace("\\", "/"), re.M):
        raise RuntimeError("Final LLVM did not use the isolated cache launcher")
    if source_diff(source) != expected_diff or source_diff(perf) != perf_diff:
        raise RuntimeError("Compiler or workload source changed during validation")
    subprocess.run(
        ["git", "-C", source / "src/llvm-project", "diff", "--exit-code", "HEAD"], check=True,
    )
    files = sorted(path for path in (source / "build/dist").iterdir() if path.is_file())
    check_distribution(files, version="nightly")
    save(output / "dist-manifest.json", [
        {"name": path.name, "bytes": path.stat().st_size, "sha256": digest(path)} for path in files
    ])
    shutil.copy2(source / "build/metrics.json", output / "metrics.json")
    save(output / "result.json", {
        **provenance, "complete": True, "production_and_tests_seconds": time.monotonic() - started,
        "profiles": profiles, "llvm_training_coverage": counts,
        "qualification": "Unmodified upstream extracted-distribution tests passed",
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    build = commands.add_parser("release")
    build.add_argument("--root", type=Path, required=True)
    build.add_argument("--scratch", type=Path, required=True)
    build.add_argument("--variant", choices=("control", "candidate"), required=True)
    apply = commands.add_parser("prepare")
    apply.add_argument("--source", type=Path, required=True)
    apply.add_argument("--variant", choices=("control", "candidate"), required=True)
    wrapper = commands.add_parser("cache-command")
    wrapper.add_argument("--cache", type=Path, required=True)
    wrapper.add_argument("--output", type=Path, required=True)
    wrapper.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare(args.source.resolve(), args.variant)
    elif args.mode == "cache-command":
        cache_command(args.cache.resolve(), args.output.resolve(), args.arguments[1:])
    else:
        output = args.root / "e"
        try:
            with telemetry(output, build_drive="D:"):
                run_release(args.root.resolve(), args.scratch.resolve(), args.variant)
        except Exception as error:
            save(output / "failure.json", {"complete": False, "error": str(error), "unix": time.time()})
            if (output / "result.json").exists():
                result = json.loads((output / "result.json").read_text())
                save(output / "result.json", {**result, "complete": False, "rejection": str(error)})
            raise


if __name__ == "__main__":
    main()
