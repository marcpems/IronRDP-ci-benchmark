"""Analyze stable Cargo HTML timings without conflating unit-seconds and wall time."""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import statistics
import tomllib


NATIVE_NAMES = (
    "xtask-bootstrap", "workspace-tests", "native-tls-tests",
    "gateway-native-tls-tests", "gateway-smartcard-tests",
)


def js_json(html, name):
    marker = f"const {name} = "
    if marker not in html:
        raise ValueError(f"missing Cargo timing data: {name}")
    return json.JSONDecoder().raw_decode(html.split(marker, 1)[1].lstrip())[0]


def analyze_units(units, wall_seconds, workspace_names):
    events = defaultdict(list)
    groups = defaultdict(lambda: {"units": 0, "unit_seconds": 0.0})
    provenance = defaultdict(lambda: {"units": 0, "unit_seconds": 0.0})
    phases = defaultdict(float)
    for index, unit in enumerate(units):
        start, duration = unit["start"], unit["duration"]
        if start < 0 or duration < 0:
            raise ValueError("negative Cargo unit interval")
        script = unit["mode"] == "run-custom-build"
        if script:
            group = "build-script-execution"
        elif "build script" in unit["target"]:
            group = "build-script-compilation"
        elif "(test)" in unit["target"]:
            group = "test-target-compilation"
        elif unit["target"].strip().startswith("bin "):
            group = "binary-compilation"
        elif unit["target"].strip().startswith("example "):
            group = "example-compilation"
        else:
            group = "library-or-other-compilation"
        origin = "workspace" if unit["name"] in workspace_names else "dependency"
        for table, key in ((groups, group), (provenance, origin)):
            table[key]["units"] += 1
            table[key]["unit_seconds"] += duration
        if unit.get("sections"):
            for name, section in unit["sections"]:
                phases[name] += max(0.0, section["end"] - section["start"])
        else:
            phases["unpartitioned"] += duration
        if duration:
            events[start].append((index, True))
            events[start + duration].append((index, False))

    active = set()
    partitions = {
        "compiler_units_only_seconds": 0.0,
        "build_scripts_only_seconds": 0.0,
        "compiler_and_build_scripts_overlap_seconds": 0.0,
    }
    sole_unit = defaultdict(float)
    concurrency = defaultdict(float)
    previous = 0.0
    for timestamp in sorted(events):
        elapsed = timestamp - previous
        if active:
            script_count = sum(units[i]["mode"] == "run-custom-build" for i in active)
            if script_count == len(active):
                key = "build_scripts_only_seconds"
            elif script_count == 0:
                key = "compiler_units_only_seconds"
            else:
                key = "compiler_and_build_scripts_overlap_seconds"
            partitions[key] += elapsed
            concurrency[len(active)] += elapsed
            if len(active) == 1:
                sole_unit[next(iter(active))] += elapsed
        for index, starting in events[timestamp]:
            if starting:
                active.add(index)
            else:
                active.remove(index)
        previous = timestamp
    covered = sum(partitions.values())
    residual = wall_seconds - covered
    if residual < -0.1:
        raise ValueError(f"Cargo intervals exceed subprocess wall by {-residual:.3f}s")
    partitions["outside_tracked_units_seconds"] = residual
    top_units = [
        {**u, "sole_active_seconds": sole_unit[i],
         "origin": "workspace" if u["name"] in workspace_names else "dependency"}
        for i, u in enumerate(units)
    ]
    return {
        "wall_seconds": wall_seconds,
        "wall_partition": partitions,
        "unit_count": len(units),
        "sum_unit_seconds": sum(u["duration"] for u in units),
        "groups": dict(groups), "provenance": dict(provenance),
        "section_unit_seconds": dict(phases),
        "active_unit_concurrency_seconds": dict(concurrency),
        "top_units": sorted(top_units, key=lambda u: u["duration"], reverse=True)[:20],
        "sole_active_units": sorted(
            (u for u in top_units if u["sole_active_seconds"] > 0),
            key=lambda u: u["sole_active_seconds"], reverse=True,
        )[:20],
    }


