"""Independently verify downloaded pilot receipts and recompute paired reductions."""

import argparse
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tomllib
import zipfile

HOST = "x86_64-pc-windows-msvc"
ARMS = ("baseline", "rust-thin")
COMMANDS = [
    ("xtask-bootstrap", ["build", "-p", "xtask"]),
    ("workspace-tests", ["test", "--workspace", "--no-run"]),
    ("native-tls-tests", ["test", "-p", "ironrdp-tls", "--test", "native_tls",
                          "--features", "native-tls", "--no-run"]),
    ("gateway-native-tls-tests", ["test", "-p", "ironrdp-mstsgu", "--test", "http_auth",
                                  "--features", "native-tls", "--no-run"]),
    ("gateway-smartcard-tests", ["test", "-p", "ironrdp-mstsgu", "--test", "http_auth",
                                 "--features", "native-tls,smartcard", "--no-run"]),
]
PROTOCOL = Path(__file__).resolve().parents[2] / "ci-benchmark/x64-rust-thin-incremental.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def number(value):
    result = Decimal(str(value))
    require(result.is_finite(), "Nonfinite measurement")
    return result


def equal_number(actual, expected):
    require(abs(number(actual) - number(expected)) < Decimal("0.000001"),
            f"Recorded total differs: {actual} versus {expected}")


def reduction(baseline, treatment):
    baseline, treatment = number(baseline), number(treatment)
    require(baseline > 0 and treatment > 0, "Reduction requires positive measurements")
    percent = 100 * (1 - treatment / baseline)
    return {"baseline_seconds": str(baseline), "treatment_seconds": str(treatment),
            "reduction_percent_decimal": str(percent),
            "reduction_percent_2dp": str(percent.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))}


def tools(identity):
    return {
        "msvc": identity["msvc"], "sdk": identity["sdk"],
        "files": {name: row["sha256"] for name, row in identity["files"].items()},
    }


def verify_block(directory, correctness):
    result = read(directory / "results.json")
    require(result["complete"] is True and result["correctness"] is correctness,
            f"Incomplete or wrong-scope block: {directory}")
    rows = result["rows"]
    require(len(rows) == len(COMMANDS), "Wrong command count")
    totals = {"wall_seconds": Decimal(0), "cpu_seconds": Decimal(0)}
    test_counts = {}
    for row, (name, arguments) in zip(rows, COMMANDS):
        require(row["name"] == name, "Original command order changed")
        require(row == read(directory / f"{name}.json"), f"Command receipt disagreement: {name}")
        args = [arg for arg in arguments if not (correctness and arg == "--no-run")]
        if correctness and name == "workspace-tests":
            args += ["--lib", "--bins", "--tests"]
        expected = [r"D:\ri\baseline\bin\cargo.exe", *args, "--frozen"]
        if not correctness:
            expected += ["--timings", "--message-format=json"]
        require(row["command"] == expected, f"Unexpected command: {row['command']}")
        require(row["exit_code"] == 0, f"Failed command: {name}")
        require(row["affinity"] == [0, 1, 2, 3], f"Wrong affinity: {name}")
        for key in ("wall_seconds", "cpu_seconds"):
            require(number(row[key]) > 0, f"Nonpositive measurement: {name}/{key}")
            totals[key] += number(row[key])
        equal_number(row["cpu_seconds"], number(row["user_seconds"]) + number(row["kernel_seconds"]))
        require((directory / f"{name}.stderr").is_file(), "Missing raw stderr")
        stdout = directory / f"{name}.stdout"
        require(stdout.is_file(), "Missing raw stdout")
        if correctness and name != "xtask-bootstrap":
            matches = re.findall(
                r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; "
                r"(\d+) measured; (\d+) filtered out;", stdout.read_text(encoding="utf-8"))
            require(matches, f"Missing native test outcomes: {name}")
            counts = {key: sum(int(row[index]) for row in matches)
                      for index, key in enumerate(("passed", "failed", "ignored", "measured", "filtered"))}
            require(counts["passed"] > 0 and counts["failed"] == 0, f"No passing native tests: {name}")
            test_counts[name] = counts
        if not correctness:
            compiled = 0
            with stdout.open(encoding="utf-8") as stream:
                for line in stream:
                    message = json.loads(line)
                    compiled += message.get("reason") == "compiler-artifact" and not message["fresh"]
            require(compiled > 0 and row["compiled_artifacts"] == compiled,
                    f"Compiled-artifact evidence disagrees: {name}")
            require((directory / f"{name}.timings.html").is_file(), "Missing Cargo timing receipt")
    for key, value in totals.items():
        equal_number(result[key], value)
    if correctness:
        totals["native_test_counts"] = test_counts
    return totals


