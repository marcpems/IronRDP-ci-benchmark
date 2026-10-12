"""Matched cold full-distribution builds; never substitutes compiler-only timings."""

import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import tomllib

from build_arm_compilers import digest, save
from msvc_experiment import (
    clang_profile_preflight, cmake_toolchain, environment, execute,
    rebuild_clang_runtime, tool_identity,
)

RUST = "7db17d9b5bbe6b16be2dc86b4bfae81d6e1ae238"
LLVM = "aab11ee0ea5ea9a1d462ad0bc1fae9d9bb643019"
PERF = "208d929efe770996eb02cd3d2712623ea48b7646"
VARIANTS = ("baseline", "msvc-pgo", "llvm-pgo-thin")


def check_build_paths(*paths):
    for path in paths:
        if len(str(path.resolve())) > 24:
            raise RuntimeError(f"native Windows tools require short physical build roots: {path}")


def configuration(host, clang, librarian, variant):
    llvm = variant == "llvm-pgo-thin"
    targets = [host] + (["arm64ec-pc-windows-msvc"] if host.startswith("aarch64") else [])
    backends = ["llvm"] + (["cranelift"] if host.startswith("x86_64") else [])
    return f'''profile = "dist"
[build]
build = "{host}"
host = ["{host}"]
target = {json.dumps(targets)}
submodules = false
jobs = 4
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
link-jobs = 1
thin-lto = {str(llvm).lower()}
link-shared = false
[rust]
channel = "nightly"
download-rustc = false
codegen-units = {1 if host.startswith("x86_64") else 16}
codegen-units-std = 1
debuginfo-level-std = 1
remap-debuginfo = true
codegen-backends = {json.dumps(backends)}
lld = true
llvm-tools = true
llvm-bitcode-linker = true
lto = "{'thin' if llvm else 'thin-local'}"
[target.{host}]
linker = "{'lld-link.exe' if llvm else 'link.exe'}"
ar = "{librarian.as_posix()}"
[dist]
src-tarball = false
compression-formats = ["xz"]
compression-profile = "balanced"
'''


def run(command, source, env, output, name):
    remaining = float(os.environ["RELEASE_JOB_STARTED"]) + 350 * 60 - time.time()
    if remaining <= 0:
        raise TimeoutError("full release job reached the 350-minute safety boundary")
    save(output / "active-stage.json", {"stage": name, "started_unix": time.time()})
    return execute(command, source, env, output, name, timeout=remaining)


def check_manifest(files, host):
    names = {p.name for p in files}
    required = (
        f"rustc-nightly-{host}.tar.xz", f"rust-std-nightly-{host}.tar.xz",
        f"cargo-nightly-{host}.tar.xz", f"rust-docs-nightly-{host}.tar.xz",
        f"rustfmt-nightly-{host}.tar.xz", f"clippy-nightly-{host}.tar.xz",
        f"rust-analyzer-nightly-{host}.tar.xz", f"rust-nightly-{host}.msi",
        "rust-src-nightly.tar.xz",
    )
    missing = set(required) - names
    if host.startswith("aarch64") and "rust-std-nightly-arm64ec-pc-windows-msvc.tar.xz" not in names:
        missing.add("rust-std-nightly-arm64ec-pc-windows-msvc.tar.xz")
    if missing:
        raise RuntimeError(f"incomplete full distribution: {sorted(missing)}")


def profile_validation(source, clang, host, env, output):
    profiles = source / "opt-artifacts"
    result = {}
    for name in ("rustc-pgo.profdata", "rustdoc-pgo.profdata", "clippy-pgo.profdata", "llvm-pgo.profdata"):
        path = profiles / name
        if not path.is_file() or not path.stat().st_size:
            raise RuntimeError(f"missing fresh release profile: {name}")
        result[name] = digest(path)
    for name in ("AArch64TargetLowering" if host.startswith("aarch64") else "X86TargetLowering", "InstCombine"):
        text = subprocess.check_output([
            clang / "llvm-profdata.exe", "show", f"--function={name}", "--counts",
            profiles / "llvm-pgo.profdata",
        ], text=True, env=env)
        rows = [json.loads(line.split(":", 1)[1]) for line in text.splitlines()
                if line.strip().startswith("Block counts:")]
        if not any(any(row) for row in rows):
            raise RuntimeError(f"no executed backend profile counters: {name}")
        (output / f"coverage-{name}.txt").write_text(text, encoding="utf-8")
    save(output / "profiles.json", result)


