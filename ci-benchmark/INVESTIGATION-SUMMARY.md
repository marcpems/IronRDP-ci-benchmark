# Windows Rust compiler performance: investigation summary

Updated 30 October 2026. This is the end-to-end summary of the problem,
investigation stages, measured results and remaining limitations. Detailed
reports and reproducible evidence are linked throughout. All experiments were
conducted in forks, followed by a check of an upstream PR try-build; no official
release rollout is claimed. The broad campaign stopped
at the user's request on 19 October. Only the requested x64 upstream/local-PGO
comparison resumed on 20 October, followed by the requested profile-only test
on 21 October and Rust 1.99.1 revalidation on 22 October. Later work validated
the current PR's full release on 25 October, checked the upstream artifact on
26 October, and reproduced a native-cache invalidation defect on 27 October.
The requested NVMe x64 4/8/16-LP timing audit on 30 October found completed
16-LP builds but no matching 4/8-LP builds. The restored runner has now passed
readiness checks and started a [fresh sequential 16/8/4-LP comparison](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/41054163612).
Its 16-LP release has qualified; 8/4-LP comparison results remain pending.
A separate hosted Rust-only ThinLTO pilot completed on 30 October and found
no meaningful incremental IronRDP wall-time gain. Arm64 and GB300 experiments
remain stopped.

