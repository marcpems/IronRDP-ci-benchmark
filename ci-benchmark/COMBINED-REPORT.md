# IronRDP / Rust compiler performance: combined findings

## Answer

**Original native CI validation: the optimized Windows Arm64 toolchain reduces
offline compilation wall time by 16.0% (95% interval 15.4-16.7%) and CPU time by
16.0% (15.4-16.6%).** The five-command native sequence falls from **709.64 to
595.99 seconds**, saving **113.65 seconds**. This confirms a substantial benefit
on the original workload, but **not the full 18-19% graphics-workload saving**.
All ten VMs completed successfully, including the original native tests.
The [opt-in setup action](OPTIMIZED-TOOLCHAIN.md) and compiler package are reusable;
all changes and releases remain in the fork, with upstream untouched.

**Controlled Arm64 result: adding rustc/LLVM PGO and Rust/LLVM ThinLTO recovers
44.7% of the observed Windows/Linux CPU-time gap (95% interval 38.0-50.6%),
and 45.6% of the wall-time gap (37.8-53.4%).** Windows compilation uses **18.0%
less CPU time and 18.8% less wall time**, measured against the matched LLD
control. This is the combined optimization bundle on the graphics workload,
not separate LLVM attribution, an x64 result, or a full-workspace CI estimate.

For the graphics workload, the Windows gap is predominantly CPU consumed
inside rustc, including its code-generation backend, rather than Cargo, external
linking or off-CPU waiting. Approximately **99.3-99.6% of the additional
process-tree CPU time** on Windows is accounted for by rustc processes themselves.
This is evidence about compiler execution cost, **not proof of an LLVM-specific
defect** or attribution of every second in the full IronRDP workspace.

The earlier [whole-workspace experiment](REPORT.md) found Windows/Linux native
compile ratios of **1.82x on x64** and **1.69x on Arm64**. The new isolation suite
reproduces approximately **2.0x / 1.7x** on a meaningful subset and retains a
substantial gap when the same WASM target is compiled directly.

## Original native CI validation: 16% less wall and CPU time

[Run 36871453828](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36871453828)
replays the original five native compilation commands, including full-workspace
test compilation, on **five standard four-CPU VMs per OS**. Windows pairs official
and optimized Rust; Linux is the official reference. Three measured rounds follow
one excluded warmup: **45 measured blocks / 315 commands**, including separate
common-package and WASM controls. All **60 untimed native correctness commands**
passed (four commands per compiler/VM).

| Native compilation component | Windows stock wall (s) | Optimized wall (s) | Wall reduction | CPU reduction |
|---|---:|---:|---:|---:|
| Build xtask | 4.06 | 3.69 | 8.9% | 12.6% |
| Workspace test compilation | 540.08 | 460.60 | 14.7% | 15.4% |
| Native TLS test compilation | 17.24 | 13.43 | 22.1% | 19.4% |
| Gateway native TLS test compilation | 74.45 | 60.24 | 19.1% | 18.6% |
| Gateway smartcard test compilation | 73.82 | 58.03 | 21.4% | 17.8% |
| **Native total** | **709.64** | **595.99** | **16.0%** | **16.0%** |

Total CPU falls from **2630.64 to 2208.94 CPU-seconds**. Linux native totals are
**414.16 wall / 1549.24 CPU seconds**. The practical replacement closes **38.5%
of this run's wall-time OS gap (36.3-40.8%)** and **39.0% of its CPU gap
(37.0-41.1%)**; Windows/Linux ratios fall from **1.71x to 1.44x wall** and
**1.70x to 1.43x CPU**. These are paired Windows effects and observed cross-runner
gap equivalents, not hardware-normalized OS attribution.

**Why the overall saving is below the earlier 18-19%:** full-workspace test
compilation dominates and improves by only 14.7% wall. Cargo's disjoint activity
intervals locate the remaining cost:

| Native wall-time interval (seconds) | Linux stock | Windows stock | Windows optimized |
|---|---:|---:|---:|
| Compiler units active, no build scripts active | 329.94 | 532.16 | 418.25 |
| Compiler units and build scripts overlap | 82.67 | 172.92 | 173.23 |
| Build scripts active alone | 0.00 | 0.00 | 0.00 |
| Outside Cargo-tracked units | 1.55 | 4.56 | 4.51 |

