# Windows Rust compiler performance: investigation summary

Updated 22 October 2026. This is the end-to-end summary of the problem,
investigation stages, measured results and remaining limitations. Detailed
reports and reproducible evidence are linked throughout. All experiments were
conducted in forks; no upstream rollout is claimed. The broad campaign stopped
at the user's request on 19 October. Only the requested x64 upstream/local-PGO
comparison resumed on 20 October, followed by the requested profile-only test
on 21 October and Rust 1.99.1 revalidation on 22 October; Arm64 and GB300 work
remain stopped.

Presentation and document versions:
[technical PowerPoint with linked report index](matched-release/Rust-Optimization-Summary-Published.pptx)
and [combined Word report](matched-release/Rust-Optimization-Combined-Report-Revised.docx).
This Markdown summary remains the full end-to-end account; the Word report is
an earlier consolidation.

## TL;DR

- **The reported Windows compilation penalty was reproduced with IronRDP:**
  Windows/Linux native-compilation wall-time ratios were **1.82x on x64**
  and **1.69x on Arm64** on standard GitHub runners. Mac was not benchmarked.
- **The primary workload bottleneck was compiler execution.** On the graphics
  isolation workload, rustc accounted for **99.3-99.6% of Windows' extra CPU
  time**. This is not proof of an LLVM-specific defect.
- **Optimized compilers improved the original offline IronRDP workload versus
  shipping Rust 1.94.1:** **23.7% less wall time on x64** and **16.0% on Arm64**.
  These compilers used rustc/LLVM PGO, Rust/LLVM ThinLTO and LLVM linking tools.
  A matched x64 comparison with identical profiles isolated a **7.6% wall-time
  reduction from adding both ThinLTO modes**.
- **Earlier direct x64 upstream-PGO versus local-PGO comparison, without added ThinLTO:**
  reanalysis of the accepted paired trials gives **957.41 to 791.12 seconds**,
  or **17.4% less IronRDP native compilation wall time (95% interval 15.2-19.1%)**.
  This is a toolchain-replacement result, not proof of better PGO profiles alone:
  compiler-build/linker differences remain.
- **Fresh full-release x64 artifacts confirmed the IronRDP benefit:** five
  independent standard Windows VMs measured **922.50 to 756.28 seconds** versus
  official shipping Rust, **18.0% less wall time (95% interval 15.0-20.8%)**.
  Compared with the separately rebuilt upstream recipe, local PGO saved **20.9%
  (18.1-23.4%)**. Same official Cargo/std and no added ThinLTO were used.
  See the [fresh-artifact report and persistent raw evidence](X64-PGO-FRESH-REPLAY.md).
- **Two matched x64 full-release PGO pairs qualified, in opposite order:**
  local production cost **2.71% more on average (3m36s)**; whole release CI
  jobs cost **4.00% more (6m38s)**. Observed per-pair increases were
  **2.34-3.09% production** and **2.51-5.55% whole job**; these ranges are
  not confidence intervals. Both upstream-recipe rebuilds lacked active LLVM
  counters in two checked backend areas; both local builds had coverage.
  A subsequent direct audit confirmed the same coverage gap in the official
  published LLVM profile. Fresh downstream replay and reverse-order production
  qualification are complete.
  See the [final x64 comparison and persistent evidence](X64-PGO-COMPARISON.md).
- **The LLVM-profile-only effect was isolated on Rust 1.94.1:** two otherwise matched
  rebuilds retained Microsoft link/lib and the official Rust-side profile.
  Switching official to repaired LLVM profile saved **13.73% IronRDP wall time
  (711.049 to 613.436 seconds)** and **14.02% CPU**, with no added ThinLTO.
  All three measured rounds improved (12.97-14.76%; one machine/build pair,
  **not** a confidence interval). This is not an untouched shipping-binary
  comparison or a whole-CI percentage.
  See the [qualified profile-only report and compact evidence](X64-PROFILE-ONLY.md).