def analyze_artifacts(root, source):
    workspace = tomllib.loads((source / "Cargo.toml").read_text(encoding="utf-8"))["workspace"]
    excluded = set(workspace.get("exclude", []))
    workspace_names = set()
    for member in workspace["members"]:
        for directory in source.glob(member):
            if directory.relative_to(source).as_posix() not in excluded:
                manifest = tomllib.loads((directory / "Cargo.toml").read_text(encoding="utf-8"))
                workspace_names.add(manifest["package"]["name"])
    results = []
    for environment in sorted(root.rglob("environment.json")):
        metadata = json.loads(environment.read_text(encoding="utf-8"))
        commands = {}
        for name in (*NATIVE_NAMES, "common", "wasm"):
            measurement = environment.parent / f"{name}.measurement.json"
            timing = environment.parent / f"{name}.timings.html"
            if not measurement.exists():
                continue
            row = json.loads(measurement.read_text(encoding="utf-8"))
            if not timing.exists():
                commands[name] = {"error": "no timing HTML", "measurement": row}
                continue
            html = timing.read_text(encoding="utf-8")
            units = js_json(html, "UNIT_DATA")
            analysis = analyze_units(units, row["seconds"], workspace_names)
            samples = js_json(html, "CPU_USAGE")
            intervals = [(b[0] - a[0], (a[1] + b[1]) / 2)
                         for a, b in zip(samples, samples[1:]) if b[0] > a[0]]
            analysis["system_cpu_sample_mean_percent"] = (
                sum(dt * pct for dt, pct in intervals) / sum(dt for dt, _ in intervals)
                if intervals else None
            )
            analysis["measurement"] = row
            commands[name] = analysis
        complete = all(
            name in commands and "error" not in commands[name]
            and commands[name]["measurement"]["exit_code"] == 0
            for name in NATIVE_NAMES
        )
        results.append({"metadata": metadata, "commands": commands, "native_complete": complete})
    if not results:
        raise ValueError("no benchmark environments found")
    return results


def markdown(results):
    platforms = sorted({r["metadata"]["environment"]["BENCHMARK_PLATFORM"] for r in results})
    lines = [
        "# Measured native Cargo command breakdown",
        "",
        "Wall seconds, median [min-max]. Complete successful native sequences only.",
        "Unit-seconds are overlapping elapsed intervals, not CPU-seconds.",
        "",
        "| Command | " + " | ".join(platforms) + " |",
        "|---|" + "---:|" * len(platforms),
    ]
    for name in (*NATIVE_NAMES, "native-total"):
        cells = []
        for platform_name in platforms:
            rows = [r for r in results if r["native_complete"]
                    and r["metadata"]["environment"]["BENCHMARK_PLATFORM"] == platform_name]
            samples = [
                sum(r["commands"][n]["wall_seconds"] for n in NATIVE_NAMES)
                if name == "native-total" else r["commands"][name]["wall_seconds"]
                for r in rows
            ]
            cells.append(
                f"{statistics.median(samples):.2f} [{min(samples):.2f}-{max(samples):.2f}], n={len(samples)}"
                if samples else "NO COMPLETE SAMPLE"
            )
        lines.append("| " + name + " | " + " | ".join(cells) + " |")
    for result in results:
        meta = result["metadata"]["environment"]
        lines.extend([
            "",
            f"## {meta['BENCHMARK_PLATFORM']} replicate {meta['BENCHMARK_REPLICATE']}",
            "",
            f"Native complete: {result['native_complete']}",
            "",
            "| Command | Wall | Compiler only | Build scripts only | Overlap | Outside units | Unit-seconds | Units | System CPU % |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for name in NATIVE_NAMES:
            if name not in result["commands"]:
                lines.append(f"| {name} | NOT MEASURED | | | | | | | |")
                continue
            item = result["commands"][name]
            if "error" in item:
                lines.append(f"| {name} | {item['error']} | | | | | | | |")
                continue
            partition = item["wall_partition"]
            cpu = item["system_cpu_sample_mean_percent"]
            cells = [f"{item['wall_seconds']:.2f}"]
            cells.extend(f"{v:.2f}" for v in partition.values())
            cells.extend([f"{item['sum_unit_seconds']:.2f}", str(item["unit_count"]),
                          f"{cpu:.1f}" if cpu is not None else "unavailable"])
            lines.append("| " + name + " | " + " | ".join(cells) + " |")
        main = result["commands"].get("workspace-tests")
        if main and "error" not in main:
            lines.extend([
                "", "### Longest workspace-test units", "",
                "| Package | Target | Origin | Unit seconds | Sole-active seconds |",
                "|---|---|---|---:|---:|",
            ])
            for unit in main["top_units"][:12]:
                lines.append(f"| {unit['name']} {unit['version']} | {unit['target']} | "
                             f"{unit['origin']} | {unit['duration']:.2f} | "
                             f"{unit['sole_active_seconds']:.2f} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    results = analyze_artifacts(args.artifacts, args.source)
    args.output.with_suffix(".json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown(results), encoding="utf-8")
    print(markdown(results).split("## ")[0])
