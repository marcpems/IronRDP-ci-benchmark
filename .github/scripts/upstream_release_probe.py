"""Measure unmodified upstream Windows release recipes on standard hosted runners."""

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time
import tomllib

from build_arm_compilers import digest, save
from matched_release import check_manifest, qualify_distribution
from native_ci_probe import telemetry_executables
from process_metrics import measure, measurement_session
from release_phase_summary import summarize

RUST = "76c90957b7e422c4b9c45192b0197214d7de5a54"
SETTINGS = ("baseline", "jobs6", "link1")
BUILD_SCRIPT = (
    'export PATH="$(cygpath -u "$NATIVE_MSVC_BIN"):$PATH"; '
    "src/ci/scripts/run-build-from-ci.sh; build_status=$?; "
    "sccache --stop-server; stop_status=$?; "
    'if [ "$stop_status" -ne 0 ]; then echo "sccache shutdown failed" >&2; fi; '
    'if [ "$build_status" -ne 0 ]; then exit "$build_status"; fi; exit "$stop_status"'
)


def validate_config(config, host, setting):
    if config["dist"]["compression-profile"] != "balanced":
        raise RuntimeError("experiment changed upstream compression quality")
    if config["dist"]["compression-formats"] != ["xz"]:
        raise RuntimeError("experiment changed upstream compression formats")
    build = config["build"]
    expected_targets = [host] + (["arm64ec-pc-windows-msvc"] if host.startswith("aarch64") else [])
    if build["build"] != host or build["host"] != [host] or build["target"] != expected_targets:
        raise RuntimeError("experiment changed upstream native targets")
    if not build["extended"] or not build["profiler"]:
        raise RuntimeError("experiment omitted full tools or profiler support")
    if build.get("docs", True) is not True:
        raise RuntimeError("experiment disabled documentation")
    if config["rust"]["codegen-units-std"] != 1:
        raise RuntimeError("experiment changed standard-library codegen")
    if host.startswith("x86_64") and config["rust"]["codegen-units"] != 1:
        raise RuntimeError("experiment changed x64 compiler codegen")
    expected_backends = ["llvm", "cranelift"] if host.startswith("x86_64") else ["llvm"]
    if config["rust"]["codegen-backends"] != expected_backends:
        raise RuntimeError("experiment changed shipped codegen backends")
    if setting == "jobs6":
        if build.get("jobs") != 6:
            raise RuntimeError("missing six-job experimental setting")
    elif build.get("jobs", 0) != 0:
        raise RuntimeError("unexpected explicit build-job override")
    if setting == "link1":
        if config["llvm"].get("link-jobs") != 1:
            raise RuntimeError("missing single-link experimental setting")
    elif config["llvm"].get("link-jobs", 0) != 0:
        raise RuntimeError("unexpected explicit link-job override")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--host", choices=("x86_64-pc-windows-msvc", "aarch64-pc-windows-msvc"), required=True)
    parser.add_argument("--setting", choices=SETTINGS, required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    expected_machine = ("arm64", "aarch64") if args.host.startswith("aarch64") else ("amd64", "x86_64")
    if (os.name != "nt" or os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted"
            or os.cpu_count() != 4 or platform.machine().lower() not in expected_machine):
        raise RuntimeError("only standard native four-CPU GitHub-hosted Windows runners are permitted")
    if os.environ.get("DIST_TRY_BUILD") != "0" or os.environ.get("DIST_REQUIRE_ALL_TOOLS") != "1":
        raise RuntimeError("full production coverage is required; fast try builds are forbidden")
    revision = subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip()
    if revision != RUST:
        raise RuntimeError("wrong upstream source revision")
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    tools = {}
    for name in ("cl.exe", "link.exe", "lib.exe", "cmake.exe", "ninja.exe", "sccache.exe"):
        path = shutil.which(name)
        if path is None:
            raise RuntimeError(f"missing upstream build tool: {name}")
        tools[name] = {"path": path, "sha256": digest(Path(path))}
    clang = source / "citools" / "clang-rust" / "bin" / "clang-cl.exe"
    tools["clang-cl.exe"] = {"path": str(clang), "sha256": digest(clang)}
    env = dict(os.environ)
    for key in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
                "SCCACHE_BUCKET", "SCCACHE_ENDPOINT"):
        if env.get(key):
            raise RuntimeError("upstream private remote-cache credentials/settings must not be used")
    env["NATIVE_MSVC_BIN"] = str(Path(tools["link.exe"]["path"]).parent)
    started = float(os.environ["THROUGHPUT_JOB_STARTED"])
    provenance = {
        "rust_sha": RUST, "host": args.host, "setting": args.setting,
        "runner_class": "github-hosted", "runner_name": os.environ["RUNNER_NAME"],
        "image": os.environ.get("ImageVersion"), "cpu_allowance": 4,
        "run_id": os.environ["GITHUB_RUN_ID"], "attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "pilot": True, "tools": tools, "job_started_unix": started,
        "configure_args": env["RUST_CONFIGURE_ARGS"], "script": env["SCRIPT"],
        "source_changes": False, "compression": "upstream balanced xz",
        "coverage": "upstream production recipe; additional extracted-dist suite for Arm64",
        "cache": "fresh per-job local sccache; no upstream private remote cache or prior objects/profiles",
        "hardware_caveat": "standard x64 has 4 CPUs, upstream x64 release runner has 8 CPUs/32GB",
    }
    save(output / "provenance.json", provenance)
    try:
        remaining = started + 340 * 60 - time.time()
        if remaining <= 0:
            raise TimeoutError("no remaining hosted release experiment time")
        command = [
            r"C:\Program Files\Git\bin\bash.exe", "--noprofile", "--norc", "-c",
            BUILD_SCRIPT,
        ]
        save(output / "active-stage.json", {"stage": "upstream-ci-recipe", "unix": time.time()})
        with measurement_session([*telemetry_executables(), tools["sccache.exe"]["path"]]) as session:
            result = measure(command, source, env, 4, output / "upstream-ci",
                             session=session, timeout=remaining)
        save(output / "upstream-ci.json", result)
        if result["exit_code"]:
            print((output / "upstream-ci.stderr").read_text(errors="replace")[-10000:])
            print((output / "upstream-ci.stdout").read_text(errors="replace")[-10000:])
            raise RuntimeError(f"upstream release recipe failed: {result['exit_code']}")
        config = source / "bootstrap.toml"
        validate_config(tomllib.loads(config.read_text()), args.host, args.setting)
        shutil.copy2(config, output / "production-bootstrap.toml")
        files = [p for p in (source / "build" / "dist").iterdir() if p.is_file()]
        check_manifest(files, args.host)
        save(output / "dist-manifest.json", [
            {"name": p.name, "bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(files)])
        save(output / "upstream-recipe-completed.json", {"unix": time.time(), "complete": True})
        if args.host.startswith("aarch64"):
            os.environ["RELEASE_JOB_STARTED"] = str(started)
            qualify_distribution(source, output, args.host, env)
        subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
        metrics = source / "build" / "metrics.json"
        save(output / "phase-summary.json", summarize(json.loads(metrics.read_text())))
        save(output / "result.json", {
            **provenance, "complete": True, "completed_unix": time.time(),
            "upstream_recipe_seconds": result["wall_seconds"],
            "qualification": "full production recipe, required distribution artifacts and extracted-dist tests passed",
        })
    except Exception as error:
        save(output / "failure.json", {"complete": False, "error": str(error), "unix": time.time()})
        raise


if __name__ == "__main__":
    main()
