"""Fresh full-distribution x64 PGO comparison on the dedicated NVMe runner."""

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import tomllib

from build_arm_compilers import RUST_SHA, LLVM_SHA, PERF_SHA, digest, save
from hosted_x64_baseline import timer_sections
from msvc_experiment import environment, equivalent_tools, execute, tool_identity
from release_phase_summary import summarize

HOST = "x86_64-pc-windows-msvc"
VARIANTS = ("upstream", "local")
CORES = 16


def preserve_literal_release_batch(llvm):
    relative = "llvm/utils/release/build_llvm_release.bat"
    original = subprocess.check_output(["git", "-C", llvm, "show", f"HEAD:{relative}"])
    path = llvm / relative
    checkout = path.read_bytes()
    restored = checkout != original
    if restored:
        if checkout.replace(b"\r\n", b"\n") != original.replace(b"\r\n", b"\n"):
            raise RuntimeError("LLVM release batch file differs beyond CRLF conversion from its pinned raw Git blob")
        path.write_bytes(original)
    # This pinned blob contains CRLF despite its text attribute. Disable only
    # its Git clean filter after verifying exact bytes; compiler inputs stay untouched.
    attributes = Path(subprocess.check_output(
        ["git", "-C", llvm, "rev-parse", "--path-format=absolute", "--git-path", "info/attributes"],
        text=True,
    ).strip())
    attributes.parent.mkdir(parents=True, exist_ok=True)
    rule = f"{relative} -text"
    existing = attributes.read_text() if attributes.exists() else ""
    if rule not in existing.splitlines():
        attributes.write_text(existing.rstrip("\n") + "\n" + rule + "\n", encoding="utf-8")
    return {"path": relative, "raw_blob_identity_verified": path.read_bytes() == original,
            "checkout_line_endings_restored": restored, "sha256": digest(path),
            "git_filter_override": "Disable this file's clean filter after restoring exact pinned bytes"}


@contextmanager
def telemetry(output):
    if os.environ.get("RUNNER_NAME") != "MARCPE-TEST01-X64":
        raise RuntimeError("Telemetry requires the dedicated x64 runner")
    with (output / "telemetry.stdout").open("wb") as stdout, (
            output / "telemetry.stderr").open("wb") as stderr:
        process = subprocess.Popen(
            ["powershell.exe", "-NoProfile", "-File",
             str(Path(__file__).with_name("x64_pgo_telemetry.ps1")), "-OutputDirectory", str(output)],
            stdout=stdout, stderr=stderr,
        )
        try:
            deadline = time.monotonic() + 60
            while not (output / "telemetry-ready").exists():
                if process.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("Telemetry failed to become ready; inspect telemetry.stderr")
                time.sleep(1)
            yield
        finally:
            (output / "telemetry-stop").touch()
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                raise
        if process.returncode:
            raise RuntimeError("Telemetry failed; release timing is not accepted")


def configuration(clang, variant):
    if variant not in VARIANTS:
        raise ValueError("Unknown release variant")
    linker = clang / "lld-link.exe" if variant == "local" else Path(shutil.which("link.exe") or "")
    librarian = clang / "llvm-lib.exe" if variant == "local" else Path(shutil.which("lib.exe") or "")
    return f'''profile = "dist"
[build]
build = "{HOST}"
host = ["{HOST}"]
target = ["{HOST}"]
submodules = false
jobs = {CORES}
extended = true
docs = true
locked-deps = true
profiler = true
cargo-native-static = true
optimized-compiler-builtins = true
metrics = true
print-step-timings = true
verbose = 2
[llvm]
download-ci-llvm = false
clang-cl = "{(clang / 'clang-cl.exe').as_posix()}"
ninja = true
thin-lto = false
link-shared = false
static-libstdcpp = true
{('use-linker = "lld"' if variant == 'local' else '')}
[rust]
channel = "stable"
download-rustc = false
codegen-units = 1
codegen-units-std = 1
debuginfo-level-std = 1
remap-debuginfo = true
codegen-backends = ["llvm", "cranelift"]
lld = true
llvm-tools = true
llvm-bitcode-linker = true
lto = "thin-local"
verbose-tests = true
[target.{HOST}]
linker = "{linker.name}"
ar = "{librarian.as_posix()}"
[dist]
src-tarball = false
compression-formats = ["xz"]
compression-profile = "balanced"
'''