Essentially all net wall savings occur in compiler-only intervals; the interval
with active build scripts is unchanged. This supports investigating native
build-script/C/C++ work next, but **overlap is not exclusive CPU attribution**:
compiler units include linking, and the table cannot assign every overlapping
second to a build script or LLVM. The independent common-package control saves
**18.2% wall / 18.7% CPU**, and WASM saves **16.4% / 17.3%**. These controls are
not added to the native total.

**Controls and limits:** same pinned IronRDP/Rust versions, original Cargo
profiles and package overrides (no forced codegen-unit setting), initially empty
native outputs per compiler/round, shared outputs only within the five-command
sequence. Setup, downloads, installation, correctness and uploads are excluded.
Intervals use 10,000 paired whole-VM bootstrap draws, not 15 independent Windows
trials. This is official-to-optimized adoption, unlike the earlier graphics
optimization-only contrast against an LLD control; it does not measure an entire
CI job, warm-cache builds, x64, or release-toolchain construction overhead.

Both Windows variants disable MSBuild node reuse. Documented telemetry opt-out
did not stop `vctip.exe`: the meter retains only exact `vswhere`-identified
telemetry helpers in an owned Job Object and includes all their CPU within each
timed build window, without charging post-build idle lifetime. Other persistent
children fail the measurement. See [implementation details](OPTIMIZED-TOOLCHAIN.md).
All pilots are excluded. The first full run, **36870970504**, was cancelled after
a scheduling race in the synthetic meter check; its entire dataset is excluded.
The accepted run uses a synchronized fixture and retains every measured sample.

