"""Render a loss-accounted timing inventory from collect.py's public evidence."""
from collections import defaultdict
from datetime import datetime
from html import escape
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
COLORS = {"Source": "#a78bfa", "Setup": "#94a3b8", "Main build": "#2563eb",
          "Upload": "#0891b2", "Unaccounted": "#cbd5e1", "LLVM/LLD": "#f59e0b",
          "Compiler": "#2563eb", "Libraries": "#06b6d4", "Tools": "#8b5cf6",
          "Docs": "#22c55e", "Packaging": "#f97316", "Tests": "#e11d48",
          "Build support": "#64748b", "Unresolved build": "#d1d5db"}


def dt(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def duration(a, b):
    return (dt(b) - dt(a)).total_seconds()


def step_category(name):
    if name in ("checkout the source code", "checkout submodules"):
        return "Source"
    if name == "run the build":
        return "Main build"
    if name.startswith("upload "):
        return "Upload"
    return "Setup"


def category(name):
    if name.startswith("Dist ") or "msi" in name:
        return "Packaging"
    if "LLVM" in name or " LLD " in name:
        return "LLVM/LLD"
    if "compiler artifacts" in name:
        return "Compiler"
    if "library artifacts" in name:
        return "Libraries"
    if (name.startswith("Documenting") or any(x in name for x in
            ("rustbook", "unstable-book", "error_index", "lint-docs"))):
        return "Docs"
    if name.startswith(("Testing", "test ", "Running")):
        return "Tests"
    if name.startswith("Building stage"):
        return "Tools"
    return "Build support"


def intervals(events, start, end):
    """GitHub groups are disjoint (bootstrap explicitly closes/resumes parents).

    Dist package timers are separate from groups. All uncovered time stays unknown;
    a container Dist extended timer is deliberately not treated as a leaf package.
    """
    groups, packages, timers, facts = [], [], [], []
    opened = None
    package = None
    active_timers = {}
    for event in events:
        line = event["text"]
        match = re.match(r"(\d{4}-\d\d-\d\dT\S+Z) (.*)", line)
        if not match:
            continue
        stamp, text = match.groups()
        if any(x in text for x in ("Cache hits", "Cache misses", "cpu cores",
                                   "MemTotal", "Image:", "Version:", "LLVM_VERSION_SUFFIX")):
            facts.append(event)
        timer = re.search(r"Section `(.+)` (starts|ended)", text)
        if timer:
            name, action = timer.groups()
            if action == "starts":
                active_timers[name] = stamp
            elif name in active_timers:
                a = active_timers.pop(name)
                timers.append({"name": name, "start": a, "end": stamp,
                               "seconds": duration(a, stamp), "end_line": event["line"]})
        if not (dt(start) <= dt(stamp) <= dt(end)):
            continue
        if "##[group]" in text:
            opened = (stamp, text.split("##[group]", 1)[1], event["line"])
        elif "##[endgroup]" in text and opened:
            a, name, number = opened
            groups.append({"start": a, "end": stamp, "name": name,
                           "line": number, "category": category(name)})
            opened = None
        elif text.startswith("Dist ") and not text.startswith("Dist extended"):
            package = (stamp, text, event["line"])
        elif "building `msi`" in text:
            package = (stamp, "MSI package", event["line"])
        elif re.search(r"finished in [\d.]+ seconds", text) and package:
            a, name, number = package
            packages.append({"start": a, "end": stamp, "name": name,
                             "line": number, "category": "Packaging"})
            package = None
    # Split at all boundaries, selecting the shortest containing observed interval.
    # This avoids double-counting even if future logs introduce nested markers.
    observed = groups + packages
    bounds = sorted({dt(start), dt(end)} |
                    {dt(i[k]) for i in observed for k in ("start", "end")})
    totals = defaultdict(float)
    for a, b in zip(bounds, bounds[1:]):
        covering = [i for i in observed if dt(i["start"]) <= a and dt(i["end"]) >= b]
        leaf = min(covering, key=lambda i: duration(i["start"], i["end"])) if covering else None
        totals[leaf["category"] if leaf else "Unresolved build"] += (b - a).total_seconds()
    for row in observed:
        row["seconds"] = duration(row["start"], row["end"])
    assert abs(sum(totals.values()) - duration(start, end)) < .01
    return dict(totals), observed, timers, facts


def svg(rows, path, title, subtitle, max_minutes=None):
    width, left, plot, step = 1200, 330, 790, 31
    height = 115 + step * len(rows)
    maximum = max_minutes or max(sum(v for _, v in parts) + offset for _, offset, parts in rows) * 1.08
    output = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
              '<rect width="100%" height="100%" fill="white"/>',
              '<g font-family="Arial,sans-serif" font-size="13" fill="#0f172a">',
              f'<text x="16" y="24" font-size="19">{escape(title)}</text>',
              f'<text x="16" y="46">{escape(subtitle)}</text>']
    for tick in range(0, int(maximum) + 1, 30):
        x = left + plot * tick / maximum
        output += [f'<path d="M{x:.2f},65 V{height-28}" stroke="#e2e8f0"/>',
                   f'<text x="{x:.2f}" y="62">{tick}m</text>']
    for number, (name, offset, parts) in enumerate(rows):
        y = 78 + step * number
        output.append(f'<text x="16" y="{y+14}">{escape(name)}</text>')
        x = left + plot * offset / maximum
        for key, value in parts:
            w = plot * value / maximum
            output.append(f'<rect x="{x:.3f}" y="{y}" width="{max(w,0):.3f}" height="20" fill="{COLORS.get(key, "#2563eb")}"><title>{escape(key)}: {value:.3f} min</title></rect>')
            x += w
        output.append(f'<text x="{x+5:.3f}" y="{y+14}">{sum(v for _, v in parts):.1f}m</text>')
    output.extend(["</g>", "</svg>"])
    rendered = "\n".join(output) + "\n"
    ET.fromstring(rendered)
    path.write_text(rendered, encoding="utf-8")


