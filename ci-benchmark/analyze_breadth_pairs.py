"""Validate frozen base/test breadth pairs and estimate wall-clock effects."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import re
import statistics
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".github/scripts"))
from analyze_arm_ab import interval
from breadth_probe import cargo_artifacts
from native_ci_probe import paired_order


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_matrix(root, protocol, corpus, reference, protocol_sha256):
    projects = {p["id"]: p for p in corpus["projects"]}
    scenarios = {s["id"]: s for s in corpus["scenarios"]}
    matrix, attempts, identities, sources, correctness = {}, set(), set(), {}, []
    for path in sorted(root.rglob("index.json")):
        index = read(path)
        require(index["complete"] and index["status"] == "passed"
                and index["protocol"] == protocol
                and index["protocol_sha256"] == protocol_sha256
                and index["corpus_sha256"] == protocol["corpus_sha256"],
                "Incomplete job or changed frozen protocol")
        project_id, vm = index["project"], index["replicate"]
        require(project_id in protocol["projects"] and vm in range(1, protocol["independent_vms"] + 1)
                and index["vm"] == vm and index["cores"] == protocol["cores"],
                "Unexpected project, machine or CPU budget")
        require(vm not in matrix.setdefault(project_id, {}), "Duplicate project/machine")
        attempts.add((index["run_id"], index["attempt"]))
        tools = index["tool_identity"]
        require(tools == read(path.parent / "toolchain.json"), "Changed tool identity receipt")
        require(tools["stdlib"] == reference["stdlib"]
                and tools["cargo_sha256"] == reference["cargo_sha256"]
                and tools["rustdoc_sha256"] == protocol["rustdoc_sha256"]
                and tools["compiler_metadata"] == reference["compiler_metadata"]["local"]
                and all(tools["artifact_evidence"][key] == reference["artifact_evidence"]["local"][key]
                        for key in ("archive_sha256", "result_sha256")),
                "Changed common tools or qualified compiler provenance")
        for variant, original in (("base", "official"), ("test", "local")):
            actual = tools["variants"][variant]
            require(actual["rustc_verbose_version"] == reference["versions"][original]
                    and all(actual[k] == v for k, v in protocol["compiler_pins"][variant].items()),
                    "Wrong base/test compiler executable or driver")
        identities.add(json.dumps({k: v for k, v in tools.items() if k != "rustdoc"}, sort_keys=True))
        expected = [(r, scenario, position, variant)
                    for r in range(protocol["warmup_rounds"] + protocol["measured_rounds"])
                    for scenario in protocol["scenarios"]
                    for position, variant in enumerate(paired_order(protocol["variants"], vm, r))]
        require([(e["round"], e["scenario"], e["position"], e["variant"]) for e in index["runs"]] == expected,
                "Incomplete or incorrectly ordered paired matrix")
        observations = {s: {v: [] for v in protocol["variants"]} for s in protocol["scenarios"]}
        result_paths = set()
        for entry in index["runs"]:
            require(entry["status"] == "passed", "Failed or pending trial")
            warmup = entry["round"] < protocol["warmup_rounds"]
            require(entry["warmup"] == warmup
                    and entry["exclusion"] == ("preplanned-warmup" if warmup else None),
                    "Changed sample exclusion")
            result_path = (path.parent / entry["path"]).resolve()
            require(result_path.is_relative_to(path.parent.resolve()) and result_path not in result_paths,
                    "Escaping or reused cell path")
            result_paths.add(result_path)
            result = read(result_path)
            project, scenario = projects[project_id], scenarios[entry["scenario"]]
            variant = entry["variant"]
            require(result["status"] == "non-qualifying-smoke"
                    and result["project"] == project_id and result["scenario"] == scenario
                    and result["source_revision"] == project["revision"]
                    and result["lock_sha256"] == project["lock_sha256"]
                    and result["target"] == protocol["host"]
                    and result["tool_identity"] == {**tools, "variant": variant}
                    and result["measurement"] == entry["measurement"],
                    "Changed cell inputs, variant or measurement")
            sources.setdefault(project_id, set()).add(
                (result["git_index_sha256"], result["edit_original_sha256"]
                 if scenario["mode"] == "edit" else None))
            compiler = result["compiler"].replace("\\", "/")
            official_suffix = f"/rustup/toolchains/{protocol['rust_version']}-{protocol['host']}/bin/"
            require(compiler.endswith(
                official_suffix + "rustc.exe" if variant == "base" else
                f"/rustc-{protocol['rust_version']}-{protocol['host']}/rustc/bin/rustc.exe")
                and result["cargo"].replace("\\", "/").endswith(official_suffix + "cargo.exe")
                and tools["rustdoc"].replace("\\", "/").endswith(official_suffix + "rustdoc.exe"),
                "Wrong compiler/common tool path")
            env = result["environment"]
            require(env["CARGO_INCREMENTAL"] == scenario["incremental"]
                    and env["CARGO_NET_OFFLINE"] == "true"
                    and env["CARGO_BUILD_JOBS"] == str(protocol["cores"]),
                    "Changed incremental/offline/worker settings")
            command = [result["cargo"], *scenario["cargo_command"], *project["cargo_args"],
                       "--frozen", "--message-format=json", "--target", protocol["host"]]
            require(len(result["setup"]) == (0 if scenario["mode"] == "full" else 1),
                    "Missing or unexpected incremental seed")
            for row in [*result["setup"], result["measurement"]]:
                require(row["exit_code"] == 0 and row["command"] == command
                        and len(set(row["affinity"])) == protocol["cores"]
                        and all(math.isfinite(row[k]) and row[k] > 0 for k in ("wall_seconds", "cpu_seconds"))
                        and abs(row["cpu_seconds"] - row["user_seconds"] - row["kernel_seconds"]) < 1e-6
                        and row["cpu_seconds"] <= row["wall_seconds"] * protocol["cores"] * 1.05 + .1,
                        "Failed command, wrong affinity or invalid timing")
                require(all(p["image"].replace("\\", "/").lower().endswith("/bin/hostx64/x64/vctip.exe")
                            and "/vc/tools/msvc/" in p["image"].replace("\\", "/").lower()
                            for p in row.get("background_processes_at_completion", [])),
                        "Unexpected surviving process")
            measured = result["measurement"]
            observed = cargo_artifacts(
                (result_path.parent / "measured.stdout").read_text(encoding="utf-8"), scenario["mode"])
            require(all(measured[key] == value for key, value in observed.items()),
                    "Changed Cargo artifact accounting")
            require((measured["compiled_artifacts"] == 0 and measured["fresh_artifacts"] > 0)
                    if scenario["mode"] == "noop" else measured["compiled_artifacts"] > 0,
                    "Incorrect fresh/compiled artifact behavior")
            policy = "original-commands" if warmup else "not-run-in-this-cell"
            require(result["correctness_policy"] == entry["correctness_policy"] == policy,
                    "Changed correctness policy")
            expected_check_path = f"r0-{variant}-{scenario['id']}/results.json"
            require(entry["correctness_path"] == expected_check_path, "Wrong warmup correctness linkage")
            check_path = path.parent / expected_check_path
            require(hashlib.sha256(check_path.read_bytes()).hexdigest() == entry["correctness_sha256"],
                    "Changed correctness evidence")
            require(len(result["correctness"]) == (len(project["correctness"]) if warmup else 0),
                    "Missing original correctness or unexpected measured-cell checks")
            for n, (check, original) in enumerate(zip(result["correctness"], project["correctness"])):
                require(check["exit_code"] == 0
                        and check["command"] == [result["cargo"], *original, "--frozen",
                                                  "--target", protocol["host"]],
                        "Failed or changed correctness command")
                text = (result_path.parent / f"correctness-{n}.stdout").read_text(encoding="utf-8")
                summaries = re.findall(r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; "
                                       r"\d+ measured; (\d+) filtered out;", text)
                require(summaries and all(int(failed) == int(filtered) == 0
                                         for _, failed, _, filtered in summaries),
                        "Missing, failed or filtered correctness output")
                correctness.append({"project": project_id, "vm": vm, "variant": variant,
                                    "scenario": scenario["id"], "command": original,
                                    "passed": sum(int(p) for p, _, _, _ in summaries),
                                    "upstream_ignored": sum(int(i) for _, _, i, _ in summaries)})
            if not warmup:
                observations[scenario["id"]][variant].append(measured["wall_seconds"])
        require(all(len(values) == protocol["measured_rounds"] for variants in observations.values()
                    for values in variants.values()), "Missing measured repetitions")
        matrix[project_id][vm] = {
            scenario: {variant: statistics.mean(values) for variant, values in variants.items()}
            for scenario, variants in observations.items()
        }
    require(set(matrix) == set(protocol["projects"]) and len(attempts) == len(identities) == 1
            and all(set(vms) == set(range(1, protocol["independent_vms"] + 1)) for vms in matrix.values()),
            "Expected all projects/machines with identical tools and one workflow attempt")
    require(all(len({index_hash for index_hash, _ in values}) == 1
                and len({edit_hash for _, edit_hash in values if edit_hash is not None}) <= 1
                for values in sources.values()), "Changed source/index identity")
    return matrix, next(iter(attempts)), correctness


def estimate(matrix, protocol):
    projects = protocol["projects"]
    scenarios = protocol["scenarios"]
    ids = {project: sorted(matrix[project]) for project in projects}
    rng = random.Random(protocol["analysis"]["bootstrap_seed"])
    draws = [{project: rng.choices(ids[project], k=len(ids[project])) for project in projects}
             for _ in range(protocol["analysis"]["bootstrap_draws"])]

    def point(project, scenario, selected):
        base = statistics.mean(matrix[project][vm][scenario]["base"] for vm in selected)
        test = statistics.mean(matrix[project][vm][scenario]["test"] for vm in selected)
        return {"base_seconds": base, "test_seconds": test, "saved_seconds": base - test,
                "reduction_fraction": 1 - test / base}

    cells = []
    samples = {}
    for project in projects:
        for scenario in scenarios:
            value = point(project, scenario, ids[project])
            resampled = [point(project, scenario, draw[project]) for draw in draws]
            samples[project, scenario] = resampled
            cells.append({"project": project, "scenario": scenario, **value,
                          "ci95": {key: interval([sample[key] for sample in resampled]) for key in value}})

    families = []
    for scenario in scenarios:
        points = [row for row in cells if row["scenario"] == scenario]
        reduction = 1 - math.exp(statistics.mean(
            math.log(row["test_seconds"] / row["base_seconds"]) for row in points))
        resampled = [1 - math.exp(statistics.mean(
            math.log(samples[project, scenario][i]["test_seconds"]
                     / samples[project, scenario][i]["base_seconds"]) for project in projects))
            for i in range(len(draws))]
        ci = interval(resampled)
        families.append({"scenario": scenario, "equal_project_reduction_fraction": reduction,
                         "ci95": ci,
                         "conclusion": ("supports-reduction" if ci[0] > 0 else
                                        "supports-slowdown" if ci[1] < 0 else "inconclusive")})
    return {"cells": cells, "families": families}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--protocol", type=Path,
                        default=Path(__file__).parent / "breadth/paired-protocol.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = read(args.protocol)
    corpus_path = Path(__file__).parent / "breadth/corpus.json"
    require(hashlib.sha256(corpus_path.read_bytes()).hexdigest() == protocol["corpus_sha256"],
            "Changed frozen corpus")
    with zipfile.ZipFile(Path(__file__).with_name("x64-pgo-fresh-replay-evidence.zip")) as archive:
        reference_bytes = archive.read(protocol["reference_index_member"])
    require(hashlib.sha256(reference_bytes).hexdigest() == protocol["reference_index_sha256"],
            "Changed qualified compiler reference")
    matrix, attempt, correctness = load_matrix(
        args.evidence, protocol, read(corpus_path), json.loads(reference_bytes),
        hashlib.sha256(args.protocol.read_bytes()).hexdigest())
    report = {"schema": 1, "protocol": protocol, "workflow_attempt": attempt,
              "vm_means": matrix, **estimate(matrix, protocol), "correctness": correctness,
              "evidence_sha256": {
                  p.relative_to(args.evidence).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(args.evidence.rglob("*")) if p.is_file()
              }}
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["families"], indent=2))


if __name__ == "__main__":
    main()
