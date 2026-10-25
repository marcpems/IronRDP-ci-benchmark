"""Offline, opt-in refinement of breadth lock intersections (never qualification).

Inputs are captured Cargo metadata --format-version=1, Cargo JSON stdout, the
pinned project Cargo.lock and a capture JSON record:
  schema: 1, project: corpus ID, scenario: corpus scenario ID,
  source_revision: pinned revision, target: explicit target triple,
  selected_package_ids: exact metadata IDs of corpus selected_packages,
  metadata: {command: [...], exit_code: 0, filter_platform: target or null},
  cargo: {command: [...], exit_code: 0}.

Commands include the executable. Cargo arguments must be scenario.cargo_command,
project.cargo_args, --frozen, --message-format=json, --target TARGET, in that order.
Metadata requires metadata, --format-version 1 (or =1), --frozen (or --locked
--offline), the project's feature arguments and optionally --filter-platform
TARGET, in any order. The metadata record can retain tool versions and receipt
fields. With --resolved-only, omit cargo and --messages entirely: observation
fields are null and observation_status is resolved-not-observed, not build success.
Capture provenance is caller-attested, not a live source/command verification.
No commands other than local git show are executed by this postprocessor.
"""

import argparse
import json
from pathlib import Path

from breadth_audit import git, overlap, packages, sha256


def strings(value, label, nonempty=False):
    if (not isinstance(value, list) or any(not isinstance(v, str) or not v for v in value)
            or (nonempty and not value)):
        raise ValueError(f"invalid {label}")
    return value


def feature_args(args):
    result = []
    index = 0
    while index < len(args):
        arg = args[index]
        if arg in ("--all-features", "--no-default-features"):
            result.append(arg)
        elif arg in ("--features", "-F"):
            if index + 1 == len(args):
                raise ValueError("missing feature argument")
            index += 1
            result.extend((arg, args[index]))
        elif arg.startswith(("--features=", "-F")):
            result.append(arg)
        index += 1
    return result


def metadata_options(command):
    parser = argparse.ArgumentParser(add_help=False, exit_on_error=False)
    parser.add_argument("--format-version")
    parser.add_argument("--filter-platform")
    parser.add_argument("--features", "-F", action="append", default=[])
    for flag in ("frozen", "locked", "offline", "all-features", "no-default-features"):
        parser.add_argument(f"--{flag}", action="store_true")
    try:
        options, unknown = parser.parse_known_args(command[2:])
    except argparse.ArgumentError as error:
        raise ValueError("invalid metadata command") from error
    if (command[1:2] != ["metadata"] or unknown or options.format_version != "1"
            or not (options.frozen or (options.locked and options.offline))):
        raise ValueError("invalid metadata command or missing frozen/offline lock constraint")
    return options


