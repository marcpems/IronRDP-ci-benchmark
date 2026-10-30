"""Verify the complete factorial matrix before publishing any effect estimate."""

import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import statistics

from verify_x64_rust_thin import equal_number, require, verify_block
from x64_factorial_thin import ARMS, HOST, PROTOCOL, order, read, summarize, verify_records


def verify(artifacts, run_id, head, attempt):
    protocol = read(PROTOCOL)
    records = {arm: read(artifacts / f"factorial-{arm}-evidence/result.json") for arm in ARMS}
    verify_records(records, protocol)
    for arm, record in records.items():
        require(record["run_id"] == run_id and record["harness_sha"] == head
                and record["attempt"] == str(attempt), "Producer run/head/attempt mismatch")
        evidence = artifacts / f"factorial-{arm}-evidence"
        require(not (evidence / "failure.json").exists(), "Producer failure exists")
        require((evidence / "bootstrap.toml").read_text() == record["configuration"], "Config changed")
        require(read(evidence / "profile-use-audit.json") == record["profile_use_audit"], "Audit changed")
        patch = (evidence / "source.patch").read_bytes()
        require(hashlib.sha256(patch).hexdigest() == record["source_patch_sha256"], "Source patch changed")
        text = patch.decode()
        additions = [line for line in text.splitlines() if line.startswith("+") and not line.startswith("+++")]
        deletions = [line for line in text.splitlines() if line.startswith("-") and not line.startswith("---")]
        require(additions == ["+    builtins_locator.run_in_dry_run();"] and not deletions
                and text.count("diff --git ") == 1, "Unexpected source changes")
        rust_thin, llvm_thin = protocol["lto_factors"][arm]
        log = (evidence / "fixed-profile-dist.stderr").read_text(errors="replace")
        commands = [line for line in log.splitlines()
                    if "--crate-name rustc_driver " in line and "-Cprofile-use=" in line]
        require(len(commands) == 1, "Missing final driver invocation")
        for flag in ("-Zdylib-lto", "-Clto=thin ", "-Cembed-bitcode=yes"):
            require((flag in commands[0]) == rust_thin, "Actual driver LTO flags differ")
        require("-C codegen-units=1" in commands[0]
                and "-Cprofile-use=D:/ri/profiles/rustc-pgo.profdata" in commands[0],
                "Actual driver codegen/profile flags differ")
        suffix = re.search(r"-C extra-filename=(-[0-9a-f]+)", commands[0]).group(1)
        require(record["driver"] == f"bin/rustc_driver{suffix}.dll", "Wrong packaged final driver")
        cache = {}
        for line in (evidence / "LLVM-CMakeCache.txt").read_text().splitlines():
            if line and not line.startswith(("#", "//")) and ":" in line and "=" in line:
                key, value = line.split("=", 1)
                cache[key.split(":", 1)[0]] = value
        require(cache.get("LLVM_ENABLE_LTO", "OFF").upper() in (("THIN",) if llvm_thin else ("OFF", "")),
                "Native LLVM LTO factor differs")
        for variable, name in (("CMAKE_LINKER", "lld-link.exe"), ("CMAKE_AR", "llvm-lib.exe")):
            require(PureWindowsPath(cache[variable]) == PureWindowsPath(record["tools"]["files"][name]["path"]),
                    "Native linker/librarian differs")
        require(cache["LLVM_PROFDATA_FILE"].replace("\\", "/") == "D:/ri/profiles/llvm-pgo.profdata"
                and not any(value for key, value in cache.items() if "COMPILER_LAUNCHER" in key),
                "Wrong native profile or enabled compiler cache")
        production = read(evidence / "fixed-profile-dist.json")
        require(production == record["production"] and production["exit_code"] == 0
                and production["affinity"] == [0, 1, 2, 3], "Unqualified compiler build")
    vm_means, identities, expected_lock = [], [], None
    expected_tests = {"workspace-tests": 3604, "native-tls-tests": 1,
                      "gateway-native-tls-tests": 10, "gateway-smartcard-tests": 13}
    prefix = f"lib/rustlib/{HOST}/lib/"
    for vm in range(1, 5):
        root = artifacts / f"factorial-consumer-{vm}"
        index = read(root / "index.json")
        require(index["complete"] is True and index["full_release_qualified"] is False
                and index["vm"] == vm and index["protocol"] == protocol, "Wrong/incomplete consumer")
        require(not (root / "failure.json").exists(), "Consumer failure exists")
        require(index["run_id"] == run_id and index["harness_sha"] == head
                and index["attempt"] == str(attempt), "Consumer run/head/attempt mismatch")
        require(index["compilers"] == records, "Consumer did not use this producer matrix")
        require(index["cargo_sha256"] == records["baseline"]["stage0_cargo_sha256"], "Wrong Cargo")
        if expected_lock is None:
            expected_lock = index["workload_lock_sha256"]
        require(index["workload_lock_sha256"] == expected_lock, "Consumer lockfiles differ")
        for arm in ARMS:
            expected = {name: value for name, value in records[arm]["files"].items()
                        if not name.startswith(prefix)}
            expected.update({prefix + name: value for name, value in records["baseline"]["stdlib"].items()})
            evaluated = index["evaluated_packages"][arm]
            require(evaluated["evaluated_files"] == expected
                    and evaluated["original_archive_sha256"] == records[arm]["archive_sha256"],
                    "Undeclared evaluated-package modification")
            identity = read(root / f"identity-{arm}/identity.json")
            expected_driver = PureWindowsPath(r"D:\ri") / arm / PureWindowsPath(records[arm]["driver"])
            require(identity["exit_code"] == 0
                    and PureWindowsPath(identity["loaded_driver"]) == expected_driver,
                    "Wrong/unobserved runtime driver")
            for name in ("bin/rustc.exe", records[arm]["driver"]):
                require(identity["files"][name] == records[arm]["files"][name], "Driver/exe hash differs")
            counts = verify_block(root / f"correctness-{arm}", True)["native_test_counts"]
            require({name: row["passed"] for name, row in counts.items()} == expected_tests,
                    "Pinned native correctness counts differ")
        expected_runs = [(round_index, arm, pos) for round_index in range(4)
                         for pos, arm in enumerate(order(vm, round_index))]
        require(len(index["runs"]) == len(expected_runs), "Incomplete rounds")
        measured = {metric: {arm: [] for arm in ARMS} for metric in ("wall_seconds", "cpu_seconds")}
        for run, (round_index, arm, position) in zip(index["runs"], expected_runs):
            name = f"round-{round_index}-{arm}"
            require((run["round"], run["variant"], run["position"], run["warmup"], run["path"]) ==
                    (round_index, arm, position, round_index == 0, f"{name}/results.json"),
                    "Prespecified order or exclusion changed")
            identity = read(root / name / "compiler-identity.json")
            expected_exe = PureWindowsPath(r"D:\ri") / arm / "bin/rustc.exe"
            require(PureWindowsPath(identity["RUSTC"]) == expected_exe, "Wrong measured compiler selection")
            for filename in ("bin/rustc.exe", records[arm]["driver"]):
                require(identity["files"][filename] == records[arm]["files"][filename],
                        "Measured compiler hash differs")
            totals = verify_block(root / name, False)
            for metric in measured:
                equal_number(run[metric], totals[metric])
                if not run["warmup"]:
                    measured[metric][arm].append(float(totals[metric]))
        vm_means.append({metric: {arm: statistics.mean(values) for arm, values in by_arm.items()}
                         for metric, by_arm in measured.items()})
        identities.append(read(root / "hardware.json"))
    require(len({row["Runner"] for row in identities}) == 4, "Consumers are not distinct runner allocations")
    return {"complete": True, "run_id": run_id, "head": head, "attempt": str(attempt),
            "protocol": protocol, "vm_means": vm_means, "hardware": identities,
            "effects": summarize(vm_means),
            "qualification": "Native correctness and loaded drivers verified; compiler-only isolation with shared stdlib, not full releases"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.artifacts, args.run_id, args.head, args.attempt)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["effects"], indent=2))