- **Rust 1.99.1 revalidation is complete:** the official LLVM profile still
  lacks both queried backend groups. Fresh repaired training restores active
  coverage, and otherwise matched rebuilds retain Microsoft link/lib, official
  Rust-side profiles and no added ThinLTO. Offline IronRDP wall time falls
  **631.608 to 549.949 seconds: 12.93% / 81.659 seconds saved**, with **13.66%
  less CPU**. Both distributions qualify; all three paired rounds improve
  (11.34-13.79%, descriptive range on one host, not a confidence interval).
  Fixed-profile production is 2.72% shorter in one ordered pair, but this
  excludes training and does **not** measure the PR's incremental release cost.
  See the [1.99.1 audit, completed comparison and reproducible evidence](X64-PGO-1991.md).
- **Keeping Microsoft linking tools captures much of the benefit.** Nine
  qualified full-release pilots measured **21.5-24.6% less IronRDP compilation
  time with PGO alone**, versus controlled no-PGO builds. Their LLVM/PGO/ThinLTO
  recipe saved **22.0-28.7%**. These percentages have a different denominator
  from the shipping-Rust results; they are not additional gains to add to them.
- **Producing the compiler can be expensive.** Training, profile processing,
  packaging and storage matter alongside compilation. GB300 assembly/compression
  remained **102-103 minutes**; x64 HDD/profile effects confounded CPU scaling.
  Arm64's observed 4/8/16-processor production times were **507.8/137.1/112.0
  minutes**, but single observations do not establish a scaling law.
- **Not every plausible optimization helped.** Controlled LLVM/LLD scheduling
  changes showed no repeatable useful gain. The final public x64 fresh-training
  reference and GB300 lower-core scaling study remained incomplete.

## 1. Problem statement and measurement scope

The investigation responded to the Windows Rust build-time gap reported by
**Marc-Andre Moreau**, using **IronRDP** as the real-project benchmark. It
continues the investigation presented in **"Windows Rust compiler performance,"
2 October 2026**; the retained [Word report](Windows-Rust-Performance-Summary.docx)
was subsequently updated on 7 October.

The question was whether Windows really took roughly twice as long as Linux
for offline Cargo compilation, where the excess time went, and which compiler
or release-pipeline changes could reduce it without sacrificing correctness.
The broader Windows/Linux/Mac concern motivated the work, but the measured OS
comparison covers **Windows and Linux only**.

The native workload contains five commands: xtask bootstrap, workspace test
compilation, native-TLS test compilation, gateway native-TLS test compilation,
and the gateway native-TLS plus smartcard variant. Dependencies are fetched
before timing; measured commands use `--frozen` and an offline Cargo environment.
Correctness tests execute outside the compilation clock.

| Quantity | What its time includes |
|---|---|
| IronRDP compilation | Five Cargo command wall times; excludes setup, dependency downloads, test execution, verification and uploads |
| Full Rust production | Helper construction, fresh PGO training/merging and complete distribution production; excludes initial setup, post-build qualification and uploads |
| Whole release job | Successful job start-to-finish, including setup, qualification, uploads and applicable cleanup; excludes queues and separate failed/recovery jobs |
| Component wall scope | Non-overlapping recorded steps, including links, waits and I/O; **not** raw compile CPU time |

Full Rust production logs contain dependency downloads: unlike the IronRDP
replay, **full production is not an offline compile-only measurement**.
LP means **Logical Processors**, not necessarily physical cores.

## 2. Reproduce the gap, then isolate compiler execution

Three independent standard GitHub jobs per OS/architecture reproduced the gap:

| Architecture | Linux native total, seconds | Windows native total, seconds | Windows/Linux |
|---|---:|---:|---:|
| x64 | 555.030 | 1,008.888 | 1.818x |
| Arm64 | 424.245 | 714.955 | 1.685x |

These are medians of per-job totals, not sums of command medians. Workspace-test
compilation explained approximately **75-79% of the excess native time**;
gateway feature variants accounted for another **18-21%**. Windows compiled
fewer workspace units, so simply counting more crates did not explain the gap.

