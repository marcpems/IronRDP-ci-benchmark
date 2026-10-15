"""Replay only the failed documentation renderer into fresh diagnostic outputs."""

import json
import os
from pathlib import Path
import sys

from build_arm_compilers import digest, save
from msvc_experiment import environment
from native_ci_probe import telemetry_executables
from process_metrics import measure, measurement_session


def main():
    if os.environ["RUNNER_NAME"] != "MARCPE-D4-Arm64":
        raise RuntimeError("Unexpected diagnostic runner")
    original = Path(r"D:\m16997224t16r1")
    provenance = json.loads((original / "e/provenance.json").read_text())
    if (provenance["run_id"] != "38716997224"
            or provenance["build_affinity_count"] != 16
            or provenance["variant"] != "msvc-pgo-rust-thin"):
        raise RuntimeError("Unexpected retained build")
    source = original / "r"
    host = provenance["host"]
    binary = source / "build" / host / "stage1-tools-bin/rustbook.exe"
    book = source / "build" / host / "md-doc/unstable-book"
    failed = source / "build" / host / "doc/unstable-book/library-features"
    run_id = os.environ["GITHUB_RUN_ID"]
    output = Path(os.environ["RUNNER_TEMP"]) / f"rustbook-diagnostic-{run_id}"
    output.mkdir(exist_ok=False)
    save(output / "input.json", {
        "source": str(source), "binary": str(binary), "binary_sha256": digest(binary),
        "failed_path": str(failed), "exists": failed.exists(),
        "is_directory": failed.is_dir(), "is_file": failed.is_file(),
        "stat": list(failed.stat()) if failed.exists() else None,
    })
    env = environment(output, source / "citools/clang-rust/bin")
    results = []
    for drive in ("D", "C"):
        destination = Path(f"{drive}:\\") / f"rustbook-diagnostic-{run_id}"
        destination.mkdir(exist_ok=False)
        for threads in (None, 1):
            for repeat in (1, 2):
                name = f"{drive}-{'default' if threads is None else threads}-{repeat}"
                child_env = dict(env)
                if threads is not None:
                    child_env["RAYON_NUM_THREADS"] = str(threads)
                command = [str(binary), "build", str(book), "-d",
                           str(destination / name), "--rust-root", str(source)]
                with measurement_session(telemetry_executables()) as session:
                    result = measure(command, source, child_env, 16, output / name,
                                     session=session, timeout=120)
                save(output / f"{name}.json", result)
                row = {"case": name, "exit_code": result["exit_code"],
                       "wall_seconds": result["wall_seconds"]}
                results.append(row)
                print(json.dumps(row), flush=True)
                if result["exit_code"]:
                    print((output / f"{name}.stderr").read_text(errors="replace")[-4000:],
                          flush=True)
    save(output / "results.json", results)
    print("Diagnostic only: the failed release is not qualified or resumed.", flush=True)


if __name__ == "__main__":
    main()
