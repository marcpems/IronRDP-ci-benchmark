"""Execute one frozen breadth project on one independent four-core hosted VM."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import zipfile

from breadth_candidate_pilot import digest, package_inventory, run_logged
from breadth_probe import compiler_environment, run_scenario, save, verify_source
from compiler_probe import validate_meter
from native_ci_probe import paired_order, telemetry_executables
from x64_pgo_replay import checked_release, share_native_libraries


ROOT = Path(__file__).resolve().parents[2]
HOST = "x86_64-pc-windows-msvc"


def load_inputs(protocol_path, corpus_path, replay_path, project_id, replicate):
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    for path, key in ((corpus_path, "corpus_sha256"),
                      (replay_path, "release_protocol_sha256")):
        if digest(path) != protocol[key]:
            raise ValueError(f"preregistered input checksum mismatch: {key}")
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    expected = {"host": HOST, "rust_version": "1.94.1", "cores": 4,
                "independent_vms": 5, "warmup_rounds": 1, "measured_rounds": 3,
                "variants": ["base", "test"]}
    if any(protocol.get(key) != value for key, value in expected.items()):
        raise ValueError("unsupported paired breadth design")
    if type(replicate) is not int or replicate not in range(1, 6):
        raise ValueError("replicate must be an integer from 1 through 5")
    if (any(corpus.get(key) != protocol[key] for key in ("host", "rust_version", "cores"))
            or any(replay.get(key) != protocol[key] for key in ("host", "rust_version", "cores"))
            or replay["release_run"] != "39456859889"
            or replay["rust_sha"] != protocol["rust_sha"]
            or replay["rust_sha"] != corpus["training"]["rust_sha"]
            or len(corpus["projects"]) != 3 or len(corpus["scenarios"]) != 5
            or [p["id"] for p in corpus["projects"]] != protocol["projects"]
            or [s["id"] for s in corpus["scenarios"]] != protocol["scenarios"]):
        raise ValueError("historical corpus or release identity mismatch")
    projects = [p for p in corpus["projects"] if p["id"] == project_id]
    if len(projects) != 1:
        raise ValueError("project must identify exactly one frozen corpus entry")
    return protocol, corpus, replay, projects[0]


def validate_host(protocol):
    if (os.name != "nt" or platform.machine().lower() not in ("amd64", "x86_64")
            or (os.cpu_count() or 0) < protocol["cores"]
            or os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted"
            or not os.environ.get("GITHUB_RUN_ID")
            or not os.environ.get("GITHUB_RUN_ATTEMPT")):
        raise ValueError("expected an independent four-core GitHub-hosted Windows x64 VM")


def load_reference(path, protocol, replay):
    member = protocol["reference_index_member"]
    with zipfile.ZipFile(path) as bundle:
        if bundle.namelist().count(member) != 1:
            raise ValueError("missing or duplicate qualified replay index")
        raw = bundle.read(member)
    if hashlib.sha256(raw).hexdigest() != protocol["reference_index_sha256"]:
        raise ValueError("qualified replay index checksum mismatch")
    reference = json.loads(raw)
    if (reference.get("complete") is not True or reference.get("benchmark_run") != "39506872211"
            or reference.get("attempt") != "1" or reference.get("protocol") != replay):
        raise ValueError("wrong or incomplete qualified replay evidence")
    return {"compiler_identity": {
                variant: {key: reference["artifact_evidence"][original][key]
                          for key in ("rustc_sha256", "driver_sha256")}
                for variant, original in (("base", "official"), ("test", "local"))},
            "cargo_sha256": reference["cargo_sha256"], "stdlib": reference["stdlib"]}


def planned_rows(protocol, scenarios, replicate):
    rows = []
    for round_index in range(protocol["warmup_rounds"] + protocol["measured_rounds"]):
        warmup = round_index < protocol["warmup_rounds"]
        for scenario in scenarios:
            for position, variant in enumerate(paired_order(protocol["variants"], replicate, round_index)):
                path = f"r{round_index}-{variant}-{scenario['id']}"
                rows.append({"variant": variant, "round": round_index, "position": position,
                             "scenario": scenario["id"], "warmup": warmup,
                             "exclusion": "preplanned-warmup" if warmup else None,
                             "path": f"{path}/results.json", "status": "pending",
                             "correctness_path": f"r0-{variant}-{scenario['id']}/results.json"})
    return rows


def clean_environment(inherited, cargo_home, rustup_home):
    # Reject knobs rather than silently accepting host-specific compilation settings.
    denied = {"CARGO_INCREMENTAL", "CARGO_BUILD_JOBS", "CARGO_NET_OFFLINE",
              "CARGO_BUILD_RUSTFLAGS", "CARGO_BUILD_RUSTDOC", "CARGO_BUILD_RUSTDOCFLAGS",
              "CARGO_BUILD_RUSTC_WRAPPER", "CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER",
              "CC", "CXX", "AR", "CFLAGS", "CXXFLAGS", "LDFLAGS", "CL", "_CL_", "LINK",
              "_LINK_", "RUSTC_FORCE_INCREMENTAL", "RUSTC_LOG", "RUSTC_BOOTSTRAP"}
    for key, value in inherited.items():
        upper = key.upper()
        if value and (upper in denied or upper.startswith(("CARGO_PROFILE_", "CARGO_TARGET_"))):
            raise ValueError(f"unregistered compilation override: {key}")
    base = {key: value for key, value in inherited.items()
            if key.upper() not in ("GH_TOKEN", "GITHUB_TOKEN", "CARGO_HOME", "RUSTUP_HOME")}
    base.update({"CARGO_HOME": str(cargo_home), "RUSTUP_HOME": str(rustup_home)})
    return base


def check_tool_identity(compiler, expected, replay, env):
    version = subprocess.check_output([str(compiler), "-vV"], env=env, text=True)
    for line in (f"host: {replay['host']}", f"release: {replay['rust_version']}",
                 f"commit-hash: {replay['rust_sha']}"):
        if line not in version.splitlines():
            raise ValueError(f"compiler version mismatch: {compiler.name}: {line}")
    actual = {"rustc_sha256": digest(compiler),
              "driver_sha256": {p.name: digest(p) for p in sorted(compiler.parent.glob("rustc_driver-*.dll"))}}
    if not actual["driver_sha256"] or actual != expected:
        raise ValueError("compiler executable/driver identity mismatch")
    return {**actual, "rustc_verbose_version": version}


def prepare_tools(artifacts, rustup_home, output, protocol, replay, base, reference):
    if not rustup_home.is_dir():
        raise ValueError("an existing isolated official rustup home is required")
    official = Path(subprocess.check_output(
        ["rustup", "which", "--toolchain", f"{replay['rust_version']}-{replay['host']}", "rustc"],
        env=base, text=True).strip()).resolve()
    if not official.is_relative_to(rustup_home.resolve()):
        raise ValueError("official compiler escaped the isolated rustup home")
    metadata, archive, release_evidence = checked_release(artifacts, "local", replay)
    destination = output / "tc"
    destination.mkdir(exist_ok=False)
    with tarfile.open(archive, "r:xz") as bundle:
        bundle.extractall(destination, filter="data")
    candidate = destination / archive.name.removesuffix(".tar.xz") / "rustc" / "bin" / "rustc.exe"
    cargo, rustdoc = official.with_name("cargo.exe"), official.with_name("rustdoc.exe")
    if (digest(cargo) != reference["cargo_sha256"]
            or digest(rustdoc) != protocol["rustdoc_sha256"]):
        raise ValueError("common official Cargo/rustdoc checksum mismatch")
    standard = share_native_libraries(official, candidate, replay["host"])
    if standard != reference["stdlib"]:
        raise ValueError("official standard library differs from the qualified replay")
    base["PATH"] = str(official.parent) + os.pathsep + base.get("PATH", "")
    compilers = {"base": official, "test": candidate}
    identities = {}
    for variant, compiler in compilers.items():
        env = compiler_environment(base, compiler, protocol["cores"], "0")
        env["RUSTDOC"] = str(rustdoc)
        identities[variant] = check_tool_identity(
            compiler, reference["compiler_identity"][variant], replay, env)
    cargo_version = subprocess.check_output([str(cargo), "-V"], env=env, text=True).strip()
    if len(cargo_version.split()) < 2 or cargo_version.split()[1] != protocol["rust_version"]:
        raise ValueError("common Cargo version mismatch")
    identity = {"variants": identities, "compiler_metadata": metadata,
                "artifact_evidence": release_evidence, "stdlib": standard,
                "cargo_sha256": digest(cargo), "rustdoc_sha256": digest(rustdoc),
                "cargo_version": cargo_version, "rustdoc": str(rustdoc)}
    return compilers, cargo, rustdoc, identity


def cleanup_cell(folder):
    removed = []
    for name in ("target", "correctness-target"):
        path = folder / name
        if path.exists():
            if path.is_symlink() or path.resolve() != folder.resolve() / name:
                raise ValueError("refusing redirected cell target cleanup")
            shutil.rmtree(path)
            removed.append(name)
    return removed


def execute_cells(source, output, project, corpus, protocol, compilers, cargo, rustdoc,
                  base, identity, index):
    background = telemetry_executables()
    scenarios = {scenario["id"]: scenario for scenario in corpus["scenarios"]}
    warmups = {(row["variant"], row["scenario"]): row for row in index["runs"] if row["warmup"]}
    for planned in index["runs"]:
        scenario = scenarios[planned["scenario"]]
        variant = planned["variant"]
        folder = output / Path(planned["path"]).parent
        planned["status"] = "running"
        save(output / "index.json", index)
        try:
            correctness_path = output / planned["correctness_path"]
            if not planned["warmup"]:
                coverage = warmups[(variant, scenario["id"])]
                if (coverage["status"] != "passed"
                        or digest(correctness_path) != coverage["correctness_sha256"]):
                    raise ValueError("original warmup correctness evidence changed")
                warmup = json.loads(correctness_path.read_text(encoding="utf-8"))
                if (warmup.get("status") != "non-qualifying-smoke"
                        or warmup.get("correctness_policy") != "original-commands"
                        or len(warmup.get("correctness", [])) != len(project["correctness"])
                        or any(row.get("exit_code") != 0 for row in warmup["correctness"])):
                    raise ValueError("missing successful original warmup correctness coverage")
            env = compiler_environment(base, compilers[variant], protocol["cores"], scenario["incremental"])
            env["RUSTDOC"] = str(rustdoc)
            row = run_scenario(
                source, folder, project, scenario, cargo, compilers[variant], env,
                protocol["cores"], background, {**identity, "variant": variant},
                target=protocol["host"], run_correctness=planned["warmup"])
            policy = "original-commands" if planned["warmup"] else "not-run-in-this-cell"
            if (row.get("correctness_policy") != policy
                    or len(row["correctness"]) != (len(project["correctness"]) if planned["warmup"] else 0)
                    or any(check.get("exit_code") != 0 for check in row["correctness"])
                    or (planned["warmup"] and [check["command"] for check in row["correctness"]] != [
                        [str(cargo), *args, "--frozen", "--target", protocol["host"]]
                        for args in project["correctness"]])):
                raise ValueError("incorrect original correctness command coverage")
            planned.update({"status": "passed", "measurement": row["measurement"],
                            "correctness_policy": policy,
                            "correctness_sha256": digest(correctness_path)})
            verify_source(source, project)
            planned["removed_target_directories"] = cleanup_cell(folder)
        except Exception as error:
            planned.update({"status": "failed", "failure": str(error)})
            raise
        finally:
            save(output / "index.json", index)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "artifacts", "output", "protocol"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--rustup-home", type=Path, default=os.environ.get("RUSTUP_HOME"))
    parser.add_argument("--corpus", type=Path, default=ROOT / "ci-benchmark" / "breadth" / "corpus.json")
    parser.add_argument("--release-protocol", type=Path,
                        default=ROOT / "ci-benchmark" / "x64-pgo-replay-protocol.json")
    parser.add_argument("--reference-evidence", type=Path,
                        default=ROOT / "ci-benchmark" / "x64-pgo-fresh-replay-evidence.zip")
    parser.add_argument("--project", required=True)
    parser.add_argument("--replicate", type=int, required=True, choices=range(1, 6))
    args = parser.parse_args()
    if args.rustup_home is None:
        parser.error("--rustup-home or explicit RUSTUP_HOME is required")
    protocol, corpus, replay, project = load_inputs(
        args.protocol, args.corpus, args.release_protocol, args.project, args.replicate)
    validate_host(protocol)
    source, output = args.source.resolve(), args.output.resolve()
    artifacts, rustup_home = args.artifacts.resolve(), args.rustup_home.resolve()
    paths = (source, output, artifacts, rustup_home)
    if any(a == b or a.is_relative_to(b) or b.is_relative_to(a)
           for i, a in enumerate(paths) for b in paths[i + 1:]):
        raise ValueError("source, output, retained artifacts and rustup home must be separate trees")
    verify_source(source, project)
    for ancestor in source.parents:
        if any((ancestor / ".cargo" / name).is_file() for name in ("config", "config.toml")):
            raise ValueError("unregistered ancestor Cargo configuration")
    output.mkdir(parents=True, exist_ok=False)
    index = {"schema": 1, "status": "in-progress", "complete": False,
             "protocol": protocol, "protocol_sha256": digest(args.protocol),
             "corpus_sha256": digest(args.corpus), "project": args.project,
             "replicate": args.replicate, "vm": args.replicate, "cores": protocol["cores"],
             "run_id": os.environ["GITHUB_RUN_ID"], "attempt": os.environ["GITHUB_RUN_ATTEMPT"],
             "runner_name": os.environ.get("RUNNER_NAME"), "computer_name": platform.node(),
             "logical_processors": os.cpu_count(),
             "image_version": os.environ.get("ImageVersion"),
             "contrast": "toolchain replacement (PGO repair and native linking), not pure PGO causality",
             "cleanup": "only successful cell target/correctness-target; outside timing; failed targets retained",
             "runs": planned_rows(protocol, corpus["scenarios"], args.replicate)}
    save(output / "index.json", index)
    try:
        cargo_home = output / "ch"
        cargo_home.mkdir(exist_ok=False)
        base = clean_environment(os.environ, cargo_home, rustup_home)
        reference = load_reference(args.reference_evidence, protocol, replay)
        compilers, cargo, rustdoc, identity = prepare_tools(
            artifacts, rustup_home, output, protocol, replay, base, reference)
        index["tool_identity"] = identity
        save(output / "toolchain.json", identity)
        for path, name in ((args.protocol, "protocol.json"), (args.corpus, "corpus.json"),
                           (args.release_protocol, "release-protocol.json")):
            shutil.copyfile(path, output / name)
        validate_meter(output / "meter-validation")
        env = compiler_environment(base, compilers["base"], protocol["cores"], "0")
        env["RUSTDOC"] = str(rustdoc)
        # Fetch every locked platform dependency so the archive inventory is complete.
        run_logged([str(cargo), "fetch", "--locked"], source,
                   {**env, "CARGO_NET_OFFLINE": "false"}, output / "fetch")
        inventory = package_inventory(source, cargo_home)
        save(output / "package-inventory.json", inventory)
        verify_source(source, project)
        execute_cells(source, output, project, corpus, protocol, compilers, cargo, rustdoc,
                      base, identity, index)
        if package_inventory(source, cargo_home) != inventory:
            raise ValueError("frozen package inventory changed during execution")
        verify_source(source, project)
        index.update({"status": "passed", "complete": True})
    except Exception as error:
        index.update({"status": "failed", "failure": str(error)})
        raise
    finally:
        save(output / "index.json", index)


if __name__ == "__main__":
    main()
