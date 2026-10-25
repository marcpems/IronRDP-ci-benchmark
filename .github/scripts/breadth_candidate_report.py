"""Summarize a complete candidate-only breadth run without comparative claims."""

import argparse
import hashlib
import json
from pathlib import Path
import re


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def summarize(evidence):
    folders = sorted(evidence.glob("breadth-candidate-pilot-*"))
    if not folders:
        raise ValueError("no per-project pilot evidence")
    manifest = read(folders[0] / "current-candidate-corpus.json")
    selection = read(folders[0] / "custom-candidate.json")
    expected_projects = {p["id"]: p for p in manifest["projects"]}
    expected_scenarios = selection["pilot_scenarios"]
    if len(set(expected_scenarios)) != len(expected_scenarios):
        raise ValueError("duplicate scenario selection")
    rows, seen, run_ids = [], set(), set()
    tool_identity = None
    for folder in folders:
        pilot = read(folder / "pilot.json")
        if pilot["status"] != "passed-candidate-only-pilot-not-comparative-qualification":
            raise ValueError(f"incomplete or failed pilot: {folder.name}")
        project_id = pilot["project"]
        if project_id in seen or project_id not in expected_projects:
            raise ValueError(f"unexpected or duplicate project: {project_id}")
        seen.add(project_id)
        run_ids.add((pilot["run_id"], pilot["attempt"]))
        if (read(folder / "current-candidate-corpus.json") != manifest
                or read(folder / "custom-candidate.json") != selection):
            raise ValueError("projects used different frozen inputs")
        tools = read(folder / "toolchain.json")
        identity = {key: tools[key] for key in
                    ("rustc_verbose_version", "cargo_version", "executables", "installed_files")}
        if tool_identity is not None and identity != tool_identity:
            raise ValueError("projects used different installed tools")
        tool_identity = identity
        project = expected_projects[project_id]
        if [s["name"] for s in pilot["scenarios"]] != expected_scenarios:
            raise ValueError(f"incomplete scenario sequence: {project_id}")
        for scenario in pilot["scenarios"]:
            name = scenario["name"]
            result = read(folder / name / "results.json")
            audit = read(folder / name / "resolved-audit.json")
            if (result["status"] != "non-qualifying-smoke"
                    or result["project"] != project_id
                    or result["source_revision"] != project["revision"]
                    or result["lock_sha256"] != project["lock_sha256"]
                    or result["measurement"] != scenario["measurement"]
                    or result["correctness"] != scenario["correctness"]):
                raise ValueError(f"inconsistent cell evidence: {project_id}/{name}")
            checks = result["correctness"]
            if (len(checks) != len(project["correctness"])
                    or result["measurement"]["exit_code"] != 0
                    or any(check["exit_code"] != 0 for check in checks)):
                raise ValueError(f"missing or failed correctness: {project_id}/{name}")
            test_counts = []
            for index, (check, command) in enumerate(zip(checks, project["correctness"])):
                if check["command"][1:] != [*command, "--frozen", "--target", manifest["host"]]:
                    raise ValueError(f"changed correctness command: {project_id}/{name}")
                text = (folder / name / f"correctness-{index}.stdout").read_text(encoding="utf-8")
                summaries = re.findall(
                    r"test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; "
                    r"\d+ measured; (\d+) filtered out;", text)
                if not summaries or any(int(failed) or int(filtered)
                                        for _, failed, _, filtered in summaries):
                    raise ValueError(f"missing, failed or filtered tests: {project_id}/{name}")
                test_counts.append({
                    "command": command,
                    "passed": sum(int(passed) for passed, _, _, _ in summaries),
                    "upstream_ignored": sum(int(ignored) for _, _, ignored, _ in summaries),
                })
            row = result["measurement"]
            scopes = {}
            for scope in ("selected_resolve", "observed_artifacts", "compiled_artifacts", "fresh_artifacts"):
                scopes[scope] = {
                    "packages": audit[scope]["package_count"],
                    "exact_training_fixture_lock_overlap": {
                        phase: len(values["exact_locked_registry_or_git_reuse"])
                        for phase, values in audit[scope]["phases"].items()
                    },
                }
            rows.append({
                "project": project_id, "scenario": name,
                "wall_seconds": row["wall_seconds"], "command_tree_cpu_seconds": row["cpu_seconds"],
                "peak_job_committed_bytes": row["peak_job_memory_bytes"],
                "fresh_artifact_records": row["fresh_artifacts"],
                "compiled_artifact_records": row["compiled_artifacts"],
                "passed_correctness_commands": len(checks), "test_counts": test_counts,
                "audit_scopes": scopes,
            })
    if seen != set(expected_projects) or len(run_ids) != 1:
        raise ValueError("missing projects or mixed execution runs")
    run_id, attempt = next(iter(run_ids))
    return {
        "schema": 1, "status": "complete-candidate-only-observations",
        "recommendation": "no-go-for-broad-performance-or-shipping-qualification",
        "run_id": run_id, "attempt": attempt,
        "runner": selection["runner"], "logical_processors": manifest["cores"],
        "selection": selection,
        "tool_identity": {k: v for k, v in tool_identity.items() if k != "installed_files"},
        "rows": rows,
        "comparative_effects": None, "confidence_intervals": None, "aggregate_weighting": None,
        "limitations": [
            "One candidate on one machine; no matched controls or official comparator observations.",
            "No runtime-throughput or code-size regression measurements.",
            "No maintainer-approved thresholds or strict dependency-disjointness established.",
            "CPU is whole-command-tree; peak memory is committed Job memory, not RSS.",
            "Package overlap is fixture-lock identity reuse, not measured training-profile contribution.",
        ],
        "evidence_sha256": {
            path.relative_to(evidence).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for folder in folders for path in sorted(folder.rglob("*")) if path.is_file()
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(args.evidence)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
