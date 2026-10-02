"""Install a checksum-pinned native Windows compiler without replacing official tools."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import urllib.request

from arm_ab_probe import extract_compiler, verify_custom, verify_shared_stdlib


def check_hash(path, expected):
    with path.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != expected:
        raise RuntimeError(f"Checksum mismatch: {path.name}")


def download(url, path, expected):
    with urllib.request.urlopen(url, timeout=120) as source, path.open("wb") as target:
        shutil.copyfileobj(source, target)
    check_hash(path, expected)


def verify_installation(root, manifest, official):
    check_hash(root / "optimized.json", manifest["metadata_sha256"])
    compiler = verify_custom(root, "optimized", manifest)
    metadata = json.loads((root / "optimized.json").read_text(encoding="utf-8"))
    verify_shared_stdlib(official, metadata, manifest["host"])
    return compiler


def install(destination, manifest, official):
    destination = destination.resolve()
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="rust-install-", dir=destination.parent) as tmp:
            staged = Path(tmp) / "payload"
            staged.mkdir()
            base = f"https://github.com/{manifest['repository']}/releases/download/{manifest['release']}"
            download(f"{base}/optimized.json", staged / "optimized.json", manifest["metadata_sha256"])
            archive = Path(tmp) / "compiler.zip"
            download(f"{base}/optimized.zip", archive, manifest["compiler_archive_sha256"]["optimized"])
            extract_compiler(archive, staged / "optimized")
            verify_installation(staged, manifest, official)
            staged.rename(destination)
    compiler = verify_installation(destination, manifest, official)
    env = {k: v for k, v in os.environ.items() if k not in ("GH_TOKEN", "GITHUB_TOKEN")}
    version = subprocess.check_output([str(compiler), "-vV"], env=env, text=True)
    for field in (f"release: {manifest['rust_version']}", f"commit-hash: {manifest['rust_sha']}",
                  f"host: {manifest['host']}", f"LLVM version: {manifest['llvm_version']}"):
        if field not in version.splitlines():
            raise RuntimeError(f"Unexpected compiler identity: {field}")
    with tempfile.TemporaryDirectory(prefix="rust-install-smoke-", dir=destination.parent) as tmp:
        smoke = Path(tmp)
        program = smoke / "smoke.rs"
        program.write_text("pub fn sum(xs: &[u64]) -> u64 { xs.iter().copied().sum() }\n")
        for target in (manifest["host"], "wasm32-unknown-unknown"):
            artifact = smoke / f"{target}.rlib"
            subprocess.run([
                str(compiler), "--edition=2024", "--crate-type=rlib", "-O",
                "--target", target, str(program), "-o", str(artifact),
            ], env={**env, "LLVM_PROFILE_FILE": str(smoke / "unexpected-%p.profraw")}, check=True)
            if not artifact.is_file() or artifact.stat().st_size == 0:
                raise RuntimeError(f"Compiler smoke test produced no library: {target}")
        if list(smoke.glob("*.profraw")):
            raise RuntimeError("Installed compiler still contains PGO instrumentation")
    record = {"manifest": manifest, "rustc": str(compiler), "official_rustc": str(official),
              "version": version, "stdlib_identity_verified": True, "native_and_wasm_smoke_passed": True}
    (destination / "installation.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--github-outputs", action="store_true")
    parser.add_argument("--activate", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    machines = {"aarch64-pc-windows-msvc": ("arm64", "aarch64"),
                "x86_64-pc-windows-msvc": ("amd64", "x86_64")}
    if os.name != "nt" or platform.machine().lower() not in machines.get(manifest["host"], ()):
        parser.error(f"This compiler requires native Windows hardware matching {manifest['host']}")
    if shutil.which("rustup") is None:
        parser.error("rustup is required on PATH; install the matching official support toolchain first")
    toolchain = f"{manifest['rust_version']}-{manifest['host']}"
    official = Path(subprocess.check_output(
        ["rustup", "which", "--toolchain", toolchain, "rustc"], text=True,
    ).strip())
    record = install(args.destination, manifest, official)
    if any(c in record["rustc"] for c in "\r\n"):
        raise RuntimeError("Compiler path is not suitable for CI environment output")
    if args.github_outputs:
        with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
            output.write(f"rustc={record['rustc']}\ninstallation={args.destination.resolve()}\nid={manifest['id']}\n")
    if args.activate:
        with Path(os.environ["GITHUB_ENV"]).open("a", encoding="utf-8") as output:
            output.write(f"RUSTC={record['rustc']}\nRUSTUP_TOOLCHAIN={toolchain}\n")
    print(f"Verified {manifest['id']}: {record['rustc']}", flush=True)


if __name__ == "__main__":
    main()