The next stage measured `ironrdp-graphics` builds and direct `yuv` rustc
invocations with one/four-processor affinity, native/shared-WASM targets,
metadata-only/full code generation, and process-tree/compiler-own CPU accounting.
Rustc consumed **97.7-99.1% of project CPU**, explaining **99.3-99.6% of Windows'
additional CPU**. The gap persisted without Cargo or an external linker.
One-to-four-processor scaling was similar across OSes; it was not primarily a
Windows parallel-scaling failure.

This points toward compiler/code-generation execution cost, not an exclusive
LLVM phase attribution. Standard OS runners were not hardware-identical.

Evidence: [original measurement and native breakdown](REPORT.md),
[compiler isolation](COMPILER-RESULTS.md), runs
[36764734498](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36764734498)
and [36771187101](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36771187101).

## 3. Audit release optimizations and validate effective training

For the measured **Rust 1.94.1** release, Windows x64 configured both rustc and
LLVM PGO; Windows Arm64 configured neither. Neither Windows architecture enabled
both cross-crate Rust ThinLTO and LLVM ThinLTO as the Linux releases did.
Native compilation used clang-cl; Microsoft's `link.exe`/`lib.exe` and LLVM's
`lld-link`/`llvm-lib` are distinct linker/librarian choices.

Our first static-LLVM training attempt produced initialization counters but no
meaningful Arm64 backend code-generation coverage. The training compiler had
not been relinked against instrumented LLVM. Explicit relinking produced
nonzero `AArch64TargetLowering` and `InstCombine` counters; the invalid initial
artifact and measurements were excluded.

**This established a real training-path defect, not that all upstream PGO was
ineffective.** At that stage official shipped x64 profiles had not been inspected.
The later [official-profile audit and isolated replay](X64-PROFILE-ONLY.md)
confirmed missing coverage in the official LLVM profile and measured a 13.73%
benefit from replacing the profile file. Separate rustc PGO was not shown ineffective.
The [1.99.1 revalidation](X64-PGO-1991.md) confirms the same official-profile
coverage gap and a 12.93% benefit from replacing only that release's LLVM profile.

Native-tool compatibility probes also established that LLVM ThinLTO bitcode
cannot be handed to Microsoft `link.exe`, including with `/LTCG`. Rust-side
ThinLTO can retain Microsoft linking because rustc emits native objects before
that link. PGO itself does not require replacing the linker.

Evidence: [release audit and training repair](COMBINED-REPORT.md),
[matched x64 design](WINDOWS-X64-OPTIMIZATION.md),
[Microsoft-tool investigation](msvc-linker/README.md).

## 4. Measure optimized compilers on the original IronRDP workload

Five independent VMs per OS, one excluded warmup and three measured rounds
compared shipping Rust with optimized compilers. Windows compiler ordering was
counterbalanced; confidence intervals resample whole VMs and preserve pairing.
Original correctness commands passed outside timing.

| Windows architecture | Shipping Rust, seconds | Optimized, seconds | Wall-time reduction | 95% interval |
|---|---:|---:|---:|---:|
| x64 | 957.41 | 730.64 | 23.7% | 21.7-25.3% |
| Arm64 | 709.64 | 595.99 | 16.0% | 15.4-16.7% |

**Optimized means rustc + LLVM PGO, Rust + LLVM ThinLTO, and LLVM
`lld-link`/`llvm-lib`; native C/C++ compilation remains clang-cl.**
CPU reductions were 24.6% and 16.0%, respectively. These are practical
replacement effects, not PGO-only effects or application-runtime improvements.

The x64 matched LLVM-linked PGO control took **791.12 seconds**. Adding both
ThinLTO modes with byte-identical PGO profiles reduced it to **730.64 seconds**:
**7.6% less wall time** (95% interval 7.1-8.0%) and **7.3% less CPU time**.
This isolates their combined addition, not Rust ThinLTO versus LLVM ThinLTO
individually. The controlled Arm64 graphics experiment likewise found a combined
PGO/ThinLTO benefit, but its 18.8% wall saving is not the full-native-workload result.

