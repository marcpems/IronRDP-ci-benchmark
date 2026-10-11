"""Diagnostic-only compiler rebuild from recorded profiles; not a release timing."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

from build_arm_compilers import digest, save
from matched_release import LLVM, PERF, prepare, run
from matched_release_probe import one_file
from msvc_experiment import equivalent_tools

PARENT_RUN = "38133940060"
PARENT_RUST = "a2bb36e3594a73a806ad9d2bf2694fcd977c3261"
HOST = "aarch64-pc-windows-msvc"


def verified_profiles(root):
    parent = json.loads(one_file(root, "provenance.json").read_text())
    expected = {"run_id": PARENT_RUN, "host": HOST, "variant": "msvc-pgo",
                "rust_sha": PARENT_RUST, "llvm_sha": LLVM, "perf_sha": PERF, "attempt": "1"}
    if any(parent.get(key) != value for key, value in expected.items()):
        raise RuntimeError("unexpected diagnostic profile parent")
    hashes = json.loads(one_file(root, "profiles.json").read_text())
    paths = {}
    for name in ("rustc-pgo.profdata", "llvm-pgo.profdata"):
        path = one_file(root, name)
        if digest(path) != hashes[name]:
            raise RuntimeError(f"diagnostic profile hash mismatch: {name}")
        paths[name] = path
    return parent, paths


def compiler_archive(sysroot, archive):
    files = [p for p in (sysroot / "bin").iterdir() if p.is_file() and p.name.startswith("rustc")]
    files += [p for p in (sysroot / "lib/rustlib" / HOST / "lib").iterdir() if p.is_file()]
    if not (sysroot / "bin/rustc.exe").is_file() or not any(p.name.startswith("libstd-") for p in files):
        raise RuntimeError("diagnostic compiler sysroot is incomplete")
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED, compresslevel=1) as bundle:
        for path in files:
            bundle.write(path, path.relative_to(sysroot))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "runtime-source", "output", "profiles"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--host", choices=(HOST,), required=True)
    parser.add_argument("--variant", choices=("msvc-pgo",), required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    parent, profiles = verified_profiles(args.profiles.resolve())
    env, _, tools, _, provenance = prepare(
        source, args.runtime_source.resolve(), output, args.host, args.variant,
        full_distribution=False, rust_revision=PARENT_RUST)
    if not equivalent_tools(parent["tools"], tools):
        raise RuntimeError("native tools changed since the failing compiler build")
    provenance["diagnostic_parent_run"] = PARENT_RUN
    provenance["reused_profiles"] = {name: digest(path) for name, path in profiles.items()}
    save(output / "provenance.json", provenance)
    destination = source / "opt-artifacts"
    destination.mkdir()
    for name, path in profiles.items():
        shutil.copy2(path, destination / name)
    command = [sys.executable, "x.py", "build", "--stage", "2", "--host", HOST,
               "--target", HOST, "library/std", "compiler/rustc"]
    for component, name in (("rustc", "rustc-pgo.profdata"), ("llvm", "llvm-pgo.profdata")):
        command.extend(["--set", f'pgo.{component}.use="{(destination / name).as_posix()}"'])
    run(command, source, env, output, "diagnostic-compiler-rebuild")
    sysroot = source / "build" / HOST / "stage2"
    archive = output / "diagnostic-compiler.zip"
    compiler_archive(sysroot, archive)
    save(output / "diagnostic-compiler.json", {
        "sha256": digest(archive), "release_qualified": False, "reused_profiles": True,
        "parent_run": PARENT_RUN,
    })
    test = source / "tests/ui/expr/if/expr-stack-overflow.rs"
    command = [sysroot / "bin/rustc.exe", test, "--sysroot", sysroot,
               "--target=" + HOST, "-Ccodegen-units=1", "-Zui-testing",
               "-Zdeduplicate-diagnostics=no", "-Zwrite-long-types-to-disk=no",
               "-Cstrip=debuginfo", "-Cprefer-dynamic", "-Znext-solver=coherence",
               "-Aunused", "-Wunused_attributes", "-Ainternal_features", "-Aincomplete_features",
               "-Aunused_parens", "-Aunused_braces", "-Crpath", "-Cdebuginfo=0", "--edition=2015"]
    observations = []
    for label, extra in (("original", []), ("phase-trace", ["-Ztime-passes"])):
        target = output / label
        target.mkdir()
        with (output / f"{label}.stdout").open("w") as stdout, \
                (output / f"{label}.stderr").open("w") as stderr:
            result = subprocess.run([*command, "--out-dir", target, *extra],
                                    cwd=source, env=env, stdout=stdout, stderr=stderr, timeout=180)
        observations.append({"probe": label, "exit_code": result.returncode})
    save(output / "stack-diagnostic.json", {"observations": observations,
                                           "release_qualified": False})
    print(json.dumps(observations), flush=True)
    if any(row["exit_code"] != 0 for row in observations):
        raise RuntimeError("nested-expression diagnostic failed; compiler archive retained")


if __name__ == "__main__":
    main()