def verify(artifacts, run_id, head, attempt):
    protocol = read(PROTOCOL)
    records = {}
    manifests = {}
    for arm in ARMS:
        evidence = artifacts / f"thin-{arm}-evidence"
        record = read(evidence / "result.json")
        require(record["build_complete"] is True and record["complete"] is False,
                "Build completion must not imply full qualification")
        require(record["variant"] == arm and record["protocol"] == protocol, "Wrong arm/protocol")
        require(record["run_id"] == run_id and record["attempt"] == str(attempt)
                and record["harness_sha"] == head, "Compiler run/head/attempt mismatch")
        require(not (evidence / "failure.json").exists(), "Compiler failure evidence is present")
        require(record["cache"] == {"enabled": False, "hit_rate": None}, "Cache policy changed")
        require(record["production"]["exit_code"] == 0
                and record["production"]["affinity"] == [0, 1, 2, 3], "Failed or wrong-affinity production")
        require(sha(evidence / "source.patch") == record["source_patch_sha256"], "Source patch hash changed")
        patch = (evidence / "source.patch").read_text()
        additions = [line for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++")]
        deletions = [line for line in patch.splitlines() if line.startswith("-") and not line.startswith("---")]
        require(additions == ["+    builtins_locator.run_in_dry_run();"]
                and not deletions and patch.count("diff --git ") == 1
                and "src/bootstrap/src/utils/helpers.rs" in patch, "Unexpected source changes")
        require((evidence / "bootstrap.toml").read_text() == record["configuration"], "Config receipt changed")
        config = tomllib.loads(record["configuration"])
        require(config["rust"]["lto"] == ("thin-local" if arm == "baseline" else "thin")
                and config["llvm"]["thin-lto"] is False
                and config["rust"]["codegen-units"] == 1
                and config["build"]["jobs"] == 4
                and config["target"][HOST]["linker"] == "link.exe", "Wrong intervention/native policy")
        for component in ("rustc", "llvm"):
            require(config["pgo"][component]["use"] == f"D:/ri/profiles/{component}-pgo.profdata",
                    "Wrong frozen profile path")
        cache = {}
        for line in (evidence / "LLVM-CMakeCache.txt").read_text().splitlines():
            if line and not line.startswith(("#", "//")) and ":" in line and "=" in line:
                key, value = line.split("=", 1)
                cache[key.split(":", 1)[0]] = value
        require(cache.get("LLVM_ENABLE_LTO", "OFF").upper() in ("", "OFF")
                and cache.get("LLVM_BUILD_INSTRUMENTED", "OFF") in ("", "OFF")
                and cache["LLVM_PROFDATA_FILE"].replace("\\", "/") == "D:/ri/profiles/llvm-pgo.profdata",
                "Native LLVM CMake profile/LTO state differs")
        for variable, name in (("CMAKE_LINKER", "link.exe"), ("CMAKE_AR", "lib.exe")):
            require(cache[variable].replace("\\", "/").lower()
                    == record["tools"]["files"][name]["path"].replace("\\", "/").lower(),
                    "Native CMake linking tool differs from recorded identity")
        audit = read(evidence / "profile-use-audit.json")
        require(audit["rustc_profile_use"] is True
                and not audit["rejected_profile_mismatch_warnings"]
                and audit["driver_thin_flag"] == (arm == "rust-thin"), "Profile/LTO audit failed")
        coverage = read(evidence / "coverage.json")
        require(all(coverage[name]["active_functions"] > 0
                    for name in ("X86TargetLowering", "InstCombine")), "Inactive backend profile")
        for smoke in ("smoke-compile", "smoke-run"):
            require(read(evidence / f"{smoke}.json")["exit_code"] == 0, "Compiler smoke failed")
        for expected in (f"host: {HOST}", f"commit-hash: {protocol['rust_sha']}",
                         f"release: {protocol['rust_version']}"):
            require(expected in record["version"].splitlines(), "Compiler version mismatch")
        package = artifacts / f"thin-{arm}-package"
        require(read(package / "e/result.json") == record, "Package and build evidence disagree")
        archive = package / "package.zip"
        require(sha(archive) == record["archive_sha256"]
                and archive.stat().st_size == record["archive_bytes"], "Package checksum/size mismatch")
        files = {}
        with zipfile.ZipFile(archive) as bundle:
            require(len(bundle.namelist()) == len(set(bundle.namelist())), "Duplicate archive member")
            for item in bundle.infolist():
                require(not item.is_dir() and not Path(item.filename).is_absolute()
                        and ".." not in Path(item.filename).parts, "Unsafe or unexpected archive member")
                with bundle.open(item) as stream:
                    files[item.filename] = hashlib.file_digest(stream, "sha256").hexdigest()
        require(files == record["files"], "Package file manifest differs from actual bytes")
        require(files["bin/cargo.exe"] == record["stage0_cargo_sha256"], "Wrong actual Cargo binary")
        prefix = f"lib/rustlib/{HOST}/lib/"
        stdlib = {name[len(prefix):]: value for name, value in files.items() if name.startswith(prefix)}
        require(stdlib == record["stdlib"], "Wrong actual native stdlib")
        records[arm] = record
        manifests[arm] = files
    baseline, treatment = (records[arm] for arm in ARMS)
    for key in ("source_patch_sha256", "native_inputs", "stage0_cargo_sha256", "stdlib", "image"):
        require(baseline[key] == treatment[key], f"Unmatched compiler input: {key}")
    require(tools(baseline["tools"]) == tools(treatment["tools"]), "Native build tool mismatch")
    left, right = (tomllib.loads(records[arm]["configuration"]) for arm in ARMS)
    right["rust"]["lto"] = "thin-local"
    require(left == right, "Additional compiler configuration intervention")
    consumer = artifacts / "thin-incremental-consumer-evidence"
    require(not (consumer / "failure.json").exists(), "Consumer failure evidence is present")
    index = read(consumer / "index.json")
    require(index["complete"] is True and index["pilot"] is True
            and index["full_release_qualified"] is False, "Wrong completion/qualification claim")
    require(index["protocol"] == protocol and index["run_id"] == run_id
            and index["attempt"] == str(attempt), "Consumer run/protocol mismatch")
    require(index["compilers"] == records and index["cargo_sha256"] == baseline["stage0_cargo_sha256"],
            "Consumer did not use the verified packages")
    require(tools(index["tools"]) == tools(baseline["tools"]), "Consumer native tools differ")
    meter = read(consumer / "meter-validation/self-test.json")
    require(meter["busy_descendant"]["exit_code"] == meter["sleep"]["exit_code"] == 0
            and meter["busy_descendant"]["cpu_seconds"] >= 0.25
            and meter["sleep"]["cpu_seconds"] <= 0.2
            and meter["affinity"]["exit_code"] == 0
            and meter["affinity"]["affinity"] == [0], "CPU meter qualification failed")
    workload_lock = subprocess.check_output(
        ["git", "-C", PROTOCOL.parents[1], "show", f"{protocol['source_sha']}:Cargo.lock"])
    require(hashlib.sha256(workload_lock).hexdigest() == index["workload_lock_sha256"],
            "Consumer lockfile differs from the exact pinned IronRDP Git blob")
    correctness_blocks = {
        arm: verify_block(consumer / f"correctness-{arm}", correctness=True)
        for arm in ARMS
    }
    correctness = {arm: result["native_test_counts"] for arm, result in correctness_blocks.items()}
    require(correctness["baseline"] == correctness["rust-thin"], "Native test populations differ")
    rounds = protocol["warmup_rounds"] + protocol["measured_rounds"]
    require(len(index["runs"]) == rounds * 2, "Incomplete round count")
    measured = {arm: [] for arm in ARMS}
    pairs = []
    for round_index in range(rounds):
        order = ARMS if round_index % 2 == 0 else ARMS[::-1]
        results = {}
        for position, arm in enumerate(order):
            entry = index["runs"][round_index * 2 + position]
            expected_path = f"round-{round_index}-{arm}/results.json"
            require(entry["variant"] == arm and entry["round"] == round_index
                    and entry["position"] == position and entry["path"] == expected_path
                    and entry["warmup"] == (round_index < protocol["warmup_rounds"]), "Order/warmup mismatch")
            totals = verify_block(consumer / f"round-{round_index}-{arm}", correctness=False)
            for key, value in totals.items():
                equal_number(entry[key], value)
            results[arm] = totals
            if not entry["warmup"]:
                measured[arm].append(totals)
        if round_index >= protocol["warmup_rounds"]:
            pairs.append({"round": round_index, **{
                key: reduction(results["baseline"][key], results["rust-thin"][key])
                for key in ("wall_seconds", "cpu_seconds")}})
    totals = {
        key: reduction(sum(row[key] for row in measured["baseline"]),
                       sum(row[key] for row in measured["rust-thin"]))
        for key in ("wall_seconds", "cpu_seconds")
    }
    return {
        "complete": True, "independently_verified": True, "run_id": run_id, "head_sha": head,
        "attempt": attempt, "full_release_qualified": False, "protocol": protocol,
        "paired_rounds": pairs, "ratio_of_sums": totals,
        "native_correctness": correctness,
        "overhead_outside_consumer_measurements": {
            "compiler_build": {
                arm: {key: records[arm]["production"][key] for key in ("wall_seconds", "cpu_seconds")}
                for arm in ARMS
            },
            "package_wall_seconds": {arm: records[arm]["packaging_seconds"] for arm in ARMS},
            "native_correctness": {
                arm: {key: str(correctness_blocks[arm][key]) for key in ("wall_seconds", "cpu_seconds")}
                for arm in ARMS
            },
            "dependency_fetch": {
                key: read(consumer / "fetch-outside-measurement.json")[key]
                for key in ("wall_seconds", "cpu_seconds")
            },
            "scope": "Compiler-only build and native correctness; not full-release production/qualification",
        },
        "paired_mean_reduction_percent": {
            key: str(sum(number(pair[key]["reduction_percent_decimal"]) for pair in pairs) / len(pairs))
            for key in ("wall_seconds", "cpu_seconds")
        },
        "rounding": "Decimal arithmetic; displayed percentage rounded half-up to two decimals",
        "limits": [
            "Descriptive one-build-pair, one-consumer-VM pilot; no population confidence intervals",
            "No full-release/extracted-distribution or doctest qualification",
            "Common stage0 Cargo, each compiler's own byte-identical native stdlib",
            "Compiler production, package transfer, dependency fetch and correctness excluded from consumer totals",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--attempt", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.artifacts.resolve(), args.run_id, args.head, args.attempt)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["ratio_of_sums"], indent=2))