def check_distribution(files):
    names = {file.name for file in files}
    required = {
        f"{component}-1.94.1-{HOST}.tar.xz" for component in (
            "rust", "rustc", "rust-std", "cargo", "rust-docs", "rustfmt",
            "clippy", "llvm-tools", "rust-analyzer",
        )
    }
    required.update({f"rust-1.94.1-{HOST}.msi", "rust-src-1.94.1.tar.xz"})
    missing = required - names
    if missing:
        raise RuntimeError(f"Incomplete full distribution: {sorted(missing)}")


def validate_reference(reference, provenance):
    if not reference["complete"] or reference["variant"] != "upstream":
        raise RuntimeError("Local release requires an accepted upstream full-distribution control")
    for key in ("rust_sha", "llvm_sha", "rustc_perf_sha", "cores", "runner_name", "clang_installer_sha256"):
        if reference[key] != provenance[key]:
            raise RuntimeError(f"Upstream/local production mismatch: {key}")
    if not equivalent_tools(reference["tools"], provenance["tools"]):
        raise RuntimeError("Native tools changed between upstream and local builds")
    left, right = (tomllib.loads(row["configuration"]) for row in (reference, provenance))
    left["llvm"].pop("use-linker", None)
    right["llvm"].pop("use-linker", None)
    for config in (left, right):
        for key in ("linker", "ar"):
            config["target"][HOST].pop(key)
        config["llvm"].pop("clang-cl")
    if left != right:
        raise RuntimeError("Release settings differ beyond the declared native-linker change")


