"""Replay a retained same-source LLVM-profile treatment; never rebuild the compiler."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile

from pgo_owned_job_meter import measure, measurement_session

ROOT = Path.cwd()
OUT = ROOT / "profile-locality-evidence"
HOST = "x86_64-pc-windows-msvc"
VERSION = "1.99.1"
XPERF = Path(r"C:\Program Files (x86)\Windows Kits\10\Windows Performance Toolkit\xperf.exe")


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(args, name, timeout=300):
    with (OUT / f"{name}.stdout").open("wb") as stdout, (OUT / f"{name}.stderr").open("wb") as stderr:
        p = subprocess.run([str(x) for x in args], stdout=stdout, stderr=stderr, timeout=timeout)
    if p.returncode:
        raise RuntimeError(f"{name} failed: {p.returncode}")


def build_environment():
    for key, value in os.environ.items():
        if value and (key.startswith("CARGO_PROFILE_") or key in (
                "RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "RUSTC", "RUSTC_WRAPPER",
                "RUSTC_WORKSPACE_WRAPPER", "CARGO_BUILD_TARGET", "CARGO_BUILD_RUSTC")):
            raise RuntimeError(f"Unexpected compiler/profile override: {key}")
    return {**{k: v for k, v in os.environ.items() if k not in ("GH_TOKEN", "GITHUB_TOKEN")},
            "CARGO_INCREMENTAL": "0", "CARGO_PROFILE_DEV_DEBUG": "0",
            "CARGO_BUILD_JOBS": "4", "CARGO_NET_OFFLINE": "true", "MSBUILDDISABLENODEREUSE": "1"}


def telemetry_executables():
    vswhere = Path(os.environ["ProgramFiles(x86)"]) / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
    return subprocess.check_output([
        str(vswhere), "-latest", "-products", "*", "-find",
        r"VC\Tools\MSVC\*\bin\Hostx64\x64\vctip.exe"], text=True).splitlines()


def main():
    OUT.mkdir()
    if shutil.disk_usage(ROOT).free < 6 * 1024**3:
        raise RuntimeError("Less than 6GiB available")
    probe = subprocess.run(["rustup", "run", f"{VERSION}-{HOST}", "rustc", "-vV"],
                           capture_output=True, timeout=30)
    if probe.returncode:
        run(["rustup", "toolchain", "install", f"{VERSION}-{HOST}", "--profile", "minimal"], "common-toolchain")
    common = Path(subprocess.check_output(
        ["rustup", "run", f"{VERSION}-{HOST}", "rustc", "--print", "sysroot"], text=True).strip())
    run(["pwsh", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json"],
        "hardware")
    common_libs = {p.name: digest(p) for p in (common / "lib" / "rustlib" / HOST / "lib").iterdir()
                   if p.is_file()}
    packages = {}
    protocols = {}
    identities = {}
    for variant in ("official", "repaired"):
        source = ROOT / "downloaded-compilers" / variant
        archive, = source.rglob(f"rustc-{VERSION}-{HOST}.tar.xz")
        manifest_path, = source.rglob("dist-manifest.json")
        manifest = json.loads(manifest_path.read_text())
        expected, = [x for x in manifest if x["name"] == archive.name]
        if digest(archive) != expected["sha256"]:
            raise RuntimeError("Compiler archive hash mismatch")
        protocol_path, = source.rglob("protocol.json")
        protocols[variant] = json.loads(protocol_path.read_text())
        stage = ROOT / f"extracted-{variant}"
        with tarfile.open(archive, "r:xz") as bundle:
            bundle.extractall(stage, filter="data")
        package = ROOT / f"replay-toolchain-{variant}"
        shutil.copytree(common, package)
        shutil.copytree(stage / f"rustc-{VERSION}-{HOST}" / "rustc", package, dirs_exist_ok=True)
        actual = {p.name: digest(p) for p in (package / "lib" / "rustlib" / HOST / "lib").iterdir()
                  if p.is_file()}
        if actual != common_libs:
            raise RuntimeError("Shared standard libraries changed")
        packages[variant] = package
        run([package / "bin" / "rustc.exe", "-vV"], f"{variant}-identity")
        version = (OUT / f"{variant}-identity.stdout").read_text()
        if protocols[variant]["rust_sha"] not in version:
            raise RuntimeError("Compiler source identity mismatch")
        identities[variant] = {"archive": expected, "compiler_version": version,
                               "bin_hashes": {p.name: digest(p) for p in (package / "bin").iterdir()
                                              if p.is_file()}}
    if protocols["official"] != protocols["repaired"]:
        raise RuntimeError("Compiler pair protocols differ")
    env = build_environment()
    env["RUSTC"] = str(packages["official"] / "bin" / "rustc.exe")
    env.update({"PATH": str(common / "bin") + os.pathsep + env["PATH"]})
    fetch_env = {**env, "CARGO_NET_OFFLINE": "false"}
    p = subprocess.run([common / "bin" / "cargo.exe", "fetch", "--locked", "--target", HOST],
                       env=fetch_env, capture_output=True, timeout=300)
    (OUT / "fetch.stderr").write_bytes(p.stderr)
    if p.returncode:
        raise RuntimeError("Locked dependency preparation failed")
    run(["logman", "query", "-ets"], "sessions-before")
    if "NT Kernel Logger" in (OUT / "sessions-before.stdout").read_text():
        raise RuntimeError("Kernel logger already exists; preserve it")
    result = {"scope": "same-source Windows x64 LLVM training-profile quality, not no-PGO versus PGO",
              "protocol": protocols["official"], "identities": identities,
              "common_std_hashes": common_libs, "common_cargo_sha256": digest(common / "bin" / "cargo.exe"),
              "workload": "cargo build -p ironrdp-pdu --lib --frozen",
              "lock_sha256": digest(ROOT / "Cargo.lock"),
              "cache": "fresh Cargo targets; warm fetched dependencies; no cache purges",
              "runner": os.environ.get("RUNNER_NAME"), "image_version": os.environ.get("ImageVersion"),
              "disk": dict(zip(("total", "used", "free"), shutil.disk_usage(ROOT))), "samples": []}
    schedule = [("official", False, True), ("repaired", False, True),
                ("official", False, False), ("repaired", False, False),
                ("repaired", True, False), ("official", True, False),
                ("repaired", False, False), ("official", False, False)]
    for index, (variant, traced, warmup) in enumerate(schedule):
        output = OUT / f"sample-{index}-{variant}"
        output.mkdir()
        target = ROOT / f"profile-locality-target-{index}"
        env.update({"RUSTC": str(packages[variant] / "bin" / "rustc.exe"), "CARGO_TARGET_DIR": str(target)})
        args = [str(common / "bin" / "cargo.exe"), "build", "-p", "ironrdp-pdu", "--lib",
                "--frozen", "--timings", "--message-format=json"]
        started = False
        if traced:
            run([XPERF, "-on", "PROC_THREAD+LOADER+PROFILE+ALL_FAULTS+HARD_FAULTS+DISK_IO+DISK_IO_INIT+FILENAME",
                 "-stackwalk", "Profile", "-BufferSize", "1024", "-MinBuffers", "64", "-MaxBuffers", "128",
                 "-MaxFile", "512", "-FileMode", "Sequential", "-f", output / "raw.etl"], f"trace-{index}-start")
            started = True
        try:
            with measurement_session(telemetry_executables()) as session:
                row = measure(args, ROOT, env, 4, output / "compile", session=session, timeout=180)
            row.update({"variant": variant, "traced": traced, "warmup": warmup, "index": index})
            save(output / "measurement.json", row)
            result["samples"].append(row)
            save(OUT / "result.json", result)
            if row["exit_code"]:
                raise RuntimeError("Compile failed")
        finally:
            if started:
                run([XPERF, "-stop", "NT Kernel Logger"], f"trace-{index}-stop")
        if traced:
            raw_bytes = (output / "raw.etl").stat().st_size
            if raw_bytes >= 500 * 1024**2:
                raise RuntimeError("Sequential trace approached cap; exclude capture")
            run([XPERF, "-merge", output / "raw.etl", output / "capture.etl"], f"trace-{index}-merge")
            run([XPERF, "-i", output / "capture.etl", "-a", "tracestats"], f"trace-{index}-loss")
            stats = (OUT / f"trace-{index}-loss.stdout").read_text()
            if "Total # Lost Events  : 0" not in stats or "Total # Lost Buffers : 0" not in stats:
                raise RuntimeError("Loss-free trace not established")
            row["raw_bytes"] = raw_bytes
            (output / "raw.etl").unlink()
        shutil.rmtree(target)
        save(OUT / "result.json", result)
        print(f"{index} {variant} traced={traced} warmup={warmup} wall={row['wall_seconds']:.3f}s", flush=True)
    result["complete"] = True
    save(OUT / "result.json", result)


if __name__ == "__main__":
    main()
