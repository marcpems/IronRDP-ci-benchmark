# IronRDP offline CI benchmark: native compilation breakdown

For the concise combined conclusion and compiler CPU validation, see
[COMBINED-REPORT.md](COMBINED-REPORT.md).

## Result

**The Windows slowdown is reproduced, but a universal 2x multiplier is not.**
The median complete native compile sequence takes **1.82x as long on Windows
x64** and **1.69x on Windows Arm64** as on the corresponding standard Linux
runner. Three independent runners were measured for each of four platforms;
all 12 jobs and all 84 measured Cargo commands succeeded.

- Fork: <https://github.com/marcpems/IronRDP-ci-benchmark>
- Successful run: <https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36764734498>
- Measured commit: `0208960a1b221c48567fe81b10436e549b9df25d`
- Product source parent: `0c5419eca6bf53563056ed252f537bca67862705`
- Toolchain: native-host Rust/Cargo **1.94.1**, LLVM **21.1.8**
- Run date: **2026-09-30**

Only the benchmark workflow and measurement scripts were added to the measured
commit. No product code, Cargo profile, feature configuration or dependency
lockfile was changed.

## 1. Detailed native test-compilation breakdown

Seconds below are **medians of three independent jobs per platform**. Each
command uses `--frozen`, `--timings`, and Cargo JSON output. Dependencies were
fetched before measurement. No test execution, linting, setup, downloads,
verification or uploads are included.

| Native component | Linux x64 | Windows x64 | W/L x64 | Linux Arm64 | Windows Arm64 | W/L Arm64 |
|---|---:|---:|---:|---:|---:|---:|
| Build xtask | 2.49 | 7.92 | 3.19x | 2.25 | 6.06 | 2.70x |
| Workspace test compilation | 432.21 | 790.08 | 1.83x | 326.28 | 543.04 | 1.66x |
| TLS native-tls test compilation | 10.86 | 17.40 | 1.60x | 9.28 | 16.54 | 1.78x |
| Gateway native-tls test compilation | 57.18 | 94.21 | 1.65x | 45.26 | 73.71 | 1.63x |
| Gateway native-tls + smartcard test compilation | 50.63 | 94.56 | 1.87x | 40.33 | 72.64 | 1.80x |
| **Complete native sequence** | **555.03** | **1008.89** | **1.82x** | **424.25** | **714.95** | **1.69x** |

The total is the median of per-job totals, **not the sum of command medians**.
This distinction matters particularly on Windows, where the median command
values do not all belong to the same replicate.

Measured commands, in order, sharing an initially empty native target directory:

```text
cargo build -p xtask
cargo test --workspace --no-run
cargo test -p ironrdp-tls --test native_tls --features native-tls --no-run
cargo test -p ironrdp-mstsgu --test http_auth --features native-tls --no-run
cargo test -p ironrdp-mstsgu --test http_auth --features native-tls,smartcard --no-run
```

