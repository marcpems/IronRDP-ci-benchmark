"""Audit published Windows x64 profiles with their release's own LLVM reader."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
from urllib.request import urlopen

HOST = "x86_64-pc-windows-msvc"
GROUPS = ("X86TargetLowering", "InstCombine")


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def coverage(text):
    shown = re.search(r"^Functions shown: (\d+)$", text, re.M)
    counters = [json.loads(line.split(":", 1)[1]) for line in text.splitlines()
                if line.strip().startswith("Block counts:")]
    if shown is None or int(shown[1]) != len(counters):
        raise RuntimeError("Unexpected llvm-profdata counter output")
    return {"functions": len(counters), "active": sum(any(row) for row in counters)}


def audit(version, root):
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Expected a stable numeric Rust version")
    root.mkdir(parents=True, exist_ok=True)
    bundles, commits = {}, []
    for component in ("reproducible-artifacts", "llvm-tools"):
        name = f"{component}-{version}-{HOST}"
        url = f"https://static.rust-lang.org/dist/{name}.tar.xz"
        with urlopen(url + ".sha256", timeout=60) as response:
            checksum = response.read().decode()
        expected = checksum.split()[0]
        if not re.fullmatch(r"[a-f0-9]{64}", expected):
            raise RuntimeError("Invalid published archive checksum")
        (root / f"{component}.sha256").write_text(checksum, encoding="utf-8")
        archive = root / f"{component}.tar.xz"
        if not archive.exists():
            with urlopen(url, timeout=180) as response, archive.open("wb") as output:
                shutil.copyfileobj(response, output)
        if digest(archive) != expected:
            raise RuntimeError(f"Archive checksum mismatch: {component}")
        with tarfile.open(archive, "r:xz") as bundle:
            bundle.extractall(root, filter="data")
        commits.append((root / name / "git-commit-hash").read_text().strip())
        bundles[component] = {"url": url, "sha256": expected, "bytes": archive.stat().st_size}
    if commits[0] != commits[1] or not re.fullmatch(r"[a-f0-9]{40}", commits[0]):
        raise RuntimeError("Profile and LLVM tool releases differ")
    reader = root / f"llvm-tools-{version}-{HOST}/llvm-tools-preview/lib/rustlib/{HOST}/bin/llvm-profdata.exe"
    reader_version = subprocess.check_output([reader, "--version"], text=True)
    if f"rust-{version}-stable" not in reader_version:
        raise RuntimeError("Wrong release's LLVM profile reader")
    profiles = {}
    directory = root / f"reproducible-artifacts-{version}-{HOST}/reproducible-artifacts"
    for profile in sorted(directory.glob("*-pgo.profdata")):
        name = profile.name.removesuffix("-pgo.profdata")
        profiles[name] = {"sha256": digest(profile), "bytes": profile.stat().st_size}
        if name == "llvm":
            profiles[name]["coverage"] = {}
            for group in GROUPS:
                text = subprocess.check_output(
                    [reader, "show", f"--function={group}", "--counts", profile], text=True)
                (root / f"official-{group}.txt").write_text(text, encoding="utf-8")
                profiles[name]["coverage"][group] = coverage(text)
    if not {"llvm", "rustc"} <= profiles.keys():
        raise RuntimeError("Official reproducibility bundle lacks compiler profiles")
    result = {
        "rust_version": version, "rust_sha": commits[0], "host": HOST,
        "archives": bundles, "reader_version": reader_version, "reader_sha256": digest(reader),
        "profiles": profiles,
        "scope": "Exact substring coverage in the published LLVM profile; not a performance estimate",
    }
    (root / "official-profile-audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.version, args.output), indent=2))