def qualify_distribution(source, output, host, env):
    dist = source / "build/dist"
    unpacked = source / "build/unpacked-dist"
    unpacked.mkdir()
    for name in (f"rustc-nightly-{host}", f"rust-std-nightly-{host}",
                 f"cargo-nightly-{host}", "rust-src-nightly"):
        subprocess.run(["tar", "-xJf", dist / (name + ".tar.xz"), "-C", unpacked], check=True)
    compiler = unpacked / f"rustc-nightly-{host}/rustc"
    library = unpacked / f"rust-std-nightly-{host}/rust-std-{host}/lib/rustlib"
    shutil.copytree(library, compiler / "lib/rustlib", dirs_exist_ok=True)
    shutil.copytree(unpacked / "rust-src-nightly/rust-src/lib/rustlib/src",
                    compiler / "lib/rustlib/src", dirs_exist_ok=True)
    if host.startswith("x86_64"):
        name = f"rustc-codegen-cranelift-nightly-{host}"
        subprocess.run(["tar", "-xJf", dist / (name + ".tar.xz"), "-C", unpacked], check=True)
        relative = Path("lib") / "rustlib" / host / "codegen-backends"
        shutil.copytree(unpacked / name / "rustc-codegen-cranelift-preview" / relative,
                        compiler / relative, dirs_exist_ok=True)
    cargo = unpacked / f"cargo-nightly-{host}/cargo/bin/cargo.exe"
    llvm_config = source / "build" / host / "llvm/bin/llvm-config.exe"
    if not llvm_config.is_file():
        raise RuntimeError("missing built LLVM configuration for extracted distribution tests")
    config = source / "bootstrap.toml"
    original = config.read_bytes()
    config.write_text(f'''profile = "user"
[rust]
channel = "nightly"
verbose-tests = true
lld = false
[build]
rustc = "{(compiler / 'bin/rustc.exe').as_posix()}"
cargo = "{cargo.as_posix()}"
local-rebuild = true
compiletest-allow-stage0 = true
jobs = 4
[target.{host}]
llvm-config = "{llvm_config.as_posix()}"
''', encoding="utf-8")
    try:
        run([sys.executable, "x.py", "test", "--build", host, "--stage", "0",
             "tests/assembly-llvm", "tests/codegen-llvm", "tests/codegen-units",
             "tests/incremental", "tests/mir-opt", "tests/pretty",
             "tests/run-make/glibc-symbols-x86_64-unknown-linux-gnu",
             "tests/run-make/rust-lld-x86_64-unknown-linux-gnu-dist",
             "tests/ui", "tests/crashes", "tests/rustdoc-html"],
            source, {**env, "COMPILETEST_ENABLE_DIST_TESTS": "1"},
            output, "extracted-dist-tests")
    finally:
        config.write_bytes(original)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--runtime-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--host", choices=("x86_64-pc-windows-msvc", "aarch64-pc-windows-msvc"), required=True)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    try:
        build(source, args.runtime_source.resolve(), output, args.host, args.variant)
    except Exception as error:
        save(output / "failure.json", {"error": str(error), "unix": time.time(), "complete": False})
        raise


def prepare(source, runtime_source, output, host, variant, full_distribution=True,
            rust_revision=RUST):
    expected_machine = ("arm64", "aarch64") if host.startswith("aarch64") else ("amd64", "x86_64")
    if os.name != "nt" or platform.machine().lower() not in expected_machine or os.cpu_count() != 4:
        raise RuntimeError("expected a native standard four-logical-CPU Windows runner")
    check_build_paths(source, runtime_source, output)
    for path, revision in ((source, rust_revision), (source / "src/llvm-project", LLVM),
                           (source / "src/tools/rustc-perf", PERF)):
        if subprocess.check_output(["git", "-C", path, "rev-parse", "HEAD"], text=True).strip() != revision:
            raise RuntimeError(f"source revision mismatch: {path}")
    if (source / "bootstrap.toml").exists() or (source / "build").exists():
        raise RuntimeError("release comparison requires a clean, uncached source checkout")
    patch = source / "src/tools/opt-dist/windows-msvc-profile-runtime.patch"
    for path in (source / "src/llvm-project", runtime_source):
        subprocess.run(["git", "-C", path, "apply", "--check", patch], check=True)
        subprocess.run(["git", "-C", path, "apply", patch], check=True)
    clang = source / "citools/clang-rust/bin"
    identity = tool_identity(clang)
    env = environment(output, clang)
    env.update({
        "WIX": str(source / "wix"), "PGO_HOST": host,
        "DIST_REQUIRE_ALL_TOOLS": "1", "DIST_TRY_BUILD": "0",
    })
    env["CMAKE_TOOLCHAIN_FILE"] = str(cmake_toolchain(output, identity))
    provenance = {
        "rust_sha": rust_revision, "llvm_sha": LLVM, "perf_sha": PERF, "host": host,
        "variant": variant, "tools": identity, "run_id": os.environ["GITHUB_RUN_ID"],
        "attempt": os.environ["GITHUB_RUN_ATTEMPT"], "vm": int(os.environ["RELEASE_REPLICATE"]),
        "pilot": os.environ["RELEASE_PILOT"] == "true",
        "job_started_unix": float(os.environ["RELEASE_JOB_STARTED"]),
        "full_distribution": full_distribution,
        "cache": ("cold; no shared compiler or profile cache" if full_distribution else
                  "cold compiler rebuild; recorded profiles reused for diagnosis only"),
        "baseline": "controlled no-PGO full distribution, not the shipped x64 PGO recipe",
        "profiling_runtime_patch_sha256": digest(patch),
        "bootstrap_cargo_sha256": digest(source / "src/bootstrap/src/core/builder/cargo.rs"),
        "paths": {"source": str(source), "runtime": str(runtime_source), "output": str(output),
                  "cargo_home": env["CARGO_HOME"], "temp": env["TEMP"]},
    }
    save(output / "provenance.json", provenance)
    preparation = time.time()
    # Build both runtimes on every variant so preparation is a common control.
    provenance["runtime"] = rebuild_clang_runtime(runtime_source, output, clang, env, identity, host)
    provenance["runtime_probe"] = clang_profile_preflight(output, clang, env, identity, host)
    librarian = Path(identity["files"]["lib.exe"]["path"])
    if variant == "llvm-pgo-thin":
        librarian = clang / "llvm-lib.exe"
        llvm_tools = output / "llvm-tools.cmake"
        llvm_tools.write_text(
            f'set(CMAKE_LINKER "{(clang / "lld-link.exe").as_posix()}" CACHE FILEPATH "" FORCE)\n'
            f'set(CMAKE_AR "{librarian.as_posix()}" CACHE FILEPATH "" FORCE)\n', encoding="utf-8")
        env["CMAKE_TOOLCHAIN_FILE"] = str(llvm_tools)
        provenance["llvm_linking_tools"] = {
            name: digest(clang / name) for name in ("lld-link.exe", "llvm-lib.exe")}
    config = configuration(host, clang, librarian, variant)
    (source / "bootstrap.toml").write_text(config, encoding="utf-8")
    (output / "bootstrap.toml").write_text(config, encoding="utf-8")
    provenance["preparation_wall_seconds"] = time.time() - preparation
    save(output / "provenance.json", provenance)
    return env, clang, identity, librarian, provenance


