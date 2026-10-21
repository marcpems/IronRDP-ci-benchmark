"""Build matched distributions differing only in supplied LLVM profile data."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time

from build_arm_compilers import digest, save
from msvc_experiment import environment, equivalent_tools, execute, tool_identity
from x64_pgo_release import (
    HOST, check_distribution, configuration, preserve_literal_release_batch, telemetry,
)

PROTOCOL = Path(__file__).resolve().parents[2] / "ci-benchmark/x64-profile-only-protocol.json"


def verify_pair(left, right):
    if not left.get("complete") or left.get("variant") != "official" or right["variant"] != "repaired":
        raise RuntimeError("Expected a qualified official-profile control")
    for key in ("protocol", "configuration", "rustc_profile_sha256", "clang_installer_sha256",
                "run_id", "attempt", "patches", "test_module_sha256", "runner"):
        if left[key] != right[key]:
            raise RuntimeError(f"Profile-only common input differs: {key}")
    if not equivalent_tools(left["tools"], right["tools"]):
        raise RuntimeError("Native tool identities changed between builds")


def tests_only_helper(source):
    path = source / "src/tools/opt-dist/src/main.rs"
    original = path.read_text(encoding="utf-8")
    old = "let result = execute_pipeline(&env, &mut timer, build_args);"
    new = '''let result = if std::env::var_os("X64_PROFILE_ONLY_TESTS").as_deref()
        == Some(std::ffi::OsStr::new("1"))
    {
        timer.section("Run tests", |_| run_tests(&env))
    } else {
        execute_pipeline(&env, &mut timer, build_args)
    };'''
    if original.count(old) != 1 or "X64_PROFILE_ONLY_TESTS" in original:
        raise RuntimeError("Pinned opt-dist dispatch changed; refusing to alter its test implementation")
    path.write_text(original.replace(old, new), encoding="utf-8")
    return digest(path)


def load_profiles(root, output, variant, protocol):
    bundle = root / "inputs/official.tar.xz"
    if digest(bundle) != protocol["official_bundle_sha256"]:
        raise RuntimeError("Official reproducibility bundle checksum mismatch")
    extracted = output / "official-input"
    extracted.mkdir()
    with tarfile.open(bundle, "r:xz") as archive:
        archive.extractall(extracted, filter="data")
    profiles = {}
    for name in ("rustc", "llvm"):
        files = list(extracted.rglob(f"{name}-pgo.profdata"))
        if len(files) != 1:
            raise RuntimeError(f"Expected one official {name} profile")
        source = files[0]
        if name == "llvm" and variant == "repaired":
            source = root / "inputs/repaired/llvm-pgo.profdata"
        destination = output / f"{name}-pgo.profdata"
        shutil.copy2(source, destination)
        expected = protocol["rustc_profile_sha256"] if name == "rustc" else protocol["llvm_profile_sha256"][variant]
        if digest(destination) != expected:
            raise RuntimeError(f"Wrong {name} profile for {variant}")
        profiles[name] = destination
    return profiles


def audit_native_cache(source, output, profiles, tools):
    for component in ("llvm", "lld"):
        caches = list((source / "build" / HOST / component).rglob("CMakeCache.txt"))
        if len(caches) != 1:
            raise RuntimeError(f"Expected one final {component} CMake cache")
        values = {}
        for line in caches[0].read_text().splitlines():
            if line and not line.startswith(("#", "//")) and ":" in line and "=" in line:
                key, value = line.split("=", 1)
                values[key.split(":", 1)[0]] = value
        for key, name in (("CMAKE_LINKER", "link.exe"), ("CMAKE_AR", "lib.exe")):
            if digest(Path(values[key])) != tools["files"][name]["sha256"]:
                raise RuntimeError(f"{component} did not retain Microsoft {name}")
        if values.get("LLVM_ENABLE_LTO", "OFF").upper() not in ("", "OFF"):
            raise RuntimeError("Unexpected native ThinLTO")
        if values.get("LLVM_BUILD_INSTRUMENTED", "OFF") not in ("", "OFF"):
            raise RuntimeError("Unexpected instrumentation")
        if component == "llvm" and digest(Path(values["LLVM_PROFDATA_FILE"])) != digest(profiles["llvm"]):
            raise RuntimeError("LLVM used the wrong optimization profile")
        shutil.copy2(caches[0], output / f"{component}-CMakeCache.txt")


def build(root, variant, correctness_temp):
    protocol = json.loads(PROTOCOL.read_text())
    output, source = root / "e" / variant, root / "r"
    if (os.name != "nt" or os.cpu_count() != protocol["build_cores"]
            or os.environ.get("RUNNER_NAME") != protocol["runner"]
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted"):
        raise RuntimeError("Wrong dedicated x64 host")
    if source.drive != protocol["build_drive"] or len(str(source)) > 24:
        raise RuntimeError("Expected the qualified short ReFS source path")
    if shutil.disk_usage(root).free < 180 * 2**30:
        raise RuntimeError("Less than 180 GiB free before the clean compiler build")
    if (source / "build").exists() or (source / "bootstrap.toml").exists():
        raise RuntimeError("Compiler objects/configuration would invalidate the clean build")
    for path, revision in ((source, protocol["rust_sha"]), (source / "src/llvm-project", protocol["llvm_sha"])):
        if subprocess.check_output(["git", "-C", path, "rev-parse", "HEAD"], text=True).strip() != revision:
            raise RuntimeError(f"Wrong source revision: {path}")
    save(output / "checkout-validation.json", preserve_literal_release_batch(source / "src/llvm-project"))
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    profiles = load_profiles(root, output, variant, protocol)
    clang = source / "citools/clang-rust/bin"
    if digest(source / "citools/LLVM-20.1.3-win64.exe") != protocol["clang_installer_sha256"]:
        raise RuntimeError("Clang installer differs from the accepted pinned 20.1.3 builder")
    tools = tool_identity(clang)
    env = environment(output, clang)
    env.update({"WIX": str(source / "wix"), "PGO_HOST": HOST, "DIST_TRY_BUILD": "0",
                "DIST_REQUIRE_ALL_TOOLS": "1", "COMPILETEST_REQUIRE_ALL_LLVM_COMPONENTS": "1",
                "MATCHED_BUILD_CORES": str(protocol["build_cores"])})
    config = configuration(clang, "upstream")
    patch = PROTOCOL.parent / "bootstrap-clang-runtime.patch"
    subprocess.run(["git", "-C", source, "apply", "--check", "--ignore-space-change", patch], check=True)
    subprocess.run(["git", "-C", source, "apply", "--ignore-space-change", patch], check=True)
    test_module = source / "src/tools/opt-dist/src/tests.rs"
    provenance = {
        "protocol": protocol, "variant": variant, "complete": False, "configuration": config,
        "run_id": os.environ["GITHUB_RUN_ID"], "attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "runner": os.environ["RUNNER_NAME"], "tools": tools,
        "rustc_profile_sha256": digest(profiles["rustc"]), "llvm_profile_sha256": digest(profiles["llvm"]),
        "clang_installer_sha256": digest(source / "citools/LLVM-20.1.3-win64.exe"),
        "test_module_sha256": digest(test_module),
        "patches": {"bootstrap-clang-runtime.patch": digest(patch),
                    "tests-only-opt-dist-main": tests_only_helper(source)},
    }
    if variant == "repaired":
        verify_pair(json.loads((root / "reference/result.json").read_text()), provenance)
    save(output / "provenance.json", provenance)
    (source / "bootstrap.toml").write_text(config, encoding="utf-8")
    (output / "production-bootstrap.toml").write_text(config, encoding="utf-8")
    native = output / "native-tools.cmake"
    native.write_text("".join(
        f'set({key} "{Path(tools["files"][name]["path"]).as_posix()}" CACHE FILEPATH "" FORCE)\n'
        for key, name in (("CMAKE_LINKER", "link.exe"), ("CMAKE_AR", "lib.exe"))), encoding="utf-8")
    env["CMAKE_TOOLCHAIN_FILE"] = str(native)
    x = [sys.executable, "x.py"]
    started = time.time()
    execute(x + ["dist", "bootstrap", "--include-default-paths",
                 "--rust-profile-use", profiles["rustc"], "--llvm-profile-use", profiles["llvm"]],
            source, env, output, "fixed-profile-dist", timeout=8 * 3600, cores=protocol["build_cores"])
    production_finished = time.time()
    shutil.copy2(source / "build/metrics.json", output / "production-metrics.json")
    audit_native_cache(source, output, profiles, tools)
    profile_use, warnings = False, []
    for suffix in ("stdout", "stderr"):
        with (output / f"fixed-profile-dist.{suffix}").open(errors="replace") as log:
            for line in log:
                if "-Cprofile-use=" in line and profiles["rustc"].as_posix() in line.replace("\\\\", "\\").replace("\\", "/"):
                    profile_use = True
                if ("mismatched data" in line.lower() or "hash mismatch" in line.lower()
                        or "out of date" in line.lower() and "profile" in line.lower()):
                    warnings.append(line.strip())
    save(output / "profile-use-audit.json", {"rustc_profile_use": profile_use, "profile_mismatch_warnings": warnings})
    if not profile_use or warnings:
        raise RuntimeError("Missing rustc profile use or mismatched profile data; inspect profile-use-audit.json")
    files = sorted(path for path in (source / "build/dist").iterdir() if path.is_file())
    check_distribution(files)
    if f"rustc-codegen-cranelift-1.94.1-{HOST}.tar.xz" not in {path.name for path in files}:
        raise RuntimeError("Missing required Cranelift distribution")
    if variant == "repaired":
        previous = json.loads((root / "reference/dist-manifest.json").read_text())
        if {row["name"] for row in previous} != {path.name for path in files}:
            raise RuntimeError("Paired distribution file sets differ")
    save(output / "dist-manifest.json",
         [{"name": path.name, "bytes": path.stat().st_size, "sha256": digest(path)} for path in files])
    qualification_start = time.time()
    execute(x + ["build", "--set", "rust.debug=true", "opt-dist"], source, env, output,
            "build-test-helper", timeout=1800, cores=protocol["build_cores"])
    helper = source / "build" / HOST / "stage1-tools-bin/opt-dist.exe"
    test_env = {**env, "X64_PROFILE_ONLY_TESTS": "1",
                "TEMP": str(correctness_temp), "TMP": str(correctness_temp)}
    execute([helper, "windows-ci"], source, test_env, output, "extracted-dist-tests",
            timeout=3600, cores=protocol["build_cores"])
    if digest(test_module) != provenance["test_module_sha256"]:
        raise RuntimeError("The upstream extracted-distribution test implementation changed")
    save(output / "result.json", {
        **provenance, "complete": True, "started_unix": started, "finished_unix": time.time(),
        "production_seconds": production_finished - started,
        "qualification_seconds": time.time() - qualification_start,
        "qualification": "Unmodified upstream opt-dist tests.rs; dispatch-only entry bypasses all training",
        "scope": protocol["scope"],
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--variant", choices=("official", "repaired"), required=True)
    parser.add_argument("--correctness-temp", type=Path, required=True)
    args = parser.parse_args()
    output = args.root / "e" / args.variant
    try:
        with telemetry(output, build_drive="D:"):
            build(args.root.resolve(), args.variant, args.correctness_temp.resolve())
    except Exception as error:
        save(output / "failure.json", {"complete": False, "error": str(error), "unix": time.time()})
        result = output / "result.json"
        if result.exists():
            value = json.loads(result.read_text())
            save(result, {**value, "complete": False, "rejection": str(error)})
        raise


if __name__ == "__main__":
    main()
