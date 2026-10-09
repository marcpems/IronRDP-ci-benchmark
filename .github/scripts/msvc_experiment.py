"""Compiler-only PGO experiment with native Microsoft linking tools throughout."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile

from build_arm_compilers import digest, excluded_sysroot_entries, save
from native_ci_probe import telemetry_executables
from process_metrics import measure, measurement_session

VARIANTS = ("baseline", "pgo", "pgo-rust-thin")
PHASES = ("rustc-profile", "llvm-profile", *VARIANTS)


def configuration(host, clang, link, librarian, phase, profiles):
    pgo = phase in ("llvm-profile", "pgo", "pgo-rust-thin")
    rustc_use = f'use = "{(profiles / "rustc-pgo.profdata").as_posix()}"' if pgo else ""
    rustc_generate = f'generate = "{(profiles / "rustc-raw").as_posix()}"' if phase == "rustc-profile" else ""
    llvm_generate = f'generate = "{(profiles / "llvm-raw" / "prof-%p").as_posix()}"' if phase == "llvm-profile" else ""
    llvm_use = f'use = "{(profiles / "llvm-pgo.profdata").as_posix()}"' if phase in ("pgo", "pgo-rust-thin") else ""
    return f"""profile = "dist"
[build]
build = "{host}"
host = ["{host}"]
target = ["{host}"]
submodules = false
jobs = 4
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
clang-cl = "{(clang / 'clang-cl.exe').as_posix()}"
optimize = true
assertions = false
ninja = true
link-jobs = 1
thin-lto = false
link-shared = false
[rust]
channel = "nightly"
download-rustc = false
optimize = true
debug-assertions = false
overflow-checks = false
codegen-units = {1 if host.startswith('x86_64') else 16}
codegen-units-std = 1
debuginfo-level-std = 1
remap-debuginfo = true
codegen-backends = ["llvm"]
lld = true
llvm-tools = true
llvm-bitcode-linker = false
lto = "{'thin' if phase == 'pgo-rust-thin' else 'thin-local'}"
[target.{host}]
linker = "{link.name}"
ar = "{librarian.as_posix()}"
[pgo.rustc]
{rustc_use}
{rustc_generate}
[pgo.llvm]
{llvm_use}
{llvm_generate}
"""


def tool_identity(clang):
    tools = {name: Path(shutil.which(name) or "") for name in
             ("cl.exe", "link.exe", "lib.exe", "cmake.exe", "ninja.exe")}
    tools.update({name: clang / name for name in ("clang-cl.exe", "llvm-profdata.exe")})
    for name, path in tools.items():
        if not path.is_file():
            raise RuntimeError(f"Missing native tool {name}: {path}")
    if "microsoft visual studio" not in str(tools["link.exe"]).lower():
        raise RuntimeError("link.exe is not from Microsoft Visual Studio")
    return {
        "files": {name: {"path": str(path), "sha256": digest(path)} for name, path in tools.items()},
        "msvc": os.environ["VCToolsVersion"],
        "sdk": os.environ["WindowsSDKVersion"],
        "image": os.environ.get("ImageVersion"),
    }


def equivalent_tools(left, right):
    return (left["msvc"] == right["msvc"] and left["sdk"] == right["sdk"]
            and {k: v["sha256"] for k, v in left["files"].items()}
            == {k: v["sha256"] for k, v in right["files"].items()})


def environment(output, clang):
    allowed = {
        "PATH", "SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "COMSPEC", "PATHEXT",
        "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE", "PROGRAMFILES", "PROGRAMFILES(X86)",
        "PROGRAMW6432", "INCLUDE", "LIB", "LIBPATH", "VCTOOLSINSTALLDIR", "VCINSTALLDIR",
        "VSINSTALLDIR", "WINDOWSSDKDIR", "WINDOWSSDKVERSION", "UCRTVERSION",
        "UNIVERSALCRTSDKDIR", "VSCMD_ARG_HOST_ARCH", "VSCMD_ARG_TGT_ARCH",
        "WINDOWSSDKBINPATH", "WINDOWSSDKVERBINPATH", "VCTOOLSVERSION", "VISUALSTUDIOVERSION",
    }
    env = {k: v for k, v in os.environ.items() if k.upper() in allowed}
    home, temp = output / "home", output / "scratch"
    for p in (home, temp, home / "AppData/Local", home / "AppData/Roaming"):
        p.mkdir(parents=True, exist_ok=True)
    env.update({
        "PATH": str(clang) + os.pathsep + env["PATH"],
        "HOME": str(home), "USERPROFILE": str(home),
        "APPDATA": str(home / "AppData/Roaming"), "LOCALAPPDATA": str(home / "AppData/Local"),
        "TEMP": str(temp), "TMP": str(temp), "CARGO_HOME": str(output / "cargo-home"),
        "CARGO_INCREMENTAL": "0", "RUST_BACKTRACE": "1", "RUSTC_BOOTSTRAP": "1",
        "PYTHONDONTWRITEBYTECODE": "1", "MSBUILDDISABLENODEREUSE": "1",
        "GIT_CONFIG_COUNT": "2", "GIT_CONFIG_KEY_0": "core.longpaths",
        "GIT_CONFIG_VALUE_0": "true", "GIT_CONFIG_KEY_1": "core.autocrlf",
        "GIT_CONFIG_VALUE_1": "false",
    })
    return env


def execute(command, cwd, env, output, name, timeout=19500, expected_success=True):
    print(f"START {name}", flush=True)
    with measurement_session(telemetry_executables()) as session:
        result = measure(list(map(str, command)), cwd, env, 4, output / name,
                         session=session, timeout=timeout)
    save(output / f"{name}.json", result)
    if (result["exit_code"] == 0) != expected_success:
        for suffix in (".stdout", ".stderr"):
            print((output / name).with_suffix(suffix).read_text(errors="replace")[-12000:])
        raise RuntimeError(f"{name}: unexpected exit code {result['exit_code']}")
    print(f"DONE {name}: wall={result['wall_seconds']:.2f}s cpu={result['cpu_seconds']:.2f}s", flush=True)
    return result


def coverage(profdata, profile, components, env, output):
    result = {}
    for name in components:
        text = subprocess.check_output(
            [str(profdata), "show", f"--function={name}", "--counts", str(profile)],
            env=env, text=True,
        )
        (output / f"coverage-{name}.txt").write_text(text, encoding="utf-8")
        counts = [json.loads(line.split(":", 1)[1]) for line in text.splitlines()
                  if line.strip().startswith("Block counts:")]
        result[name] = {"functions": len(counts), "active_functions": sum(any(row) for row in counts)}
        if not result[name]["active_functions"]:
            raise RuntimeError(f"No executed {name} functions in {profile}")
    return result


def training_crates(source, backend):
    text = (source / "src/build_helper/src/lib.rs").read_text()
    name = "BACKEND_PGO_CRATES" if backend else "RUSTC_PGO_CRATES"
    match = re.search(rf"pub const {name}:.*?= &\[(.*?)\];", text, re.S)
    if match is None:
        raise RuntimeError(f"Cannot locate upstream training list {name}")
    return re.findall(r'"([^"]+)"', match[1])


def preflight(output, clang, env, identity):
    fixture = output / "linker-fixture"
    fixture.mkdir()
    (fixture / "a.c").write_text("int add(int x) { return x + 1; }\n")
    (fixture / "b.c").write_text("extern int add(int); int main(void) { return add(41) != 42; }\n")
    cases = [
        ("clang-native", clang / "clang-cl.exe", [], [], True),
        ("clang-thin", clang / "clang-cl.exe", ["-flto=thin"], [], False),
        ("clang-thin-ltcg", clang / "clang-cl.exe", ["-flto=thin"], ["/LTCG"], False),
        ("msvc-ltcg", Path(identity["files"]["cl.exe"]["path"]), ["/GL"], ["/LTCG"], True),
    ]
    rows = []
    for name, compiler, ccflags, ldflags, expected in cases:
        objects = []
        for src in ("a", "b"):
            obj = fixture / f"{name}-{src}.obj"
            execute([compiler, "/nologo", "/O2", "/MD", "/c", fixture / f"{src}.c",
                     f"/Fo{obj}", *ccflags], fixture, env, output, f"preflight-{name}-{src}", timeout=120)
            objects.append(obj)
        exe = fixture / f"{name}.exe"
        result = execute([identity["files"]["link.exe"]["path"], "/nologo", *objects,
                          f"/out:{exe}", *ldflags], fixture, env, output,
                         f"preflight-{name}-link", timeout=120, expected_success=expected)
        if expected:
            execute([exe], fixture, env, output, f"preflight-{name}-run", timeout=30)
        else:
            text = (output / f"preflight-{name}-link.stdout").read_text(errors="replace")
            text += (output / f"preflight-{name}-link.stderr").read_text(errors="replace")
            if not re.search(r"LNK1107|invalid or corrupt|unrecognized file", text, re.I):
                raise RuntimeError("LLVM bitcode rejection did not fail for the expected format reason")
        rows.append({"case": name, "link_succeeded": result["exit_code"] == 0,
                     "expected_success": expected})
    save(output / "preflight.json", rows)


def train(source, output, host, env, backend, clang):
    build = source / "build" / host
    stage0 = build / "stage0/bin"
    training = output / "training"
    shutil.copytree(source / "src/tools/rustc-perf", training, ignore=shutil.ignore_patterns(".git", "target"))
    raw = output / ("llvm-raw" if backend else "rustc-raw")
    raw.mkdir(exist_ok=True)
    child = {**env, "RUSTC": str(stage0 / "rustc.exe"),
             "LLVM_PROFILE_FILE": str(raw / "default_%m_%p.profraw")}
    fixture = training / "collector/compile-benchmarks/token-stream-stress"
    before = tomllib.loads((fixture / "Cargo.lock").read_text())
    execute([stage0 / "cargo.exe", "generate-lockfile", "--offline"], fixture, child,
            output, "training-lockfile", timeout=120)
    after = tomllib.loads((fixture / "Cargo.lock").read_text())
    if before["package"] != after["package"]:
        raise RuntimeError("Training lockfile migration changed the dependency graph")
    crates = training_crates(source, backend)
    command = [
        stage0 / "cargo.exe", "run", "--locked", "-p", "collector", "--bin", "collector", "--",
        "profile_local", "eprintln", build / "stage2/bin/rustc.exe", "--id", "MSVC-experiment",
        "--cargo", stage0 / "cargo.exe",
        "--profiles", "Debug,Opt" if backend else "Check,Debug,Opt",
        "--scenarios", "Full" if backend else "All", "--exact-match", ",".join(crates),
        "--frontend-threads", "1", "--jobs", "4",
    ]
    execute(command, training, child, output, "training", timeout=5400)
    if not list(raw.rglob("*.profraw")):
        raise RuntimeError("Training emitted no raw profiles")
    profdata = clang / "llvm-profdata.exe" if backend else build / "llvm/build/bin/llvm-profdata.exe"
    merged = output / ("llvm-pgo.profdata" if backend else "rustc-pgo.profdata")
    execute([profdata, "merge", "-o", merged, raw], source, env, output, "merge", timeout=600)
    if backend:
        components = ["X86TargetLowering" if host.startswith("x86_64") else "AArch64TargetLowering", "InstCombine"]
    else:
        components = ["rustc_middle", "rustc_mir_transform"]
    return {"crates": crates, "cargo": "pinned stage0 (uninstrumented, compiler-only experiment)",
            "token_stream_lockfile_sha256": digest(fixture / "Cargo.lock"),
            "coverage": coverage(profdata, merged, components, env, output)}


def verify_profiles(root, phase, identity, source_sha, host):
    metadata = json.loads((root / "metadata.json").read_text())
    expected = "rustc-profile" if phase == "llvm-profile" else "llvm-profile"
    if metadata["phase"] != expected or metadata["rust_sha"] != source_sha or metadata["host"] != host:
        raise RuntimeError("Profiles do not belong to this experiment/source/host")
    if not equivalent_tools(identity, metadata["tools"]):
        raise RuntimeError("Native compiler/linker/librarian/SDK versions changed between jobs")
    for name, expected_hash in metadata["profiles"].items():
        if digest(root / name) != expected_hash:
            raise RuntimeError(f"Profile hash mismatch: {name}")
    return metadata


def audit_build(source, host, phase, output, identity):
    cache_path = source / "build" / host / "llvm/build/CMakeCache.txt"
    cache = {}
    for line in cache_path.read_text().splitlines():
        if line and not line.startswith(("#", "//")) and ":" in line and "=" in line:
            name, value = line.split("=", 1)
            cache[name.split(":", 1)[0]] = value
    if cache.get("LLVM_ENABLE_LTO", "OFF").upper() not in ("", "OFF"):
        raise RuntimeError("LLVM LTO unexpectedly enabled")
    if digest(Path(cache["CMAKE_LINKER"])) != identity["files"]["link.exe"]["sha256"]:
        raise RuntimeError("LLVM CMake is not using the pinned Microsoft linker")
    if digest(Path(cache["CMAKE_AR"])) != identity["files"]["lib.exe"]["sha256"]:
        raise RuntimeError("LLVM CMake is not using the pinned Microsoft librarian")
    if digest(Path(cache["CMAKE_CXX_COMPILER"])) != identity["files"]["clang-cl.exe"]["sha256"]:
        raise RuntimeError("LLVM C++ compiler changed")
    expected_instrumented = phase == "llvm-profile"
    instrumented = cache.get("LLVM_BUILD_INSTRUMENTED", "OFF") not in ("", "OFF")
    if instrumented != expected_instrumented:
        raise RuntimeError("LLVM instrumentation state is incorrect")
    if phase in ("pgo", "pgo-rust-thin"):
        if digest(Path(cache["LLVM_PROFDATA_FILE"])) != digest(output / "llvm-pgo.profdata"):
            raise RuntimeError("LLVM did not use the verified profile")
    log = (output / "build.stdout").read_text(errors="replace") + (output / "build.stderr").read_text(errors="replace")
    # Building the shipped rust-lld tool is not the same as using it to link rustc.
    if re.search(r"-C\s*linker=[^\r\n]*lld-link", log, re.I):
        raise RuntimeError("Unexpected lld-link selection for a Rust compilation")
    if phase == "pgo-rust-thin" and ("-Clto=thin" not in log or "-Zdylib-lto" not in log):
        raise RuntimeError("No evidence that Rust-side dylib ThinLTO was enabled")
    if phase in ("pgo", "pgo-rust-thin") and "-Cprofile-use=" not in log:
        raise RuntimeError("No evidence of rustc PGO use")
    shutil.copy2(cache_path, output / "CMakeCache.txt")
    save(output / "audit.json", {"llvm_lto": False, "microsoft_linker": True,
                               "clang_cpp_compiler": True, "rust_thin_lto": phase == "pgo-rust-thin"})


def package(source, output, host, env, metadata):
    stage = source / "build" / host / "stage2"
    with tempfile.TemporaryDirectory(prefix="compiler-package-", dir=output) as temp:
        sysroot = Path(temp) / "sysroot"
        shutil.copytree(stage, sysroot, ignore=lambda p, names: excluded_sysroot_entries(stage, p, names))
        if metadata["phase"] == "baseline":
            shutil.copy2(source / "build" / host / "stage0/bin/cargo.exe", sysroot / "bin/cargo.exe")
        for name in ("COPYRIGHT", "LICENSE-MIT", "LICENSE-APACHE"):
            shutil.copy2(source / name, sysroot / name)
        compiler = sysroot / "bin/rustc.exe"
        version = subprocess.check_output([compiler, "-vV"], env=env, text=True)
        if f"host: {host}" not in version or f"commit-hash: {metadata['rust_sha']}" not in version:
            raise RuntimeError("Wrong packaged compiler identity")
        probe = Path(temp) / "smoke.rs"
        probe.write_text("fn main() { assert_eq!((0..10).sum::<u32>(), 45); }\n")
        child = {**env, "LLVM_PROFILE_FILE": str(Path(temp) / "unexpected-%m-%p.profraw")}
        execute([compiler, probe, "-C", f"linker={metadata['tools']['files']['link.exe']['path']}",
                 "-o", Path(temp) / "smoke.exe"], source, child, output, "smoke-compile", timeout=120)
        execute([Path(temp) / "smoke.exe"], source, child, output, "smoke-run", timeout=120)
        if list(Path(temp).glob("*.profraw")):
            raise RuntimeError("Final toolchain still emits profiling instrumentation")
        metadata["rustc_version"] = version
        metadata["files"] = {p.relative_to(sysroot).as_posix(): digest(p)
                             for p in sorted(sysroot.rglob("*")) if p.is_file()}
        archive = output / "compiler.zip"
        with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED, compresslevel=1) as package_file:
            for p in sorted(sysroot.rglob("*")):
                if p.is_file():
                    package_file.write(p, p.relative_to(sysroot))
        metadata["archive_sha256"] = digest(archive)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--clang", type=Path, required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--phase", choices=PHASES, required=True)
    parser.add_argument("--profiles", type=Path)
    args = parser.parse_args()
    machine = platform.machine().lower()
    expected = ("arm64", "aarch64") if args.host.startswith("aarch64") else ("amd64", "x86_64")
    if os.name != "nt" or machine not in expected or os.cpu_count() != 4:
        parser.error("Use a native standard four-vCPU Windows runner")
    source, output, clang = args.source.resolve(), args.output.resolve(), args.clang.resolve()
    output.mkdir(parents=True, exist_ok=False)
    identity = tool_identity(clang)
    env = environment(output, clang)
    source_sha = subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip()
    metadata = {
        "phase": args.phase, "host": args.host, "rust_sha": source_sha, "tools": identity,
        "run_id": os.environ["GITHUB_RUN_ID"], "attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "profiles": {}, "scope": "compiler-only, not release packaging or full tool PGO",
        "llvm_sha": subprocess.check_output(["git", "-C", source / "src/llvm-project", "rev-parse", "HEAD"], text=True).strip(),
        "perf_sha": subprocess.check_output(["git", "-C", source / "src/tools/rustc-perf", "rev-parse", "HEAD"], text=True).strip(),
    }
    save(output / "started.json", metadata)
    if args.phase == "baseline":
        preflight(output, clang, env, identity)
    if args.phase in ("llvm-profile", "pgo", "pgo-rust-thin"):
        if args.profiles is None:
            parser.error("This phase requires verified profiles")
        parent = verify_profiles(args.profiles, args.phase, identity, source_sha, args.host)
        metadata["profile_parent_sha256"] = digest(args.profiles / "metadata.json")
        metadata["training"] = parent["training"]
        for name in parent["profiles"]:
            shutil.copy2(args.profiles / name, output / name)
    config = configuration(args.host, clang, Path(identity["files"]["link.exe"]["path"]),
                           Path(identity["files"]["lib.exe"]["path"]), args.phase, output)
    (source / "bootstrap.toml").write_text(config, encoding="utf-8")
    (output / "bootstrap.toml").write_text(config, encoding="utf-8")
    targets = args.host + (",wasm32-unknown-unknown" if args.phase == "baseline" else "")
    command = [sys.executable, "x.py", "build", "--stage", "2", "--host", args.host,
               "--target", targets, "library/std"]
    if args.phase == "baseline":
        command.append("rustdoc")
    execute(command, source, env, output, "build")
    audit_build(source, args.host, args.phase, output, identity)
    metrics = source / "build/metrics.json"
    if metrics.is_file():
        shutil.copy2(metrics, output / "bootstrap-metrics.json")
    if args.phase.endswith("-profile"):
        metadata.setdefault("training", {})[args.phase] = train(
            source, output, args.host, env, args.phase == "llvm-profile", clang)
    metadata["profiles"] = {p.name: digest(p) for p in output.glob("*.profdata")}
    if args.phase in VARIANTS:
        package(source, output, args.host, env, metadata)
    save(output / "metadata.json", metadata)


if __name__ == "__main__":
    main()
