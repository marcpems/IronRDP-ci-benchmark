"""Reproduce the excluded GB300 UDP correctness failure; never benchmark data."""

import json
import os
from pathlib import Path
import subprocess

from build_arm_compilers import digest, save
from matched_release import RUST, VARIANTS
from native_ci_probe import build_environment
from offline_benchmark import NATIVE_COMMANDS


def main():
    if os.environ["RUNNER_NAME"] != "GB300-Arm64":
        raise RuntimeError("UDP diagnosis requires the original GB300 runner")
    root = Path(r"D:\b31290827")
    source = root / "s"
    index = json.loads((root / "e" / "index.json").read_text())
    if index["benchmark_run"] != "38431290827" or index["complete"]:
        raise RuntimeError("Expected the original incomplete replay")
    actual = subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip()
    if actual != index["protocol"]["source_sha"]:
        raise RuntimeError("Diagnostic workload revision mismatch")
    subprocess.run(["git", "-C", source, "diff", "--exit-code"], check=True)
    output = root / f"udp-diagnostic-{os.environ['GITHUB_RUN_ID']}"
    output.mkdir(exist_ok=False)
    host = index["host"]
    installed = root / "e" / "compilers"
    cargo = installed / "baseline" / f"cargo-nightly-{host}" / "cargo" / "bin" / "cargo.exe"
    if digest(cargo) != index["cargo_sha256"]:
        raise RuntimeError("Retained baseline Cargo changed")
    common = {
        **os.environ, "CARGO_HOME": str(root / "c"), "TEMP": str(root / "t"),
        "TMP": str(root / "t"), "RUST_TEST_THREADS": "1",
        "PATH": os.pathsep.join([str(cargo.parent), str(root / "tools" / "clang" / "bin"),
                                os.environ["PATH"]]),
    }
    record = {"scope": "diagnostic only; excluded replay remains failed",
              "original_run": index["benchmark_run"], "source_sha": actual,
              "variants": {}, "complete": False}
    save(output / "diagnostic.json", record)
    for variant in VARIANTS:
        compiler = installed / variant / f"rustc-nightly-{host}" / "rustc" / "bin" / "rustc.exe"
        version = subprocess.check_output([compiler, "-vV"], text=True)
        if RUST not in version or f"host: {host}" not in version:
            raise RuntimeError("Retained compiler identity mismatch")
        env = build_environment(common, compiler, 64)
        env["CARGO_TARGET_DIR"] = str(output / f"target-{variant}")
        env["RUSTDOC"] = str(installed / "baseline" / f"rustc-nightly-{host}" /
                            "rustc" / "bin" / "rustdoc.exe")
        rows = []
        record["variants"][variant] = {"rustc_sha256": digest(compiler), "commands": rows}
        commands = [(name, [str(cargo), *args, "--frozen"]) for name, args in NATIVE_COMMANDS]
        test = "e2e::egfx_moves_onto_the_udp_tunnel_with_soft_sync"
        commands += [(f"isolated-{attempt}", [str(cargo), "test", "--workspace", "--frozen",
                      test, "--", "--exact", "--nocapture"]) for attempt in range(1, 4)]
        for name, command in commands:
            with (output / f"{variant}-{name}.stdout").open("w") as stdout, \
                    (output / f"{variant}-{name}.stderr").open("w") as stderr:
                result = subprocess.run(command, cwd=source, env=env, stdout=stdout,
                                        stderr=stderr, timeout=1200)
            rows.append({"name": name, "command": command, "exit_code": result.returncode})
            save(output / "diagnostic.json", record)
            print(f"{variant} {name}: exit={result.returncode}", flush=True)
            if name.startswith("isolated-"):
                stdout_text = (output / f"{variant}-{name}.stdout").read_text()
                if f"test {test} ... " not in stdout_text:
                    raise RuntimeError("Diagnostic did not execute the exact UDP test")
            if result.returncode and not name.startswith("isolated-"):
                raise RuntimeError(f"Diagnostic build failed: {variant}/{name}")
    subprocess.run(["git", "-C", source, "diff", "--exit-code"], check=True)
    record["complete"] = True
    save(output / "diagnostic.json", record)
    failures = [(variant, row["name"]) for variant, data in record["variants"].items()
                for row in data["commands"] if row["exit_code"]]
    if failures:
        raise RuntimeError(f"UDP correctness failure reproduced: {failures}")


if __name__ == "__main__":
    main()
