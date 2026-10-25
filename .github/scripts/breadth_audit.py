"""Audit pinned validation projects against the pinned opt-dist training selectors."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tomllib


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def selectors(source):
    result = {}
    for phase, constants in (("llvm", ("LLVM_PGO_CRATES", "BACKEND_PGO_CRATES")),
                             ("rustc", ("RUSTC_PGO_CRATES",))):
        declared = [
            constant for constant in constants
            for _ in re.finditer(rf"pub const {constant}\s*:", source)
        ]
        if len(declared) != 1:
            problem = "missing" if not declared else "ambiguous"
            raise ValueError(f"{problem} training selector for {phase}: {constants}")
        constant = declared[0]
        match = re.search(rf"pub const {constant}\s*:[^;=]*=\s*&\[(.*?)\];", source, re.S)
        if not match:
            raise ValueError(f"missing training selector {constant}")
        result[phase] = re.findall(r'"([^"]+)"', match[1])
    return result


def packages(lock):
    return tomllib.loads(lock.decode("utf-8"))["package"]


def identity(package):
    return tuple(package.get(key, "") for key in ("name", "version", "source", "checksum"))


def overlap(candidate, training):
    exact, names = {}, {}
    for fixture, rows in training.items():
        for package in rows:
            names.setdefault(package["name"], set()).add(fixture)
            # Local packages lack a registry checksum/source; equal name/version is not identity.
            if package.get("source"):
                exact.setdefault(identity(package), set()).add(fixture)
    return {
        "exact_locked_registry_or_git_reuse": [
            {"package": dict(zip(("name", "version", "source", "checksum"), identity(p))),
             "training_fixtures": sorted(exact[identity(p)])}
            for p in candidate if p.get("source") and identity(p) in exact
        ],
        "name_reuse_including_different_versions": [
            {"name": name, "training_fixtures": sorted(names[name])}
            for name in sorted({p["name"] for p in candidate} & names.keys())
        ],
    }


def audit(manifest, rust, perf, corpus):
    rust_sha = manifest["training"]["rust_sha"]
    perf_sha = manifest["training"]["rustc_perf_sha"]
    if git(perf, "rev-parse", "HEAD").decode().strip() != perf_sha:
        raise ValueError("wrong rustc-perf revision")
    if git(perf, "status", "--porcelain", "--untracked-files=all").strip():
        raise ValueError("dirty training source")
    selector_bytes = git(rust, "show", f"{rust_sha}:src/build_helper/src/lib.rs")
    chosen = selectors(selector_bytes.decode())
    fixtures, training = [], {}
    for name in sorted(set(chosen["llvm"] + chosen["rustc"])):
        base = f"collector/compile-benchmarks/{name}"
        lock = git(perf, "show", f"{perf_sha}:{base}/Cargo.lock")
        cargo = git(perf, "show", f"{perf_sha}:{base}/Cargo.toml")
        package = tomllib.loads(cargo.decode()).get("package", {})
        training[name] = packages(lock)
        fixtures.append({
            "fixture": name, "phases": [phase for phase, rows in chosen.items() if name in rows],
            "package": package.get("name"), "version": package.get("version"),
            "lock_sha256": sha256(lock), "manifest_sha256": sha256(cargo),
            "locked_packages": len(training[name]),
            "url": f"https://github.com/rust-lang/rustc-perf/tree/{perf_sha}/{base}",
        })
    roots = {row["package"] for row in fixtures}
    projects = []
    for project in manifest["projects"] + manifest["reserves"]:
        root = corpus / project["id"]
        actual = git(root, "rev-parse", "HEAD").decode().strip()
        if actual != project["revision"]:
            raise ValueError(f"wrong project revision: {project['id']}")
        if git(root, "status", "--porcelain", "--untracked-files=all").strip():
            raise ValueError(f"dirty project: {project['id']}")
        lock_path = root / "Cargo.lock"
        lock = lock_path.read_bytes() if lock_path.exists() else None
        if project.get("lock_sha256") and (lock is None or sha256(lock) != project["lock_sha256"]):
            raise ValueError(f"wrong lockfile: {project['id']}")
        rows = packages(lock) if lock else []
        root_overlap = sorted(set(project["selected_packages"]) & roots)
        projects.append({
            "id": project["id"], "revision": actual,
            "lock_sha256": sha256(lock) if lock else None, "locked_packages": len(rows),
            "selected_training_root_name_overlap": root_overlap,
            "classification": ("trained-root" if root_overlap else
                               "root-held-out-only" if lock else "reserve-missing-lock"),
            "phases": {
                phase: overlap(rows, {key: training[key] for key in names})
                for phase, names in chosen.items()
            } if lock else {},
        })
    return {
        "schema": 1, "status": "preparation-not-candidate-qualification",
        "training": manifest["training"], "selectors": chosen,
        "selector_source_sha256": sha256(selector_bytes), "fixtures": fixtures,
        "projects": projects,
        "interpretation": [
            "Selected root packages are not selected training roots; this is not dependency-disjointness.",
            "Lock intersections conservatively include unused features, dev and non-Windows dependencies.",
            "Exact means matching name/version/source/checksum, not observed execution of that package.",
            "Name overlap includes versions and copied source without registry identity.",
            "No zero-overlap or runtime/general-speedup claim follows from root holdout.",
            "Historical token-stream-stress lock-format migration preserved its package records.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("manifest", "rust", "perf", "corpus", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    result = audit(json.loads(args.manifest.read_text()), args.rust, args.perf, args.corpus)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
