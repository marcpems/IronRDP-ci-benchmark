"""Exercise the actual runner environment before scheduling long Rust releases."""

import argparse
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time

from build_arm_compilers import save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    root = parser.parse_args().root.resolve()
    evidence = root / "e"
    host = "aarch64-pc-windows-msvc"
    if platform.machine().lower() not in ("arm64", "aarch64") or os.name != "nt":
        raise RuntimeError("validation must use native Windows Arm64 Python")
    tools = {}
    for name in ("cl.exe", "link.exe", "lib.exe", "cmake.exe", "ninja.exe", "git.exe"):
        path = shutil.which(name)
        if path is None:
            raise RuntimeError(f"native build dependency missing: {name}")
        tools[name] = path
    save(evidence / "tools.json", {
        "files": tools, "msvc": os.environ.get("VCToolsVersion"),
        "sdk": os.environ.get("WindowsSDKVersion"), "logical_cpus": os.cpu_count(),
        "python": sys.version, "runner": os.environ["RUNNER_NAME"],
    })
    env = dict(os.environ, CARGO_BUILD_JOBS="4", RUSTC_BOOTSTRAP="1")

    def run(command, cwd, name):
        start = time.time()
        with (evidence / f"{name}.stdout").open("w") as stdout, \
                (evidence / f"{name}.stderr").open("w") as stderr:
            result = subprocess.run(command, cwd=cwd, env=env, stdout=stdout, stderr=stderr,
                                    timeout=2400)
        save(evidence / f"{name}.json", {
            "command": [str(arg) for arg in command], "exit_code": result.returncode,
            "wall_seconds": time.time() - start, "measurement_sample": False,
        })
        if result.returncode:
            print((evidence / f"{name}.stderr").read_text(errors="replace")[-6000:])
            raise RuntimeError(f"runner validation failed: {name}")
        print(f"PASS {name}", flush=True)

    fixture = root / "native.cpp"
    fixture.write_text('#include <windows.h>\nint main() { return sizeof(void*) == 8 ? 0 : 1; }\n')
    run(["cl.exe", "/nologo", fixture, f"/Fe{root / 'native.exe'}"], root, "native-sdk-link")
    run([root / "native.exe"], root, "native-executable")
    source = root / "r"
    (source / "bootstrap.toml").write_text(
        'profile = "compiler"\nchange-id = "ignore"\n'
        f'[build]\nbuild = "{host}"\nhost = ["{host}"]\ntarget = ["{host}"]\n'
        'jobs = 4\n[rust]\ndownload-rustc = false\n'
        '[llvm]\ndownload-ci-llvm = false\n', encoding="utf-8")
    run([sys.executable, "x.py", "check", "--stage", "1", "compiler/rustc_mir_build"],
        source, "rust-compiler-check")
    compiler = source / "build" / host / "stage0/bin"
    version = subprocess.check_output([compiler / "rustc.exe", "-vV"], text=True, env=env)
    if f"host: {host}" not in version:
        raise RuntimeError(f"bootstrap selected a non-native compiler: {version}")
    (evidence / "bootstrap-rustc.txt").write_text(version, encoding="utf-8")
    env["PATH"] = str(compiler) + os.pathsep + env["PATH"]
    env["RUSTC"] = str(compiler / "rustc.exe")
    cargo = compiler / "cargo.exe"
    run([cargo, "build", "--locked", "-p", "ironrdp-core", "--message-format=json"],
        root / "s", "ironrdp-core-build")
    artifacts = [json.loads(line) for line in (evidence / "ironrdp-core-build.stdout").read_text().splitlines()]
    if not any(row.get("reason") == "compiler-artifact" and not row["fresh"]
               and row["target"]["name"] == "ironrdp_core" for row in artifacts):
        raise RuntimeError("IronRDP validation did not compile any artifacts")
    tests = ["test", "-p", "ironrdp-tls", "--test", "native_tls", "--features", "native-tls"]
    run([cargo, *tests, "--locked", "--no-run"], root / "s", "ironrdp-test-build")
    run([cargo, *tests, "--frozen", "--", "--test-threads=1"], root / "s", "ironrdp-native-tls-tests")
    test_output = (evidence / "ironrdp-native-tls-tests.stdout").read_text()
    passed = re.findall(r"test result: ok\. (\d+) passed;", test_output)
    if not passed or sum(map(int, passed)) == 0:
        raise RuntimeError("IronRDP validation did not execute passing native TLS tests")
    save(evidence / "validation.json", {
        "complete": True, "runner": os.environ["RUNNER_NAME"], "host": host,
        "release_qualified": False, "measurement_sample": False,
        "scope": "native MSVC/SDK executable, MIR compiler component check, IronRDP core build and native TLS tests",
    })


if __name__ == "__main__":
    main()
