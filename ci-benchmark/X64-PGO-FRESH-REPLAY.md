# Fresh x64 PGO compilers: qualified IronRDP performance

## Answer

The freshly produced local-PGO compiler reduced offline native IronRDP
compilation wall time by **18.0% versus official shipping Rust 1.94.1**
(95% paired interval **15.0-20.8%**): **922.50 to 756.28 seconds**.
The saving is **166.23 seconds**, about **2m46s**, per five-command native build.

Against the matched, locally rebuilt upstream recipe, the reduction was
**20.9%** (95% interval **18.1-23.4%**): **955.95 to 756.28 seconds**,
saving **199.68 seconds**.

| Compiler | Mean native wall time | Meaning |
|---|---:|---|
| Official Rust 1.94.1 | 922.50s | Actual downloadable shipping distribution, including its upstream optimizations |
| Rebuilt upstream PGO recipe | 955.95s | Full-release control built on the dedicated NVMe runner |
| Fresh local PGO recipe | 756.28s | Static-LLVM training relink plus LLVM native linking tools; no added ThinLTO |

The rebuilt upstream compiler was **3.6% slower than official shipping Rust**
(95% interval **2.6-5.7% slower**). The two baselines are not interchangeable.
These results establish a toolchain-replacement benefit, not a causal estimate
of profile quality alone: native compiler-build linking tools and official
production-environment differences remain.

## Measurement and qualification

[Run 39506872211](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39506872211),
attempt 1, harness `d9cbd240d4ff99dd4db7930bba4f6e70d03ce327`,
completed on 21 October 2026. All five independent standard `windows-2025`
four-logical-processor VMs completed the full matrix and correctness checks.

The [preregistered protocol](x64-pgo-replay-protocol.json) pins the new compiler
archive and release-provenance hashes from full-release run `39456859889`.
This is a replay of those actual qualified artifacts, not the earlier
compiler-only experiment. All three variants used identical official
Rust 1.94.1 Cargo and byte-identical official native standard libraries.
IronRDP remained at `0c5419eca6bf53563056ed252f537bca67862705`.

Each VM ran one excluded warmup and three measured rounds for each of three
compilers. Compiler order used the established rotation by VM and round,
reversing alternate rounds. Every block started with a fresh native target;
the five original native Cargo commands then shared that target. Dependency
fetching was outside timing; commands used `--frozen`, offline Cargo,
four workers, debug information disabled and incremental compilation disabled.
No optimization-level or codegen-unit overrides were added.

The accepted dataset contains **45 measured blocks / 225 measured commands**,
plus **15 excluded warmup blocks / 75 warmup commands**. All **60 original
native correctness commands** passed outside the compilation clock. No failed
VMs, selective rounds or slow-sample exclusions enter the estimate.

Analysis revalidated the complete ordered matrix, compiler/provenance hashes,
common inputs, source and compiler identities, command sequences, cold targets,
four-CPU affinity, descendant CPU accounting, allowed helper processes,
correctness commands and one consistent workflow attempt.

Three measured totals were averaged within each VM, then VM means received
equal weight. Reduction is the ratio of those aggregate means, not the mean
of per-VM percentages. The 95% intervals use 10,000 paired whole-VM bootstrap
draws with seed 1012026. They are pointwise intervals, conditional on these
fixed compiler/profile artifacts; they do not quantify PGO retraining variance.

## Per-command wall time versus official Rust

| Native command | Official seconds | Local seconds | Reduction |
|---|---:|---:|---:|
| xtask bootstrap | 4.60 | 4.17 | 9.3% |
| Workspace test compilation | 707.46 | 587.29 | 17.0% |
| Native-TLS test compilation | 19.60 | 14.53 | 25.9% |
| Gateway native-TLS test compilation | 93.93 | 75.85 | 19.2% |
| Gateway native-TLS plus smartcard test compilation | 96.91 | 74.44 | 23.2% |
| **Total** | **922.50** | **756.28** | **18.0%** |

The small xtask-bootstrap wall-time effect is uncertain: its interval spans
-4.5% to +17.2%. Workspace test compilation supplies most absolute savings:
120.17 seconds, with a 14.1-19.5% reduction interval.
Total process-tree CPU time fell from **3,407.85 to 2,773.21 seconds**,
an **18.6%** reduction (95% interval **16.4-20.4%**).

## Paired VM means

| VM | Official seconds | Rebuilt upstream seconds | Local seconds |
|---|---:|---:|---:|
| 1 | 674.43 | 731.77 | 582.00 |
| 2 | 1,131.70 | 1,162.75 | 928.10 |
| 3 | 838.04 | 858.06 | 675.77 |
| 4 | 830.62 | 853.78 | 715.08 |
| 5 | 1,137.74 | 1,173.41 | 880.43 |

Absolute times vary substantially across hosted VMs; the paired comparison
preserves the same-machine controls rather than pooling individual commands
as independent observations.

## Relationship to compiler-production CI cost

These are the same first-pair full-release artifacts for which production cost
was **+2.34%** and whole successful CI-job cost was **+2.51%**, or **4m16s extra**.
See the [release report](X64-PGO-RELEASE-PILOT.md).
The completed [two-pair CI comparison](X64-PGO-COMPARISON.md) reports a
**2.71% mean production increase** and **4.00% mean whole-job increase**,
with observed whole-job increases of 2.51% and 5.55%.
The reverse-order fresh-production repetition is analyzed separately;
its newly trained compilers are not substituted into this fixed-artifact replay.

Do not divide the hosted IronRDP saving by the dedicated-runner release cost
to claim a general break-even count: the machines, allocations and endpoints
differ. Do not add the earlier 17.4% result to this 18.0% result; this is an
independent new-artifact confirmation, not an additional optimization.

The profile evidence supports a training gap in our reproduced upstream recipe,
but this benchmark does not reveal the official shipping compiler's original
profile contents. It directly measures the official binary as a separate baseline.

## Persistent evidence and reproduction

- [Structured estimates, VM means and evidence hashes](X64-PGO-FRESH-REPLAY.json).
- [Compact raw evidence archive](x64-pgo-fresh-replay-evidence.zip): all five
  indexes, every warmup/measured block result and meter-validation evidence
  (100 files). This copy persists in Git independently of Actions retention.
- [Analysis implementation](analyze_x64_pgo_replay.py) and
  [regression tests](test_analyze_x64_pgo_replay.py).
- The run's `x64-pgo-fresh-replay-1` through `-5` artifacts additionally retain
  full command logs and Cargo timing HTML for 30 days.

From the repository root, extract the compact archive into a new directory
and reproduce the estimates:

```powershell
Expand-Archive ci-benchmark\x64-pgo-fresh-replay-evidence.zip <new-evidence-directory>
python ci-benchmark\analyze_x64_pgo_replay.py <new-evidence-directory> --output <results.json>
```
