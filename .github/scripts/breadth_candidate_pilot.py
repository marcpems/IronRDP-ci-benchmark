"""Run the bounded fd pilot from a pinned, already-qualified custom distribution."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tomllib

from breadth_probe import compiler_environment, run_scenario, save, verify_source
from compiler_probe import validate_meter
from install_optimized_rust import download
from native_ci_probe import telemetry_executables


def digest(path):
    import hashlib
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def checked_candidate(retained, selection):
    evidence = retained / "e"
    for name, key in (("result.json", "result_sha256"),
                      ("dist-manifest.json", "dist_manifest_sha256")):
        if digest(evidence / name) != selection[key]:
            raise ValueError(f"candidate evidence checksum mismatch: {name}")
    result = json.loads((evidence / "result.json").read_text(encoding="utf-8"))
    expected = {
        "complete": True, "run_id": selection["run_id"], "attempt": selection["attempt"],
        "rust_sha": selection["source_revision"], "llvm_sha": selection["llvm_revision"],
        "rustc_perf_sha": selection["rustc_perf_revision"],
        "patch_sha256": selection["source_patch_sha256"], "runner": selection["runner"],
    }
    if any(result.get(key) != value for key, value in expected.items()):
        raise ValueError("candidate provenance mismatch")
    profiles = result.get("profiles", {})
    if set(profiles) != {"llvm", "rustc", "rustdoc", "clippy", "cranelift"}:
        raise ValueError("missing candidate PGO profiles")
    for name, profile in profiles.items():
        path = evidence / f"{name}-pgo.profdata"
        if digest(path) != profile["sha256"] or path.stat().st_size != profile["bytes"]:
            raise ValueError(f"candidate profile checksum mismatch: {name}")
    manifest = json.loads((evidence / "dist-manifest.json").read_text(encoding="utf-8"))
    archives = {}
    for row in selection["components"]:
        entries = [item for item in manifest if item["name"] == row["name"]]
        expected_entry = {key: row[key] for key in ("name", "bytes", "sha256")}
        if entries != [expected_entry]:
            raise ValueError(f"candidate component manifest mismatch: {row['name']}")
        path = retained / "r" / "build" / "dist" / row["name"]
        if digest(path) != row["sha256"] or path.stat().st_size != row["bytes"]:
            raise ValueError(f"candidate archive checksum mismatch: {row['name']}")
        archives[row["component"]] = path
    if set(archives) != {"rustc", "cargo", "rust-std"}:
        raise ValueError("candidate must supply rustc, Cargo and native std")
    return result, archives


def install_components(archives, destination, host):
    destination.mkdir(parents=True, exist_ok=False)
    for archive in archives.values():
        with tarfile.open(archive, "r:xz") as bundle:
            bundle.extractall(destination, filter="data")
    compiler = destination / archives["rustc"].name.removesuffix(".tar.xz") / "rustc/bin/rustc.exe"
    cargo = destination / archives["cargo"].name.removesuffix(".tar.xz") / "cargo/bin/cargo.exe"
    rustdoc = compiler.with_name("rustdoc.exe")
    standard = (destination / archives["rust-std"].name.removesuffix(".tar.xz")
                / f"rust-std-{host}/lib/rustlib")
    if (not all(path.is_file() for path in (compiler, cargo, rustdoc))
            or not list((standard / host / "lib").glob("libstd-*.rlib"))):
        raise ValueError("incomplete extracted native toolchain")
    shutil.copytree(standard, compiler.parent.parent / "lib/rustlib", dirs_exist_ok=True)
    return compiler, cargo, rustdoc


def run_logged(command, source, env, prefix):
    print(f"Starting {prefix.name}", flush=True)
    with prefix.with_suffix(".stdout").open("wb") as stdout, \
            prefix.with_suffix(".stderr").open("wb") as stderr:
        result = subprocess.run(command, cwd=source, env=env, stdout=stdout,
                                stderr=stderr, timeout=900)
    receipt = {"command": list(map(str, command)), "exit_code": result.returncode,
               "sha256": {"stdout": digest(prefix.with_suffix(".stdout")),
                          "stderr": digest(prefix.with_suffix(".stderr"))}}
    save(prefix.with_suffix(".json"), receipt)
    if result.returncode:
        raise RuntimeError(f"command failed: {prefix.name}")
    return receipt


def package_inventory(source, cargo_home):
    lock = tomllib.loads((source / "Cargo.lock").read_text(encoding="utf-8"))
    expected = {f"{p['name']}-{p['version']}.crate": p["checksum"]
                for p in lock["package"] if "checksum" in p}
    rows = []
    for path in sorted((cargo_home / "registry/cache").glob("*/*.crate")):
        actual = digest(path)
        if expected.get(path.name) != actual:
            raise ValueError(f"cached package does not match frozen lock: {path.name}")
        rows.append({"name": path.name, "sha256": actual, "bytes": path.stat().st_size})
    if {row["name"] for row in rows} != set(expected) or len(rows) != len(expected):
        raise ValueError("missing or duplicate frozen package archives")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("root", "retained", "selection", "manifest", "training-audit", "perf"):
        parser.add_argument(f"--{key}", type=Path, required=True)
    args = parser.parse_args()
    root, source = args.root.resolve(), args.root.resolve() / "source"
    output = root / "e"
    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    project = next(p for p in manifest["projects"] if p["id"] == "fd")
    if (os.name != "nt" or os.environ.get("RUNNER_NAME") != selection["runner"]
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted"
            or os.cpu_count() != selection["logical_processors"]
            or manifest["cores"] != selection["logical_processors"]
            or manifest["training"]["rust_sha"] != selection["source_revision"]
            or manifest["training"]["rustc_perf_sha"] != selection["rustc_perf_revision"]):
        raise ValueError("pilot runner or candidate manifest mismatch")
    if root == args.retained.resolve() or root.is_relative_to(args.retained.resolve()):
        raise ValueError("pilot must not modify the retained compiler build")
    output.mkdir(exist_ok=True)
    summary = {"status": "in-progress-non-qualifying-pilot", "selection": selection,
               "run_id": os.environ["GITHUB_RUN_ID"], "attempt": os.environ["GITHUB_RUN_ATTEMPT"],
               "cores": manifest["cores"], "scenarios": []}
    try:
        result, archives = checked_candidate(args.retained.resolve(), selection)
        common_cargo = selection.get("common_cargo")
        if common_cargo:
            downloads = root / "downloads"
            downloads.mkdir(exist_ok=False)
            archive = downloads / common_cargo["name"]
            download(common_cargo["url"], archive, common_cargo["sha256"])
            archives = {**archives, "cargo": archive}
        compiler, cargo, rustdoc = install_components(archives, root / "toolchain", manifest["host"])
        verify_source(source, project)
        base = dict(os.environ)
        for key in ("GH_TOKEN", "GITHUB_TOKEN"):
            base.pop(key, None)
        base["CARGO_HOME"] = str(root / "cargo")
        base["PATH"] = str(compiler.parent) + os.pathsep + str(cargo.parent) + os.pathsep + base["PATH"]
        base["TEMP"] = base["TMP"] = str(root / "temp")
        (root / "temp").mkdir(exist_ok=True)
        env = compiler_environment(base, compiler, manifest["cores"], "0")
        env["RUSTDOC"] = str(rustdoc)
        version = subprocess.check_output([compiler, "-vV"], env=env, text=True)
        for expected in (f"host: {manifest['host']}", f"release: {manifest['rust_version']}",
                         f"commit-hash: {selection['source_revision']}"):
            if expected not in version.splitlines():
                raise ValueError(f"candidate executable identity mismatch: {expected}")
        cargo_version = subprocess.check_output([cargo, "-V"], env=env, text=True).strip()
        if common_cargo and cargo_version.split()[1] != common_cargo["version"]:
            raise ValueError("common Cargo executable version mismatch")
        identity = {"rustc_verbose_version": version, "cargo_version": cargo_version, "selection": selection,
            "executables": {p.name: digest(p) for p in (compiler, cargo, rustdoc)},
            "installed_files": {p.relative_to(root / "toolchain").as_posix(): digest(p)
                                for p in sorted((root / "toolchain").rglob("*")) if p.is_file()},
            "manifest_sha256": digest(args.manifest)}
        save(output / "toolchain.json", identity)
        save(output / "candidate-result.json", result)
        for path in (args.selection, args.manifest, args.training_audit):
            shutil.copyfile(path, output / path.name)
        validate_meter(output / "meter-validation")
        run_logged([cargo, "fetch", "--locked"], source,
                   {**env, "CARGO_NET_OFFLINE": "false"}, output / "fetch")
        save(output / "package-inventory.json", package_inventory(source, root / "cargo"))
        verify_source(source, project)
        metadata_command = [str(cargo), "metadata", "--format-version", "1", "--locked", "--offline",
                            "--filter-platform", manifest["host"], "--all-features"]
        metadata_receipt = run_logged(metadata_command, source, env, output / "metadata")
        metadata_receipt.update({"filter_platform": manifest["host"],
                                 "source_revision": project["revision"],
                                 "lock_sha256": project["lock_sha256"], "source_status": ""})
        metadata = json.loads((output / "metadata.stdout").read_text(encoding="utf-8"))
        roots = [p["id"] for p in metadata["packages"]
                 if p["name"] in project["selected_packages"] and p["source"] is None]
        background = telemetry_executables()
        for name in selection["pilot_scenarios"]:
            scenario = next(s for s in manifest["scenarios"] if s["id"] == name)
            scenario_env = {**env, "CARGO_INCREMENTAL": scenario["incremental"]}
            folder = output / name
            row = run_scenario(source, folder, project, scenario, cargo, compiler, scenario_env,
                               manifest["cores"], background, identity, target=manifest["host"])
            capture = {"schema": 1, "project": "fd", "scenario": name,
                       "source_revision": project["revision"], "target": manifest["host"],
                       "selected_package_ids": roots, "metadata": metadata_receipt,
                       "cargo": {"command": row["measurement"]["command"], "exit_code": 0}}
            save(folder / "capture.json", capture)
            subprocess.run([
                sys.executable, str(Path(__file__).with_name("breadth_resolved_audit.py")),
                "--manifest", str(args.manifest.resolve()), "--training-audit",
                str(args.training_audit.resolve()), "--perf", str(args.perf.resolve()),
                "--lock", str(source / "Cargo.lock"), "--metadata", str(output / "metadata.stdout"),
                "--capture", str(folder / "capture.json"), "--messages", str(folder / "measured.stdout"),
                "--output", str(folder / "resolved-audit.json"),
            ], check=True, env=env)
            summary["scenarios"].append({"name": name, "status": row["status"],
                                         "measurement": row["measurement"],
                                         "correctness": row["correctness"]})
            print(f"Passed {name}: {row['measurement']['wall_seconds']:.3f}s; "
                  f"{len(row['correctness'])} correctness commands", flush=True)
            save(output / "pilot.json", summary)
        verify_source(source, project)
        summary["status"] = "passed-candidate-only-pilot-not-comparative-qualification"
    except Exception as error:
        summary.update({"status": "failed-candidate-pilot", "error": str(error)})
        raise
    finally:
        save(output / "pilot.json", summary)


if __name__ == "__main__":
    main()
