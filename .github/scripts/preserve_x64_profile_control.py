"""Preserve a qualified retained control with explicit, separate run identities."""

import json
import os
from pathlib import Path
import shutil

from build_arm_compilers import digest, save
from qualify_x64_profile_existing import verify_retained_evidence
from x64_profile_only import PROTOCOL

QUALIFICATION_RUN = "39608556774"


def recovered_result(qualification, expected, protocol, run_id, attempt):
    original = qualification["original_provenance"]
    if (not qualification["complete"] or qualification["original_evidence"] != expected
            or qualification["production_run_id"] != expected["run_id"]
            or qualification["production_attempt"] != expected["attempt"]
            or qualification["qualification_run_id"] != QUALIFICATION_RUN
            or qualification["qualification_attempt"] != "1"
            or original["protocol"] != protocol or original["variant"] != "official"
            or qualification["production_measurement"]["exit_code"] != 0):
        raise RuntimeError("Only the designated qualified control can be preserved")
    return {
        **original, "complete": True, "run_id": run_id, "attempt": attempt,
        "production_run_id": expected["run_id"], "production_attempt": expected["attempt"],
        "qualification_run_id": QUALIFICATION_RUN, "qualification_attempt": "1",
        "production_seconds": qualification["production_measurement"]["wall_seconds"],
        "qualification_seconds": qualification["qualification_seconds"],
        "qualification": qualification["qualification"],
        "recovered_control": True,
        "whole_job_note": "Production and qualification occurred in separate recorded runs; not a fresh whole-CI sample",
        "scope": protocol["scope"],
    }


def main():
    expected = json.loads((PROTOCOL.parent / "x64-profile-qualification-input.json").read_text())
    root = Path(expected["root"])
    if (os.environ.get("RUNNER_NAME") != "MARCPE-TEST01-X64"
            or os.environ.get("RUNNER_ENVIRONMENT") != "self-hosted"):
        raise RuntimeError("Wrong dedicated runner")
    if (root / "owner-run.txt").read_text().strip() != f"{expected['run_id']}/{expected['attempt']}":
        raise RuntimeError("Wrong original experiment owner")
    evidence = root / "e/official"
    original, production = verify_retained_evidence(evidence, expected)
    qualified = root / "e" / f"qualification-{QUALIFICATION_RUN}-1"
    qualification = json.loads((qualified / "qualification-result.json").read_text())
    if qualification["original_provenance"] != original or qualification["production_measurement"] != production:
        raise RuntimeError("Qualification does not identify the archived production evidence")
    protocol = json.loads(PROTOCOL.read_text())
    result = recovered_result(qualification, expected, protocol,
                              os.environ["GITHUB_RUN_ID"], os.environ["GITHUB_RUN_ATTEMPT"])
    manifest = json.loads((qualified / "dist-manifest.json").read_text())
    for row in manifest:
        archive = root / "r/build/dist" / row["name"]
        if archive.stat().st_size != row["bytes"] or digest(archive) != row["sha256"]:
            raise RuntimeError(f"Qualified archive changed: {row['name']}")
    destination = root / "e" / f"preserved-{os.environ['GITHUB_RUN_ID']}-{os.environ['GITHUB_RUN_ATTEMPT']}"
    destination.mkdir()
    for label, source in (("production", evidence), ("qualification", qualified)):
        folder = destination / label
        folder.mkdir()
        for path in source.iterdir():
            if path.is_file() and path.suffix in (".json", ".jsonl", ".toml", ".cmake", ".txt", ".stdout", ".stderr", ".profdata"):
                shutil.copy2(path, folder / path.name)
    shutil.copy2(Path(r"C:\pq085567741\readiness.json"), destination / "qualification/readiness.json")
    save(destination / "result.json", result)
    save(destination / "dist-manifest.json", manifest)
    with (root / "pair-run.txt").open("x") as owner:
        owner.write(f"{os.environ['GITHUB_RUN_ID']}/{os.environ['GITHUB_RUN_ATTEMPT']}\n")
    with Path(os.environ["GITHUB_ENV"]).open("a", encoding="utf-8") as github_env:
        github_env.write(f"PRESERVED_CONTROL={destination}\n")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
