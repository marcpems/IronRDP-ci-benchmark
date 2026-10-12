"""Paired clean LLVM sub-builds; exploratory throughput, not full-release timings."""

import argparse
import os
from pathlib import Path
import platform
import shutil
import statistics
import subprocess

from build_arm_compilers import digest, save
from matched_release import LLVM
from msvc_experiment import execute


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--clang", type=Path, required=True)
    parser.add_argument("--cores", type=int, required=True)
    args = parser.parse_args()
    if os.environ.get("RUNNER_ENVIRONMENT") == "self-hosted" or os.environ.get("COMPUTERNAME") in (
        "MARCPE-D4-Arm64", "MARCPE-TEST01-X64",
    ):
        raise RuntimeError("throughput experiments must not run on the custom timing runners")
    if os.name != "nt" or args.cores <= 4 or args.cores > (os.cpu_count() or 0):
        raise RuntimeError("probe requires native Windows with more than four available logical CPUs")
    host = {"arm64": "aarch64-pc-windows-msvc", "aarch64": "aarch64-pc-windows-msvc",
            "amd64": "x86_64-pc-windows-msvc", "x86_64": "x86_64-pc-windows-msvc"}[platform.machine().lower()]
    source, output, clang = args.source.resolve(), args.output.resolve(), args.clang.resolve()
    revision = subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip()
    if revision != LLVM:
        raise RuntimeError("LLVM source must match the release source pin")
    output.mkdir(exist_ok=False)
    tools = {}
    for name in ("link.exe", "lib.exe", "cmake.exe", "ninja.exe"):
        found = shutil.which(name)
        if found is None:
            raise RuntimeError(f"missing native tool: {name}")
        tools[name] = Path(found)
    if "microsoft visual studio" not in str(tools["link.exe"]).lower():
        raise RuntimeError("the probe must retain the native Microsoft linker")
    fixture = output / "probe.ll"
    fixture.write_text('define i32 @answer() {\n  ret i32 42\n}\n', encoding="utf-8")
    provenance = {
        "llvm_sha": revision, "machine": os.environ["COMPUTERNAME"], "host": host,
        "logical_cpus": os.cpu_count(), "requested_cores": args.cores,
        "tools": {name: {"path": str(path), "sha256": digest(path)}
                  for name, path in {**tools, "clang-cl.exe": clang / "clang-cl.exe"}.items()},
        "scope": "LLVMCore/Support and llvm-as/llvm-dis dependency graph, not the full LLVM or Rust release",
        "cache": "new CMake/object directory every build; source/OS caches not flushed; AB/BA order",
        "excludes": "configure, tool/source setup and verification",
    }
    save(output / "provenance.json", provenance)
    rows = []
    env = dict(os.environ)
    for round_index, order in enumerate(((4, args.cores), (args.cores, 4))):
        for jobs in order:
            name = f"r{round_index}-j{jobs}"
            build = output / name
            execute(
                ["cmake", "-S", source / "llvm", "-B", build, "-G", "Ninja",
                 f"-DCMAKE_C_COMPILER={(clang / 'clang-cl.exe').as_posix()}",
                 f"-DCMAKE_CXX_COMPILER={(clang / 'clang-cl.exe').as_posix()}",
                 f"-DCMAKE_C_COMPILER_TARGET={host}", f"-DCMAKE_CXX_COMPILER_TARGET={host}",
                 f"-DCMAKE_LINKER={tools['link.exe'].as_posix()}",
                 f"-DCMAKE_AR={tools['lib.exe'].as_posix()}",
                 "-DCMAKE_BUILD_TYPE=Release", "-DLLVM_ENABLE_ASSERTIONS=OFF",
                 "-DLLVM_ENABLE_LTO=OFF", "-DBUILD_SHARED_LIBS=OFF",
                 "-DLLVM_TARGETS_TO_BUILD=AArch64;X86", "-DLLVM_PARALLEL_LINK_JOBS=1",
                 "-DLLVM_INCLUDE_TESTS=OFF", "-DLLVM_INCLUDE_BENCHMARKS=OFF",
                 "-DLLVM_ENABLE_ZSTD=OFF", "-DLLVM_ENABLE_ZLIB=OFF"],
                source, env, output, f"{name}-configure", timeout=600)
            cache = {}
            for line in (build / "CMakeCache.txt").read_text().splitlines():
                if "=" in line and ":" in line.split("=", 1)[0]:
                    key, value = line.split("=", 1)
                    cache[key.split(":", 1)[0]] = value
            for variable, path in (("CMAKE_LINKER", tools["link.exe"]), ("CMAKE_AR", tools["lib.exe"])):
                if Path(cache.get(variable, "")).resolve() != path.resolve():
                    raise RuntimeError(f"CMake did not retain the native tool: {variable}")
            row = execute(["cmake", "--build", build, "--parallel", str(jobs),
                           "--target", "llvm-as", "llvm-dis"], source, env, output, name,
                          timeout=5400, cores=jobs)
            binary = build / "bin"
            bitcode, restored = build / "probe.bc", build / "probe.ll"
            subprocess.run([binary / "llvm-as.exe", fixture, "-o", bitcode], check=True)
            subprocess.run([binary / "llvm-dis.exe", bitcode, "-o", restored], check=True)
            if "ret i32 42" not in restored.read_text():
                raise RuntimeError("built LLVM assembler/disassembler did not preserve the IR fixture")
            objects = list(build.rglob("*.obj"))
            if not objects:
                raise RuntimeError("LLVM probe did not compile any object files")
            row.update({"round": round_index, "jobs": jobs, "fresh_objects": len(objects),
                        "ir_roundtrip_passed": True})
            rows.append(row)
            save(output / "samples.json", rows)
    seconds = {jobs: statistics.median(row["wall_seconds"] for row in rows if row["jobs"] == jobs)
               for jobs in (4, args.cores)}
    save(output / "comparison.json", {
        "complete": True, "provenance": provenance, "median_seconds": seconds,
        "wall_saving_percent": 100 * (1 - seconds[args.cores] / seconds[4]),
        "speedup": seconds[4] / seconds[args.cores], "samples": rows,
    })


if __name__ == "__main__":
    main()