def build(source, runtime_source, output, host, variant):
    env, clang, identity, librarian, provenance = prepare(
        source, runtime_source, output, host, variant)
    start = time.time()
    dist = [sys.executable, "x.py", "dist", "bootstrap", "--include-default-paths"]
    if variant == "baseline":
        run(dist, source, env, output, "full-dist")
    else:
        run([sys.executable, "x.py", "build", "--host", host, "--target", host,
             "--set", "rust.debug=true", "opt-dist"], source, env, output, "build-opt-dist")
        fixture = source / "src/tools/rustc-perf/collector/compile-benchmarks/token-stream-stress"
        lock = fixture / "Cargo.lock"
        before = tomllib.loads(lock.read_text())
        cargo = source / "build" / host / "stage0/bin/cargo.exe"
        run([cargo, "generate-lockfile", "--offline"], fixture, env, output, "training-lockfile")
        if before["package"] != tomllib.loads(lock.read_text())["package"]:
            raise RuntimeError("training lock migration changed package graph")
        helper = source / "build" / host / "stage1-tools-bin/opt-dist.exe"
        run([helper, "local", "--target-triple", host, "--checkout-dir", source,
             "--llvm-dir", clang.parent, "--python", sys.executable, "--llvm-shared", "false",
             "--", *dist], source, env, output, "fresh-pgo-full-dist")
    save(output / "distribution-timing.json", {
        "started_unix": start, "finished_unix": time.time(),
        "wall_seconds": time.time() - start, "includes": "helper, fresh full-tool PGO training, full dist",
        "excludes": "source/tool preparation, post-build verification, uploads",
    })
    files = [p for p in (source / "build/dist").iterdir() if p.is_file()]
    check_manifest(files, host)
    save(output / "dist-manifest.json", [
        {"name": p.name, "bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted(files)])
    if variant != "baseline":
        profile_validation(source, clang, host, env, output)
    for component in ("llvm", "lld"):
        # LLVM and LLD put their CMake caches at different bootstrap levels.
        candidates = list((source / "build" / host / component).rglob("CMakeCache.txt"))
        if len(candidates) != 1:
            raise RuntimeError(f"expected one {component} CMake cache, found {candidates}")
        cache = candidates[0]
        values = {}
        for line in cache.read_text(errors="replace").splitlines():
            if "=" in line and ":" in line.split("=", 1)[0]:
                key, value = line.split("=", 1)
                values[key.split(":", 1)[0]] = value
        expected = {"CMAKE_LINKER": clang / "lld-link.exe" if variant == "llvm-pgo-thin"
                    else Path(identity["files"]["link.exe"]["path"]), "CMAKE_AR": librarian}
        for key, binary in expected.items():
            if digest(Path(values[key])) != digest(binary):
                raise RuntimeError(f"{component} used an unexpected {key}")
        shutil.copy2(cache, output / f"{component}-CMakeCache.txt")
    qualify_distribution(source, output, host, env)
    # The retained archives are the actual distribution outputs used by downstream checks.
    save(output / "result.json", {
        **provenance, "complete": True, "completed_unix": time.time(),
        "qualification": "full manifest, profile validation and common extracted-distribution test suite passed",
    })


if __name__ == "__main__":
    main()