def run_release(root, variant, reference_dir=None):
    source, output = root / "r", root / "e"
    if (os.name != "nt" or os.environ.get("RUNNER_NAME") != "MARCPE-TEST01-X64"
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted" or os.cpu_count() != CORES):
        raise RuntimeError("Expected the dedicated native 16-LP x64 runner")
    if source.drive.upper() != "C:" or len(str(source)) > 24:
        raise RuntimeError("Build must use the reserved short C: NVMe path")
    if shutil.disk_usage(root).free < 180 * 2**30:
        raise RuntimeError("A fresh full release requires at least 180 GiB free on C:")
    if (source / "bootstrap.toml").exists() or (source / "build").exists():
        raise RuntimeError("Existing configuration or compiler objects would invalidate a cold build")
    for directory, revision in (
        (source, RUST_SHA), (source / "src/llvm-project", LLVM_SHA),
        (source / "src/tools/rustc-perf", PERF_SHA),
    ):
        actual = subprocess.check_output(["git", "-C", directory, "rev-parse", "HEAD"], text=True).strip()
        if actual != revision:
            raise RuntimeError(f"Wrong source revision: {directory}")
    checkout_evidence = preserve_literal_release_batch(source / "src/llvm-project")
    save(output / "checkout-validation.json", checkout_evidence)
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    clang = source / "citools/clang-rust/bin"
    tools = tool_identity(clang)
    env = environment(output, clang)
    env.update({
        "WIX": str(source / "wix"), "PGO_HOST": HOST,
        "DIST_REQUIRE_ALL_TOOLS": "1", "DIST_TRY_BUILD": "0",
        "MATCHED_BUILD_CORES": str(CORES),
        "COMPILETEST_REQUIRE_ALL_LLVM_COMPONENTS": "1",
    })
    config = configuration(clang, variant)
    provenance = {
        "schema": 1, "variant": variant, "complete": False, "pilot": True,
        "rust_sha": RUST_SHA, "llvm_sha": LLVM_SHA, "rustc_perf_sha": PERF_SHA,
        "runner_name": os.environ["RUNNER_NAME"], "cores": CORES,
        "run_id": os.environ["GITHUB_RUN_ID"], "attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "configuration": config, "tools": tools,
        "clang_installer_sha256": digest(source / "citools/LLVM-20.1.3-win64.exe"),
        "measurement": "Fresh complete Rust 1.94.1 distribution using opt-dist windows-ci; not compiler-only",
        "common_controls": [
            "16 LP on C: NVMe; sequential isolated jobs; fresh Cargo home and no compiler cache",
            "Full tools, docs, MSI, balanced XZ and upstream extracted-distribution tests",
            "Rust thin-local; LLVM ThinLTO disabled; identical upstream training corpus",
            "Common bootstrap-only clang-runtime discovery fix; no compiler/LLVM implementation changes",
        ],
        "intervention": (
            "None to the upstream PGO training sequence or Microsoft native linkers" if variant == "upstream"
            else "Static LLVM training relink plus LLVM lld-link/llvm-lib; no added ThinLTO"
        ),
        "limits": "Cold local release recipe; not upstream eight-CPU/private-cache infrastructure",
        "job_started_unix": float(os.environ["PGO_CELL_STARTED"]),
    }
    reference = None
    if variant == "local":
        if reference_dir is None:
            raise RuntimeError("Missing upstream reference evidence")
        reference = json.loads((reference_dir / "result.json").read_text())
        validate_reference(reference, provenance)
    patches = Path(__file__).resolve().parents[2] / "ci-benchmark"
    selected = ["bootstrap-clang-runtime.patch"]
    if variant == "local":
        selected.append("static-llvm-pgo.patch")
    for patch in selected:
        subprocess.run(["git", "-C", source, "apply", "--check", "--ignore-space-change", patches / patch], check=True)
        subprocess.run(["git", "-C", source, "apply", "--ignore-space-change", patches / patch], check=True)
    provenance["patches"] = {name: digest(patches / name) for name in selected}
    (source / "bootstrap.toml").write_text(config, encoding="utf-8")
    (output / "production-bootstrap.toml").write_text(config, encoding="utf-8")
    save(output / "provenance.json", provenance)
    native_tools = output / "native-tools.cmake"
    native_tools.write_text(
        "".join(f'set({key} "{value}" CACHE FILEPATH "" FORCE)\n' for key, value in (
            ("CMAKE_LINKER", (clang / "lld-link.exe").as_posix() if variant == "local"
             else Path(tools["files"]["link.exe"]["path"]).as_posix()),
            ("CMAKE_AR", tomllib.loads(config)["target"][HOST]["ar"]),
        )), encoding="utf-8",
    )
    env["CMAKE_TOOLCHAIN_FILE"] = str(native_tools)

    def measured(command, name):
        remaining = provenance["job_started_unix"] + 1430 * 60 - time.time()
        if remaining <= 0:
            raise TimeoutError("Release reached the 1430-minute evidence-preservation deadline")
        save(output / "active-stage.json", {"stage": name, "unix": time.time()})
        return execute(command, source, env, output, name, timeout=remaining, cores=CORES)

    x = [sys.executable, "x.py"]
    started = time.time()
    measured(x + ["build", "--set", "rust.debug=true", "opt-dist"], "build-opt-dist")
    fixture = source / "src/tools/rustc-perf/collector/compile-benchmarks/token-stream-stress"
    before = tomllib.loads((fixture / "Cargo.lock").read_text())
    # The upstream fixture's old lockfile format needs migration without changing dependencies.
    execute(
        [source / "build" / HOST / "stage0/bin/cargo.exe", "generate-lockfile", "--offline"],
        fixture, env, output, "training-lockfile", timeout=120, cores=CORES,
    )
    if tomllib.loads((fixture / "Cargo.lock").read_text())["package"] != before["package"]:
        raise RuntimeError("Training lockfile migration changed dependencies")
    helper = source / "build" / HOST / "stage1-tools-bin/opt-dist.exe"
    measured([helper, "windows-ci", "--", *x, "dist", "bootstrap", "--include-default-paths"],
             "upstream-pgo-full-dist")
    finished = time.time()
    sections = timer_sections(output / "upstream-pgo-full-dist.stderr")
    completed = {row["name"]: row for row in sections["completed"]}
    required_sections = (
        "Stage 1 (Rustc PGO)", "Stage 2 (LLVM PGO)", "Stage 5 (final build)", "Run tests",
    )
    if any(name not in completed or completed[name]["status"] != "OK" for name in required_sections):
        raise RuntimeError("Missing successful full training, distribution or extracted-test timer section")
    save(output / "production-sections.json", sections)
    profiles = {}
    for name in ("rustc-pgo.profdata", "llvm-pgo.profdata"):
        path = source / "opt-artifacts" / name
        if not path.is_file() or not path.stat().st_size:
            raise RuntimeError(f"Missing generated profile: {name}")
        profiles[name] = {"sha256": digest(path), "bytes": path.stat().st_size}
        shutil.copy2(path, output / name)
    profile = output / "llvm-pgo.profdata"
    coverage = {}
    for component in ("X86TargetLowering", "InstCombine"):
        text = subprocess.check_output(
            [clang / "llvm-profdata.exe", "show", f"--function={component}", "--counts", profile],
            env=env, text=True,
        )
        (output / f"coverage-{component}.txt").write_text(text, encoding="utf-8")
        blocks = [json.loads(line.split(":", 1)[1]) for line in text.splitlines()
                  if line.startswith("    Block counts:")]
        coverage[component] = {"functions": len(blocks), "nonzero_functions": sum(any(row) for row in blocks)}
        if variant == "local" and not coverage[component]["nonzero_functions"]:
            raise RuntimeError(f"Local LLVM training did not execute {component}")
    cache = source / "build" / HOST / "llvm/build/CMakeCache.txt"
    entries = {}
    for line in cache.read_text().splitlines():
        if line and not line.startswith(("#", "//")) and ":" in line and "=" in line:
            key, value = line.split("=", 1)
            entries[key.split(":", 1)[0]] = value
    if entries.get("LLVM_BUILD_INSTRUMENTED", "OFF") not in ("", "OFF"):
        raise RuntimeError("Final LLVM remains instrumented")
    if entries.get("LLVM_ENABLE_LTO", "OFF").upper() not in ("", "OFF"):
        raise RuntimeError("Unexpected LLVM ThinLTO")
    if digest(Path(entries["LLVM_PROFDATA_FILE"])) != profiles["llvm-pgo.profdata"]["sha256"]:
        raise RuntimeError("Final LLVM did not use this release's generated profile")
    shutil.copy2(cache, output / "CMakeCache.txt")
    profile_use = False
    for suffix in ("stdout", "stderr"):
        with (output / f"upstream-pgo-full-dist.{suffix}").open(errors="replace") as log:
            profile_use |= any("-Cprofile-use=" in line for line in log)
    if not profile_use:
        raise RuntimeError("No evidence of rustc profile use")
    files = [path for path in (source / "build/dist").iterdir() if path.is_file()]
    check_distribution(files)
    manifest = [{"name": path.name, "bytes": path.stat().st_size, "sha256": digest(path)}
                for path in sorted(files)]
    if reference_dir is not None:
        previous = json.loads((reference_dir / "dist-manifest.json").read_text())
        if {row["name"] for row in previous} != {row["name"] for row in manifest}:
            raise RuntimeError("Upstream/local distribution file sets differ")
    save(output / "dist-manifest.json", manifest)
    metrics = source / "build/metrics.json"
    shutil.copy2(metrics, output / "metrics.json")
    save(output / "phase-summary.json", summarize(json.loads(metrics.read_text())))
    qualification = completed["Run tests"]["wall_seconds"]
    save(output / "result.json", {
        **provenance, "complete": True, "profiles": profiles, "llvm_training_coverage": coverage,
        "started_unix": started, "finished_unix": finished,
        "preparation_seconds": started - provenance["job_started_unix"],
        "production_and_qualification_seconds": finished - started,
        "qualification_seconds": qualification,
        "production_seconds": finished - started - qualification,
        "whole_job_seconds": None,
        "whole_job_note": "Obtain final job duration from GitHub after evidence/distribution uploads and cleanup",
        "qualification": "Unmodified opt-dist windows-ci extracted-distribution tests passed",
        "attribution": "Local recipe also changes native linking tools; not isolated PGO profile quality",
    })
    print("Qualified full distribution; result.json written.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    parser.add_argument("--reference", type=Path)
    args = parser.parse_args()
    try:
        with telemetry(args.root / "e"):
            run_release(args.root.resolve(), args.variant, args.reference)
    except Exception as error:
        save(args.root / "e/failure.json", {
            "complete": False, "error_type": type(error).__name__, "error": str(error), "unix": time.time(),
        })
        result = args.root / "e/result.json"
        if result.exists():
            data = json.loads(result.read_text())
            data["complete"] = False
            data["rejection"] = str(error)
            save(result, data)
        raise


if __name__ == "__main__":
    main()
