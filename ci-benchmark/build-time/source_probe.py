"""Bounded Git/archive source acquisition experiment; no compiler build or SDK edits."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time

LLVM_SHA = "76a3a9d0075fe0df4bb57160372700006e3d0b2b"
RUST_SHA = "0ed41eb4142dda2df61eb1145a312c1a9d62eb56"
ROOT = Path.cwd() / "source-probe"
RESULTS = ROOT / "results"
# No GitHub tokens enter the subprocess environment or saved command output.
ENV = {k: v for k, v in os.environ.items() if k.upper() in {
    "PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "PROGRAMFILES",
    "PROGRAMFILES(X86)", "PROGRAMW6432", "USERPROFILE", "HOMEDRIVE", "HOMEPATH",
    "APPDATA", "LOCALAPPDATA", "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS",
    "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY"}}
ENV["GIT_TERMINAL_PROMPT"] = "0"
ENV["GIT_CONFIG_NOSYSTEM"] = "1"
ENV["GIT_CONFIG_GLOBAL"] = os.devnull
# All intermediate storage is scoped to the owned workspace.
ENV["TMP"] = ENV["TEMP"] = str(ROOT / "scratch")


def invoke(args, cwd=ROOT, timeout=1500):
    start = time.perf_counter()
    proc = subprocess.run(args, cwd=cwd, env=ENV, capture_output=True, timeout=timeout)
    elapsed = time.perf_counter() - start
    log = RESULTS / "commands.log"
    with log.open("ab") as out:
        out.write((json.dumps({"argv": args, "seconds": elapsed, "returncode": proc.returncode}) + "\n").encode())
        out.write(proc.stdout + proc.stderr + b"\n")
    if proc.returncode:
        raise RuntimeError(f"command failed ({proc.returncode}): {args[0:2]}")
    return elapsed, proc.stdout


def blob_hash(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def verify(path, entries):
    digest = hashlib.sha256()
    mismatches = []
    total = 0
    for mode, expected, relative in entries:
        item = path / relative
        if mode == "160000":
            raise RuntimeError("nested submodule requires separate acquisition")
        if item.is_symlink():
            content = os.readlink(item).encode()
        elif item.is_file():
            content = item.read_bytes()
        else:
            mismatches.append(relative + ": missing")
            continue
        actual = blob_hash(content)
        total += len(content)
        digest.update(relative.encode() + b"\0" + actual.encode() + b"\n")
        if actual != expected:
            mismatches.append(relative + ": blob mismatch")
    expected_paths = {entry[2] for entry in entries}
    actual_paths = set()
    for parent, directories, filenames in os.walk(path):
        if Path(parent) == path and ".git" in directories:
            directories.remove(".git")
        for name in filenames:
            actual_paths.add((Path(parent) / name).relative_to(path).as_posix())
    extras = sorted(actual_paths - expected_paths)
    return {"files": len(entries), "bytes": total, "digest": digest.hexdigest(),
            "mismatch_count": len(mismatches), "mismatches_first20": mismatches[:20],
            "extra_count": len(extras), "extras_first20": extras[:20],
            "qualification": "file content/path equivalence; executable mode and full Rust bootstrap not qualified"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--order", choices=["git-first", "archive-first"], required=True)
    args = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    (ROOT / "scratch").mkdir(exist_ok=True)
    record = {"rust_sha": RUST_SHA, "llvm_sha": LLVM_SHA, "order": args.order,
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "platform": platform.platform(), "machine": platform.machine(),
              "cpu_count": os.cpu_count(), "image_version": os.environ.get("ImageVersion"),
              "run_id": os.environ.get("GITHUB_RUN_ID"), "steps": {},
              "cache_state": "fresh paths/no Actions cache; OS/CDN caches uncontrolled"}

    def save():
        (RESULTS / "result.json").write_text(json.dumps(record, indent=2) + "\n")

    save()
    try:
        for tool in ("git", "curl.exe", "tar.exe"):
            _, output = invoke([tool, "--version"], timeout=60)
            record[tool] = {"path": shutil.which(tool), "version": output.decode(errors="replace").splitlines()[0]}
        methods = ["git", "archive"] if args.order == "git-first" else ["archive", "git"]
        for method in methods:
            start = time.perf_counter()
            target = ROOT / method
            target.mkdir()
            if method == "git":
                invoke(["git", "init", "--quiet", str(target)])
                invoke(["git", "-C", str(target), "config", "core.autocrlf", "false"])
                invoke(["git", "-C", str(target), "config", "core.longpaths", "true"])
                invoke(["git", "-C", str(target), "remote", "add", "origin", "https://github.com/rust-lang/llvm-project.git"])
                fetch, _ = invoke(["git", "-C", str(target), "fetch", "--quiet", "--depth=1", "origin", LLVM_SHA])
                checkout, _ = invoke(["git", "-C", str(target), "checkout", "--quiet", "--detach", "FETCH_HEAD"])
                record["steps"][method] = {"fetch_seconds": fetch, "checkout_seconds": checkout}
            else:
                archive = ROOT / "llvm-source.tar.gz"
                fetch, _ = invoke(["curl.exe", "--fail", "--location", "--silent", "--show-error",
                                   "--retry", "2", "--output", str(archive),
                                   f"https://codeload.github.com/rust-lang/llvm-project/tar.gz/{LLVM_SHA}"])
                extract, _ = invoke(["tar.exe", "-xf", str(archive), "-C", str(target), "--strip-components=1"])
                record["steps"][method] = {"fetch_seconds": fetch, "extract_seconds": extract,
                                           "archive_bytes": archive.stat().st_size,
                                           "archive_sha256": hashlib.file_digest(archive.open("rb"), "sha256").hexdigest()}
            record["steps"][method]["total_seconds"] = time.perf_counter() - start
            save()
        _, tree = invoke(["git", "-C", str(ROOT / "git"), "ls-tree", "-r", "-z", LLVM_SHA])
        entries = []
        for row in tree.split(b"\0"):
            if not row:
                continue
            meta, name = row.split(b"\t", 1)
            mode, kind, sha = meta.decode().split()
            entries.append((mode, sha, name.decode()))
        for method in methods:
            start = time.perf_counter()
            record["steps"][method]["verification"] = verify(ROOT / method, entries)
            record["steps"][method]["verification_seconds"] = time.perf_counter() - start
            save()
        record["passed"] = all(s["verification"]["mismatch_count"] == 0 and
                               s["verification"]["extra_count"] == 0 for s in record["steps"].values())
        if not record["passed"]:
            raise RuntimeError("source content equivalence failed")
    except Exception as error:
        record["error"] = repr(error)
        raise
    finally:
        record["ended_utc"] = datetime.now(timezone.utc).isoformat()
        save()
        print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
