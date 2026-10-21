"""Qualify one hash-pinned retained distribution without repeating its production."""

import json
import os
from pathlib import Path
import subprocess
import time

from build_arm_compilers import digest, save
from msvc_experiment import environment, equivalent_tools, tool_identity
from x64_pgo_release import check_distribution, telemetry
from x64_profile_only import PROTOCOL, audit_native_cache, audit_profile_use, qualify_distribution


def verify_retained_evidence(evidence, expected):
    for name, sha256 in expected["evidence_sha256"].items():
        if digest(evidence / name) != sha256:
            raise RuntimeError(f"Retained production evidence changed: {name}")
    provenance = json.loads((evidence / "provenance.json").read_text())
    measurement = json.loads((evidence / "fixed-profile-dist.json").read_text())
    if (provenance["run_id"] != expected["run_id"] or provenance["attempt"] != expected["attempt"]
            or provenance["variant"] != "official" or measurement["exit_code"] != 0):
        raise RuntimeError("Retained distribution is not the designated successful production")
    return provenance, measurement


def qualify(root, evidence, output, expected):
    source = root / "r"
    protocol = json.loads(PROTOCOL.read_text())
    provenance, production = verify_retained_evidence(evidence, expected)
    if provenance["protocol"] != protocol:
        raise RuntimeError("Protocol differs from the retained production")
    for path, revision in ((source, protocol["rust_sha"]), (source / "src/llvm-project", protocol["llvm_sha"])):
        if subprocess.check_output(["git", "-C", path, "rev-parse", "HEAD"], text=True).strip() != revision:
            raise RuntimeError("Retained source identity changed")
    if (source / "bootstrap.toml").read_bytes() != (evidence / "production-bootstrap.toml").read_bytes():
        raise RuntimeError("Retained bootstrap configuration changed")
    test_module = source / "src/tools/opt-dist/src/tests.rs"
    if digest(test_module) != provenance["test_module_sha256"]:
        raise RuntimeError("Retained upstream test implementation changed")
    if digest(source / "src/tools/opt-dist/src/main.rs") != provenance["patches"]["tests-only-opt-dist-main"]:
        raise RuntimeError("Retained qualification dispatch changed")
    clang = source / "citools/clang-rust/bin"
    tools = tool_identity(clang)
    if not equivalent_tools(provenance["tools"], tools):
        raise RuntimeError("Native tool identities changed before qualification")
    profiles = {name: evidence / f"{name}-pgo.profdata" for name in ("rustc", "llvm")}
    if (digest(profiles["rustc"]) != protocol["rustc_profile_sha256"]
            or digest(profiles["llvm"]) != protocol["llvm_profile_sha256"]["official"]):
        raise RuntimeError("Retained profile inputs changed")
    audit_native_cache(source, output, profiles, tools)
    audit = audit_profile_use(source, evidence, profiles["rustc"])
    save(output / "profile-use-audit.json", audit)
    if not audit["rustc_profile_use"] or audit["rejected_profile_mismatch_warnings"]:
        raise RuntimeError("Retained profile-use audit failed")
    files = sorted(path for path in (source / "build/dist").iterdir() if path.is_file())
    check_distribution(files)
    manifest = [{"name": path.name, "bytes": path.stat().st_size, "sha256": digest(path)} for path in files]
    save(output / "dist-manifest.json", manifest)
    env = environment(output, clang)
    env.update({"PGO_HOST": protocol["host"], "DIST_TRY_BUILD": "0",
                "DIST_REQUIRE_ALL_TOOLS": "1", "COMPILETEST_REQUIRE_ALL_LLVM_COMPONENTS": "1",
                "WIX": str(source / "wix"), "CMAKE_TOOLCHAIN_FILE": str(evidence / "native-tools.cmake")})
    correctness = Path(os.environ["CORRECTNESS_TEMP"])
    start = time.time()
    qualify_distribution(source, output, env, correctness, provenance["test_module_sha256"],
                         protocol["build_cores"])
    if any(digest(source / "build/dist" / row["name"]) != row["sha256"] for row in manifest):
        raise RuntimeError("Distribution archive changed during qualification")
    save(output / "qualification-result.json", {
        "complete": True, "original_provenance": provenance, "production_measurement": production,
        "production_run_id": expected["run_id"], "production_attempt": expected["attempt"],
        "qualification_run_id": os.environ["GITHUB_RUN_ID"],
        "qualification_attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        "qualification_seconds": time.time() - start, "original_evidence": expected,
        "qualification": "Unmodified upstream opt-dist tests.rs passed; distribution archives unchanged",
        "scope": "Qualification-only recovery; no production rebuild or new production timing",
    })


def main():
    expected = json.loads((PROTOCOL.parent / "x64-profile-qualification-input.json").read_text())
    root = Path(expected["root"])
    if (os.name != "nt" or os.environ.get("RUNNER_NAME") != "MARCPE-TEST01-X64"
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted" or os.cpu_count() != 16):
        raise RuntimeError("Expected the dedicated 16-LP x64 runner")
    if (root / "owner-run.txt").read_text(encoding="utf-8-sig").strip() != f"{expected['run_id']}/{expected['attempt']}":
        raise RuntimeError("Retained experiment ownership mismatch")
    output = root / "e" / f"qualification-{os.environ['GITHUB_RUN_ID']}-{os.environ['GITHUB_RUN_ATTEMPT']}"
    output.mkdir()
    try:
        with telemetry(output, build_drive="D:"):
            qualify(root, root / "e/official", output, expected)
    except Exception as error:
        save(output / "failure.json", {"complete": False, "error": str(error), "unix": time.time()})
        result = output / "qualification-result.json"
        if result.exists():
            save(result, {**json.loads(result.read_text()), "complete": False, "rejection": str(error)})
        raise


if __name__ == "__main__":
    main()
