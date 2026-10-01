"""Build matched Rust 1.94.1 Arm64 compilers using an isolated native toolchain."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import tomllib
import zipfile

RUST_SHA = "e408947bfd200af42db322daf0fadfe7e26d3bd1"
LLVM_SHA = "00d23d10dc48c6bb9d57ba96d4a748d85d77d0c7"
PERF_SHA = "c0301bc44d175b9b2c5442b25049475c39d7700c"
HOST = "aarch64-pc-windows-msvc"
VARIANTS = ("baseline-msvc", "baseline-lld", "optimized")
OFFICIAL_STD = {
    HOST: "9b3237662e22bd337f1dafbbf0c07178bb2907b6d2b3008c7f1dabbec68990b2",
    "wasm32-unknown-unknown": "26b8953083b942aeaf870de742962e4ba17c0da2095725fbf4ab5ab85a4d5fd5",
}


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def clean_environment(root, msvc):
    tools = root / "tools"
    clang = tools / "clang20" / "bin"
    sdk = tools / "microsoft.windows.sdk.cpp" / "c"
    libs = tools / "microsoft.windows.sdk.cpp.arm64" / "c"
    sdk_version = "10.0.26100.0"
    sdk_bin = sdk / "bin" / sdk_version / "arm64"
    vc_bin = msvc / "bin" / "Hostarm64" / "arm64"
    required = [
        clang / "clang-cl.exe", clang / "lld-link.exe", clang / "llvm-lib.exe", vc_bin / "cl.exe",
        vc_bin / "link.exe", sdk_bin / "rc.exe",
        sdk / "Include" / sdk_version / "ucrt" / "stdlib.h",
        libs / "um" / "arm64" / "kernel32.lib",
    ]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    env = {k: os.environ[k] for k in (
        "SystemRoot", "SystemDrive", "WINDIR", "COMSPEC", "PATHEXT",
        "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE",
    ) if k in os.environ}
    paths = [clang, vc_bin, sdk_bin, Path(sys.executable).parent]
    for name in ("cmake", "ninja", "git", "7z", "perl", "bash"):
        executable = shutil.which(name)
        if executable is None:
            raise FileNotFoundError(f"Required build tool: {name}")
        paths.append(Path(executable).parent)
    paths += [Path(env["SystemRoot"]) / "System32", Path(env["SystemRoot"])]
    home = root / "home"
    temp = root / "temp"
    for path in (home, temp, home / "AppData" / "Roaming", home / "AppData" / "Local"):
        path.mkdir(parents=True, exist_ok=True)
    include = [msvc / "include"] + [
        sdk / "Include" / sdk_version / part for part in ("ucrt", "shared", "um", "winrt")
    ]
    lib = [msvc / "lib" / "arm64", libs / "ucrt" / "arm64", libs / "um" / "arm64"]
    env.update({
        "PATH": os.pathsep.join(dict.fromkeys(str(p) for p in paths)),
        "INCLUDE": os.pathsep.join(map(str, include)),
        "LIB": os.pathsep.join(map(str, lib)),
        "LIBPATH": os.pathsep.join(map(str, lib)),
        "VCToolsInstallDir": str(msvc) + "\\",
        "VCINSTALLDIR": str(msvc.parents[2]) + "\\",
        "VSINSTALLDIR": str(msvc.parents[3]) + "\\",
        "WindowsSdkDir": str(sdk) + "\\",
        "WindowsSDKVersion": sdk_version + "\\",
        "UCRTVersion": sdk_version,
        "UniversalCRTSdkDir": str(sdk) + "\\",
        "VSCMD_ARG_HOST_ARCH": "arm64", "VSCMD_ARG_TGT_ARCH": "arm64",
        "TEMP": str(temp), "TMP": str(temp), "HOME": str(home),
        "USERPROFILE": str(home), "APPDATA": str(home / "AppData" / "Roaming"),
        "LOCALAPPDATA": str(home / "AppData" / "Local"),
        "CARGO_HOME": str(root / "cargo"), "CARGO_INCREMENTAL": "0",
        "PYTHONDONTWRITEBYTECODE": "1", "RUST_BACKTRACE": "1",
        "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.longpaths",
        "GIT_CONFIG_VALUE_0": "true",
    })
    return env


def configuration(root, msvc, variant, jobs):
    optimized = variant == "optimized"
    build_dir = "build-ab-optimized" if optimized else "build-ab-baseline"
    clang = root / "tools" / "clang20" / "bin"
    linker = clang / "lld-link.exe" if variant != "baseline-msvc" else "link.exe"
    archiver = clang / "llvm-lib.exe" if variant != "baseline-msvc" else (
        msvc / "bin" / "Hostarm64" / "arm64" / "lib.exe"
    )
    llvm_linker_setting = "" if optimized else 'use-linker = "lld"'
    # Literal TOML strings preserve Windows path separators.
    text = f"""profile = "dist"
