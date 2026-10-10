"""Repeat the unchanged Windows backend tests; no results are performance samples."""

import argparse
import json
import os
from pathlib import Path
import subprocess

from build_arm_compilers import save
from msvc_ironrdp_probe import install
from native_ci_probe import build_environment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--compilers", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    output.mkdir(exist_ok=False)
    protocol = json.loads(Path("ci-benchmark/msvc-linker/protocol.json").read_text())
    revision = subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip()
    if revision != protocol["source_sha"] or os.cpu_count() != 4:
        raise RuntimeError("Wrong workload source or runner size")
    compilers, metadata, _ = install(args.compilers.resolve(), protocol, "x86_64-pc-windows-msvc", "38021536352")
    cargo = compilers["baseline"].parent / "cargo.exe"
    env = build_environment(os.environ, compilers["baseline"])
    env.pop("CARGO_NET_OFFLINE")
    subprocess.run([cargo, "fetch", "--locked"], cwd=source, env=env, check=True)
    result = {"diagnostic_only": True, "source_sha": revision, "compiler_metadata": metadata, "runs": []}
    save(output / "index.json", result)
    for variant in ("baseline", "pgo", "pgo-rust-thin"):
        child = {**build_environment(os.environ, compilers[variant]),
                 "CARGO_TARGET_DIR": str(output / f"target-{variant}")}
        command = [cargo, "test", "-p", "ironrdp-rdpdr-native", "--test", "windows_backend",
                   "--no-run", "--frozen", "--message-format=json"]
        with (output / f"{variant}-build.stdout").open("w") as stdout, \
             (output / f"{variant}-build.stderr").open("w") as stderr:
            subprocess.run(command, cwd=source, env=child, stdout=stdout, stderr=stderr, check=True)
        artifacts = [json.loads(line) for line in (output / f"{variant}-build.stdout").read_text().splitlines()]
        executables = {item["executable"] for item in artifacts
                       if item.get("reason") == "compiler-artifact" and item.get("executable")
                       and item["target"]["name"] == "windows_backend"}
        if len(executables) != 1:
            raise RuntimeError("Expected one Windows backend test executable")
        executable = executables.pop()
        for threads in (4, 1):
            failures = 0
            for iteration in range(100):
                name = f"{variant}-threads-{threads}-{iteration}"
                run = subprocess.run([executable, f"--test-threads={threads}"], cwd=source,
                                     env=child, capture_output=True, text=True, timeout=120)
                (output / f"{name}.stdout").write_text(run.stdout)
                (output / f"{name}.stderr").write_text(run.stderr)
                if run.returncode not in (0, 101):
                    raise RuntimeError(f"Unexpected diagnostic process failure: {run.returncode}")
                failures += run.returncode != 0
                result["runs"].append({"variant": variant, "threads": threads, "iteration": iteration,
                                       "exit_code": run.returncode, "log": name})
                save(output / "index.json", result)
            print(f"{variant}: threads={threads}, failures={failures}/100", flush=True)
    subprocess.run(["git", "-C", source, "diff", "--exit-code"], check=True)
    result["complete"] = True
    save(output / "index.json", result)


if __name__ == "__main__":
    main()
