"""Read-only inventory of explicitly scoped earlier local compiler-build evidence."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
LOGS = Path(r"D:\copilot\arm-compiler-ab\logs")
X64 = Path(r"D:\copilot\arm-compiler-ab\x64-build-36946671654")
FILES = [
    (LOGS / "baseline-msvc-build.log", "5-second no-op/resumed compiler-only control; not a clean production baseline"),
    (LOGS / "baseline-lld-build.log", "9m10s incremental compiler-only control; prior LLVM state unknown; not a clean production baseline"),
    (LOGS / "optimized-pipeline-attempt-02.log", "initial instrumentation completed; frontend training failed; exclude total"),
    (LOGS / "optimized-pipeline.log", "resumed; static LLVM training invalid; exclude total"),
    (LOGS / "optimized-v2-instrument.log", "valid corrected instrumentation; resumed LLVM objects; component only"),
    (LOGS / "optimized-v2-training-1.log", "corrected LLVM training; component only"),
    (LOGS / "optimized-v2-final.log", "valid compiler-only final; pruned standalone LLVM tools; component only"),
    (X64 / "x64-compiler-pgo-control" / "logs" / "pgo-pipeline.log",
     "completed hosted x64 compiler-only PGO control; not Arm64/full distribution"),
    (X64 / "x64-compiler-optimized" / "logs" / "pgo-pipeline.log",
     "hosted x64 ThinLTO timed out; no completed optimized artifact; exclude total"),
]
records = []
for path, classification in FILES:
    raw = path.read_bytes()
    events = []
    for number, line in enumerate(raw.decode(errors="replace").splitlines(), 1):
        if ("opt_dist::timer" in line or re.match(r"^\s*(?:Build completed|finished in|Total duration:)", line)
                or ("test result:" in line and len(line) < 250)):
            events.append({"line": number, "text": line})
    records.append({"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
                    "bytes": len(raw), "classification": classification,
                    "events": events})
result = {
    "rust_sha": "e408947bfd200af42db322daf0fadfe7e26d3bd1",
    "llvm_sha": "00d23d10dc48c6bb9d57ba96d4a748d85d77d0c7",
    "rustc_perf_sha": "c0301bc44d175b9b2c5442b25049475c39d7700c",
    "local_arm_hardware": "Snapdragon X2 Elite, 12 cores/~64GB; builder jobs=8",
    "local_arm_configuration": "custom portable SDK; DIA off; final standalone utilities pruned",
    "local_arm_evidence_release": "https://github.com/marcpems/IronRDP-ci-benchmark/releases/tag/arm64-compiler-ab-v2",
    "x64_run": "https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36946671654",
    "x64_hardware": "windows-2025 standard, 4CPU/16GB; not upstream 8CPU/32GB dist",
    "qualification": "Local logs generally lack wall-clock boundaries except opt-dist timers; unknown intervals stay unknown",
    "files": records,
}
(ROOT / "data" / "local-evidence.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(f"Inventoried {len(records)} prior logs without modifying build trees")