[build]
build = "{HOST}"
host = ["{HOST}"]
target = ["{HOST}"]
build-dir = "{build_dir}"
jobs = {jobs}
extended = false
docs = false
locked-deps = true
profiler = true
optimized-compiler-builtins = true
metrics = true
print-step-timings = true
verbose = 2
[llvm]
download-ci-llvm = false
clang-cl = '{clang / "clang-cl.exe"}'
optimize = true
assertions = false
ninja = true
link-jobs = 2
thin-lto = {str(optimized).lower()}
link-shared = false
static-libstdcpp = true
{llvm_linker_setting}
[llvm.build-config]
LLVM_ENABLE_DIA_SDK = "OFF"
[rust]
channel = "stable"
download-rustc = false
optimize = true
debug-assertions = false
overflow-checks = false
debuginfo-level-std = 1
codegen-units-std = 1
remap-debuginfo = true
codegen-backends = ["llvm"]
lld = true
llvm-tools = true
llvm-bitcode-linker = false
lto = "{'thin' if optimized else 'thin-local'}"
[target.{HOST}]
linker = '{linker}'
cc = '{msvc / "bin" / "Hostarm64" / "arm64" / "cl.exe"}'
cxx = '{msvc / "bin" / "Hostarm64" / "arm64" / "cl.exe"}'
ar = '{archiver}'
"""
    return build_dir, text


def execute(command, source, env, log):
    started = time.time()
    print(f"START {log.name}: {subprocess.list2cmdline(command)}", flush=True)
    with log.open("wb") as stream:
        subprocess.run(command, cwd=source, env=env, stdout=stream,
                       stderr=subprocess.STDOUT, check=True)
    print(f"DONE {log.name}: {time.time() - started:.1f}s", flush=True)


def excluded_sysroot_entries(original, directory, names):
    directory = Path(directory)
    excluded = set()
    if directory == original / "lib" / "rustlib":
        excluded = {"src", "rustc-src"} & set(names)
    for name in set(names) - excluded:
        path = directory / name
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or (
            getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
        ):
            raise RuntimeError(f"Unexpected sysroot link: {path}")
    return excluded


def prepare_training_lockfile(source, build_dir, env, logs):
    directory = source / "src" / "tools" / "rustc-perf" / "collector" / "compile-benchmarks" / "token-stream-stress"
    lockfile = directory / "Cargo.lock"
    before = tomllib.loads(lockfile.read_text(encoding="utf-8"))
    if before.get("package") != [{"name": "token-stream-stress", "version": "0.0.0"}]:
        raise RuntimeError("Unexpected dependencies in token-stream-stress training fixture")
    cargo = source / build_dir / HOST / "stage0" / "bin" / "cargo.exe"
    execute([str(cargo), "generate-lockfile", "--offline"], directory, env,
            logs / "training-lockfile-migration.log")
    after = tomllib.loads(lockfile.read_text(encoding="utf-8"))
    if after.get("package") != before["package"]:
        raise RuntimeError("Training lockfile migration changed dependency resolution")
    return {"workload": "token-stream-stress", "change": "Legacy lockfile format to Cargo v4; no dependency changes",
            "sha256": digest(lockfile)}


def package(source, root, variant, build_dir, provenance, env):
    original = source / build_dir / HOST / "stage2"
    with tempfile.TemporaryDirectory(prefix=f"package-{variant}-", dir=root) as tmp:
        sysroot = Path(tmp) / "sysroot"
        shutil.copytree(
            original, sysroot,
            ignore=lambda directory, names: excluded_sysroot_entries(original, directory, names),
        )
        for target, checksum in OFFICIAL_STD.items():
            archive = root / "tools" / f"rust-std-{target}.tar.xz"
            if digest(archive) != checksum:
                raise RuntimeError(f"Official standard library checksum mismatch: {target}")
            std = (root / "tools" / f"rust-std-1.94.1-{target}" / f"rust-std-{target}"
                   / "lib" / "rustlib" / target / "lib")
            destination = sysroot / "lib" / "rustlib" / target / "lib"
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(std, destination)
        provenance["evaluation_stdlib_sha256"] = OFFICIAL_STD
        package_contents(source, root, variant, build_dir, provenance, env, sysroot)


def package_contents(source, root, variant, build_dir, provenance, env, sysroot):
    compiler = sysroot / "bin" / "rustc.exe"
    version = subprocess.check_output([str(compiler), "-vV"], env=env, text=True)
    if RUST_SHA not in version or f"host: {HOST}" not in version or "LLVM version: 21.1.8" not in version:
        raise RuntimeError(f"Unexpected compiler identity:\n{version}")
    for target in (HOST, "wasm32-unknown-unknown"):
        if not list((sysroot / "lib" / "rustlib" / target / "lib").glob("libstd-*.rlib")):
            raise RuntimeError(f"Missing standard library: {target}")
    cache_path = source / build_dir / HOST / "llvm" / "build" / "CMakeCache.txt"
    cache = {}
    for line in cache_path.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith(("#", "//")) and ":" in line and "=" in line:
            key, value = line.split("=", 1)
            key = key.split(":", 1)[0]
            if key.startswith(("LLVM_", "CMAKE_CXX_COMPILER", "CMAKE_BUILD_TYPE", "CMAKE_AR")):
                cache[key] = value
    expected_lto = "Thin" if variant == "optimized" else "OFF"
    if cache.get("LLVM_ENABLE_LTO", "OFF").lower() != expected_lto.lower():
        raise RuntimeError("Actual LLVM LTO configuration differs from the experiment")
    if cache.get("LLVM_BUILD_INSTRUMENTED", "OFF") not in ("", "OFF"):
        raise RuntimeError("Final LLVM build is still instrumented")
    if variant == "optimized":
        profile_path = Path(cache.get("LLVM_PROFDATA_FILE", ""))
        if not profile_path.is_file() or digest(profile_path) != provenance["profiles"]["llvm-pgo.profdata"]["sha256"]:
            raise RuntimeError("Final LLVM build did not use its PGO profile")
        flag_log = provenance.get("compiler_flag_log", "optimized-pipeline.log")
        log = (root / "logs" / flag_log).read_text(encoding="utf-8", errors="replace")
        for flag in ("-Cprofile-use=", "-Clto=thin", "-Zdylib-lto"):
            if flag not in log:
                raise RuntimeError(f"Missing actual rustc build flag evidence: {flag}")
    elif cache.get("LLVM_PROFDATA_FILE"):
        raise RuntimeError("Baseline LLVM unexpectedly used a PGO profile")
    provenance["llvm_cmake_cache"] = cache
    if variant != "baseline-msvc" and not cache.get("CMAKE_AR", "").lower().endswith("llvm-lib.exe"):
        raise RuntimeError("LLVM build did not use the bitcode-capable librarian")
    probe = root / "final-compiler-check.rs"
    probe.write_text("pub fn add(a: u64, b: u64) -> u64 { a.wrapping_add(b) }\n")
    prefix = f"final-{variant}-{time.time_ns()}-"
    probe_env = {**env, "LLVM_PROFILE_FILE": str(root / "temp" / f"{prefix}%p.profraw")}
    subprocess.run([str(compiler), "--crate-type", "lib", "--emit=llvm-ir",
                    str(probe), "-o", str(root / "temp" / f"{variant}.ll")],
                   env=probe_env, check=True)
    if list((root / "temp").glob(f"{prefix}*.profraw")):
        raise RuntimeError("Final compiler is still PGO-instrumented")
    provenance["final_instrumentation_check"] = "Code generation produced no profiling output"
    provenance["tool_archive_sha256"] = {
        name: digest(root / "tools" / name) for name in (
            "LLVM-20.1.3-woa64.exe", "microsoft.windows.sdk.cpp.10.0.26100.9169.zip",
            "microsoft.windows.sdk.cpp.arm64.10.0.26100.9169.zip", "rustc-official.tar.xz",
        )
    }
    notices = (root / "tools" / f"rustc-1.94.1-{HOST}" / "rustc" / "share" / "doc" / "rust")
    if not (notices / "COPYRIGHT.html").is_file():
        raise FileNotFoundError("Extract official Rust 1.94.1 compiler license notices before packaging")
    shutil.copytree(notices, sysroot / "share" / "doc" / "rust", dirs_exist_ok=True)
    for name in ("COPYRIGHT", "LICENSE-MIT", "LICENSE-APACHE"):
        shutil.copy2(source / name, sysroot / name)
    provenance["rustc_version"] = version
    provenance["files"] = {
        str(p.relative_to(sysroot)): digest(p) for p in sorted(sysroot.rglob("*")) if p.is_file()
    }
    archive = root / f"{variant}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as output:
        for path in sorted(sysroot.rglob("*")):
            if path.is_file():
                output.write(path, path.relative_to(sysroot))
    provenance["archive_sha256"] = digest(archive)
    provenance["archive_bytes"] = archive.stat().st_size
    save(root / f"{variant}.json", provenance)
    print(f"PACKAGED {variant}: {archive.stat().st_size} bytes", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--msvc", type=Path, required=True)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--package-only", action="store_true")
    args = parser.parse_args()
    source, root, msvc = args.source.resolve(), args.root.resolve(), args.msvc.resolve()
    env = clean_environment(root, msvc)
    for relative, expected in ((".", RUST_SHA), ("src/llvm-project", LLVM_SHA),
                               ("src/tools/rustc-perf", PERF_SHA)):
        actual = subprocess.check_output(
            ["git", "-C", str(source / relative), "rev-parse", "HEAD"], env=env, text=True,
        ).strip()
        if actual != expected:
            raise RuntimeError(f"Wrong source revision for {relative}: {actual}")
    build_dir, config = configuration(root, msvc, args.variant, args.jobs)
    (source / "bootstrap.toml").write_text(config, encoding="utf-8")
    (root / f"{args.variant}.toml").write_text(config, encoding="utf-8")
    logs = root / "logs"
    logs.mkdir(exist_ok=True)
    fixture = root / "native-toolchain-check.c"
    fixture.write_text("#include <stdio.h>\nint main(void) { puts(\"ARM64 SDK OK\"); return 0; }\n")
    exe = root / "native-toolchain-check.exe"
    execute(["clang-cl.exe", str(fixture), f"/Fe{exe}", f"/Fo{root / 'native-toolchain-check.obj'}"],
            root, env, logs / "toolchain-check.log")
    subprocess.run([str(exe)], env=env, check=True)
    if args.prepare_only:
        return
    if args.package_only:
        provenance = json.loads((root / f"{args.variant}.json").read_text(encoding="utf-8"))
        package(source, root, args.variant, build_dir, provenance, env)
        return
    provenance = {
        "variant": args.variant, "rust_sha": RUST_SHA, "llvm_sha": LLVM_SHA,
        "rustc_perf_sha": PERF_SHA, "configuration": config,
        "clang": subprocess.check_output(
            [str(root / "tools" / "clang20" / "bin" / "clang-cl.exe"), "--version"],
            env=env, text=True,
        ),
        "sdk_package": "Microsoft.Windows.SDK.CPP(.arm64) 10.0.26100.9169",
        "common_build_deviations": [
            "Portable SDK and local MSVC version; compare rebuilt MSVC baseline to official compiler.",
            "DIA-based PDB reader disabled in every variant because ATL headers are absent.",
            "LLVM utility executables linked with LLD in every variant.",
            "Only compiler/native+WASM standard libraries packaged; no auxiliary Rust tools.",
        ],
        "msvc": msvc.name, "jobs": args.jobs,
        "started_unix": time.time(),
        "intervention": {
            "rust_pgo": args.variant == "optimized",
            "llvm_pgo": args.variant == "optimized",
            "rust_lto": "thin" if args.variant == "optimized" else "thin-local",
            "llvm_thin_lto": args.variant == "optimized",
            "rust_linker": "msvc" if args.variant == "baseline-msvc" else "lld-20.1.3",
        },
    }
    x = [sys.executable, "x.py"]
    build = x + ["build", "--stage", "2", "library/std"]
    if args.variant == "baseline-lld":
        # Bootstrap's LLVM stamp tracks source changes, not archiver configuration.
        (source / build_dir / HOST / "llvm" / ".llvm-stamp").unlink(missing_ok=True)
    if args.variant == "optimized":
        execute(x + ["build", "--set", "rust.debug=true", "opt-dist"], source, env,
                logs / "optimized-helper.log")
        provenance["training_lockfile_migration"] = prepare_training_lockfile(source, build_dir, env, logs)
        helper = source / build_dir / HOST / "stage1-tools-bin" / "opt-dist.exe"
        command = [
            str(helper), "local", "--target-triple", HOST, "--checkout-dir", str(source),
            "--llvm-dir", str(root / "tools" / "clang20"), "--python", sys.executable,
            "--artifact-dir", "opt-artifacts-ab", "--build-dir", build_dir,
            "--llvm-shared", "false", "--", *build,
        ]
        execute(command, source, env, logs / "optimized-pipeline.log")
        profiles = source / "opt-artifacts-ab"
        provenance["profiles"] = {}
        for name in ("rustc-pgo.profdata", "llvm-pgo.profdata"):
            path = profiles / name
            if not path.is_file() or not path.stat().st_size:
                raise RuntimeError(f"Missing trained profile: {path}")
            shutil.copy2(path, root / name)
            provenance["profiles"][name] = {"sha256": digest(path), "bytes": path.stat().st_size}
    else:
        execute(build, source, env, logs / f"{args.variant}-build.log")
    provenance["completed_unix"] = time.time()
    package(source, root, args.variant, build_dir, provenance, env)


if __name__ == "__main__":
    main()