Presentation and document versions:
[technical PowerPoint with linked report index](matched-release/Rust-Optimization-Summary-Published.pptx)
and [combined Word report](matched-release/Rust-Optimization-Combined-Report-30Oct2026.docx).
Both Office reports were refreshed on 30 October to include the same-tools
PGO/LTO distinction, D: NVMe timings, upstream artifact/cache findings and
explicitly pending scaling results. They are on the same reporting branch.
See [Document locations and currency](#document-locations-and-currency).

## TL;DR

- **The reported Windows compilation penalty was reproduced when building
  IronRDP, not Rust itself:**
  Windows/Linux native-compilation wall-time ratios were **1.82x on x64**
  and **1.69x on Arm64** on standard GitHub runners. Mac was not benchmarked.
- **The primary workload bottleneck was compiler execution.** On the graphics
  isolation workload, rustc accounted for **99.3-99.6% of Windows' extra CPU
  time**. This is not proof of an LLVM-specific defect.
- **For adoption without changing Windows native tools, separate PGO from LTO.**
  Matched x64 LLVM-profile-only rebuilds retained clang-cl and Microsoft
  `link.exe`/`lib.exe`, saving **13.73% on Rust 1.94.1** and **12.93% on 1.99.1**.
  Earlier same-tools fresh-PGO pilots saved **24.62% x64 / 24.44% ordinary
  Arm64 versus no-PGO controls**, a different denominator. A new matched x64
  **Rust-only ThinLTO pilot found no meaningful wall gain**: **812.586 to
  812.961s**, 0.05% slower, with 0.36% less CPU. This is one compiler/sysroot
  build pair on one consumer VM, not full-release qualification. Arm64's
  incremental effect remains unmeasured.
  See the [adoption evidence matrix](#31-adoption-view-keep-the-windows-tool-stack).
- **Historical broader optimized bundles improved the original offline IronRDP workload versus
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
- **The x64 D: NVMe results provide the practical CI reference.**
  The 25 October full fresh-PGO release retained Microsoft tools and took
  **2h33m44s including extracted tests / 2h59m01s for the whole job**, at
  **16 logical processors (8 physical cores)**. Rust 1.94.1 and 1.99.1
  fixed-profile builds have different scopes and are listed separately below.
  No completed matched NVMe x64 4/8/16 scaling curve exists; a fresh comparison
  is running. The Arm64 4/8/16 figures must not be relabelled as x64 results.
  These custom builds used no compiler
  object-cache service; that is **not a measured 0% cache-hit rate**.
- **The actual upstream try artifact did not reproduce the PGO gain.**
  `51dae839` averaged **628.71s versus 630.07s** for its parent: only **0.21%**
  less IronRDP wall time. Its LLVM profile has active backend coverage, but its
  producer reported **100% native C/C++ cache hits**. A local reproduction
  confirmed that sccache 0.10.0 can reuse objects after the profile changes.
  This strongly supports the cache explanation; a cache-corrected full build
  and downstream replay are still required to prove recovered performance.
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

**Two different builds are measured throughout this report:**
**building IronRDP with a Rust toolchain** measures the toolchain's benefit to
developers; **building the Rust compiler and its distribution** measures the
cost of producing that toolchain. A percentage improvement in one is not an
improvement in the other. Neither endpoint measures application runtime.

| Quantity | What its time includes |
|---|---|
| IronRDP compilation | Five Cargo command wall times; excludes setup, dependency downloads, test execution, verification and uploads |
| Full Rust production | Helper construction, fresh PGO training/merging and complete distribution production; excludes initial setup, post-build qualification and uploads |
| Whole Rust release job | Successful compiler/distribution job start-to-finish, including setup, qualification, uploads and applicable cleanup; excludes queues and separate failed/recovery jobs |
| Component wall scope | Non-overlapping recorded steps, including links, waits and I/O; **not** raw compile CPU time |

Full Rust production logs contain dependency downloads: unlike the IronRDP
replay, **full production is not an offline compile-only measurement**.
LP means **Logical Processors**, not necessarily physical cores.

## 2. Building IronRDP: reproduce the OS gap and isolate compiler execution

**Measured build: IronRDP's five-command offline Cargo workload, using an
already-built Rust toolchain. These are not times to build Rust itself.**
Three independent standard GitHub jobs per OS/architecture reproduced the gap:

| Architecture | IronRDP on Linux, seconds | IronRDP on Windows, seconds | Windows/Linux IronRDP time |
|---|---:|---:|---:|
| x64 | 555.030 | 1,008.888 | 1.818x |
| Arm64 | 424.245 | 714.955 | 1.685x |

These are medians of per-job totals, not sums of command medians. Workspace-test
compilation explained approximately **75-79% of the excess native time**;
gateway feature variants accounted for another **18-21%**. Windows compiled
fewer workspace units, so simply counting more crates did not explain the gap.

The next stage narrowed the IronRDP workload to `ironrdp-graphics` builds and
direct `yuv` rustc invocations with one/four-processor affinity, native/shared-WASM targets,
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

## 3. Building Rust: audit release optimizations and validate PGO training

**Subject: the recipe used to produce the Rust compiler, and whether its
training profiles contain useful coverage.** Coverage counts are not build
times. The performance benefits cited below are measured separately by
building IronRDP with the resulting compilers.

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

### 3.1 Adoption view: keep the Windows tool stack

**Benefit endpoint: reduced IronRDP compilation time**, not reduced time to
build Rust. Rows marked feasibility or unmeasured do not supply a speedup.

The preferred delivery path retains **clang-cl, Microsoft `link.exe` and
`lib.exe`**, and ships a normal complete Rust toolchain. This is an adoption
and maintenance preference, not a claim that alternative tools cannot work.
It does not require users to transplant compiler components between releases.

Open PRs (30 October): [Rust #164707](https://github.com/rust-lang/rust/pull/164707)
repairs static-LLVM PGO training;
[Rust #165138](https://github.com/rust-lang/rust/pull/165138) adds the
profile-aware cache workaround;
[sccache #2962](https://github.com/mozilla/sccache/pull/2962) fixes upstream
clang-cl profile hashing.

| Optimization, with Windows native tools unchanged | x64 IronRDP benefit / status | Arm64 IronRDP benefit / status | What can be claimed |
|---|---|---|---|
| Repair LLVM PGO; retain Rust-side profiles and existing LTO settings | **13.73%** less IronRDP wall on 1.94.1; **12.93%** on 1.99.1 | No equivalent profile-only estimate | Isolated x64 LLVM-profile benefit, not a linker gain |
| Enable fresh PGO in the release recipe; no added cross-crate LTO | **24.62%**: 737.35 to 555.78s | **24.44%**: 1348.55 to 1018.93s on ordinary Arm64; GB300 **21.46%** | Same-tools PGO-recipe benefit versus controlled **no-PGO** builds; one accepted pilot per machine, not additional savings over shipping x64 Rust |
| Add Rust-side cross-crate ThinLTO to PGO; native LLVM ThinLTO remains off | **No meaningful wall gain in the 30 October pilot:** 812.586 to 812.961s (0.05% slower); CPU 0.36% lower | Earlier full releases qualified; **incremental IronRDP gain not measured** | New x64 result is one compiler/sysroot pair and one consumer VM, not full-distribution qualification or a population estimate |
| Enable native LLVM ThinLTO while retaining `link.exe` | Compatibility probe rejected LLVM bitcode, including with `/LTCG` | No qualified same-tools result | Not an available drop-in change in the tested clang-cl pipeline |

Rust-side ThinLTO is performed inside rustc before native objects reach
`link.exe`. LLVM-side ThinLTO needs a linker that understands LLVM bitcode;
MSVC `/LTCG` is not a substitute. PGO uses the profile during compilation,
so retaining Microsoft linking does not prevent the measured PGO benefit.

**Do not use the historical x64 7.6% ThinLTO result as the same-tools LTO
estimate:** that experiment used LLVM linking tools and added both Rust and
LLVM ThinLTO. Likewise, the 23.7% x64 / 16.0% Arm64 shipping comparisons below
measure broader bundles. Subtracting them from PGO-only percentages would mix
different controls, sources, machines and profile inputs.

The older isolation benchmarks deliberately held Cargo and the standard
library constant across compiler variants. That is an experimental control,
**not a deployment recipe**, and it does not establish an untouched-package
speedup. The complete distributions separately passed qualification. The
later upstream-artifact check retained each compiler's own bundled standard
library (and a common Cargo), but did not show the expected gain.

The [30 October x64 pilot](X64-RUST-THIN-INCREMENTAL.md) now compares repaired
PGO against PGO plus **Rust-only** ThinLTO at the same source revision with
identical frozen profiles and matching native tools. Three measured pairs gave
wall reductions of **0.69%, 0.05%, -0.88%**: no meaningful incremental gain.
Native correctness passed for both arms. Full-distribution qualification,
multiple independent consumer VMs and the Arm64 incremental comparison remain
separate work; release-production scaling does not answer those questions.

The [discrepancy audit](X64-RUST-THIN-INCREMENTAL.md#why-this-differs-from-the-earlier-76-result)
confirmed effective DLL ThinLTO flags and different executable code in the new
packages. It also recomputed the old gain on every VM, including two with the
new consumer's CPU model. The old contrast changed **both LTO modes while
retaining LLD in both arms**. Expecting that gain from Rust-only ThinLTO
overstated the original attribution; LLVM's contribution and cross-version
effects remain unseparated, not measured explanations.

Evidence: [profile-only 1.94.1](X64-PROFILE-ONLY.md),
[profile-only 1.99.1](X64-PGO-1991.md),
[incremental x64 Rust-only ThinLTO](X64-RUST-THIN-INCREMENTAL.md),
[same-tools full-release pilot measurements](matched-release/selfhost-pilot-results.json).

## 4. Measure optimized compilers on the original IronRDP workload

Five independent VMs per OS, one excluded warmup and three measured rounds
compared shipping Rust with optimized compilers. Windows compiler ordering was
counterbalanced; confidence intervals resample whole VMs and preserve pairing.
Original correctness commands passed outside timing.

| Windows architecture | IronRDP using shipping Rust, seconds | IronRDP using optimized Rust, seconds | IronRDP wall-time reduction | 95% interval |
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

## 5. Building Rust distributions: production cost versus IronRDP benefit

**Cost endpoint: building and packaging Rust itself.** Where a table also
reports an IronRDP saving, that is a separate downstream compilation
measurement using the resulting toolchain, not a release-build speedup.

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

| Machine / allocation | Rust production: no PGO, min | Rust production: MS PGO, min (+% vs no PGO) | Rust production: LLVM recipe, min (+%) | IronRDP compile saving: MS / LLVM |
|---|---:|---:|---:|---:|
| Arm64 / 4 LP | 180.1 | 431.9 (+139.8%) | 656.4 (+264.5%) | 24.4% / 27.9% |
| GB300 Arm64 / 64 LP | 138.5 | 182.6 (+31.8%) | 203.3 (+46.8%) | 21.5% / 22.0% |

The LLVM recipe's extra downstream saving versus Microsoft PGO was
**4.54% ordinary Arm64 and 0.65% GB300**, at additional production costs of
**224.50 and 20.70 minutes**, respectively. Here linker, both LTO settings
and fresh profiles change together; this is not the matched-profile ThinLTO
contrast from the previous stage.

Production decomposition exposed substantial non-compilation work. On GB300:

| Exclusive Rust-production scope, minutes | No PGO | MS PGO | LLVM recipe |
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

## 6. Building Rust distributions: storage and CPU scaling

**Measured build: Rust compiler/distribution production, not IronRDP.**
The worker allocations in this section apply to toolchain production;
IronRDP replay worker counts are separate.

### 6.1 Arm64 full-release CPU scaling

A further recipe retained Microsoft tools and fresh PGO, enabled **Rust
ThinLTO**, and left native LLVM ThinLTO off. Three Arm64 releases qualified:

| Machine | Logical Processors | Rust-production minutes | Rust-production time saved vs same-machine 4 LP |
|---|---:|---:|---:|
| Arm64 | 4 | 507.79 | Baseline |
| Arm64 | 8 | 137.13 | 73.00% |
| Arm64 | 16 | 112.03 | 77.94% |

The runner was **MARCPE-D4-Arm64**.
These are fixed-order, single observations, not a validated scaling curve.
Arm64's superlinear 4-to-16 ratio requires explanation and repetition; its
self-hosted timings are not guarantees for GitHub larger runners.
**No IronRDP replay measured the downstream benefit of this scaling recipe.**

**Compiler cache: not enabled.** The retained bootstrap configurations do not
enable sccache/ccache, and the final LLVM/LLD CMake configurations have no C/C++
compiler-cache launcher. Each release started with fresh build objects.
There is no recorded cache-hit percentage; report **N/A (no compiler-cache
service)** rather than an observed 0%.

Evidence and run identities: [Arm64 scaling details](matched-release/README.md).
Arm64 4/8/16 runs: **38756702383 / 38873093226 / 38728610658**.

### 6.2 x64 D: NVMe compiler-production and CI times

The dedicated `MARCPE-TEST01-X64` has **8 physical cores / 16 logical
processors**, not 16 physical cores. All release timings in this subsection
use **D: ReFS on the 2-TB SK hynix NVMe SSD**, with correctness scratch on
C: NTFS. They are not a controlled filesystem comparison.

| Rust build / scope | Build allocation | Rust-production wall | Separate extracted tests / qualification | Whole successful Rust release job |
|---|---:|---:|---:|---:|
| Rust 1.94.1 official LLVM profile, fixed-profile distribution | 16 LP | **1h15m06s** | **10m31s**, including helper/orchestration; recovered separately | No matched whole-job total: split production/qualification |
| Rust 1.94.1 repaired LLVM profile, fixed-profile distribution | 16 LP | **1h12m17s** | **9m42s**, including helper/orchestration | No matched whole-job comparison in this recovery workflow |
| Rust 1.99.1 official LLVM profile, fixed-profile distribution on D: NVMe | 16 LP | **1h12m17s** | **9m44s**, including separate helper | **1h52m42s** |
| Rust 1.99.1 repaired LLVM profile, fixed-profile distribution on D: NVMe | 16 LP | **1h10m19s** | **9m41s**, including separate helper | **1h53m20s** |
| PR `4da678aa` plus dry-run prerequisite, fresh full PGO on D: NVMe, 25 October | 16 LP | **2h24m37s**, derived by excluding the recorded test section | **9m07s** | **2h59m01s** |

**All five rows retain Microsoft `link.exe`/`lib.exe` and do not add cross-crate
ThinLTO.** For 1.94.1, fixed-profile production was **4506.154s versus
4337.160s**; the control was qualified later without rebuilding its compiler.
These are accepted production timings, not successful uninterrupted whole-job
measurements. The 1.99.1 fixed-profile rows likewise exclude training; that
study's separate repaired training took
**1h20m33s** (whole training job **1h34m52s**). Do not compare their approximately
70-minute production directly with a fresh-training full release.

**Compiler-cache status for every row above: N/A (not enabled), not a measured
0% hit rate.** Retained bootstrap configurations and final LLVM/LLD
`CMakeCache.txt` files show direct clang-cl compilation without a compiler-cache
launcher; the harness also excludes inherited compiler-wrapper settings.
Build-object trees were fresh for each distribution. The supplied PGO profiles
in the fixed-profile studies are deliberate inputs, not cached object files.

This does not mean all reuse was disabled: normal bootstrap/Cargo reuse
within a release pipeline remains, and filesystem/OS caches are not measured
as sccache hits. `CMakeCache.txt` stores configuration, not compiled objects.
In contrast, the **official upstream try-build** in section 8 explicitly used
sccache and reported **100% native C/C++ hits**; it must not be described as a
zero-hit build.

For the 25 October validation, the measured production-plus-tests interval was
**9,223.797s (2h33m44s)**. Its non-overlapping breakdown is:

| Rust release-build component | Seconds | Minutes |
|---|---:|---:|
| Rust-side PGO stage, including its builds and profile collection | 4066.980 | 67.78 |
| LLVM PGO stage, including instrumented compiler and profile collection | 1435.190 | 23.92 |
| Final distribution build, including compilation and packaging | 2959.670 | 49.33 |
| Extracted-distribution tests | 546.800 | 9.11 |
| Helper preparation and other measured orchestration | 215.157 | 3.59 |
| **Production plus tests** | **9223.797** | **153.73** |
| Setup, uploads and remaining whole-job overhead | 1517.203 | 25.29 |
| **Whole job** | **10741.000** | **179.02** |

All **25,648 tests passed**, with zero failures, 739 ignored and 541 filtered
out by the unchanged upstream suite. Twenty distribution files were preserved.
These are stage wall times, not raw compile CPU, and include fresh training and
packaging. Native objects and profiles were fresh; this successful self-hosted
validation does not establish the duration of a cache-corrected hosted build.

#### Requested NVMe 4/8/16-LP matrix: evidence status

| Allocation on the custom x64 NVMe host | Available full-release timing | Status as of 30 October |
|---|---|---|
| 4 LP | **None for a matched NVMe scaling recipe** | Scheduled after the 8-LP cell succeeds |
| 8 LP | **None for a matched NVMe scaling recipe** | Scheduled after the new 16-LP reference qualifies |
| 16 LP | **2h23m54s production; 8m58s qualification; 3h02m41s whole job** | Fresh matched reference qualified; 8-LP build is running |

The four-worker **IronRDP replay** is not a four-worker **Rust release build**.
The upstream eight-processor GitHub try job is also not an eight-processor
observation on this custom host. The completed **4/8/16 study was ordinary
Arm64**, not the requested x64 NVMe matrix.
After the user restored the runner, [run 41054163612](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/41054163612)
started on 30 October. The runner, idle-process, exact D: NVMe and free-space
checks passed. The [recorded protocol](x64-nvme-scaling-protocol.json) runs
**16, then 8, then 4 LP**, using the same pinned full-PGO Microsoft-tool recipe
as the 25 October validation. Every cell starts fresh compiler objects and
training; no compiler-cache service is enabled, so its hit rate is **N/A**,
not an observed 0%. Lower-worker cells must match the new reference's source,
tool hashes, normalized configuration, hardware and power scheme.

The study records inherited affinity and physical-core topology and separates
production, extracted tests, phase timings and whole-job time. It measures
**building Rust**, not IronRDP performance or incremental LTO benefit.
This first, fixed-order pass uses freshly generated profiles per cell and
will be descriptive; repetitions would be needed for a stable scaling estimate.

Evidence: [1.94.1 D: NVMe study](X64-PROFILE-ONLY.md),
[1.94.1 raw configuration/timing records](x64-profile-only-evidence.zip),
[1.99.1 D: NVMe study](X64-PGO-1991.md),
[1.99.1 raw configuration/timing records](x64-profile-1991-evidence.zip),
[25 October complete validation](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/40170434889),
and [persistent later evidence](later-pgo-evidence.zip).

## 7. Building Rust/LLVM: production-throughput probes and negative results

**Measured work: compiler-production components, packaging, and release
continuations.** These are not IronRDP compilation measurements; a faster
packaging or LLVM-build step does not itself establish a faster shipped compiler.

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

## 8. Rust-release validation and the separate IronRDP artifact check

The public reference and release validations below measure **building Rust
distributions**. The explicitly labelled upstream-artifact check instead
measures **building IronRDP with those already-built distributions**.

The public four-LP reference requested to contextualize x64 scaling landed on
an **AMD EPYC 7763 with 16 GiB RAM**, not Intel. Run **39110448524** completed both
PGO stages but reached its deadline in the final build. Its **5h44m18s production
interval is unfinished**, not a completed release time.

Completed PGO-gathering sections totaled **52.72 minutes** on that public
runner. This is a partial phase measurement, not a completed release time.

The subsequent whole-workspace continuation attempt **39135351977** completed
fresh training in **4h39m37s**, then timed out archiving; the final job did not run.
Replacement **39218601376** was cancelled when testing was stopped. **No completed
continuous or whole-workspace-segmented public x64 release resulted from this
reference study.** GB300's requested 32/16/4-LP scaling remained incomplete after
storage and runner-disconnection failures; its qualified 64-LP pilots remain valid.

See the [preserved phase evidence and recovery history](matched-release/README.md).
Incomplete attempts are never successful totals, zero-gain samples or forecasts.

### 21 October: Rust-production cost and separate IronRDP compilation benefit

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

### 25 October: building and qualifying the current-PR Rust distribution

The PR's static-LLVM rebuild exposed an independent bootstrap dry-run
prerequisite: the read-only Clang profiling-runtime lookup must execute during
the dry run. The exact upstream panic was reproduced without that one-line
fix and disappeared with it; formatting, 271 bootstrap tests and the opt-dist
build passed. A fresh same-tools full Windows release then passed all extracted
tests on the 16-LP NVMe runner, as detailed in section 6.2. This was release
qualification, **not an additional downstream performance experiment**.

### 26 October: building IronRDP with the actual upstream Rust artifact

The requested upstream Rust 1.101.0-nightly try artifact
`51dae83933ec0602516d385a07cea7c692d15261` was compared with its exact first parent,
`dc44e7f2c436b6041742e138b9c2176f093196d5`. Two cold five-command IronRDP blocks
per compiler used the same host, four-CPU affinity, the parent Cargo and each
compiler's own bundled standard library. There was no excluded warmup or
statistical qualification. Setup/downloads/correctness were untimed.

| Toolchain used to build IronRDP | Mean IronRDP offline wall | Mean IronRDP descendant CPU |
|---|---:|---:|
| Exact parent | 630.066s | 2443.008s |
| Requested upstream try artifact | 628.713s | 2439.039s |
| Reduction | **0.21%** | **0.16%** |

This **did not reproduce the earlier approximately 13% gain**. The final parent
block initially failed reading a Cargo registry source file with Windows
`os error 87`; only that block was repeated after source/compiler verification.
All three completed original blocks and the failure evidence were retained.
The completed set contains 20 successful measured commands. See the
[original run](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/40403546509)
and [successful continuation](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/40409913485).

### Cache diagnosis: strong evidence, not yet recovered end-to-end performance

**Cache scope: native C/C++ compilation while producing Rust/LLVM**, not
Cargo's cache when building IronRDP. The missing performance gain is the
separate IronRDP result above.

The actual parent/try reproducibility profiles were inspected:

| LLVM query | Parent functions / active | Try functions / active |
|---|---:|---:|
| `X86TargetLowering` | 0 / 0 | 273 / 176 |
| `InstCombine` | 0 / 0 | 980 / 631 |

Training therefore restored coverage. However, the
[upstream producer log](https://triage.rust-lang.org/gha-logs/rust-lang/rust/121229977135)
at **25 October 19:10:06 UTC**, under `sccache stats`, reports:

```text
Cache hits (c [msvc])                212
Cache hits (c++ [msvc])            10341
Cache misses                          88
Cache misses (rust)                   88
Cache hits rate (c [msvc])        100.00 %
Cache hits rate (c++ [msvc])      100.00 %
Forced recaches                        0
Non-cacheable compilations             0
```

These are **whole-job aggregate** counters, not a per-object provenance trace.
The final command requested the newly generated LLVM profile at 18:25:33 UTC;
CMake enabled that profile and the sccache native compiler launchers.

The pinned sccache 0.10.0 MSVC handler does not hash profile contents for the
bare `-fprofile-instr-use=<path>` spelling emitted by this LLVM CMake version.
A session-local reproduction using the exact CI sccache binary, actual
parent/try profiles and local Clang 23.1.4 targeting x64 (upstream used Clang
22.1.8) confirmed a cache hit after replacing the valid profile at the same
path. A profile-hash cache-buster, the `-clang:` wrapped flag, and
`SCCACHE_EXTRAFILES` each correctly invalidated that reuse.

The likely chain is **new profile -> stale native LLVM objects -> newly linked
rustc without the expected gain**. PGO optimization occurs during native
compilation here; the final Microsoft linker cannot redo the missed work.
This establishes a cache-key defect and a strong explanation of the upstream
result. It does **not** identify the historical profile behind every cached
object or prove that correcting the cache restores 13%.

The smallest proposed mitigation is to include the merged LLVM profile in
`SCCACHE_EXTRAFILES` only for the Windows profile-use build, preserving existing
entries and all earlier-stage caches. A global purge would add unrelated cold
build work; a one-off global cache-buster would not fix recurring invalidation.
New profiles may differ on every build, so correct final-stage cache misses
must be budgeted rather than assumed to disappear after one run.

The cached upstream job took **2h19m30s** on `windows-2025-8core-32gb`.
That leaves nominal headroom below GitHub-hosted jobs' six-hour limit, but the
corrected cold final-stage duration is **unmeasured**. Require a complete
cache-corrected release, qualification and IronRDP replay before claiming
official adoption/performance recovery. If necessary, evaluate a larger runner
or artifact-verified job split; neither is an established result here.

Evidence: [late validation, replay and cache-reproduction records](later-pgo-evidence.zip).

## 9. Conclusions and prioritized follow-up

The separate [30 October incremental x64 ThinLTO pilot](X64-RUST-THIN-INCREMENTAL.md)
completed successfully: repaired-PGO versus the same compiler plus Rust-only
ThinLTO produced **812.586 / 812.961s mean offline IronRDP wall** and
**3141.375 / 3130.063s CPU**. The mixed sub-percent wall results do not justify
a speedup claim. This narrow pilot retained Microsoft linking and frozen
profiles; it did not build/qualify all release tools or measure application
runtime. Raw receipts, recovery history and limitations are preserved in
[compact evidence](x64-rust-thin-incremental-evidence.zip).

| Priority | Action if work is resumed | Evidence / acceptance condition |
|---|---|---|
| 1 | Make final Windows LLVM native-cache keys profile-aware, then validate the shipped artifact | Correct training is insufficient if stale objects are reused; require full release/correctness and downstream recovery within the runner budget |
| 2 | Apply effective PGO while retaining Microsoft linking tools | Use isolated x64 profile evidence and explicitly labelled Arm64 no-PGO pilots; do not imply a same-tools LTO gain |
| 3 | Complete the running custom x64 NVMe 4/8/16-LP production matrix | Match source/tools/recipe/cache policy; report each phase and whole job |
| 4 | Reassess Rust-only ThinLTO after the null x64 pilot; Arm64 remains unmeasured | Require repeatable benefit and full-package qualification before adoption; the older LLVM-linked 7.6% result is not this estimate |
| 5 | Optimize packaging and qualify a complete hosted production strategy | Preserve tools/docs/MSI, include training/setup/transfers/tests, and report segmented versus continuous time explicitly |

The evidence does **not** establish blanket ineffectiveness of upstream x64 PGO,
a universal OS or architecture factor, a useful incremental Rust-only ThinLTO
gain on x64, application-runtime gains, stable x64
scaling, or a completed cold, cache-corrected public x64 release duration. The compiler
benefits are real on the measured workloads; production feasibility and
infrastructure must be evaluated independently rather than hidden in one number.

### Reproducibility anchors

| Investigation scope | Rust source |
|---|---|
| Shipping comparison and matched compiler controls | Rust 1.94.1, `e408947bfd200af42db322daf0fadfe7e26d3bd1` |
| Matched full-release pilots and CPU scaling | `7db17d9b5bbe6b16be2dc86b4bfae81d6e1ae238`, with declared common experimental repairs |
| Upstream-equivalent scheduling study | Unmodified `76c90957b7e422c4b9c45192b0197214d7de5a54` |
| Rust 1.99.1 profile-only revalidation | `58cf8f9c35b355199727627d07ae34a4e2846d67`, declared training prerequisite/repair |
| Current-PR full-release qualification | `4da678aada4683607acbd67a8da37a320c791f93` plus exact dry-run prerequisite |
| Actual upstream artifact check | Try `51dae83933ec0602516d385a07cea7c692d15261` versus parent `dc44e7f2c436b6041742e138b9c2176f093196d5` |

IronRDP source: `0c5419eca6bf53563056ed252f537bca67862705`.
The linked protocols/results preserve LLVM/tool/profile identities, qualification
gates and run provenance. This summary integrates the findings, but does not
pool different workloads, source revisions, controls or hardware into one estimate.

### Document locations and currency

The canonical report branch is **`experiment/x64-pgo-1991`** in
**`marcpems/IronRDP-ci-benchmark`**. Every relative link in this document resolves
within that branch unless explicitly identified as an external run/source.
The following files are tracked together there; no branch switching is needed
to retrieve the PowerPoint or Word reports.

| Document | Currency / purpose |
|---|---|
| [This investigation summary](INVESTIGATION-SUMMARY.md) | Current synthesis, updated 30 October; use this for the latest limitations |
| [Combined detailed findings](COMBINED-REPORT.md) | Historical experiment detail; links back to this current synthesis |
| [Technical PowerPoint and report index](matched-release/Rust-Optimization-Summary-Published.pptx) | Updated 30 October; 14 slides, completed ThinLTO pilot and pending NVMe matrix |
| [Combined Word report](matched-release/Rust-Optimization-Combined-Report-30Oct2026.docx) | Updated 30 October; ten-page consolidation, current evidence and limitations |
| [Maintainer brief](matched-release/Rust-Compiler-Optimization-Maintainer-Brief.docx) | Earlier full-release proposal and pilot interpretation |
| [Self-hosted release pilots](matched-release/Self-Hosted-Rust-Release-Pilots.docx) | Earlier x64 / ordinary Arm64 pilots |
| [GB300 release pilot](matched-release/GB300-Rust-Release-Pilot.docx) | Earlier GB300 result, not a completed lower-core scaling study |
| [Original Windows performance report](Windows-Rust-Performance-Summary.docx) | Earlier OS/compiler investigation |
| [Late compact evidence](later-pgo-evidence.zip) | 25-27 October release, artifact replay and cache diagnosis; 30 October runner availability |
| [Incremental x64 Rust-only ThinLTO](X64-RUST-THIN-INCREMENTAL.md) | 30 October completed compiler/sysroot pilot; no meaningful IronRDP wall benefit |
| [ThinLTO pilot evidence](x64-rust-thin-incremental-evidence.zip) | Verified inputs, raw timing/correctness outputs, failure history and reproduction scripts |

The linked PowerPoint and combined Word report reflect this 30 October
update, without inventing results for the running NVMe study. The earlier
`Rust-Optimization-Combined-Report-Revised.docx` is retained unchanged as a
historical version. Other Office reports remain historical snapshots; their
projections are not promoted to current results. The same-branch links above
are the retrieval index for this update.