def validate_capture(manifest, capture, resolved_only=False):
    if capture.get("schema") != 1:
        raise ValueError("unsupported capture schema")
    project = next((p for p in manifest["projects"] if p["id"] == capture.get("project")), None)
    scenario = next((s for s in manifest["scenarios"] if s["id"] == capture.get("scenario")), None)
    if project is None or scenario is None:
        raise ValueError("unknown project or scenario")
    if capture.get("source_revision") != project["revision"]:
        raise ValueError("wrong captured source revision")
    target = capture.get("target")
    if not isinstance(target, str) or not target or target != manifest["host"]:
        raise ValueError("target must match the pinned Windows host")
    roots = strings(capture.get("selected_package_ids"), "selected package IDs", True)
    if len(roots) != len(set(roots)):
        raise ValueError("duplicate selected package IDs")
    metadata = capture.get("metadata")
    cargo = capture.get("cargo")
    if not isinstance(metadata, dict) or (not resolved_only and not isinstance(cargo, dict)):
        raise ValueError("missing command capture")
    if resolved_only and "cargo" in capture:
        raise ValueError("resolved-only capture must not include a Cargo build record")
    for row in (metadata,) if resolved_only else (metadata, cargo):
        if type(row.get("exit_code")) is not int or row["exit_code"] != 0:
            raise ValueError("missing or failed Cargo exit status")
        strings(row.get("command"), "captured command", True)
    if "filter_platform" not in metadata or metadata["filter_platform"] not in (None, target):
        raise ValueError("invalid metadata filter platform")
    for key, expected in (("source_revision", project["revision"]),
                          ("lock_sha256", project["lock_sha256"])):
        if key in metadata and metadata[key] != expected:
            raise ValueError(f"metadata receipt {key} mismatch")
    if "source_status" in metadata and metadata["source_status"] != "":
        raise ValueError("metadata receipt source was not clean")
    actual = metadata_options(metadata["command"])
    expected = metadata_options(["cargo", "metadata", "--format-version=1", "--frozen",
                                 *feature_args(project["cargo_args"])])
    if (actual.filter_platform != metadata["filter_platform"]
            or any(getattr(actual, key) != getattr(expected, key)
                   for key in ("features", "all_features", "no_default_features"))):
        raise ValueError("metadata command does not match declared platform/features")
    expected = [*scenario["cargo_command"], *project["cargo_args"],
                "--frozen", "--message-format=json", "--target", target]
    if not resolved_only and cargo["command"][1:] != expected:
        raise ValueError("Cargo command does not match project/scenario/target")
    return project, scenario


def training_packages(manifest, audit, locks):
    if (audit.get("schema") != 1 or audit.get("training") != manifest["training"]
            or not isinstance(audit.get("selectors"), dict)):
        raise ValueError("training audit does not match corpus")
    selectors = audit["selectors"]
    if set(selectors) != {"llvm", "rustc"}:
        raise ValueError("missing training phases")
    names = set()
    for phase, selected in selectors.items():
        names.update(strings(selected, f"{phase} selectors", True))
    fixtures = audit.get("fixtures", [])
    if (len(fixtures) != len(names) or {f["fixture"] for f in fixtures} != names
            or set(locks) != names):
        raise ValueError("incomplete training fixture locks")
    result = {}
    for fixture in fixtures:
        name = fixture["fixture"]
        if sha256(locks[name]) != fixture["lock_sha256"]:
            raise ValueError(f"wrong training lockfile: {name}")
        result[name] = packages(locks[name])
    return result


def resolved_packages(metadata, lock):
    if metadata.get("version") != 1 or not isinstance(metadata.get("packages"), list):
        raise ValueError("invalid Cargo metadata format")
    resolve = metadata.get("resolve")
    if not isinstance(resolve, dict) or not isinstance(resolve.get("nodes"), list):
        raise ValueError("missing Cargo metadata resolve (do not use --no-deps)")
    locked = {}
    for row in packages(lock):
        key = (row["name"], row["version"], row.get("source"))
        locked.setdefault(key, []).append(row)
    catalog = {}
    for row in metadata["packages"]:
        if not isinstance(row, dict):
            raise ValueError("invalid metadata package")
        package_id = row.get("id")
        if not isinstance(package_id, str) or not package_id or package_id in catalog:
            raise ValueError("missing or duplicate metadata package ID")
        if not all(isinstance(row.get(key), str) and row[key] for key in ("name", "version")):
            raise ValueError("missing metadata package name/version")
        source = row.get("source")
        if "source" not in row or (source is not None and (not isinstance(source, str) or not source)):
            raise ValueError("invalid metadata package source")
        matches = locked.get((row["name"], row["version"], source), [])
        if len(matches) != 1:
            raise ValueError(f"metadata package has no unique lock identity: {package_id}")
        # IDs are opaque: registry IDs need not resemble source strings, and path
        # IDs must never be mistaken for registry identity by parsing their text.
        catalog[package_id] = {
            "package_id": package_id, "package": matches[0],
            "metadata_source": source, "manifest_path": row.get("manifest_path"),
        }
    nodes = {}
    for row in resolve["nodes"]:
        if not isinstance(row, dict) or row.get("id") not in catalog or row["id"] in nodes:
            raise ValueError("unknown or duplicate resolve node")
        strings(row.get("dependencies"), "resolve dependencies")
        strings(row.get("features"), "resolved features")
        nodes[row["id"]] = row
    if set(nodes) != set(catalog):
        raise ValueError("metadata packages and resolve nodes differ")
    if any(dep not in nodes for row in nodes.values() for dep in row["dependencies"]):
        raise ValueError("unknown resolve dependency")
    return catalog, nodes