Evidence: [x64 native results](X64-NATIVE-RESULTS.md),
[Arm64 native results](NATIVE-AB-RESULTS.md), [Arm64 controls](ARM64-AB-RESULTS.md).
Principal native runs:
[37001433534](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/37001433534)
and [36871453828](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36871453828).

## 5. Qualify full releases and measure their production cost

A [completed-log CI audit](https://github.com/marcpems/IronRDP-ci-benchmark/blob/96e8f5d65ffd6d50955c9480b3ae8bdcfe3251ff/ci-benchmark/build-time/README.md)
covered 313 upstream CI jobs. Stock Arm64 distribution jobs took **117-127
minutes**, but their C/C++ cache-hit rate was 100%: those were not cold-build
baselines. Tools and packaging accounted for 49-54 minutes. Arm64 distribution
was not the sampled merge workflows' critical path; i686 MSVC or macOS test jobs
finished last. Making Arm64 distribution faster would deliver its artifacts
earlier, not necessarily shorten the whole merge workflow.

Release promotion reuses built artifacts for signing, recompression and
publication; it is not another rustc rebuild. Larger-runner budgets and pipeline
splitting were explored as planning scenarios, not measured optimized releases.

The investigation then progressed from compiler packages to **complete Rust
distributions** on three self-hosted machines. All nine selected releases and
three accepted paired IronRDP replays qualified, retaining tools, documentation,
MSI, x64 Cranelift and Arm64 Arm64EC coverage.

| Full-release recipe | PGO | Linker / librarian | LLVM / Rust cross-crate LTO |
|---|---|---|---|
| No-PGO control | Off | Microsoft link.exe / lib.exe | Off / off |
| Microsoft-linked PGO | Fresh profiles | Same Microsoft tools | Off / off |
| LLVM + PGO + ThinLTO | Fresh profiles | LLVM lld-link / llvm-lib | Thin / thin |

All use clang-cl. The source included common experimental profiling/runtime,
DLL-import and MIR stack-scope repairs. The baseline is the same-revision
**no-PGO compiler, not shipping x64 Rust**. Each machine has **one accepted
non-warmup paired pilot round**, not the originally planned repeated hosted study.

| Machine / allocation | No-PGO production, min | MS PGO production, min (+% vs no PGO) | LLVM recipe production, min (+%) | IronRDP saving: MS / LLVM |
|---|---:|---:|---:|---:|
| x64 / 4 LP | 134.1 | 548.1 (+308.7%) | 787.3 (+487.0%) | 24.6% / 28.7% |
| Arm64 / 4 LP | 180.1 | 431.9 (+139.8%) | 656.4 (+264.5%) | 24.4% / 27.9% |
| GB300 Arm64 / 64 LP | 138.5 | 182.6 (+31.8%) | 203.3 (+46.8%) | 21.5% / 22.0% |

The LLVM recipe's extra downstream saving versus Microsoft PGO was **5.36% x64,
4.54% ordinary Arm64 and 0.65% GB300**, at additional production costs of
**239.16, 224.50 and 20.70 minutes**, respectively. Here linker, both LTO settings
and fresh profiles change together; this is not the matched-profile ThinLTO
contrast from the previous stage.

Production decomposition exposed substantial non-compilation work. On GB300:

| Exclusive production scope, minutes | No PGO | MS PGO | LLVM recipe |
|---|---:|---:|---:|
| Assembly/compression | 102.21 | 102.91 | 103.38 |
| Compiler/std/backends | 7.79 | 13.14 | 17.09 |
| LLVM/LLD | 4.23 | 14.56 | 21.88 |
| Tools | 13.00 | 18.28 | 21.59 |
| Documentation | 7.76 | 7.48 | 10.51 |
| Other/bootstrap unattributed | 2.40 | 2.07 | 2.13 |
| Outside bootstrap: training, profiles, orchestration | 1.09 | 24.16 | 26.71 |

Unrounded scopes reconcile to production. The 102-103-minute packaging component
does not disappear when compilation is optimized.

Evidence: [full-release history and qualification](matched-release/README.md),
[all nine exact pilot measurements](matched-release/selfhost-pilot-results.json),
[GB300 cost decomposition](matched-release/gb300-release-costs.json).
Accepted replays: x64 **38636440191**, Arm64 **38695519744**, GB300 **38441909371**.
The earlier GB300 UDP correctness timeout remains unexplained; a fresh accepted
replay does not erase it.

## 6. Investigate capacity, storage and CPU scaling

A further recipe retained Microsoft tools and fresh PGO, enabled **Rust
ThinLTO**, and left native LLVM ThinLTO off. Six releases qualified:

| Machine | Logical Processors | Production minutes | Time saved vs same-machine 4 LP |
|---|---:|---:|---:|
| Arm64 | 4 | 507.79 | Baseline |
| Arm64 | 8 | 137.13 | 73.00% |
| Arm64 | 16 | 112.03 | 77.94% |
| x64 | 4 | 726.81 | Baseline |
| x64, original | 16 | 610.70 | 15.97% |
| x64, repeat | 16 | 916.98 | -26.17% |

Arm64 was **MARCPE-D4-Arm64**; x64 was **MARCPE-TEST01-X64**.
These are fixed-order, single observations, not a validated scaling curve.
Arm64's superlinear 4-to-16 ratio requires explanation and repetition; its
self-hosted timings are not guarantees for GitHub larger runners.
**No IronRDP replay measured the downstream benefit of this scaling recipe.**

The x64 repeat was **50.15% slower than its original 16-LP run**. Investigation
found an HDD/ReFS release volume versus an NVMe/NTFS system volume. A CPU-only
probe scaled **2.6-3.2x** from 4 to 16 LP, whereas historical opt-dist trees averaged
only **1.12-1.78 occupied LP**. Four LP selected two physical cores with SMT.
Synchronous small-file writes were much slower on the HDD; profile datasets
exceeded RAM. Profile merging alone explained only about six minutes of the
five-hour repeat slowdown.

These are strong storage/profile-processing leads, not proof that HDD latency
explains the entire difference or that ReFS alone is responsible.

Evidence and run identities: [scaling and diagnostics](matched-release/README.md).
Arm64 4/8/16 runs: **38756702383 / 38873093226 / 38728610658**.
X64 4/original-16/repeat-16 runs: **38869758791 / 38716997224 / 38980060732**.

## 7. Test production-throughput ideas, including negative results

The supporting throughput work distinguished component opportunities from
demonstrated full-release improvements:

| Experiment | Measured result | Interpretation |
|---|---|---|
| Local Arm64 LLVM subset, 4 to 12 LP | 207.54 to 81.11 seconds: 60.9% less wall time | 845 fresh objects per trial; not a full LLVM/Rust release |
| Local existing fast XZ profile | 56.13 to 13.71 seconds: 75.6% less packaging time; 21.6% larger archive | Identical decompressed payload; full-release/transfer tradeoff not qualified |
| Same-VM hosted LLVM/LLD: six jobs on four LP | Median paired time change **+0.35%** | No repeatable useful gain; peak memory increased 45.45% |
| Same-VM hosted LLVM/LLD: one concurrent link | Median paired time change **-0.19%** | No repeatable useful gain |

The hosted crossover used three VMs, counterbalanced setting positions,
identical PGO profiles and fresh object/cache trees. Neither scheduling change
met the preregistered advancement rule. **Retain upstream scheduling defaults
on the evidence collected.** Earlier unmatched-VM apparent gains were confounded;
the unchanged x64 final-build baseline varied by 35.75%.

The upstream-equivalent study also qualified three Arm64 full-recipe pilots
and six x64 **final-build continuations**. Those continuations did not measure
an end-to-end fresh-training release and must not substitute for one.

Evidence: [local component probes](release-throughput/README.md),
[upstream-equivalent scheduling study](upstream-release-throughput/README.md),
[controlled crossover results](upstream-release-throughput/crossover1-results.json).

## 8. Public reference, incomplete work and final status

The public four-LP reference requested to contextualize x64 scaling landed on
an **AMD EPYC 7763 with 16 GiB RAM**, not Intel. Run **39110448524** completed both
PGO stages but reached its deadline in the final build. Its **5h44m18s production
interval is unfinished**, not a completed release time.

Completed PGO-gathering sections totaled **52.72 minutes publicly versus 356.60
minutes on self-hosted x64/4**. Source pins, recipe and all 65 logged scenario
records matched, but hardware and raw profile byte counts differed. Conversely,
the initial instrumented-compiler build was slower publicly. This localizes a
phase difference; it does not establish a general public-CPU speedup.

The subsequent whole-workspace continuation attempt **39135351977** completed
fresh training in **4h39m37s**, then timed out archiving; the final job did not run.
Replacement **39218601376** was cancelled when testing was stopped. **No completed
continuous or whole-workspace-segmented public x64 release resulted from this
reference study.** GB300's requested 32/16/4-LP scaling remained incomplete after
storage and runner-disconnection failures; its qualified 64-LP pilots remain valid.

See the [preserved phase evidence and recovery history](matched-release/README.md).
Incomplete attempts are never successful totals, zero-gain samples or forecasts.

### Requested x64 PGO follow-up completed on 21 October

The separately resumed x64 comparison completed **four fresh full releases**
on the dedicated NVMe runner, using opposite order in two pairs, and replayed
the first pair's fixed artifacts on **five independent standard Windows VMs**.
It measured **18.0% less offline IronRDP wall time versus official Rust**
(95% interval 15.0-20.8%), with **2.71% more compiler-production time** and
**4.00% more whole release-job time** on average. Observed whole-job increases
were 2.51% and 5.55%, not a population confidence interval.

This completes the requested x64 toolchain-benefit/CI-cost comparison. It does
not complete the older hosted-release reference or GB300 scaling study.
See the [final report, limits and permanent evidence](X64-PGO-COMPARISON.md).

## 9. Conclusions and prioritized follow-up

| Priority | Action if work is resumed | Evidence / acceptance condition |
|---|---|---|
| 1 | Apply effective PGO where absent; retain Microsoft linking as the simpler option | Strongest observed compiler-throughput lever; verify actual backend counters and downstream correctness |
| 2 | Control storage and profile processing before interpreting x64 scaling | Use NVMe, matched source/tools, counterbalanced repetitions and phase CPU/I/O telemetry |
| 3 | Optimize packaging as its own release bottleneck | Preserve full tools/docs/MSI and unpacked payloads; include archive-size and transfer costs |
| 4 | Separate individual Rust-LTO, LLVM-LTO and linker contributions | Build on the existing matched combined-ThinLTO result; hold profiles fixed where feasible |
| 5 | Qualify a complete hosted production strategy | Include fresh training, handoff/setup, packaging and extracted tests; report segmented versus continuous time explicitly |

The evidence does **not** establish blanket ineffectiveness of upstream x64 PGO,
a universal OS or architecture factor, application-runtime gains, stable x64
scaling, or a completed public x64 fresh-training release duration. The compiler
benefits are real on the measured workloads; production feasibility and
infrastructure must be evaluated independently rather than hidden in one number.

### Reproducibility anchors

| Investigation scope | Rust source |
|---|---|
| Shipping comparison and matched compiler controls | Rust 1.94.1, `e408947bfd200af42db322daf0fadfe7e26d3bd1` |
| Matched full-release pilots and CPU scaling | `7db17d9b5bbe6b16be2dc86b4bfae81d6e1ae238`, with declared common experimental repairs |
| Upstream-equivalent scheduling study | Unmodified `76c90957b7e422c4b9c45192b0197214d7de5a54` |

IronRDP source: `0c5419eca6bf53563056ed252f537bca67862705`.
The linked protocols/results preserve LLVM/tool/profile identities, qualification
gates and run provenance. This summary integrates the findings, but does not
pool different workloads, source revisions, controls or hardware into one estimate.
