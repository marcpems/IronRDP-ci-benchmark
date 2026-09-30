# IronRDP / Rust compiler performance: combined findings

## Answer

**Yes: for the graphics workload, the Windows gap is predominantly CPU consumed
inside rustc, including its code-generation backend, rather than Cargo, external
linking or off-CPU waiting.** Approximately **99.3-99.6% of the additional
process-tree CPU time** on Windows is accounted for by rustc processes themselves.
This is evidence about compiler execution cost, **not proof of an LLVM-specific
defect** or attribution of every second in the full IronRDP workspace.

The earlier [whole-workspace experiment](REPORT.md) found Windows/Linux native
compile ratios of **1.82x on x64** and **1.69x on Arm64**. The new isolation suite
reproduces approximately **2.0x / 1.7x** on a meaningful subset and retains a
substantial gap when the same WASM target is compiled directly.

## Real-project validation

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
throughput remain possible explanations; LLVM self-profiling is the next
discriminating experiment, not a conclusion already established.

## Controls and limitations

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

**Prioritize compiler profiling on the common-target `yuv` replay**, followed by
an optimization/codegen A/B on matched CPU strata. Keep native crypto/Opus
build-script profiling as a separate track for full-workspace CI. Cargo cache
tuning may improve CI latency, but it does not explain this isolated CPU gap.