def artifact_messages(text, catalog, nodes):
    artifacts = []
    finished = False
    for line in text.splitlines():
        event = json.loads(line)
        if (not isinstance(event, dict) or not isinstance(event.get("reason"), str)
                or finished):
            raise ValueError("invalid Cargo message or message after build-finished")
        reason = event["reason"]
        if reason == "build-finished":
            if event.get("success") is not True:
                raise ValueError("failed Cargo build-finished")
            finished = True
        elif reason == "compiler-message":
            message = event.get("message")
            if not isinstance(message, dict) or not isinstance(message.get("level"), str):
                raise ValueError("invalid Cargo compiler message")
            if message["level"] in ("error", "failure-note"):
                raise ValueError("failed Cargo compiler message")
        elif reason == "compiler-artifact":
            package_id = event.get("package_id")
            if package_id not in catalog:
                raise ValueError("unknown artifact package ID")
            if type(event.get("fresh")) is not bool:
                raise ValueError("missing Cargo artifact freshness")
            target = event.get("target")
            if not isinstance(target, dict) or not isinstance(target.get("name"), str):
                raise ValueError("missing Cargo artifact target")
            strings(target.get("kind"), "artifact target kind", True)
            features = strings(event.get("features"), "artifact features")
            if not set(features) <= set(nodes[package_id]["features"]):
                raise ValueError("artifact features absent from captured resolve")
            artifacts.append({"package_id": package_id, "target": target,
                              "features": features, "fresh": event["fresh"]})
        elif reason != "build-script-executed":
            raise ValueError(f"unknown Cargo message reason: {reason}")
    if not finished or not artifacts:
        raise ValueError("missing Cargo build-finished or compiler artifacts")
    return artifacts


