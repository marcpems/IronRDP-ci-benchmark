"""Reuse a preserved instrumented compiler for tiny C/E profile-emission diagnostics."""

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

from build_arm_compilers import digest, save
from process_metrics import measure
from relocate_failed_scaling_build import physical_directory

RETAINED = Path(r"C:\matched-retained\m16997224t4r1-38869758791")
RELATIVE_BIN = Path(r"x86_64-pc-windows-msvc\stage2\bin")
RECEIPT_SHA256 = "e19f16ede889522d59bc9eb9366d3d0c66293a868c3c98427e1fe34a75ee8281"


def verify_retained_compiler(retained):
    receipt_path = retained / "relocation.json"
    if digest(receipt_path) != RECEIPT_SHA256:
        raise RuntimeError("Preservation receipt differs from the archived verified copy")
    receipt = json.loads(receipt_path.read_text())
    build = retained / "build"
    if (receipt.get("complete") is not True
            or receipt.get("source") != r"E:\m16997224t4r1\r\build"
            or receipt.get("destination") != str(build)):
        raise RuntimeError("Expected the exact preserved interrupted x64 build")
    for path in (retained, build, build / RELATIVE_BIN):
        physical_directory(path)
    expected = {row["path"]: row for row in receipt["files"]}
    compiler = build / RELATIVE_BIN / "rustc.exe"
    for path in [compiler, *sorted(compiler.parent.glob("*.dll"))]:
        row = expected.get(str(path.relative_to(build)))
        if (row is None or path.is_symlink() or path.resolve() != path
                or path.stat().st_size != row.get("bytes") or digest(path) != row.get("sha256")):
            raise RuntimeError("Preserved compiler binary no longer matches its verified receipt")
    return compiler


def batch(compiler, scratch, cores):
    def invoke(index):
        completed = subprocess.run(
            [str(compiler), "--crate-type=lib", "--emit=metadata", "--crate-name=diagnostic",
             str(scratch / "fixture.rs"), "-o", str(scratch / f"out-{index}.rmeta")],
            cwd=scratch, capture_output=True, text=True, timeout=60)
        if completed.returncode or completed.stderr:
            raise RuntimeError(f"Instrumented compiler diagnostic failed: {completed.stderr}")
        if not (scratch / f"out-{index}.rmeta").is_file():
            raise RuntimeError("Instrumented compiler emitted no metadata")
    with ThreadPoolExecutor(max_workers=cores) as executor:
        list(executor.map(invoke, range(16)))
    print(json.dumps({"completed_compilations": 16}), flush=True)


def run_probe(output):
    if os.environ.get("RUNNER_NAME") != "MARCPE-TEST01-X64":
        raise RuntimeError("Instrumented compiler probe is restricted to the original x64 runner")
    compiler = verify_retained_compiler(RETAINED)
    cells = []
    # Warm the same retained compiler once; subsequent cells change only allocation and scratch volume.
    with tempfile.TemporaryDirectory(prefix="matched-rustc-warmup-", dir="C:\\") as name:
        scratch = Path(name)
        env = {**os.environ, "LLVM_PROFILE_FILE": str(scratch / "default_%m_%p.profraw")}
        version = subprocess.run([str(compiler), "-vV"], cwd=scratch, env=env,
                                 capture_output=True, text=True, timeout=60, check=True)
        if ("commit-hash: 7db17d9b5bbe6b16be2dc86b4bfae81d6e1ae238" not in version.stdout
                or version.stderr or not list(scratch.glob("*.profraw"))):
            raise RuntimeError("Preserved compiler is not the expected instrumented pinned build")
        save(output / "instrumented-compiler.json",
             {"path": str(compiler), "sha256": digest(compiler), "version": version.stdout})
    for index, (cores, volume) in enumerate(((4, "C:\\"), (16, "E:\\"), (16, "C:\\"), (4, "E:\\"),
                                            (4, "E:\\"), (16, "C:\\"), (16, "E:\\"), (4, "C:\\"))):
        with tempfile.TemporaryDirectory(prefix="matched-rustc-diagnostic-", dir=volume) as name:
            scratch = Path(name)
            raw = scratch / "raw"
            raw.mkdir()
            (scratch / "fixture.rs").write_text("#![no_std]\npub fn add(x: u64) -> u64 { x.wrapping_add(1) }\n")
            env = {**os.environ, "LLVM_PROFILE_FILE": str(raw / "default_%m_%p.profraw")}
            prefix = output / f"instrumented-rustc-{index}-{volume[0]}-{cores}"
            started = time.time()
            result = measure([sys.executable, str(Path(__file__).resolve()), "--batch",
                              str(compiler), str(scratch), str(cores)],
                             scratch, env, cores, prefix, timeout=180)
            profiles = list(raw.glob("*.profraw"))
            result.update(volume=volume, profile_files=len(profiles),
                          profile_bytes=sum(path.stat().st_size for path in profiles),
                          started_unix=started, finished_unix=time.time())
            save(prefix.with_suffix(".json"), result)
            if result["exit_code"] or not profiles:
                raise RuntimeError("Instrumented compiler/profile emission failed; partial evidence retained")
            cells.append({"phase": prefix.name, **result})
            save(output / "instrumented-compiler-cells.json", cells)


if __name__ == "__main__":
    if len(sys.argv) != 5 or sys.argv[1] != "--batch" or sys.argv[4] not in ("4", "16"):
        raise SystemExit("Internal compiler batch requires compiler, scratch path and four/sixteen workers")
    batch(Path(sys.argv[2]), Path(sys.argv[3]), int(sys.argv[4]))
