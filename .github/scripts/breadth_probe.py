"""Run one non-qualifying breadth smoke scenario using the existing native meter."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

from breadth_audit import git, sha256
from native_ci_probe import build_environment, telemetry_executables
from process_metrics import measure, measurement_session


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def cargo_artifacts(text, mode):
    fresh = compiled = 0
    finished = []
    for line in text.splitlines():
        event = json.loads(line)
        if event.get("reason") == "compiler-artifact":
            if type(event.get("fresh")) is not bool:
                raise ValueError("missing Cargo artifact freshness")
            if event["fresh"]:
                fresh += 1
            else:
                compiled += 1
        elif event.get("reason") == "build-finished":
            finished.append(event.get("success"))
    if finished != [True]:
        raise ValueError("missing or failed Cargo build-finished")
    if mode not in ("full", "noop", "edit"):
        raise ValueError("unknown scenario mode")
    if mode == "noop":
        if compiled or not fresh:
            raise ValueError("no-op must reuse artifacts without compiling")
    elif not compiled:
        raise ValueError("full/edit scenario compiled no artifacts")
    return {"fresh_artifacts": fresh, "compiled_artifacts": compiled}


def verify_source(source, project):
    if git(source, "rev-parse", "HEAD").decode().strip() != project["revision"]:
        raise ValueError("wrong source revision")
    if git(source, "status", "--porcelain", "--untracked-files=all").strip():
        raise ValueError("source must be clean, including untracked files")
    if sha256((source / "Cargo.lock").read_bytes()) != project["lock_sha256"]:
        raise ValueError("wrong source lockfile")
    return sha256(git(source, "ls-files", "-s"))


def compiler_environment(base, compiler, cores, incremental):
    for name, value in base.items():
        key = name.upper()
        if value and (key.startswith("CARGO_PROFILE_") or key.startswith("CARGO_TARGET_")
                      or key in ("RUSTDOC", "RUSTUP_TOOLCHAIN", "RUSTC_BOOTSTRAP")):
            raise ValueError(f"unregistered compiler override: {name}")
    env = build_environment(base, compiler, cores)
    # Preserve each project's original debug information and release profile settings.
    env.pop("CARGO_PROFILE_DEV_DEBUG", None)
    env["CARGO_INCREMENTAL"] = incremental
    return env


def metered(command, source, env, cores, prefix, background):
    # A new Job for every command makes its memory peak independent of setup/correctness.
    with measurement_session(background) as session:
        row = measure(command, source, env, cores, prefix, session=session, timeout=1800)
    save(prefix.with_suffix(".measurement.json"), row)
    if row["exit_code"]:
        raise RuntimeError(f"command failed: {prefix.name}")
    return row


def run_scenario(source, output, project, scenario, cargo, compiler, env, cores,
                 background=(), identity=None, target=None):
    if scenario["mode"] not in ("full", "noop", "edit"):
        raise ValueError("unknown scenario mode")
    if source == output or source in output.parents:
        raise ValueError("output must be outside the source tree")
    input_identity = verify_source(source, project)
    output.mkdir(exist_ok=False, parents=True)
    target_directory = output / "target"
    if target_directory.exists():
        raise ValueError("scenario requires a fresh target")
    command = [str(cargo), *scenario["cargo_command"], *project["cargo_args"],
               "--frozen", "--message-format=json"]
    target_args = ["--target", target] if target else []
    command.extend(target_args)
    child_env = {**env, "CARGO_TARGET_DIR": str(target_directory)}
    result = {
        "schema": 1, "status": "non-qualifying-smoke", "project": project["id"],
        "scenario": scenario, "source_revision": project["revision"],
        "lock_sha256": project["lock_sha256"], "git_index_sha256": input_identity,
        "compiler": str(compiler), "cargo": str(cargo), "target": target,
        "setup": [], "correctness": [],
        "tool_identity": identity or {},
        "environment": {key: env.get(key) for key in (
            "CARGO_INCREMENTAL", "CARGO_NET_OFFLINE", "CARGO_BUILD_JOBS",
            "CARGO_HOME", "RUSTC", "RUSTDOC", "MSBUILDDISABLENODEREUSE",
        )},
        "memory_scope": "fresh Windows Job per command; committed bytes, not RSS",
        "cpu_scope": "whole command process tree, not rustc-only",
    }
    edit = source.joinpath(*project["source_edit"].split("/"))
    if not edit.resolve().is_relative_to(source.resolve()):
        raise ValueError("source edit escapes source tree")
    before = edit.read_bytes()
    result["edit_original_sha256"] = sha256(before)
    changed = False
    try:
        if scenario["mode"] in ("noop", "edit"):
            setup = metered(command, source, child_env, cores, output / "seed", background)
            setup.update(cargo_artifacts((output / "seed.stdout").read_text(encoding="utf-8"), "full"))
            result["setup"].append(setup)
        if scenario["mode"] == "edit":
            edit.write_bytes(before + b"\n// breadth incremental comment-only edit\n")
            changed = True
            result["edit_modified_sha256"] = sha256(edit.read_bytes())
        row = metered(command, source, child_env, cores, output / "measured", background)
        row.update(cargo_artifacts((output / "measured.stdout").read_text(encoding="utf-8"),
                                   scenario["mode"]))
        result["measurement"] = row
        for index, args in enumerate(project["correctness"]):
            check = metered([str(cargo), *args, "--frozen", *target_args], source,
                            {**env, "CARGO_TARGET_DIR": str(output / "correctness-target")},
                            cores, output / f"correctness-{index}", background)
            result["correctness"].append(check)
    except Exception as error:
        result["status"] = "failed-non-qualifying-smoke"
        result["failure"] = str(error)
        raise
    finally:
        if changed:
            edit.write_bytes(before)
        try:
            if verify_source(source, project) != input_identity:
                raise ValueError("source identity changed")
        except Exception as error:
            result["status"] = "failed-non-qualifying-smoke"
            result["input_integrity_failure"] = str(error)
            raise
        finally:
            save(output / "results.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("manifest", "source", "output", "cargo", "compiler", "rustdoc"):
        parser.add_argument(f"--{key}", type=Path, required=True)
    for key in ("project", "scenario", "compiler-sha256", "cargo-sha256", "rustdoc-sha256"):
        parser.add_argument(f"--{key}", required=True)
    parser.add_argument("--non-qualifying-smoke", action="store_true", required=True)
    args = parser.parse_args()
    if os.name != "nt":
        raise ValueError("Windows x64 smoke harness only")
    manifest = json.loads(args.manifest.read_text())
    project = next(p for p in manifest["projects"] if p["id"] == args.project)
    scenario = next(s for s in manifest["scenarios"] if s["id"] == args.scenario)
    cargo, compiler, rustdoc = args.cargo.resolve(), args.compiler.resolve(), args.rustdoc.resolve()
    for path, expected in ((cargo, args.cargo_sha256), (compiler, args.compiler_sha256),
                           (rustdoc, args.rustdoc_sha256)):
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"executable hash mismatch: {path}")
    env = compiler_environment(os.environ, compiler, manifest["cores"], scenario["incremental"])
    env["RUSTDOC"] = str(rustdoc)
    version = subprocess.check_output([str(compiler), "-vV"], text=True, env=env)
    for expected in (f"host: {manifest['host']}", f"release: {manifest['rust_version']}",
                     f"commit-hash: {manifest['training']['rust_sha']}"):
        if expected not in version.splitlines():
            raise ValueError("wrong compiler identity")
    identity = {
        "executable_sha256": {"rustc": args.compiler_sha256, "cargo": args.cargo_sha256,
                              "rustdoc": args.rustdoc_sha256},
        "rustdoc": str(rustdoc), "rustc_verbose_version": version,
        "cargo_version": subprocess.check_output([str(cargo), "-V"], text=True, env=env).strip(),
        "manifest_sha256": sha256(args.manifest.read_bytes()),
    }
    run_scenario(args.source.resolve(), args.output.resolve(), project, scenario,
                 cargo, compiler, env, manifest["cores"], telemetry_executables(), identity)


if __name__ == "__main__":
    main()
