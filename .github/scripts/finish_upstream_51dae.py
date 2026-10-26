"""Repeat only the parent block interrupted by a source-file read error."""

import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tomllib

from build_arm_compilers import digest, save
from native_ci_probe import run_block
from upstream_51dae_replay import HOST, REVISIONS, SOURCE_SHA, summarize

previous = Path(r"D:\u035465091")
root = Path(os.environ["REPLAY_ROOT"])
output = root / "e"
try:
    if (os.environ.get("RUNNER_NAME") != "MARCPE-TEST01-X64"
            or os.cpu_count() != 16 or (previous / "owner-run.txt").read_text().strip() != "40403546509/1"):
        raise RuntimeError("Wrong runner or original run owner")
    original = previous / "e"
    index = json.loads((original / "index.json").read_text())
    if (index["revisions"] != REVISIONS or index["complete"]
            or [(row["round"], row["variant"]) for row in index["runs"]]
            != [(0, "parent"), (0, "try"), (1, "try")]):
        raise RuntimeError("Unexpected original comparison state")
    diagnostics = [
        json.loads(line) for line in (original / "round-1-parent/workspace-tests.stdout").read_text().splitlines()
    ]
    errors = [row["message"]["message"] for row in diagnostics
              if row.get("reason") == "compiler-message" and row["message"]["level"] == "error"]
    if len(errors) != 1 or "rand_core-0.10.1" not in errors[0] or "os error 87" not in errors[0]:
        raise RuntimeError("Only the recorded source-file I/O failure may be continued")
    source = previous / "s"
    if subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip() != SOURCE_SHA:
        raise RuntimeError("Original workload revision changed")
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    libraries = list((previous / "cargo/registry/src").glob("*/rand_core-0.10.1/src/lib.rs"))
    if len(libraries) != 1:
        raise RuntimeError("Cannot identify the original dependency source")
    archives = list((previous / "cargo/registry/cache").glob("*/rand_core-0.10.1.crate"))
    packages = [item for item in tomllib.loads((source / "Cargo.lock").read_text())["package"]
                if item["name"] == "rand_core" and item["version"] == "0.10.1"]
    if len(archives) != 1 or len(packages) != 1 or digest(archives[0]) != packages[0]["checksum"]:
        raise RuntimeError("Cannot verify the original locked dependency archive")
    with tarfile.open(archives[0], "r:gz") as archive:
        expected_source = archive.extractfile("rand_core-0.10.1/src/lib.rs").read()
    if digest(libraries[0]) != hashlib.sha256(expected_source).hexdigest():
        raise RuntimeError("Dependency source checksum mismatch")
    package = previous / "compilers/parent" / f"rust-nightly-{HOST}"
    compiler, cargo = package / "rustc/bin/rustc.exe", package / "cargo/bin/cargo.exe"
    identity = index["artifacts"]["parent"]
    if digest(compiler) != identity["rustc_sha256"] or digest(cargo) != index["common_cargo_sha256"]:
        raise RuntimeError("The original parent compiler or shared Cargo changed")
    for name, expected in identity["driver_sha256"].items():
        if digest(compiler.parent / name) != expected:
            raise RuntimeError("Parent compiler driver changed")
    version = subprocess.check_output([compiler, "-vV"], text=True)
    if version != identity["rustc_version"]:
        raise RuntimeError("Parent compiler version changed")
    shutil.copytree(original, output)
    (output / "failure.json").rename(output / "original-failure.json")
    shutil.copy2(root / "readiness.json", output / "continuation-readiness.json")
    if shutil.which("nasm.exe") is None:
        nasm = previous / "nasm/nasm-2.16.03/nasm.exe"
        if not nasm.is_file():
            raise RuntimeError("The original assembler is unavailable")
        os.environ["PATH"] = str(nasm.parent) + os.pathsep + os.environ["PATH"]
    os.environ["PATH"] = str(cargo.parent) + os.pathsep + str(compiler.parent) + os.pathsep + os.environ["PATH"]
    os.environ["RUSTDOC"] = str(compiler.parent / "rustdoc.exe")
    os.environ["CARGO_HOME"] = str(previous / "cargo")
    os.environ["TEMP"] = os.environ["TMP"] = str(previous / "t")
    os.environ["RUNNER_TEMP"] = str(root / "t")
    release = next(line.removeprefix("release: ") for line in version.splitlines() if line.startswith("release: "))
    protocol = {"source_sha": SOURCE_SHA, "rust_sha": REVISIONS["parent"], "rust_version": release, "cores": 4}
    index["continuation"] = {
        "run_id": os.environ["GITHUB_RUN_ID"], "original_run_id": index["run_id"],
        "reason": errors[0], "dependency_source_sha256": digest(libraries[0]),
        "note": "First three successful blocks retained unchanged; only interrupted final parent block repeated.",
    }
    save(output / "index.json", index)
    run_block(source, output / "round-1-parent-retry", compiler, protocol,
              {"variant": "parent", "round": 1}, False, native_only=True)
    index["runs"].append({"variant": "parent", "round": 1, "position": 1,
                          "path": "round-1-parent-retry/results.json"})
    subprocess.run(["git", "-C", source, "diff", "--exit-code", "HEAD"], check=True)
    summary = summarize(output, index["runs"])
    summary["continuation"] = index["continuation"]
    save(output / "summary.json", summary)
    index["complete"] = True
    save(output / "index.json", index)
    print(json.dumps(summary, indent=2), flush=True)
except Exception as error:
    output.mkdir(exist_ok=True)
    save(output / "continuation-failure.json", {"complete": False, "error": str(error)})
    raise