These reproduce the underlying compile commands in
[`xtask/src/check.rs:236-254`](https://github.com/Devolutions/IronRDP/blob/0c5419eca6bf53563056ed252f537bca67862705/xtask/src/check.rs#L236-L254).
The small xtask executable's own execution is omitted; its compilation is
measured separately. This is an **offline cold-artifact baseline**, not a replay
of the original dependency-cached checks job.

### Which commands explain the extra time?

Arithmetic means are used here so excess seconds add correctly:

| Component | Windows x64 excess over Linux (s) | Share of x64 excess | Windows Arm64 excess over Linux (s) | Share of Arm64 excess |
|---|---:|---:|---:|---:|
| Workspace test compilation | 365.17 | 78.6% | 220.73 | 75.2% |
| Gateway native-tls | 40.63 | 8.7% | 28.54 | 9.7% |
| Gateway smartcard | 45.09 | 9.7% | 31.78 | 10.8% |
| TLS native-tls | 6.98 | 1.5% | 7.03 | 2.4% |
| xtask bootstrap | 6.53 | 1.4% | 5.41 | 1.8% |
| **Total mean native excess** | **464.40** | **100%** | **293.50** | **100%** |

Prioritize the main workspace build, then the two gateway feature variants.
The xtask multiplier looks large but its absolute opportunity is small.

### Rust compilation versus build scripts versus other work

Cargo HTML unit intervals were decoded and merged to produce **disjoint wall
time categories**. This avoids summing overlapping compiler processes.

Mean seconds across each platform's three complete native sequences:

| Disjoint wall interval | Linux x64 | Windows x64 | Linux Arm64 | Windows Arm64 |
|---|---:|---:|---:|---:|
| One or more compiler units active, no build script running | 413.82 | 706.34 | 333.98 | 472.94 |
| Compiler units and build-script execution overlap | 124.85 | 290.24 | 84.51 | 235.71 |
| Build scripts active with no compiler unit active | 0.00 | 0.00 | 0.00 | 0.00 |
| Outside all tracked units | 1.60 | 8.10 | 1.53 | 4.88 |
| **Total native process wall time** | **540.28** | **1004.68** | **420.03** | **713.53** |

**These are activity intervals, not a CPU-cost attribution.** A compiler unit
includes rustc startup, frontend/codegen, linking and waits. A running build
script may invoke C/assembly compilation, CMake or tool discovery. An overlapping
second cannot be uniquely assigned to either compiler work or a build script
from Cargo timings alone.

The small outside-unit residual means outer Cargo orchestration alone is not
the observed multi-minute gap. It does **not** prove that filesystem, security
scanning, native tool discovery or process waits inside compiler/build-script
units are negligible.

Cargo recorded high **system-wide** CPU utilization during workspace
compilation: Linux x64 96.3-96.7%, Windows x64 90.2-98.5%, Linux Arm64
94.7-94.9%, Windows Arm64 91.7-96.6%. This favors investigating expensive
compilation/native work before assuming mostly-idle Cargo scheduling. These are
not rustc-only CPU measurements; background activity and internal contention
remain possible.

### Longest individual workspace units

Median **unit elapsed seconds**; concurrent units overlap, so do not sum these
rows or treat their differences as independently recoverable wall time.

| Unit | Linux x64 | Windows x64 | Linux Arm64 | Windows Arm64 |
|---|---:|---:|---:|---:|
| `yuv` library | 121.56 | 240.87 | 66.31 | 107.70 |
| `aws-lc-sys` build-script execution, including native build | 87.70 | 172.83 | 59.25 | 119.49 |
| `ironrdp-testsuite-core` integration-test target | 91.73 | 170.61 | 74.05 | 108.86 |
| `ironrdp-testsuite-extra` integration-test target | 60.90 | 115.61 | 48.34 | 73.40 |
| `libopus_sys` build-script execution | 34.74 | 70.13 | 17.88 | 54.94 |
| `sspi` library | 38.96 | 71.62 | 27.75 | 44.11 |
| `windows` library, large API feature surface | not in top-unit set | 94.89 | not in top-unit set | 80.45 |
| `ironrdp-activex` library test target | not in top-unit set | 94.94 | not in top-unit set | 62.55 |

Windows x64 also has a particularly variable native tooling case:
`libopus_sys` build-script durations span **49.49-170.07 seconds**.
The fastest Windows x64 job nevertheless spends **76.95 seconds** in
`vswhom-sys`'s build script. These are leads for native build/tool discovery
profiling, not established root causes.

The report's `NATIVE-BREAKDOWN.md` includes the twelve individual samples, their
wall partitions and longest units. Its JSON companion includes grouped unit
durations, Cargo's partial frontend/codegen sections, fresh/compiled artifact
counts, and sole-active-unit intervals.

### Is the Windows graph simply larger?

**No, not by total executed unit count.** The workspace command executes:

| Platform | Tracked units | Workspace-origin units | Dependency-origin units |
|---|---:|---:|---:|
| Linux x64 | 741 | 105 | 636 |
| Windows x64 | 693 | 108 | 585 |
| Linux Arm64 | 739 | 105 | 634 |
| Windows Arm64 | 691 | 108 | 583 |

Windows has three more workspace-origin units, but fewer overall units because
the platform dependency graphs differ. Its Windows-only ActiveX/COM and API
bindings are meaningful extra work, while Linux builds other backends.
**The initial hypothesis that a larger Windows graph alone explains the gap is
not supported.** Unit count is not complexity-weighted, so it does not by itself
settle the issue in either direction.

### Why do the later gateway commands still take time?

They change feature and dependency contexts and really compile new units:

| Command | Linux x64 executed units | Windows x64 | Linux Arm64 | Windows Arm64 |
|---|---:|---:|---:|---:|
| TLS native-tls | 25 | 15 | 25 | 15 |
| Gateway native-tls | 119 | 123 | 122 | 123 |
| Gateway smartcard | 63 | 77 | 63 | 77 |

Examples from Windows Arm64 replicate 3:

- Gateway native-tls compiles `rustls` for **27.10 s**, `sspi` for **19.67 s**
  and `reqwest` for **13.15 s**.
- The following smartcard command compiles `picky` for **31.09 s**, `rustls`
  for **26.45 s**, and `sspi` for **19.64 s**.
- The artifact stream records **117 newly compiled / 155 fresh artifacts** in
  the gateway native-tls command and **74 newly compiled / 254 fresh** in the
  smartcard command. Artifact counts differ from unit counts because build
  script execution is a separate kind of work.
- `sspi` gains `scard` and `dns_resolver`; `tokio` and `picky` feature sets also
  expand. Even a crate showing the same direct features can rebuild when its
  dependency fingerprints differ. These variants must not be merged blindly:
  they intentionally exercise different configurations.

## 2. Shared-workload controls

Separately cold target directories were used for a shared core/PDU/graphics
test-compilation control and the upstream WASM compile command.

| Workload | Linux x64 median (s) | Windows x64 (s) | W/L | Linux Arm64 (s) | Windows Arm64 (s) | W/L |
|---|---:|---:|---:|---:|---:|---:|
| Common core/PDU/graphics packages | 62.54 | 112.28 | 1.80x | 43.62 | 68.24 | 1.56x |
| `ironrdp-web` WASM compilation only | 104.95 | 182.64 | 1.74x | 79.49 | 133.00 | 1.67x |

The slowdown persists without building the full Windows product. The common
control still has target-specific code generation/dependencies, and the WASM
build still uses native host build scripts/proc macros. These are useful
controls, not identical-hardware pure-OS experiments.

No `wasm2wat`, tests, Clippy, .NET builds or lock checks run inside these timers.
The three workloads are alternative measurements, **not three stages to add
together and call production CI build time**.

## 3. Runner variation and confidence

Native sequence totals, seconds:

| Replicate | Linux x64 | Windows x64 | Linux Arm64 | Windows Arm64 |
|---|---:|---:|---:|---:|
| 1 | 572.74 | 1231.04 | 424.25 | 746.69 |
| 2 | 493.07 | 1008.89 | 429.36 | 678.94 |
| 3 | 555.03 | 774.10 | 406.48 | 714.95 |

The x64 replicate-index ratios are 2.15x, 2.05x and 1.39x, but replicate
indices **do not identify matched hardware pairs**. This is why the headline
uses ratio-of-medians and reports all samples rather than a selected pair.
Three samples are a pilot; no tight confidence interval is justified.

All jobs had four logical CPUs and approximately 16 GB RAM. The actual hardware
and image labels were not homogeneous:

| Platform | CPU models observed | Runner label | Actual image versions |
|---|---|---|---|
| Linux x64 | AMD EPYC 7763 (replicates 1,3); Intel Xeon Platinum 8573C (2) | `ubuntu-24.04` | 20260927.320.1; 20260920.314.1 |
| Windows x64 | AMD EPYC 7763 (1); AMD EPYC 9V74 (2); Intel Xeon 6973P-C (3) | `windows-2025` | 20260922.246.2; 20260925.250.1 |
| Linux Arm64 | Neoverse-N2 | `ubuntu-24.04-arm` | 20260927.135.1 |
| Windows Arm64 | Cobalt 100 | `windows-11-arm` | 20260924.168.1; 20260920.164.1 |

x64 exposed two cores/four hardware threads; Arm64 exposed four cores/four
threads. Cross-architecture comparisons therefore measure hosted runner
offerings, not an isolated ISA effect. Both Windows labels resolved to VS2026
images. Every Rust compiler host matched its expected native architecture;
auxiliary compiler/linker executable architecture was not separately traced.

Windows image metadata initially appeared as null in the Python capture due to
case normalization in a copied environment dictionary. The exact image/version
values above were recovered from the saved setup-job logs, not inferred.
The collector is corrected on the results branch for future runs.

## 4. Compile time versus other CI activity

This benchmark's **whole job** deliberately includes extra diagnostic control
workloads. Its additive arithmetic-mean accounting is:

| Mean component (s) | Linux x64 | Windows x64 | Linux Arm64 | Windows Arm64 |
|---|---:|---:|---:|---:|
| Native sequence | 540.28 | 1004.68 | 420.03 | 713.53 |
| Shared-crate control | 60.73 | 110.87 | 43.28 | 69.41 |
| WASM compile control | 100.65 | 178.45 | 79.27 | 134.14 |
| Everything outside measured Cargo commands | 41.01 | 124.67 | 36.76 | 127.58 |
| **Whole benchmark job** | **742.67** | **1418.67** | **579.33** | **1044.67** |

The final outside-Cargo row includes checkout, toolchain/native dependencies,
fetch, metadata/feature-tree collection, evidence processing, verification,
upload, post steps and inter-step time. Job queue time is excluded.
Original step timestamps are retained in `fork-job-components.json`.

For context, the earlier five upstream cached x64 runs (August 30) averaged:

| Upstream component (s) | Linux | Windows |
|---|---:|---:|
| Native compile-labelled step | 137.6 | 358.8 |
| WASM compile **and verification** | 22.0 | 41.8 |
| Tests, Clippy, dependency/lock verification | 61.2 | 94.4 |
| Windows-only .NET host harness | 0.0 | 29.6 |
| Setup/cache/post/inter-step work | 45.0 | 82.0 |
| **Whole upstream checks job** | **265.8** | **606.6** |

Those upstream native-step medians were 149 s Linux and 372 s Windows, ratio
2.50x. They did not enforce offline mode, had unknown cache state, and used
different source revisions/images. They must not be merged with these fresh
cold-target results. Cache restoration can save time and alter the Windows/Linux
ratio; this investigation has not yet measured a controlled warm-cache matrix.

## 5. Prioritized plan to close the gap

| Priority | Experiment | Why it is high impact | Required evidence / decision |
|---|---|---|---|
| P0: establish repeatability | Extend to 5-10 independent samples per cell, recording CPU/image and alternating control order | Windows x64 totals span 774-1231 s, with different CPU families/images | Report stratified distributions; keep existing outliers, avoid claiming a universal 2x penalty |
| P1: main workspace hotspots | Profile `yuv`, large integration-test targets, daemon and Windows API/ActiveX compilation; A/B targeted dev optimization or dependency feature reductions | Workspace command explains 75-79% of native excess; shared controls retain much of the slowdown | Identify codegen/frontend/link contributions on the critical path; retain required features, binary compatibility and complete test coverage |
| P2: native build scripts | Trace `aws-lc-sys`, `libopus_sys`, `vswhom-sys`; record native compiler/linker paths, child CPU, CMake invocations and discovery times | Windows native builds are substantially slower; Opus and tool discovery show large variance | Check native tool architecture and jobserver/parallelism; distinguish actual compilation from discovery/scanning/waits before choosing fixes |
| P3: variant recompilation/cache effectiveness | Collect Cargo fingerprints and unit identities for the four test commands; measure a seeded dependency-cache run and no-change replay separately | Gateway feature variants account for another 18-21% of mean native excess and compile substantial repeated dependency work | Avoid redundant units while preserving distinct native-tls/smartcard tests; evaluate cache hit rate and added restore/save cost |
| P4: targeted linker/filesystem diagnosis | If P1/P2 traces show link or file-I/O bottlenecks, compare a supported linker/native toolchain or build-volume layout | Plausible Windows overhead, but not quantified by current Cargo intervals | Use WPR/ETW or equivalent traces, validate resources/symbols/ABI; do not globally disable Defender or assume its contribution |
| P5: other CI latency | Improve cache transfer, separate Windows-only .NET work or job structure only after build analysis | Helps full-job latency, not the requested offline Cargo metric | Report job critical path and runner-seconds separately; do not claim gains merely by moving work outside the timer |

Specific first A/B: on unchanged feature coverage, compare the baseline dev
`opt-level=1` with a targeted override for the measured heavy library/test
targets or `opt-level=0`. Capture excluded test-runtime effects separately:
faster compilation can mean slower tests. The repository already disables
debug information and incremental compilation in CI; neither is a new fix.

Do not promise that eliminating a 170-second unit saves 170 wall seconds:
many heavy units run concurrently. Use the dependency-unblocking graph and
process traces to quantify critical-path savings. Build-script execution
overlaps Rust compilation in every sample; even a native optimization may
primarily free CPU resources rather than shorten an isolated serial phase.

Acceptance for an optimization: repeat unchanged-source baseline and candidate
with balanced order on comparable runner strata; prefer a material median gain
(for example >=10%) with improvement larger than within-stratum variance, no
coverage/ABI regressions, no new work shifted to excluded setup, and reported
effects on all four platforms. The 10% threshold is an investigation decision
rule, not an achieved result.

## 6. Measurement boundaries and reproduction

- Public standard hosted runners; three separately provisioned jobs per
  platform. Rust/Cargo host versions were pinned and checked. Runner image
  labels are stable selectors, not immutable image contents.
- `cargo fetch --locked` and Rust/native dependency installation occur before
  timers; measured commands use both `--frozen` and `CARGO_NET_OFFLINE=true`.
  This prohibits Cargo fetching. It is not a network sandbox for arbitrary
  build scripts; no claim of OS-level zero network traffic is made.
- No restored target cache or compiler wrapper. Fresh native/common/WASM target
  directories, with native commands sharing artifacts only within their
  sequence. Source/page caches are warm after fetch; this is not a cold-disk test.
- `CARGO_BUILD_JOBS=4`, `CARGO_INCREMENTAL=0`,
  `CARGO_PROFILE_DEV_DEBUG=0`. Existing root profile/feature configuration is
  otherwise unchanged.
- Replicate 2 reverses workload order; this exposes some host warmup/order
  effects but is not a fully balanced crossover design.
- Timer encloses the Cargo process and wait only. Local output writing and
  Cargo HTML-timing generation are included; post-processing and Actions log
  streaming/upload are excluded.
- Native bootstrap is compile-only, not xtask execution. WASM has its own cold
  target, rather than reusing prior native host artifacts as upstream does.
- Cargo HTML data are pinned-format structured JSON decoded from the report,
  never executed as JavaScript. Interval rounding is approximately 10 ms.
  Stable frontend/codegen sections are incomplete, especially for binaries,
  and are not a reliable independent linker measurement.

One aggregation guard correctly detected different raw Cargo.lock hashes.
Verification against the immutable Git blob showed the difference was **only
LF versus CRLF checkout endings**:

```text
LF:   0dd7b71a6c0e0fe89fa21199af4eecbecabfc125c4b54d62453f63cb8b5a02f9
CRLF: 2d2191b7753c0f0a27c238d941a30fb91a8bf38c4b6f878d3f99104127a8067b
```

The post-processing fix accepts this difference only after verifying both hashes
against the pinned Git blob. It does not change raw measurements or suppress
arbitrary mismatches. All jobs' lockfile checks passed. Standard checkout line
endings remain a documented platform difference.

The measured branch is `ci/offline-cargo-benchmark`. The separate
`analysis/offline-cargo-results` branch contains this report, derived data,
analysis code and the post-processing/metadata fixes; it does not change the
already completed experiment. No upstream PR was opened and no upstream
repository setting was changed.

From a checkout containing the results branch:

```powershell
gh run download 36764734498 --repo marcpems/IronRDP-ci-benchmark --dir artifacts
python .github\scripts\offline_benchmark.py summarize artifacts --source .
python ci-benchmark\analyze_native.py --artifacts artifacts --source . --output native-breakdown
python -m unittest discover -s .github\scripts -p test_offline_benchmark.py
python -m unittest discover -s ci-benchmark -p test_analyze_native.py
```

Raw artifacts have 30-day retention on Actions. Local copies, raw run logs and
API metadata are retained under
`D:\copilot\IronRDP-benchmark\artifacts-36764734498` and
`D:\copilot\IronRDP-benchmark\evidence`. The complete collected artifact set is
also preserved in `raw-timings-36764734498.zip` alongside the derived results,
so analysis remains reproducible after Actions artifact expiration. To use that
archive instead of downloading:

```powershell
Expand-Archive ci-benchmark\raw-timings-36764734498.zip -DestinationPath archived-artifacts
python .github\scripts\offline_benchmark.py summarize archived-artifacts --source .
```

No second build run was needed for the post-processing corrections.

## References

- [Measured workflow](https://github.com/marcpems/IronRDP-ci-benchmark/blob/0208960a1b221c48567fe81b10436e549b9df25d/.github/workflows/offline-cargo-benchmark.yml)
- [Measurement implementation](https://github.com/marcpems/IronRDP-ci-benchmark/blob/0208960a1b221c48567fe81b10436e549b9df25d/.github/scripts/offline_benchmark.py)
- [Original checks CI](https://github.com/Devolutions/IronRDP/blob/0c5419eca6bf53563056ed252f537bca67862705/.github/workflows/ci.yml#L12-L159)
- [Native test commands](https://github.com/Devolutions/IronRDP/blob/0c5419eca6bf53563056ed252f537bca67862705/xtask/src/check.rs#L236-L276)
- [WASM check combines compile and verification](https://github.com/Devolutions/IronRDP/blob/0c5419eca6bf53563056ed252f537bca67862705/xtask/src/wasm.rs#L4-L34)
- [Windows ActiveX dependency features](https://github.com/Devolutions/IronRDP/blob/0c5419eca6bf53563056ed252f537bca67862705/crates/ironrdp-activex/Cargo.toml#L15-L72)
- [Optimization profiles](https://github.com/Devolutions/IronRDP/blob/0c5419eca6bf53563056ed252f537bca67862705/Cargo.toml#L184-L206)
- [Cargo 1.94 timing documentation](https://github.com/rust-lang/cargo/blob/rust-1.94.0/src/doc/src/reference/timings.md)
- [Cargo timing serialization/interval definitions](https://github.com/rust-lang/cargo/blob/rust-1.94.0/src/cargo/core/compiler/timings/report.rs)
- [Dependency cache defaults](https://github.com/Swatinem/rust-cache/tree/v2.9.1#cache-details)
- [Standard runner specifications](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
