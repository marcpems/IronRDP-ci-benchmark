# Qualified x64 PGO comparison: IronRDP benefit and compiler CI cost

Completed 21 October 2026. This report answers the two requested endpoints using
fresh full-release compiler artifacts and a reverse-order production repetition.

## Executive result

| Question | Qualified observation |
|---|---|
| IronRDP wall time versus official shipping Rust 1.94.1 | **18.0% lower**, 95% paired interval **15.0-20.8%**; **922.50 to 756.28 seconds**, saving **2m46s** |
| IronRDP wall time versus our rebuilt upstream PGO recipe | **20.9% lower**, interval **18.1-23.4%**; **955.95 to 756.28 seconds**, saving **3m20s** |
| Full compiler-production wall time | **2.71% higher on average**, adding **3m36s**; observed pair increases **2.34% and 3.09%** |
| Whole successful compiler-release CI job | **4.00% higher on average**, adding **6m38s**; observed pair increases **2.51% and 5.55%** |

The downstream intervals come from five independent standard Windows VMs.
The production figures are descriptive results from **two fresh pairs / four
qualified full releases** on one dedicated runner, with order reversed in the
second pair. The observed CI range is **not a confidence interval** or a
guarantee for other runners.

Both compilers retain Rust `thin-local`; neither adds LLVM ThinLTO or Rust
cross-crate ThinLTO. The local recipe changes static-LLVM training relinking
**and** native linking tools. These are recipe/toolchain effects, not an isolated
estimate of better PGO profiles alone.

## 1. IronRDP compilation: actual official binary and matched rebuild

The [fresh-artifact replay](X64-PGO-FRESH-REPLAY.md) uses the first production
pair's actual compiler archives, with archive and provenance hashes fixed
before measurement. All three compilers share official Rust 1.94.1 Cargo and
byte-identical official native target libraries. IronRDP source is fixed at
`0c5419eca6bf53563056ed252f537bca67862705`.

Five independent `windows-2025` four-logical-processor VMs each completed one
excluded warmup and three measured rounds per compiler, with counterbalanced
order. The dataset includes 45 measured native blocks / 225 timed commands,
15 excluded warmup blocks and all 60 original correctness commands outside
timing. Fresh targets, offline Cargo, command identity and process-tree CPU
accounting were enforced. No slow-sample trimming was used.

Means are computed within VM, then equally across VMs. The primary 18.0%
reduction uses actual **official shipping Rust**, not the rebuilt upstream
control. The rebuilt upstream compiler was itself 3.6% slower than official
Rust (95% interval 2.6-5.7%); that distinction is why both contrasts are reported.
Intervals use 10,000 paired whole-VM bootstrap draws, seed 1012026, and are
conditional on fixed compiler/profile artifacts.

Workspace test compilation provided most absolute savings: **707.46 to
587.29 seconds**, a 17.0% reduction. Total descendant CPU time decreased
**18.6%** (interval 16.4-20.4%). The earlier compiler-only-artifact finding of
17.4% is consistent with this new result but is neither pooled with it nor
added to it.

## 2. Compiler-production and whole-job CI impact

Both pairs use Rust 1.94.1, the same LLVM/rustc-perf source revisions and
recorded native tool hashes, 16 logical processors (8 physical cores), and
isolated C: NVMe build roots on `MARCPE-TEST01-X64`. Every cell starts with
fresh compiler objects, Cargo home and PGO profiles. Configuration differs
only by the declared local intervention and run-specific paths.

| Pair and execution order | Upstream production | Local production | Increase | Upstream whole job | Local whole job | Increase |
|---|---:|---:|---:|---:|---:|---:|
| 1: upstream then local | 2h14m19s | 2h17m28s | **2.34%** | 2h49m44s | 2h54m00s | **2.51%** |
| 2: local then upstream | 2h11m26s | 2h15m30s | **3.09%** | 2h41m55s | 2h50m54s | **5.55%** |
| Equal-weight means | **2h12m53s** | **2h16m29s** | **2.71%** | **2h45m50s** | **2h52m27s** | **4.00%** |

Aggregate percentages are ratios of the per-variant means, not averages of
the two percentage changes. Displayed times are rounded; calculations use
full-precision seconds. Production increased in both orders, with a smaller
range than whole-job time. Four releases do not justify a precise population
confidence interval or a general claim about official Rust CI.

All four releases passed the unmodified upstream extracted-distribution tests,
final-profile-use checks and full-output qualification. Each produced the same
18-file distribution set, including complete bundles, MSI, docs, tools and
selected backends. Native-tool/source/configuration matching and raw profile
hashes were rechecked after download.

### Mean whole-job breakdown

