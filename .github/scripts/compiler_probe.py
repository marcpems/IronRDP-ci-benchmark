"""Compiler CPU validation: real graphics project and direct yuv rustc replay."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

from process_metrics import measure


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def validate_meter(output):
    output.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    burn = "import time;t=time.process_time();\nwhile time.process_time()-t<0.3: pass"
    descendant = f"import subprocess,sys;subprocess.run([sys.executable,'-c',{burn!r}],check=True)"
    busy = measure([sys.executable, "-c", descendant], output, env, 1, output / "busy")
    sleepy = measure([sys.executable, "-c", "import time;time.sleep(0.4)"],
                     output, env, 1, output / "sleep")
    if busy["exit_code"] or sleepy["exit_code"]:
        raise RuntimeError("CPU meter fixture failed")
    if busy["cpu_seconds"] < 0.25 or sleepy["cpu_seconds"] > 0.2:
        raise RuntimeError(f"invalid CPU accounting: busy={busy}, sleep={sleepy}")
    if sleepy["wall_seconds"] < 0.38:
        raise RuntimeError("invalid wall timer")
    if len(busy["affinity"]) != 1:
        raise RuntimeError("single-CPU affinity was not applied")
    save(output / "self-test.json", {"busy_descendant": busy, "sleep": sleepy})


def replay_arguments(original, output, mode):
    arguments = original.copy()
    if "--crate-type" not in arguments or arguments[arguments.index("--crate-type") + 1] not in ("lib", "rlib"):
        raise RuntimeError("expected a library-only compiler invocation")
    arguments[arguments.index("--out-dir") + 1] = str(output)
    emit = next(i for i, arg in enumerate(arguments) if arg.startswith("--emit="))
    arguments[emit] = "--emit=metadata" if mode == "metadata" else "--emit=metadata,link"
    return arguments


def run(source, output, wrapper):
    source, output, wrapper = source.resolve(), output.resolve(), wrapper.resolve()
    output.mkdir(parents=True, exist_ok=False)
    validate_meter(output / "meter-validation")
    env = dict(os.environ)
    for key in ("RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER"):
        if env.get(key):
            raise RuntimeError(f"unexpected inherited compiler override: {key}")
    env.update({
        "CARGO_NET_OFFLINE": "true", "CARGO_INCREMENTAL": "0",
        "CARGO_PROFILE_DEV_DEBUG": "0", "CARGO_PROFILE_DEV_OPT_LEVEL": "1",
        "CARGO_PROFILE_DEV_CODEGEN_UNITS": "16", "RUSTC_WRAPPER": str(wrapper),
    })
    # Bypass rustup proxies: Windows proxies spawn rustc as a separate process.
    env["RUSTC"] = subprocess.check_output(
        ["rustup", "which", "rustc"], cwd=source, env=env, text=True,
    ).strip()
    rustc = subprocess.check_output(["rustc", "-vV"], cwd=source, env=env, text=True)
    if f"host: {env['BENCHMARK_HOST']}\n" not in rustc or os.cpu_count() != 4:
        raise RuntimeError("wrong native compiler host or standard runner CPU count")
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    metadata = {
        "source_sha": sha, "rustc": rustc, "compiler_executable": env["RUSTC"],
        "platform": platform.platform(),
        "python_machine": platform.machine(), "logical_cpus": os.cpu_count(),
        "lock_lf_sha256": hashlib.sha256(
            (source / "Cargo.lock").read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest(),
        "environment": {key: os.environ.get(key) for key in (
            "BENCHMARK_PLATFORM", "BENCHMARK_REPLICATE", "BENCHMARK_HOST",
            "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "ImageOS", "ImageVersion",
        )},
        "profile": {"opt_level": 1, "codegen_units": 16, "debug": 0, "incremental": False},
    }
    hardware = (
        ["pwsh", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,"
         "NumberOfLogicalProcessors | ConvertTo-Json"]
        if os.name == "nt" else ["lscpu", "--json"]
    )
    metadata["hardware"] = subprocess.check_output(hardware, text=True)
    save(output / "environment.json", metadata)
    wrapper_test = output / "wrapper-validation"
    wrapper_test.mkdir()
    burn = "import time;t=time.process_time();\nwhile time.process_time()-t<0.3: pass"
    subprocess.run([str(wrapper), sys.executable, "-c", burn], check=True,
                   env={**env, "RUST_METRICS_DIR": str(wrapper_test)})
    check = json.loads(next(wrapper_test.glob("*.json")).read_text(encoding="utf-8"))
    if check["user_seconds"] + check["kernel_seconds"] < 0.25:
        raise RuntimeError("native wrapper CPU accounting failed validation")

    temporary = Path(env["RUNNER_TEMP"]) / f"compiler-validation-{env['GITHUB_RUN_ID']}"
    temporary.mkdir(exist_ok=False)
    rows = []
    invocations = {}
    core_order = [1, 4] if int(env["BENCHMARK_REPLICATE"]) % 2 else [4, 1]
    for cores in core_order:
        name = f"graphics-project-{cores}"
        metrics = output / f"{name}-rustc"
        metrics.mkdir()
        build_env = {
            **env, "CARGO_BUILD_JOBS": str(cores),
            "CARGO_TARGET_DIR": str(temporary / name), "RUST_METRICS_DIR": str(metrics),
        }
        command = ["cargo", "build", "-p", "ironrdp-graphics", "--lib", "--frozen",
                   "--message-format=json", "--timings"]
        row = measure(command, source, build_env, cores, output / name)
        compiler_rows = [json.loads(p.read_text(encoding="utf-8")) for p in metrics.glob("*.json")]
        actual_compiles = [
            r for r in compiler_rows if "--crate-name" in r["argv"]
            and not any(a.startswith("--print") for a in r["argv"])
        ]
        row.update({
            "name": name, "cores": cores, "workload": "graphics-project",
            "rustc_user_seconds": sum(r["user_seconds"] for r in actual_compiles),
            "rustc_kernel_seconds": sum(r["kernel_seconds"] for r in actual_compiles),
            "compiler_invocations": len(actual_compiles),
        })
        save(output / f"{name}.measurement.json", row)
        if row["exit_code"]:
            raise RuntimeError(f"{name} failed; inspect stderr and measurement")
        if any(r["exit_code"] for r in compiler_rows):
            raise RuntimeError("compiler invocation failed")
        invocations["native"] = select_yuv(actual_compiles)
        rows.append(row)
        print(f"{name}: wall={row['wall_seconds']:.3f}s CPU={row['cpu_seconds']:.3f}s", flush=True)

    prep_metrics = output / "wasm-preparation-rustc"
    prep_metrics.mkdir()
    prep_env = {
        **env, "CARGO_BUILD_JOBS": "4", "CARGO_TARGET_DIR": str(temporary / "wasm-preparation"),
        "RUST_METRICS_DIR": str(prep_metrics),
    }
    prep = measure(
        ["cargo", "build", "-p", "ironrdp-graphics", "--lib", "--frozen",
         "--target", "wasm32-unknown-unknown"],
        source, prep_env, 4, output / "wasm-preparation",
    )
    save(output / "wasm-preparation.measurement.json", prep)
    if prep["exit_code"]:
        raise RuntimeError("WASM prerequisite build failed")
    invocations["wasm"] = select_yuv([
        json.loads(p.read_text(encoding="utf-8")) for p in prep_metrics.glob("*.json")
    ])
    save(output / "replayed-invocations.json", invocations)
    for cores in core_order:
        targets = ["native", "wasm"]
        modes = ["metadata", "codegen"]
        if int(env["BENCHMARK_REPLICATE"]) % 2 == 0:
            targets.reverse()
            modes.reverse()
        for target in targets:
            for mode in modes:
                name = f"yuv-{target}-{mode}-{cores}"
                destination = temporary / name
                destination.mkdir()
                original = invocations[target]
                arguments = replay_arguments(original["argv"], destination, mode)
                replay_env = {**env, **original["environment"]}
                for key in ("RUSTC_WRAPPER", "CARGO_MAKEFLAGS", "MAKEFLAGS", "MFLAGS"):
                    replay_env.pop(key, None)
                row = measure(arguments, Path(original["cwd"]), replay_env, cores, output / name)
                row.update({"name": name, "cores": cores, "workload": f"yuv-{target}-{mode}"})
                files = list(destination.iterdir())
                row["output_files"] = [{"name": p.name, "bytes": p.stat().st_size} for p in files]
                save(output / f"{name}.measurement.json", row)
                if row["exit_code"]:
                    raise RuntimeError(f"{name} failed; inspect stderr and measurement")
                expected = ".rmeta" if mode == "metadata" else ".rlib"
                if not any(p.suffix == expected and p.stat().st_size for p in files):
                    raise RuntimeError(f"{name} produced no nonempty {expected}")
                rows.append(row)
                print(f"{name}: wall={row['wall_seconds']:.3f}s CPU={row['cpu_seconds']:.3f}s", flush=True)
    save(output / "results.json", {"metadata": metadata, "measurements": rows})


def select_yuv(rows):
    candidates = [
        r for r in rows if "--crate-name" in r["argv"]
        and r["argv"][r["argv"].index("--crate-name") + 1] == "yuv"
        and "--out-dir" in r["argv"]
    ]
    if len(candidates) != 1:
        raise RuntimeError(f"expected one yuv compilation, found {len(candidates)}")
    return candidates[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wrapper", type=Path)
    parser.add_argument("--validate-meter", action="store_true")
    args = parser.parse_args()
    if args.validate_meter:
        validate_meter(args.output)
    else:
        if args.source is None or args.wrapper is None:
            parser.error("--source and --wrapper are required")
        run(args.source, args.output, args.wrapper)
