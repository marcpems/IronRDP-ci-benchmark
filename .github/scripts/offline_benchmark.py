"""Measure offline Cargo process wall time, not compiler CPU time."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import time


NATIVE_COMMANDS = [
    ("xtask-bootstrap", ["build", "-p", "xtask"]),
    ("workspace-tests", ["test", "--workspace", "--no-run"]),
    (
        "native-tls-tests",
        ["test", "-p", "ironrdp-tls", "--test", "native_tls",
         "--features", "native-tls", "--no-run"],
    ),
    (
        "gateway-native-tls-tests",
        ["test", "-p", "ironrdp-mstsgu", "--test", "http_auth",
         "--features", "native-tls", "--no-run"],
    ),
    (
        "gateway-smartcard-tests",
        ["test", "-p", "ironrdp-mstsgu", "--test", "http_auth",
         "--features", "native-tls,smartcard", "--no-run"],
    ),
]
WASM_COMMAND = [
    "rustc", "--target", "wasm32-unknown-unknown", "--package", "ironrdp-web",
    "--lib", "--crate-type", "cdylib",
]
COMMON_COMMAND = [
    "test", "-p", "ironrdp-core", "-p", "ironrdp-pdu", "-p", "ironrdp-graphics",
    "--no-run",
]


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def measure(name, arguments, source, target, output, env):
    command = ["cargo", *arguments, "--frozen", "--timings",
               "--message-format=json"]
    child_env = {**env, "CARGO_TARGET_DIR": str(target),
                 "CARGO_NET_OFFLINE": "true"}
    stdout_path = output / f"{name}.stdout.jsonl"
    stderr_path = output / f"{name}.stderr.log"
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        started = time.perf_counter()
        result = subprocess.run(
            command, cwd=source, env=child_env, stdout=stdout, stderr=stderr,
            check=False,
        )
        elapsed = time.perf_counter() - started
    row = {
        "name": name, "command": command, "seconds": elapsed,
        "exit_code": result.returncode, "target_directory": str(target),
        "fresh_artifacts": 0, "compiled_artifacts": 0,
    }
    for line in stdout_path.read_text(encoding="utf-8").splitlines():
        message = json.loads(line)
        if message.get("reason") == "compiler-artifact":
            key = "fresh_artifacts" if message["fresh"] else "compiled_artifacts"
            row[key] += 1
    timings = target / "cargo-timings" / "cargo-timing.html"
    if timings.exists():
        shutil.copyfile(timings, output / f"{name}.timings.html")
    save_json(output / f"{name}.measurement.json", row)
    print(f"{name}: {elapsed:.3f}s, exit {result.returncode}", flush=True)
    if result.returncode:
        print(stderr_path.read_text(encoding="utf-8"), file=sys.stderr)
        raise subprocess.CalledProcessError(result.returncode, command)
    return row


def run(source, output):
    source = source.resolve()
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    for key, expected in {
        "CARGO_INCREMENTAL": "0", "CARGO_PROFILE_DEV_DEBUG": "0",
        "CARGO_BUILD_JOBS": "4", "CARGO_NET_OFFLINE": "true",
    }.items():
        if env.get(key) != expected:
            raise RuntimeError(f"{key} must be {expected!r}")
    for key in ("RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER", "RUSTFLAGS",
                "CARGO_ENCODED_RUSTFLAGS", "CARGO_BUILD_TARGET",
                "CARGO_PROFILE_TEST_DEBUG", "CARGO_PROFILE_DEV_OPT_LEVEL",
                "CARGO_PROFILE_TEST_OPT_LEVEL"):
        if env.get(key):
            raise RuntimeError(f"unexpected build override: {key}")
    rustc = subprocess.check_output(
        ["rustc", "-vV"], cwd=source, env=env, text=True,
    )
    host = next(line[6:] for line in rustc.splitlines() if line.startswith("host: "))
    if host != env["BENCHMARK_HOST"]:
        raise RuntimeError(f"compiler host {host} != {env['BENCHMARK_HOST']}")
    if (os.cpu_count() or 0) != 4:
        raise RuntimeError("expected a standard public runner with 4 logical CPUs")
    sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=source, text=True,
    ).strip()
    lock_hash = hashlib.sha256((source / "Cargo.lock").read_bytes()).hexdigest()
    metadata = {
        "source_sha": sha, "lock_sha256": lock_hash, "rustc": rustc,
        "cargo": subprocess.check_output(
            ["cargo", "-V"], cwd=source, env=env, text=True,
        ).strip(),
        "os": platform.platform(), "machine": platform.machine(),
        "logical_cpus": os.cpu_count(),
        "environment": {key: os.environ.get(key) for key in (
            "BENCHMARK_PLATFORM", "BENCHMARK_REPLICATE", "RUNNER_OS", "RUNNER_ARCH",
            "ImageOS", "ImageVersion", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT",
            "RUSTUP_TOOLCHAIN", "CARGO_INCREMENTAL", "CARGO_PROFILE_DEV_DEBUG",
            "CARGO_BUILD_JOBS",
        )},
    }
    if os.name == "nt":
        hardware_command = [
            "pwsh", "-NoProfile", "-Command",
            "Get-CimInstance Win32_Processor | Select-Object Name,"
            "NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json; "
            "Get-CimInstance Win32_ComputerSystem | "
            "Select-Object TotalPhysicalMemory | ConvertTo-Json",
        ]
    else:
        hardware_command = ["lscpu", "--json"]
        metadata["memory"] = subprocess.check_output(["free", "--bytes"], text=True)
    metadata["hardware"] = subprocess.check_output(hardware_command, text=True)
    metadata["disk"] = {
        "workspace": shutil.disk_usage(source)._asdict(),
        "runner_temp": shutil.disk_usage(env["RUNNER_TEMP"])._asdict(),
    }
    save_json(output / "environment.json", metadata)
    with (output / "native-feature-tree.txt").open("w", encoding="utf-8") as tree:
        subprocess.run(
            ["cargo", "tree", "--frozen", "--workspace", "--edges", "features",
             "--target", host],
            cwd=source, env=env, stdout=tree, check=True,
        )
    target_root = Path(env["RUNNER_TEMP"]) / (
        f"ironrdp-benchmark-{env['GITHUB_RUN_ID']}-"
        f"{env['GITHUB_RUN_ATTEMPT']}-{env['BENCHMARK_REPLICATE']}"
    )
    target_root.mkdir(exist_ok=False)
    rows = []
    # Reverse workload order across replicates to expose warm-host order effects.
    workloads = ["native", "common", "wasm"]
    if int(env["BENCHMARK_REPLICATE"]) % 2 == 0:
        workloads.reverse()
    for workload in workloads:
        target = target_root / workload
        if workload == "native":
            for name, args in NATIVE_COMMANDS:
                rows.append(measure(name, args, source, target, output, env))
        else:
            args = COMMON_COMMAND if workload == "common" else WASM_COMMAND
            rows.append(measure(workload, args, source, target, output, env))
    if hashlib.sha256((source / "Cargo.lock").read_bytes()).hexdigest() != lock_hash:
        raise RuntimeError("Cargo.lock changed")
    save_json(output / "results.json", {"metadata": metadata, "measurements": rows})


def summarize(root, source=None):
    results = [json.loads(p.read_text(encoding="utf-8"))
               for p in root.rglob("results.json")]
    if not results:
        raise RuntimeError("no successful benchmark results found")
    identities = {
        (r["metadata"]["source_sha"], r["metadata"]["cargo"]) for r in results
    }
    if len(identities) != 1:
        raise RuntimeError("cannot aggregate different revisions or Cargo versions")
    lock_hashes = {r["metadata"]["lock_sha256"] for r in results}
    if len(lock_hashes) != 1:
        if source is None:
            raise RuntimeError("different lock hashes; provide --source to verify checkout line endings")
        sha = results[0]["metadata"]["source_sha"]
        blob = subprocess.check_output(["git", "-C", str(source), "show", f"{sha}:Cargo.lock"])
        lf = blob.replace(b"\r\n", b"\n")
        accepted = {hashlib.sha256(data).hexdigest()
                    for data in (blob, lf, lf.replace(b"\n", b"\r\n"))}
        if not lock_hashes <= accepted:
            raise RuntimeError("lock hashes do not match the pinned Git blob with LF/CRLF endings")
    samples = {}
    seen = set()
    for result in results:
        meta = result["metadata"]["environment"]
        identity = (meta["BENCHMARK_PLATFORM"], meta["BENCHMARK_REPLICATE"])
        if identity in seen:
            raise RuntimeError(f"duplicate platform/replicate: {identity}")
        seen.add(identity)
        values = {row["name"]: row["seconds"] for row in result["measurements"]}
        if any(row["exit_code"] for row in result["measurements"]):
            raise RuntimeError("failed measurement cannot be aggregated")
        values["native-total"] = sum(values[name] for name, _ in NATIVE_COMMANDS)
        for name, seconds in values.items():
            samples.setdefault((identity[0], name), []).append(seconds)
    expected = {(p, str(n)) for p in (
        "linux-x64", "windows-x64", "linux-arm64", "windows-arm64",
    ) for n in (1, 2, 3)}
    if seen != expected:
        raise RuntimeError(
            f"invalid matrix: missing={sorted(expected - seen)}, "
            f"unexpected={sorted(seen - expected)}"
        )
    lines = ["| Platform | Component | n | Median seconds | Min | Max |",
             "|---|---|---:|---:|---:|---:|"]
    for (platform_name, component), values in sorted(samples.items()):
        lines.append(f"| {platform_name} | {component} | {len(values)} | "
                     f"{statistics.median(values):.3f} | "
                     f"{min(values):.3f} | {max(values):.3f} |")
    for arch in ("x64", "arm64"):
        for component in ("native-total", "common", "wasm"):
            win = statistics.median(samples[(f"windows-{arch}", component)])
            linux = statistics.median(samples[(f"linux-{arch}", component)])
            lines.append(f"\nWindows/Linux {arch} {component}: {win / linux:.3f}x")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    execute = commands.add_parser("run")
    execute.add_argument("--source", type=Path, required=True)
    execute.add_argument("--output", type=Path, required=True)
    aggregate = commands.add_parser("summarize")
    aggregate.add_argument("artifacts", type=Path)
    aggregate.add_argument("--source", type=Path, help="verify LF/CRLF hashes against the pinned Git lockfile")
    args = parser.parse_args()
    if args.action == "run":
        run(args.source, args.output)
    else:
        print(summarize(args.artifacts, args.source))


if __name__ == "__main__":
    main()