def main():
    summary = []
    details = ["# Completed CI job and step inventory", "",
               "Generated by `python analyze.py`; all durations are elapsed minutes, not CPU time.",
               "Zero-duration skipped steps are retained in JSON. API timestamps have one-second precision.",
               "Raw-log nested timings are not added to their containing Actions step.", ""]
    stages_doc = ["# Extracted bootstrap and opt-dist intervals", "",
                  "Log markers, not inferred pure compilation. Tiny bootstrap dry-run groups are retained.",
                  "Nested intervals must not be summed. Exclusive categories are in `summary.json`.", ""]
    diagram_rows, arm_rows = [], []
    for folder in sorted((ROOT / "data").iterdir()):
        if not folder.is_dir() or not (folder / "run.json").exists():
            continue
        run = json.loads((folder / "run.json").read_text())
        jobs = json.loads((folder / "jobs.json").read_text())
        active = [j for j in jobs if j["started_at"] and j["completed_at"]]
        end = max(j["completed_at"] for j in active)
        elapsed = duration(run["run_started_at"], end)
        last = max(active, key=lambda j: j["completed_at"])
        matrix = [j for j in active if j["name"].startswith(("auto -", "PR -"))]
        last_matrix = max(matrix, key=lambda j: j["completed_at"])
        row = {"run": run, "job_count": len(jobs), "makespan_seconds": elapsed,
               "runner_seconds": sum(j["elapsed_seconds"] or 0 for j in active),
               "last_job": last["name"], "last_matrix_job": last_matrix["name"],
               "jobs": []}
        details += [f"## [{run['id']}]({run['html_url']}) — {run['event']}", "",
                    f"Source `{run['head_sha']}`; start **{run['run_started_at']}**, last job end **{end}**.",
                    f"Conclusion **{run['conclusion']}**; {len(jobs)} jobs; makespan **{elapsed/60:.2f} min**; summed job elapsed **{row['runner_seconds']/60:.2f} runner-min**.", "",
                    "| Job | Runner label | Start UTC | End UTC | Minutes | Result |",
                    "|---|---|---|---|---:|---|"]
        for job in active:
            details.append(f"| [{job['name']}]({job['html_url']}) | {', '.join(job['labels'])} | {job['started_at']} | {job['completed_at']} | {job['elapsed_seconds']/60:.2f} | {job['conclusion']} |")
        details.append("")
        for job in active:
            parts = defaultdict(float)
            for step in job["steps"]:
                parts[step_category(step["name"])] += step["elapsed_seconds"] or 0
            remainder = job["elapsed_seconds"] - sum(parts.values())
            assert remainder >= -1, (job["id"], remainder)
            parts["Unaccounted"] = remainder
            record = {k: job[k] for k in ("id", "name", "labels", "elapsed_seconds")}
            record["actions_categories_seconds"] = dict(parts)
            record["slack_to_last_matrix_seconds"] = duration(job["completed_at"], last_matrix["completed_at"])
            evidence = folder / f"{job['id']}-log.json"
            if evidence.exists():
                raw = json.loads(evidence.read_text())
                main_step = next((s for s in job["steps"] if s["name"] == "run the build"), None)
                if raw.get("events") and main_step:
                    totals, observed, timers, facts = intervals(raw["events"], main_step["started_at"], main_step["completed_at"])
                    record["build_categories_seconds"] = totals
                    record["log_facts"] = facts
                    record["opt_dist_timers"] = timers
                    record["intervals"] = observed
                    stages_doc += [f"## [{job['name']}: {job['id']}]({job['html_url']})", "",
                                   f"Run {run['id']}; raw SHA256 `{raw['sha256']}`.", "",
                                   "| Category | Exclusive minutes |", "|---|---:|"]
                    stages_doc += [f"| {k} | {v/60:.3f} |" for k, v in totals.items()]
                    stages_doc += ["", "<details><summary>All observed bootstrap intervals</summary>", "",
                                   "| Start UTC | End UTC | Marker | Minutes | Log line |", "|---|---|---|---:|---:|"]
                    for i in observed:
                        stages_doc.append(f"| {i['start']} | {i['end']} | {i['name'].replace('|', '/')} | {i['seconds']/60:.3f} | {i['line']} |")
                    stages_doc += ["", "</details>", ""]
                    if timers:
                        stages_doc += ["| opt-dist timer (nested) | Minutes |", "|---|---:|"]
                        stages_doc += [f"| {t['name']} | {t['seconds']/60:.3f} |" for t in timers]
                        stages_doc.append("")
            row["jobs"].append(record)
            details += [f"<details><summary>{job['name']} — {job['elapsed_seconds']/60:.2f} min</summary>", "",
                        "| Actions step | Minutes | Conclusion |", "|---|---:|---|"]
            details += [f"| {s['name']} | {(s['elapsed_seconds'] or 0)/60:.3f} | {s['conclusion']} |"
                        for s in job["steps"] if (s["elapsed_seconds"] or 0) > 0]
            details += [f"| **Unaccounted runner/step gaps** | **{remainder/60:.3f}** | unknown |", "", "</details>", ""]
            if job["name"] == "auto - dist-aarch64-msvc":
                arm_rows.append((f"{run['id']} Arm64 dist", 0,
                                 [(k, v/60) for k, v in parts.items()]))
            if run["id"] == 33865610474 and job["name"] in {
                    "Calculate job matrix", "auto - dist-aarch64-msvc",
                    "auto - aarch64-msvc-1", "auto - aarch64-msvc-2",
                    "auto - dist-x86_64-msvc", "auto - i686-msvc-1",
                    "auto - x86_64-mingw-1", "auto - dist-aarch64-linux",
                    "auto - dist-x86_64-linux", "publish toolstate"}:
                diagram_rows.append((job["name"].replace("auto - ", ""),
                                     duration(run["run_started_at"], job["started_at"])/60,
                                     [("Main build", job["elapsed_seconds"]/60)]))
        summary.append(row)
    (ROOT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (ROOT / "ALL-JOBS-AND-STEPS.md").write_text("\n".join(details).rstrip() + "\n", encoding="utf-8")
    (ROOT / "BOOTSTRAP-INTERVALS.md").write_text("\n".join(stages_doc).rstrip() + "\n", encoding="utf-8")
    svg(diagram_rows, ROOT / "timeline.svg", "Completed merge CI: selected job timeline",
        "2026-09-04 run 33865610474 | actual starts; bars overlap; all 96 jobs in inventory")
    svg(arm_rows, ROOT / "arm64-steps.svg", "Arm64 distribution: completed Actions step costs",
        "Purple: source | grey: setup | blue: main build incl. docs/tools/package | teal: upload | pale: gaps")
    detailed = []
    for row in summary:
        for job in row["jobs"]:
            if job["name"] == "auto - dist-aarch64-msvc":
                detailed.append((str(row["run"]["id"]), 0, [(k, v/60) for k, v in job["build_categories_seconds"].items()]))
    svg(detailed, ROOT / "arm64-components.svg", "Arm64 main build: exclusive observed categories",
        "Orange: LLVM | blue: rustc | cyan: libraries | purple: tools | green: docs | dark orange: package | pale: unknown")
    print(f"Validated {sum(r['job_count'] for r in summary)} job totals and generated 3 SVGs")


if __name__ == "__main__":
    main()
