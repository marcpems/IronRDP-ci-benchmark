# Source acquisition: bounded completed experiment

[Run 36992548740](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36992548740)
at harness commit `d5ce01b29feac6a6e04d85447cac0984b2ff32a1`.
Two standard 4CPU Windows Arm64 VMs, image `20260924.168.1`, 2026-10-02.

Whole experiment: **10.63 min**; summed job elapsed: **21.05 runner-min**.

**Result: no useful archive-only speedup; do not adopt this candidate.**

| Order | Shallow Git acquire (s) | Archive acquire (s) | Archive minus Git (s) |
|---|---:|---:|---:|
| git-first | 250.82 | 257.87 | +7.05 |
| archive-first | 260.42 | 259.96 | -0.46 |

Mean archive-minus-Git: **+3.30 seconds**.
Two VMs are not enough for a precise effect interval. Opposite order mitigates,
but does not eliminate, uncontrolled OS/CDN caches and within-VM I/O effects.

| Order | Git fetch | Git checkout | Archive download | Archive extraction |
|---|---:|---:|---:|---:|
| git-first | 37.66s | 212.92s | 45.91s | 209.34s |
| archive-first | 51.72s | 206.42s | 48.29s | 208.21s |

Both methods are dominated by creating **180,584 files (~2.25 GB)**, not just
network transfer. The downloaded archive is **277,646,076 bytes (~264.8 MiB)**;
retaining archive + one extracted tree needs at least ~2.52 GB before metadata.
The probe stores both trees plus Git objects, so its own disk use is higher.
Acquisition includes archive SHA256 calculation and small setup; the additional
39.6–50.6-second per-tree verification passes are **outside** acquisition time.
This isolates LLVM only; it is not a replay of all concurrent Rust submodules.

## Qualification failed: interpret the failure correctly

Both workflow jobs deliberately exited nonzero on the strict content guard,
after successfully finishing both acquisitions and preserving all result JSON.
The Git control has **521** literal Git-blob differences; the archive has **16**.
Both paths have zero extra files. Each method's digest and difference counts
repeat identically across the two VMs.

**This is not proof of corrupt downloads.** The initial oracle compared working
file bytes against canonical Git object IDs, which is too strict for Windows
checkout/archive transformations. Pinned `llvm/.gitattributes` explicitly
requires CRLF for several named failing fixtures; root `.gitattributes` marks
`clang/bindings/python/.git_archival.txt` as `export-subst`; the remaining
differences include symlink fixtures and third-party text. The exact reason
for every mismatch was not established after the VMs terminated.

Therefore **no normalized equivalence, executable-mode, source metadata or
full Rust bootstrap qualification is claimed**. A follow-up would compare
attribute-filtered checkout content, export-substitution policy and normalized
symlink semantics, not ignore arbitrary mismatches. Given no timing benefit,
further hosted runs were not warranted for this candidate.

The negative performance conclusion concerns **observed acquisition cost**;
failed qualification is a separate reason not to recommend a production patch.
Keep the existing shallow parallel Git path. A content-addressed pre-staged
source tree or fewer filesystem writes is a different, unmeasured proposal.

## Identity and reproduction

* Rust sample: `0ed41eb4142dda2df61eb1145a312c1a9d62eb56`.
* LLVM: `76a3a9d0075fe0df4bb57160372700006e3d0b2b`.
* Archive SHA256: `52431f3ff4c447f5201e072923df9b3c3d69514491f5a54f005fe85aafde2205`.
* Git 2.55.0.windows.5; Windows curl 8.21.0; bsdtar 3.8.8.
* [source_probe.py](source_probe.py) uses no compiler, SDK mutation or secrets.
* [Runner outputs, Actions steps and command-log hashes](data/source-probe-36992548740).

Run the dedicated workflow manually to reproduce acquisition (the strict guard
is expected to reject this pinned source; it is not an upstream-ready validator).
`python summarize_probe.py` regenerates this document and machine-readable
summary offline from saved runner JSON. Source and Git attributes are separately
pinned in `data/sources.json`.

No existing workflows were cancelled/rerun, no release assets overwritten,
and no full compiler build duplicated. The bounded experiment is complete.