**Reproduction:** [endpoint estimates and intervals](NATIVE-AB-RESULTS.md),
[machine-readable results](NATIVE-AB-RESULTS.json),
[preregistered protocol](native-ab-protocol.json).
Measured harness and reusable action commit:
`c18826dab98f510a418493daa47642d7aac1f181`.
The [v2 release](https://github.com/marcpems/IronRDP-ci-benchmark/releases/tag/arm64-compiler-ab-v2)
contains `native-ab-raw-36871453828.zip` (2,025 files), SHA-256
`648ae3f80db11b83e968bc64c97c3d6cbab4d7ed758801efd72e234ea2705e75`.

```powershell
gh release download arm64-compiler-ab-v2 --repo marcpems/IronRDP-ci-benchmark --pattern native-ab-raw-36871453828.zip
Expand-Archive native-ab-raw-36871453828.zip -DestinationPath native-ab-evidence
python ci-benchmark\analyze_native_ab.py native-ab-evidence --output native-ab-results
```

## Initial real-project validation

Workload: cold `cargo build -p ironrdp-graphics --lib --frozen`, including real
RDP graphics/PDU code, crypto/parsing dependencies and `yuv 0.8.16` SIMD image
conversion. This is not a generated toy loop or an empty crate.

Each cell is **wall seconds / CPU seconds**, median of three independent runners.
CPU means **user + kernel process time**, summed across threads and descendants;
it can exceed wall time.

| Allowed logical CPUs | Linux x64 | Windows x64 | Linux Arm64 | Windows Arm64 |
|---|---:|---:|---:|---:|
| **1** | **133.31 / 133.27** | **265.66 / 261.48** | **122.14 / 122.05** | **212.14 / 205.55** |
| **4** | **56.48 / 210.26** | **113.56 / 409.64** | **35.99 / 126.36** | **60.92 / 212.09** |

| Windows/Linux ratio | x64 wall | x64 CPU | Arm64 wall | Arm64 CPU |
|---|---:|---:|---:|---:|
| 1 CPU | 1.99x | 1.96x | 1.74x | 1.68x |
| 4 CPUs | 2.01x | 1.95x | 1.69x | 1.68x |

Native per-rustc meters attribute **97.7-99.1% of all project CPU time** to rustc,
excluding descendant linker processes. Cargo, meter overhead, build scripts and
external tools together account for the small remainder. The similar CPU and
wall ratios show that waiting alone does not explain the gap.

**Parallel scaling is not the main problem.** Median within-run 1-to-4 CPU wall
speedups are **2.38x Linux / 2.35x Windows on x64**, and **3.47x / 3.46x on Arm64**.
x64 exposes two physical cores with four SMT threads; Arm64 exposes four cores.
SMT/resource contention also helps explain why aggregate x64 CPU-seconds rise
with four active threads. CPU-seconds are elapsed scheduled time, not instruction
counts or a frequency-normalized measure of work.

## Direct compiler control: no Cargo or external linker

The suite captures the actual `yuv` invocation and replays rustc against prepared
dependencies. It builds an **rlib**, not an executable. Windows Job Objects
confirm **exactly one process** in every direct replay. The native and common
`wasm32-unknown-unknown` variants use matching features and optimization settings.

Direct full WASM compilation, **wall / CPU seconds**:

| Allowed CPUs | Linux x64 | Windows x64 | Linux Arm64 | Windows Arm64 |
|---|---:|---:|---:|---:|
| 1 | 43.41 / 43.40 | 82.54 / 80.91 | 48.48 / 48.46 | 70.26 / 68.78 |
| 4 | 16.75 / 60.49 | 35.07 / 122.98 | 13.05 / 44.40 | 20.16 / 69.02 |

At four CPUs, Windows/Linux is **2.09x wall / 2.03x CPU on x64** and **1.55x /
1.55x on Arm64**. The gap therefore persists without the Windows RDP backend,
COFF executable linking, Cargo scheduling or native C build scripts.

A metadata-only replay takes just **1.3-3.1% of full WASM compilation CPU time**.
Most measured cost is in work omitted by metadata-only compilation:
monomorphization, optimization/code generation, and archive/output work.
Kernel CPU is small in direct replays; for four-CPU WASM its median is
**0.42 / 1.63 seconds on Linux/Windows x64**, and **0.69 / 1.19 seconds on Arm64**.
The large difference is predominantly user-mode CPU.

**This narrows the investigation to the compiler/code-generation path, but does
not separately measure LLVM passes.** Metadata/full differencing is not an LLVM
phase timer. Compiler builds, allocator behavior, OS services and hardware
throughput remain possible explanations. The release-build audit identifies
optimization differences; the controlled Arm64 A/B below measures their combined impact.

## Rust release-build audit: Windows is not optimization-equivalent

Scope: official **Rust 1.94.1**, commit
`e408947bfd200af42db322daf0fadfe7e26d3bd1`, matching the measured compiler.
These settings optimize **the compiler binaries themselves**, not the user's
Cargo project.

| Release setting | Windows x64 MSVC | Windows Arm64 MSVC |
|---|---|---|
| LLVM backend | Rust's LLVM **21.1.8** fork | Same revision/version |
| C++ compiler building LLVM | **clang-cl 20.1.3**, win64 package | **clang-cl 20.1.3**, woa64 package |
| LLVM linkage | Static into compiler, not a separate shared LLVM library | Same |
| LLVM ThinLTO | **No** | **No** |
| Cross-crate ThinLTO for rustc | **No**; default `thin-local` mode | **No**; default `thin-local` mode |
| rustc PGO / LLVM PGO | **Configured / Configured** in the distribution job; see training caveat below | **No / No** |
| BOLT | No | No |

The backend is built from
[`rust-lang/llvm-project@00d23d10`](https://github.com/rust-lang/llvm-project/tree/00d23d10dc48c6bb9d57ba96d4a748d85d77d0c7);
its [version file](https://github.com/rust-lang/llvm-project/blob/00d23d10dc48c6bb9d57ba96d4a748d85d77d0c7/cmake/Modules/LLVMVersion.cmake#L3-L10)
specifies 21.1.8. Do not confuse this with the separate
[20.1.3 clang-cl installation](https://github.com/rust-lang/rust/blob/1.94.1/src/ci/scripts/install-clang.sh#L12-L14)
used to build it; the script selects
[native x64/Arm64 installer packages](https://github.com/rust-lang/rust/blob/1.94.1/src/ci/scripts/install-clang.sh#L47-L83).
MSVC shared-LLVM builds are
[explicitly rejected](https://github.com/rust-lang/rust/blob/1.94.1/src/bootstrap/src/core/build_steps/llvm.rs#L307-L309).

The [Windows release jobs](https://github.com/rust-lang/rust/blob/1.94.1/src/ci/github-actions/jobs.yml#L623-L660)
send only x64 through `opt-dist windows-ci`; Arm64 runs `x.py dist` directly.
Tracing shared CI setup, the `dist` defaults and bootstrap confirms
[`llvm.thin-lto=false`](https://github.com/rust-lang/rust/blob/1.94.1/src/bootstrap/src/core/config/config.rs#L1394)
and [`rust.lto=thin-local`](https://github.com/rust-lang/rust/blob/1.94.1/src/bootstrap/src/core/config/mod.rs#L403-L410).
**Thin-local is within a crate, not cross-crate ThinLTO.** x64 also explicitly
sets one compiler codegen unit; that is not an LTO switch. Bootstrap's
[Cargo/compiler-tool LTO override](https://github.com/rust-lang/rust/blob/1.94.1/src/bootstrap/src/core/build_steps/tool.rs#L124-L138)
likewise does not request cross-crate LTO in this mode.
`--enable-profiler` enables the profiling runtime, not PGO optimization of rustc.

**PGO training project: `rust-lang/rustc-perf`, not IronRDP or one standalone
application.** The release pins
[`rustc-perf@c0301bc4`](https://github.com/rust-lang/rustc-perf/tree/c0301bc44d175b9b2c5442b25049475c39d7700c).
Its collector compiles these
[exact workload sets](https://github.com/rust-lang/rust/blob/1.94.1/src/build_helper/src/lib.rs#L14-L36):

| Instrumented component | Training workloads | Compilation modes / scenarios |
|---|---|---|
| LLVM | `syn-2.0.101`, `cargo-0.87.1`, `serde-1.0.219`, `ripgrep-14.1.1`, `regex-automata-0.4.8`, `clap_derive-4.5.32`, `hyper-1.6.0` | `Debug,Opt` / `Full` |
| rustc | `externs`, `ctfe-stress-5`, `cargo-0.87.1`, `token-stream-stress`, `match-stress`, `tuple-stress`, `diesel-2.2.10`, `bitmaps-3.2.1`, `serde-1.0.219-new-solver` | `Check,Debug,Opt` / `All` |

The [training code](https://github.com/rust-lang/rust/blob/1.94.1/src/tools/opt-dist/src/training.rs#L105-L177)
merges separately collected data into `rustc-pgo.profdata` and
`llvm-pgo.profdata`; the
[pipeline applies both to the final distribution build](https://github.com/rust-lang/rust/blob/1.94.1/src/tools/opt-dist/src/main.rs#L233-L385).
Windows x64 generates its own profiles in that build. **There is no corresponding
Windows Arm64 PGO training/profile-use stage, nor reuse of the x64 profile.**
Current main's
[Windows job definitions at `21b707e3`](https://github.com/rust-lang/rust/blob/21b707e3f97e0b522ebd2f277a862339625ad83f/src/ci/github-actions/jobs.yml#L793-L828)
still show this same PGO pipeline split; the detailed settings above are pinned
to 1.94.1.

**Relevant Linux contrast:** both
[x64](https://github.com/rust-lang/rust/blob/1.94.1/src/ci/docker/host-x86_64/dist-x86_64-linux/Dockerfile#L85-L103)
and [Arm64](https://github.com/rust-lang/rust/blob/1.94.1/src/ci/docker/host-aarch64/dist-aarch64-linux/Dockerfile#L83-L105)
explicitly enable LLVM ThinLTO and `rust.lto=thin`. Both use rustc/LLVM PGO
through `opt-dist linux-ci`; its
[environment enables BOLT on x64 but not Arm64](https://github.com/rust-lang/rust/blob/1.94.1/src/tools/opt-dist/src/main.rs#L174-L219).
The configuration audit alone does not quantify their impact; the following
experiment measures the combined bundle on Windows Arm64.

## Controlled Windows Arm64 A/B: approximately 45% of the gap recovered

[Successful run 36811145829](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36811145829):
**five standard VMs per OS, three measured rounds, 750 measured commands**,
plus excluded warmups. Four Windows variants are paired on each VM; Linux runs
the official reference. Same compiler/LLVM source revisions and workload settings;
all Windows variants use byte-identical official native/WASM target libraries.
Compiler builds/training, downloads, setup and correctness checks are outside
the measured intervals. See the [preregistered protocol](arm64-ab-protocol.json).

**Graphics workload, four allowed CPUs; seconds, equal-weight VM means:**

| Compiler | Wall | Total CPU | rustc-own CPU |
|---|---:|---:|---:|
| Linux official | 35.69 | 127.34 | 124.43 |
| Windows official | 60.77 | 213.61 | 210.44 |
| Windows rebuilt MSVC baseline | 60.85 | 215.31 | 212.02 |
| Windows rebuilt LLD control | 60.93 | 214.34 | 211.08 |
| Windows PGO + ThinLTO | **49.49** | **175.74** | **172.43** |

| Controlled result | CPU time | Wall time |
|---|---:|---:|
| Optimization-only reduction versus LLD control | **18.0%** (16.1-19.4%) | **18.8%** (16.6-20.6%) |
| Equivalent fraction of official Windows/Linux gap recovered | **44.7%** (38.0-50.6%) | **45.6%** (37.8-53.4%) |

Parentheses are 95% VM-cluster bootstrap intervals, not independent-trial intervals.
The CPU attribution is `(214.34 - 175.74) / (213.61 - 127.34)`.
The preregistered baseline-equivalence gate passed: rebuilt-MSVC/official CPU
ratio **1.008**, 90% interval **0.994-1.023**, wholly inside 0.95-1.05.
The linker/librarian-only control saves just **0.97 CPU seconds**
(95% interval -2.05 to 3.79) and has no clear wall-time benefit.
Approximately **38.65 CPU seconds are saved inside rustc itself**;
other process-tree CPU remains approximately 3.3 seconds.

Single-core compilation agrees: **18.8% less CPU / 18.3% less wall time**.
Direct four-CPU `yuv` compilation saves **17.3% native / 17.4% WASM CPU**,
without Cargo or external linker processes. This is not merely better parallel
scaling. Optimized Windows remains approximately **1.38x Linux CPU / 1.39x wall**
time on the primary endpoint, versus official Windows at 1.68x CPU / 1.70x wall.

**Scope:** this identifies the recoverable effect of the **combined PGO/ThinLTO
bundle**, not each optimization separately or an LLVM defect. Standard OS runners
are not guaranteed hardware-identical; the causal compiler contrast is paired
within Windows VMs. The earlier graphics-gap equivalent is **44.7% CPU / 46.0%
wall**, conditional on the relative saving transferring to that earlier sample.
Do not generalize the percentage to the entire native IronRDP CI or to x64.
Custom compilers share the local SDK/toolchain and disabled DIA reader; the
equivalence gate checks their bridge to official Rust. The corrected build also
omits unused LLVM utility executables, with identical LLVM library components,
and applies a bootstrap-only runtime-lookup fix; compiler/LLVM source is unchanged.

**The first treatment is invalid for attribution.** Its nominal LLVM training
profile recorded target initialization but no meaningful Arm64 code generation.
The static-LLVM training path retains stage 1 instead of relinking rustc against
instrumented LLVM. Run
[36805183652](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36805183652)
was cancelled; all its samples and the v1 optimized artifact are excluded.
The corrected build explicitly relinks rustc and verifies nonzero
`AArch64TargetLowering` and `InstCombine` counters, first from a standalone
compiler smoke test and then from the exact upstream training corpus.
The accepted profile contains **179 / 595 active functions** in these groups;
specific return-lowering and instruction-combining counters also confirm execution.
This demonstrates why configured PGO is not proof of effective training;
**it does not establish that official Windows x64 profiles have the same defect**.

**Reproducible evidence:** [all endpoint tables](ARM64-AB-RESULTS.md),
[machine-readable estimates and intervals](ARM64-AB-RESULTS.json),
[compiler artifacts, PGO profiles, build logs and raw measurements](https://github.com/marcpems/IronRDP-ci-benchmark/releases/tag/arm64-compiler-ab-v2).
Measured harness commit: `ae78965f7240aad40925c6c03f46bf388f17f614`.
Raw archive SHA-256: `d11aae980de745de0128ef5ab065c827c9c31d9d1c74740ff6cf9c8ddd8b0685`.
No failed run, pilot, warmup or post-hoc slow-sample trimming enters these estimates.

```powershell
gh release download arm64-compiler-ab-v2 --repo marcpems/IronRDP-ci-benchmark --pattern arm64-ab-raw-36811145829.zip
Expand-Archive arm64-ab-raw-36811145829.zip -DestinationPath arm64-ab-evidence
python ci-benchmark\analyze_arm_ab.py arm64-ab-evidence --output arm64-ab-results
```

## Initial isolation-suite controls and limitations

- **12 successful jobs, 120 measured commands**, three fresh VMs per platform.
  Standard labels: `ubuntu-24.04`, `windows-2025`, `ubuntu-24.04-arm`,
  `windows-11-arm`. Same source and Rust **1.94.1 / LLVM 21.1.8**.
- Actual **CPU affinity** enforces one or four logical CPUs for the whole tree;
  Cargo jobs match the limit. Direct rustc also inherits the affinity. Child
  affinity, busy/sleep CPU accounting and self-versus-descendant accounting are
  checked before measurements.
- Sources/toolchains are fetched first; Cargo is frozen/offline; incremental
  compilation/debug info are disabled. Optimization is **1**, codegen units
  explicitly **16** for both CPU limits. This controlled profile is not an exact
  replay of the original full-workspace CI profile/workload.
- Compiler-own CPU: Windows `GetProcessTimes`, Linux exited-process `/proc`
  counters before reaping. Whole-tree CPU: Windows Job Object accounting,
  Linux `wait4`. These are OS counters, not sampled system utilization.
- Single/four tests share a VM but separate Cargo output directories. Direct
  replays use prepared dependencies and new output directories. Replicate 2
  reverses order. Results are pilots with warm source/page caches, not cold-disk
  or hardware-identical OS tests.
- CPU models/images vary. Nevertheless, restricting x64 to **EPYC 7763**
  samples still gives **1.92x wall / 1.87x CPU** for one-CPU direct WASM and
  **2.05x / 1.96x** for four CPUs. This is a useful stratum, not perfectly matched
  hardware or a confidence interval.
- A discarded initial run exposed intentionally failing compiler capability
  probes. The corrected suite records their CPU cost and relies on Cargo's
  actual success status; no pilot samples enter these results.

## Evidence and next priority

New successful [run 36771187101](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36771187101),
measured commit `0b2a6b532a954131fbc47b796211fa925c962a13`.
The product source remains the same as the prior IronRDP experiment.

See [full CPU/wall tables](COMPILER-RESULTS.md), [machine-readable results](COMPILER-RESULTS.json),
[suite workflow](../.github/workflows/compiler-validation.yml) and
[raw evidence archive](compiler-raw-36771187101.zip).
The original [native CI breakdown](REPORT.md) remains available.

To reproduce the aggregation from the archived evidence:

```powershell
Expand-Archive ci-benchmark\compiler-raw-36771187101.zip -DestinationPath compiler-evidence
python ci-benchmark\analyze_compiler.py compiler-evidence --output compiler-results
```

**Next investigations, ranked by likely impact and directness:**

1. **Qualify the Windows Arm64 bundle for a full Rust distribution:** the reusable
   fork package now saves 16% on the original native compilation sequence.
   Preserve static-LLVM relinking and real profile-coverage gates; broaden to
   all distributed tools and Arm64EC, and measure release-build time and memory.
   The experimental package is not a fully qualified official release.
2. **Separate PGO/ThinLTO contributions and extend the controlled test to x64:**
   ablate rustc PGO, LLVM PGO and both ThinLTO settings to find the best benefit
   versus compiler-build cost. Verify actual x64 training coverage, not just flags.
   Do not copy Linux's shared-LLVM configuration onto MSVC; bootstrap rejects it.
3. **Profile the remaining common-target gap:** sample rustc/LLVM execution and
   separate compiler phases on matched CPU strata. x64 configures PGO, but
   actual backend-training coverage should also be checked. Investigate hot passes, allocation and
   hardware throughput; Linux x64's BOLT is another controlled-build variable.

Native crypto/Opus build-script profiling remains a separate full-workspace track.
Cargo cache tuning may improve
CI latency, but it does not explain this isolated CPU gap.