| Non-overlapping component | Upstream seconds | Local seconds | Local minus upstream |
|---|---:|---:|---:|
| Full production, including fresh PGO and packaging | 7,972.68 | 8,188.94 | +216.26 |
| Extracted-distribution qualification | 401.69 | 383.58 | -18.11 |
| Evidence/profile uploads | 18.50 | 41.50 | +23.00 |
| Full distribution uploads | 769.50 | 880.50 | +111.00 |
| Generated-build cleanup | 129.00 | 129.50 | +0.50 |
| Setup and other job overhead, including inter-step gaps | 658.13 | 722.99 | +64.85 |
| **Whole job** | **9,949.50** | **10,347.00** | **+397.50** |

This explains why the whole-job increase is larger and more variable than
the production increase. The local-only reference-evidence download took
34 and 27 seconds and is included in those whole-job figures. This is experiment
CI bookkeeping, not an intrinsic compiler-production requirement.

Whole-job time uses GitHub's individual release-job start/completion timestamps.
It excludes queue wait, the shared parent preflight and separate failed
preparation attempts. Each release job includes its own readiness inspection.
Production includes helper construction, training, compilation and packaging,
and contains dependency downloads: unlike the IronRDP endpoint, it is
**not offline raw compile time**.

### Mean production phases

| Non-overlapping phase | Upstream seconds | Local seconds | Local minus upstream |
|---|---:|---:|---:|
| Rustc PGO stage | 3,068.35 | 3,049.70 | -18.65 |
| LLVM PGO stage | 1,473.54 | 1,677.02 | +203.48 |
| Final full-distribution build | 3,241.42 | 3,261.28 | +19.87 |
| Helper and remaining production overhead | 189.38 | 200.94 | +11.57 |
| **Total production** | **7,972.68** | **8,188.94** | **+216.26** |

The additional elapsed production time is concentrated in the LLVM training
stage. These are inclusive stage wall times partitioned without double counting,
not a claim of exclusive LLVM CPU attribution.

## 3. The observed profile gap

Both independent upstream-recipe rebuilds and both local rebuilds reproduced
the same function-coverage pattern:

| Checked LLVM area | Upstream functions / active | Local functions / active |
|---|---:|---:|
| `X86TargetLowering` | 0 / 0 | 255 / 167 |
| `InstCombine` | 6 / 0 | 873 / 597 |

The upstream profiles were nonempty but did not show executed counters in
these two backend areas. The local static-LLVM training relink produced
substantial coverage in both, consistent with addressing the training-path
gap in this reproduced x64 recipe.

This does **not** establish the content or effectiveness of profiles used for
official shipping Rust. Its binary is measured directly as a separate baseline.
Profile coverage is evidence of execution, not by itself a performance estimate;
the fresh IronRDP replay supplies that estimate.

## 4. Resource checks and limits

All four runs retained valid CPU, memory and disk telemetry. Median NVMe read
latency was approximately 0.125 ms; sampled 95th-percentile latency was below
0.55 ms. Median disk queues were zero. Minimum available memory was at least
8,095 MiB and minimum observed C: free space at least 134.41 GiB. The 180-GiB
admission requirement applies before each build, not throughout it.

These samples do not show sustained NVMe queueing or exhausted memory, but
cannot exclude every transient disturbance. The study does not attribute the
large improvement over earlier HDD experiments solely to storage: recipes,
source/training revisions and other conditions also differ.

The comparison is deliberately limited to these recipes and machines.
Official Rust's release infrastructure uses different allocation/cache
conditions. The second pair repeats production with fresh profiles; only the
first pair's preregistered compiler artifacts enter the hosted IronRDP replay.
Do not infer a general CI break-even count by dividing hosted build savings
by dedicated-runner compiler-production costs.

## Evidence and reproducibility

- [Final structured comparison](X64-PGO-COMPARISON.json), including exact means,
  observed ranges, non-overlapping breakdowns and source evidence hashes.
- [Fresh IronRDP report](X64-PGO-FRESH-REPLAY.md),
  [estimates](X64-PGO-FRESH-REPLAY.json) and
  [permanent compact raw replay evidence](x64-pgo-fresh-replay-evidence.zip).
  Reanalysis from this archive reproduces all estimates and intervals exactly.
- [First release pair](X64-PGO-RELEASE-PILOT.json) and
  [reverse-order pair](X64-PGO-RELEASE-REVERSE.json).
- [Permanent compact release evidence](x64-pgo-release-compact-evidence.zip):
  both job API records, all four result/provenance records, timer sections,
  manifests, profile-coverage dumps, native settings and full telemetry.
  Large compiler distributions, binary profiles and full build logs remain in
  the Actions artifacts with 30-day retention; they are not in this compact ZIP.
- [First release run 39456859889](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39456859889),
  [reverse run 39506380543](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39506380543),
  [five-VM replay 39506872211](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39506872211).
- [Production protocol](x64-pgo-release-protocol.json),
  [replay protocol](x64-pgo-replay-protocol.json) and
  [replay analyzer](analyze_x64_pgo_replay.py).