def postprocess(manifest, audit, locks, lock, metadata, messages, capture, resolved_only=False):
    if (messages is None) != resolved_only:
        raise ValueError("omit messages only in explicit resolved-only mode")
    project, scenario = validate_capture(manifest, capture, resolved_only)
    if sha256(lock) != project["lock_sha256"]:
        raise ValueError("wrong project lockfile")
    training = training_packages(manifest, audit, locks)
    catalog, nodes = resolved_packages(metadata, lock)
    roots = capture["selected_package_ids"]
    if any(root not in catalog or catalog[root]["metadata_source"] is not None for root in roots):
        raise ValueError("selected roots must be known path packages")
    if sorted(catalog[root]["package"]["name"] for root in roots) != sorted(project["selected_packages"]):
        raise ValueError("selected roots do not match corpus packages")
    selected = set()
    pending = list(roots)
    while pending:
        current = pending.pop()
        if current not in selected:
            selected.add(current)
            pending.extend(nodes[current]["dependencies"])
    artifacts = artifact_messages(messages, catalog, nodes) if not resolved_only else []
    if any(row["package_id"] not in selected for row in artifacts):
        raise ValueError("artifact outside selected-root resolve reachability")

    def scope(ids):
        rows = [{**catalog[key], "resolved_features": nodes[key]["features"]}
                for key in sorted(ids)]
        return {
            "package_count": len(rows), "packages": rows,
            "phases": {
                phase: overlap([row["package"] for row in rows],
                               {name: training[name] for name in names})
                for phase, names in audit["selectors"].items()
            },
        }

    return {
        "schema": 1, "status": "preparation-not-candidate-qualification",
        "project": project["id"], "scenario": scenario, "source_revision": project["revision"],
        "target": capture["target"], "requested_feature_args": feature_args(project["cargo_args"]),
        "capture": capture, "training": manifest["training"], "selectors": audit["selectors"],
        "training_fixture_locks": [
            {"fixture": name, "lock_sha256": sha256(locks[name])} for name in sorted(locks)
        ],
        "lock_sha256": sha256(lock),
        "resolve_scope": ("platform-filtered-selected-root-reachability"
                          if capture["metadata"]["filter_platform"] else
                          "unfiltered-selected-root-reachability"),
        "observation_status": "resolved-not-observed" if resolved_only else "observed-cargo-artifacts",
        "selected_resolve": scope(selected),
        "observed_artifacts": None if resolved_only else scope({row["package_id"] for row in artifacts}),
        "compiled_artifacts": (None if resolved_only else
                               scope({row["package_id"] for row in artifacts if not row["fresh"]})),
        "fresh_artifacts": (None if resolved_only else
                            scope({row["package_id"] for row in artifacts if row["fresh"]})),
        "artifacts": None if resolved_only else artifacts,
        "interpretation": [
            "Resolve reachability is not a compilation unit graph; dev edges and workspace feature "
            "unification may overapproximate the command even with --filter-platform.",
            "Unfiltered metadata also includes non-target dependencies; it is not a Windows closure.",
            "Resolved-only mode has no build evidence; null observation fields do not mean zero "
            "compiled packages. Input-preparation tool versions are not study compiler qualification.",
            "Only fresh=false compiler-artifact messages are observed compilations in this capture; "
            "fresh=true artifacts are reused, not compiled here. A package may appear in both.",
            "Artifact targets include host build scripts/proc macros; the requested target does not "
            "establish each artifact's compilation platform.",
            "Exact reuse means matching pinned lock name/version/source/checksum, never proof "
            "of actual training contributions. Path packages have name overlap only.",
            "Provenance is capture-declared; hashes bind input bytes, not their execution history. "
            "No dependency-disjointness, profile contribution or performance decision follows.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ("manifest", "training-audit", "perf", "lock", "metadata", "capture", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--messages", type=Path)
    parser.add_argument("--resolved-only", action="store_true")
    args = parser.parse_args()
    if (args.messages is None) != args.resolved_only:
        raise ValueError("supply --messages, or explicitly --resolved-only without --messages")
    names = ["manifest", "training_audit", "lock", "metadata", "capture"]
    if args.messages is not None:
        names.append("messages")
    inputs = {name: getattr(args, name).read_bytes()
              for name in names}
    manifest = json.loads(inputs["manifest"])
    audit = json.loads(inputs["training_audit"])
    locks = {
        row["fixture"]: git(args.perf, "show",
                            f"{manifest['training']['rustc_perf_sha']}:"
                            f"collector/compile-benchmarks/{row['fixture']}/Cargo.lock")
        for row in audit["fixtures"]
    }
    capture = json.loads(inputs["capture"])
    recorded_hash = capture.get("metadata", {}).get("sha256", {}).get("stdout")
    if recorded_hash is not None and recorded_hash != sha256(inputs["metadata"]):
        raise ValueError("metadata receipt stdout hash mismatch")
    result = postprocess(manifest, audit, locks, inputs["lock"], json.loads(inputs["metadata"]),
                         inputs["messages"].decode("utf-8") if "messages" in inputs else None,
                         capture, args.resolved_only)
    result["inputs"] = {name: {"path": str(getattr(args, name)), "sha256": sha256(data)}
                        for name, data in inputs.items()}
    if args.output.resolve() in {getattr(args, name).resolve() for name in inputs}:
        raise ValueError("output must not overwrite an input")
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
