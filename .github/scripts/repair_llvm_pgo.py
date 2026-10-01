"""Relink static LLVM into rustc before PGO training, then build the final treatment."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from build_arm_compilers import (
    HOST, LLVM_SHA, PERF_SHA, RUST_SHA, clean_environment, configuration, digest,
    execute, package, save,
)

LLVM_CRATES = ["syn-2.0.101", "cargo-0.87.1", "serde-1.0.219", "ripgrep-14.1.1",
               "regex-automata-0.4.8", "clap_derive-4.5.32", "hyper-1.6.0"]


def coverage(profdata, profile, env):
    result = {}
    for part in ("AArch64TargetLowering", "InstCombine"):
        text = subprocess.check_output(
            [str(profdata), "show", f"--function={part}", "--counts", str(profile)],
            env=env, text=True,
        )
        rows = [json.loads(line.split(":", 1)[1]) for line in text.splitlines()
                if line.startswith("    Block counts:")]
        result[part] = {
            "functions": len(rows), "nonzero_functions": sum(any(row) for row in rows),
            "max_block_count": max((max(row, default=0) for row in rows), default=0),
        }
        if result[part]["nonzero_functions"] == 0:
            raise RuntimeError(f"PGO profile did not exercise {part}: {profile}")
    return result


def archive_llvm(build_root, suffix):
    for name in ("llvm", "lld"):
        directory = build_root / name
        if directory.exists():
            destination = build_root / f"{name}-{suffix}"
            if destination.exists():
                raise FileExistsError(destination)
            directory.rename(destination)


def trimmed_configuration(source, root, msvc):
    build_dir, config = configuration(root, msvc, "optimized", 8)
    # These standalone executables are not part of rustc's linked LLVM libraries.
    disabled = []
    for directory in sorted((source / "src" / "llvm-project" / "llvm" / "tools").iterdir()):
        if (directory / "CMakeLists.txt").is_file() and directory.name not in (
            "llvm-config", "llvm-profdata", "llvm-dwarfdump",
        ):
            disabled.append("LLVM_TOOL_" + directory.name.upper().replace("-", "_") + "_BUILD")
    settings = "".join(f'{name} = "OFF"\n' for name in disabled)
    settings += 'LLVM_TOOL_LLVM_DWARFDUMP_BUILD = "ON"\n'
    config = config.replace("[rust]\n", settings + "[rust]\n")
    config = config.replace("llvm-tools = true", "llvm-tools = false")
    return build_dir, config, disabled


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--msvc", type=Path, required=True)
    args = parser.parse_args()
    source, root = args.source.resolve(), args.root.resolve()
    env = clean_environment(root, args.msvc.resolve())
    for relative, expected in ((".", RUST_SHA), ("src/llvm-project", LLVM_SHA),
                               ("src/tools/rustc-perf", PERF_SHA)):
        if subprocess.check_output(
            ["git", "-C", str(source / relative), "rev-parse", "HEAD"], text=True,
        ).strip() != expected:
            raise RuntimeError(f"Wrong source revision: {relative}")
    patch = Path(__file__).resolve().parents[2] / "ci-benchmark" / "bootstrap-clang-runtime.patch"
    subprocess.run(["git", "-C", str(source), "apply", "--reverse", "--check",
                    "--ignore-space-change", str(patch)],
                   check=True)
    work = root / "corrected-llvm-pgo"
    work.mkdir(exist_ok=True)
    state_path = work / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    logs = root / "logs"
    build_dir, config, disabled = trimmed_configuration(source, root, args.msvc.resolve())
    (source / "bootstrap.toml").write_text(config, encoding="utf-8")
    (root / "optimized-v2.toml").write_text(config, encoding="utf-8")
    build_root = source / build_dir / HOST
    stage0 = build_root / "stage0" / "bin"
    compiler = build_root / "stage2" / "bin" / "rustc.exe"
    profdata = root / "tools" / "clang20" / "bin" / "llvm-profdata.exe"
    rust_profile = root / "rustc-pgo-stage1-checkpoint.profdata"
    if digest(rust_profile) != "845ad4391e281c559ef66e2f6ab2ec1fbcc3c60f5fcdc9e6e6ccac0b20ab4bbc":
        raise RuntimeError("Wrong validated frontend profile")
    x = [sys.executable, "x.py", "build", "--stage", "2", "library/std",
         "--rust-profile-use", str(rust_profile), "--keep-stage", "0"]
    profile = work / "llvm-pgo.profdata"
    if not state.get("instrumented"):
        if not state.get("instrumentation_started"):
            archive_llvm(build_root, "before-corrected-training")
            state["instrumentation_started"] = True
            save(state_path, state)
        build_raw = work / "build-raw"
        build_raw.mkdir(exist_ok=True)
        execute(x + ["--llvm-profile-generate"], source,
                {**env, "LLVM_PROFILE_DIR": str(build_raw / "prof-%p")},
                logs / "optimized-v2-instrument.log")
        smoke = work / "smoke"
        smoke.mkdir(exist_ok=True)
        program = smoke / "probe.rs"
        program.write_text("pub fn sum(xs: &[u64]) -> u64 { xs.iter().copied().sum() }\n")
        execute([str(compiler), "--crate-type", "lib", "-O", str(program),
                 "-o", str(smoke / "probe.rlib")], source,
                {**env, "LLVM_PROFILE_FILE": str(smoke / "counter-%m-%p.profraw")},
                logs / "optimized-v2-instrument-smoke.log")
        raw = sorted(smoke.glob("*.profraw"))
        if not raw:
            raise RuntimeError("Relinked compiler did not emit any LLVM instrumentation profile")
        smoke_profile = smoke / "smoke.profdata"
        execute([str(profdata), "merge", "-o", str(smoke_profile), *map(str, raw)],
                source, env, logs / "optimized-v2-smoke-merge.log")
        state["instrumentation_smoke_coverage"] = coverage(profdata, smoke_profile, env)
        state["instrumented"] = True
        save(state_path, state)
    if not state.get("trained"):
        attempt = state.get("training_attempt", 0) + 1
        state["training_attempt"] = attempt
        save(state_path, state)
        raw_dir = work / f"training-raw-{attempt}"
        raw_dir.mkdir(exist_ok=False)
        training_env = {
            **env, "RUSTC": str(stage0 / "rustc.exe"), "RUSTC_BOOTSTRAP": "1",
            "LLVM_PROFILE_FILE": str(raw_dir / "counter-%m-%p.profraw"),
        }
        command = [
            str(stage0 / "cargo.exe"), "run", "-p", "collector", "--bin", "collector",
            "--", "profile_local", "eprintln", str(compiler), "--id", "Test",
            "--cargo", str(stage0 / "cargo.exe"), "--profiles", "Debug,Opt",
            "--scenarios", "Full", "--exact-match", ",".join(LLVM_CRATES),
        ]
        execute(command, source / "opt-artifacts-ab" / "rustc-perf", training_env,
                logs / f"optimized-v2-training-{attempt}.log")
        execute([str(profdata), "merge", "-o", str(profile), str(raw_dir)],
                source, env, logs / "optimized-v2-merge.log")
        state["training_coverage"] = coverage(profdata, profile, env)
        state["profile_sha256"] = digest(profile)
        state["profile_files"] = len(list(raw_dir.glob("*.profraw")))
        state["trained"] = True
        save(state_path, state)
    if not state.get("built"):
        if not state.get("final_started"):
            archive_llvm(build_root, "corrected-instrumented")
            state["final_started"] = True
            save(state_path, state)
        execute(x + ["--llvm-profile-use", str(profile)], source, env,
                logs / "optimized-v2-final.log")
        state["built"] = True
        save(state_path, state)
    old_provenance = root / "optimized-invalid-v1.json"
    if not old_provenance.exists():
        shutil.copy2(root / "optimized.json", old_provenance)
        (root / "optimized.zip").rename(root / "optimized-invalid-v1.zip")
    provenance = json.loads(old_provenance.read_text())
    provenance.update({
        "configuration": config, "completed_unix": time.time(),
        "clang": subprocess.check_output(
            [str(root / "tools" / "clang20" / "bin" / "clang-cl.exe"), "--version"],
            env=env, text=True,
        ),
        "compiler_flag_log": "optimized-v2-final.log",
        "bootstrap_only_patch": {
            "file": patch.name, "sha256": digest(patch),
            "reason": "Run read-only clang runtime lookup during bootstrap dry-run; no compiler/LLVM code changes",
        },
        "llvm_training_repair": state,
        "unbuilt_standalone_llvm_tools": disabled,
        "note": "Static LLVM relinked into rustc for training; all LLVM libraries/backends retained.",
    })
    for name, path in (("rustc-pgo.profdata", rust_profile), ("llvm-pgo.profdata", profile)):
        shutil.copy2(path, root / name)
        provenance["profiles"][name] = {"sha256": digest(path), "bytes": path.stat().st_size}
    components = subprocess.check_output(
        [str(build_root / "llvm" / "bin" / "llvm-config.exe"), "--components"], env=env, text=True,
    ).split()
    original_components = subprocess.check_output(
        [str(build_root / "llvm-before-corrected-training" / "bin" / "llvm-config.exe"),
         "--components"], env=env, text=True,
    ).split()
    if components != original_components:
        raise RuntimeError("LLVM library components changed when standalone tools were excluded")
    provenance["unchanged_llvm_library_components"] = components
    package(source, root, "optimized", build_dir, provenance, env)
    state["packaged"] = True
    save(state_path, state)


if __name__ == "__main__":
    main()
