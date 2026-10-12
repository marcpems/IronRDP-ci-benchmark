"""Aggregate exclusive bootstrap timings without double-counting nested steps."""

import argparse
from collections import defaultdict
import json
from pathlib import Path

from build_arm_compilers import save


def summarize(metrics):
    rows = []
    for invocation in metrics["invocations"]:
        totals = defaultdict(float)

        def visit(node):
            name = node.get("type", "")
            category = "other"
            for marker, label in (
                ("::llvm::", "llvm_and_lld"),
                ("::compile::", "compiler_std_backends"),
                ("::tool::", "tools"),
                ("::dist::", "assembly_and_compression"),
                ("::doc::", "documentation"),
                ("::test::", "tests"),
            ):
                if marker in name:
                    category = label
                    break
            seconds = node.get("duration_excluding_children_sec", 0)
            if seconds < 0:
                raise ValueError("negative bootstrap exclusive duration")
            totals[category] += seconds
            for child in node.get("children", []):
                visit(child)

        for node in invocation["children"]:
            visit(node)
        wall = invocation["duration_including_children_sec"]
        accounted = sum(totals.values())
        if accounted > wall + max(1, wall * 0.01):
            raise ValueError("exclusive durations exceed invocation wall time")
        rows.append({
            "command": invocation["cmdline"], "wall_seconds": wall,
            "exclusive_seconds": dict(totals), "unattributed_seconds": wall - accounted,
        })
    return {
        "system": metrics["system_stats"], "invocations": rows,
        "note": "exclusive bootstrap scopes; compile scopes include linking and waits, not raw compiler CPU",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metrics", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    save(args.output, summarize(json.loads(args.metrics.read_text())))
