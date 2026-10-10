# Windows compiler optimization without changing native tools

## Question and scope

Can Rust and LLVM PGO, optionally combined with Rust-side ThinLTO, improve
IronRDP compilation while retaining clang-cl, Microsoft's link.exe and lib.exe?
The previous LLVM-ThinLTO review branch is preserved. The new Rust branch is
[`experiment/windows-msvc-pgo`](https://github.com/marcpems/rust-arm64-compiler-ab/tree/experiment/windows-msvc-pgo).

This study uses current Rust source, not the earlier Rust 1.94.1 experiments.
It is compiler-only: it does not qualify full tools, Arm64EC distribution
packaging, MSI generation, or an upstream six-hour release job.

## Preregistered comparisons

| Variant | rustc PGO | LLVM PGO | Rust LTO | LLVM LTO | Native linking tools |
|---|---|---|---|---|---|
| baseline | No | No | Existing thin-local | Off | link.exe / lib.exe |
| pgo | Yes | Yes | Existing thin-local | Off | Same binaries |
| pgo-rust-thin | Same profile | Same profile | Cross-crate ThinLTO | Off | Same binaries |

Clang-cl remains the C/C++ compiler in every variant. Tool hashes and SDK
versions must match within each architecture; mismatch rejects the comparison.
The benchmark uses identical Cargo, native standard libraries and WASM standard
libraries from the baseline package for every variant.

Fresh per-architecture profiles use Rust's upstream training crate lists, not
IronRDP. Rustc-profile collection, LLVM-profile collection and final builds are
separate jobs on standard `windows-2025` and `windows-11-arm` runners. This
avoids assuming that the entire experiment fits one six-hour job, but repeats
some compilation. Summed runner time is not the same as workflow elapsed time.

After the toolchains are available, five independent VMs per architecture run
one warmup and three measured rounds, with counterbalanced compiler order.
The primary endpoint is the original five-command offline native compilation
total. Original native tests run outside timing; common-package and WASM
compilation remain secondary controls. See [protocol.json](protocol.json).

## Options being distinguished

* PGO does not inherently require a replacement linker.
* Rust-side ThinLTO happens inside rustc before native objects reach link.exe.
* LLVM-side ThinLTO emits LLVM bitcode which link.exe cannot consume directly.
* MSVC `/GL` plus `/LTCG` works on MSVC intermediate objects. It is not a flag
  substitution for clang-cl's LLVM bitcode. Building LLVM with cl.exe would
  change the compiler and require a different PGO pipeline, outside this study.

Small native compatibility probes check ordinary clang-cl objects, LLVM
ThinLTO objects with and without `/LTCG`, and cl.exe `/GL` objects. These probes
are not compiler-performance measurements.

## Results

**x64: fresh rustc and LLVM PGO reduced native offline Cargo wall time by
18.98% (paired 95% bootstrap interval 15.78% to 21.55%) while retaining
clang-cl, link.exe and lib.exe. Adding Rust-side ThinLTO did not demonstrate
an additional benefit.**

All five VMs in replacement
[run 38056790312](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38056790312)
passed. The complete dataset contains 420 compilation commands: 105 excluded
warmup commands and 315 measured commands, plus 60 original correctness
commands outside timing. The native primary endpoint uses the first five
compile commands; common-package and WASM builds are secondary controls.

| x64 variant | Native wall (s) | Native CPU (s) | Wall reduction vs baseline |
|---|---:|---:|---:|
| Baseline | 786.91 | 2914.24 | Reference |
| PGO | 637.54 | 2346.16 | 18.98% |
| PGO + Rust-side ThinLTO | 640.89 | 2355.11 | 18.56% |

PGO saved **149.37 seconds** per native compilation replay and **19.49% CPU**
(95% interval 17.25% to 21.78%). ThinLTO's incremental wall-time reduction
was **-0.53%**, with an interval from **-3.67% to +2.40%**: the point estimate
is slightly slower, but these data do not establish either an incremental
improvement or a regression.

The [detailed x64 report](x64/RESULTS.md) includes every Cargo command's wall
and CPU time, uncertainty intervals, and compiler construction/training costs.
[Machine-readable results](x64/results.json) retain the five paired VM means,
compiler metadata, profile hashes, and construction provenance.

### Runner variability

These were standard hosted `windows-2025` machines, not a homogeneous dedicated
CPU pool. All reported four logical CPUs and two physical cores, with the same
image and native-tool identities. Their reported CPU models differed:

| VM | Reported CPU | Baseline native (s) | PGO (s) | PGO + Rust ThinLTO (s) |
|---|---|---:|---:|---:|
| 1 | AMD EPYC 7763 | 1086.72 | 840.09 | 822.01 |
| 2 | AMD EPYC 9V45 | 653.43 | 530.12 | 549.59 |
| 3 | AMD EPYC 9V74 | 811.06 | 658.33 | 682.91 |
| 4 | AMD EPYC 9V45 | 627.75 | 507.58 | 525.47 |
| 5 | Intel Xeon 6973P-C | 755.57 | 651.58 | 624.48 |

Each cell is the mean of three measured rounds. Every VM ran every compiler;
PGO improved its paired mean on all five. Hardware heterogeneity is an observed
source of non-comparability between independent machines, not a proven
explanation for every timing difference. Do not compare unmatched pilot and
full-study absolute times as an optimization effect. Uncertainty resamples
whole paired VMs; five VMs still provide limited coverage of the hosted pool.
The [runner hardware record](x64/runner-hardware.json) preserves the reported
hardware and image identity from each VM's benchmark metadata.

### Arm64 status

All three final Arm64 compilers succeeded in
[run 38056115559](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38056115559).
The [Arm64 pilot](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38060313028)
passed all 21 compilation and 12 serial correctness commands. Its native wall
totals were 724.62 seconds baseline, 569.67 with PGO, and 561.44 with PGO plus
Rust-side ThinLTO. These are **one-VM, one-round feasibility observations**,
not final Arm64 estimates and not a matched architecture comparison.
The [full five-VM Arm64 study](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38063669491)
is running separately; its results are not yet included.

### Qualification and excluded data

The first full x64 study (38029169738) is excluded in its entirety: one VM
failed an original filesystem test with `STATUS_DELETE_PENDING`. A separate
600-run diagnostic found one parallel PGO-only failure in a different
filesystem-notification assertion and no failures in 300 serial runs. This
does not reproduce the exact original failure or prove its root cause.

Protocol schema 2 makes correctness test harnesses serial for every compiler,
outside measured commands. No tests are removed, ignored or retried; timed
compilation stays unchanged and four-way parallel. This is a uniform control
for the replacement study, not proof of release correctness under every
concurrency pattern. All five VMs are repeated; successful VMs from the
incomplete attempt are not substituted into the replacement dataset.

The original x64 pilot
[38025384632](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38025384632)
is also excluded. Its x64 job succeeded, but the overall workflow failed
because a matrix include appended an unintended Arm64 job; that matrix bug
was corrected before the full study.

There is a remaining x64 runtime-provenance limitation: its backend training
predates the bootstrap runtime search-path repair and PDB provenance audit.
The recorded standalone Clang profiling-library hash does **not** prove which
library was embedded in that training compiler. Successful training, matching
final runtime sources, and identical final PGO profiles are verified; the
unrecorded embedded-library identity is not.

The measured Rust source is `5b615ab3eb2cd5a26afc6025b5863180ffdc20d7` plus
recorded source patches. The later
[consolidated experimental commit](https://github.com/marcpems/rust-arm64-compiler-ab/commit/07bb50a774b11375032aacc16fd9a70f090f8642)
preserves the Arm64 bootstrap fix, exact runtime patch and manual reproduction
instructions; it is not the commit identified by the benchmark binaries.
The original LLVM-ThinLTO review branch is unchanged. Full distribution
automation and release qualification remain incomplete.

The analyzer requires both architectures by default. Analyze these independently
scheduled datasets with `--architecture x64` or `--architecture arm64`; each
scope still requires all five VMs, all paired rounds, and one complete workflow
attempt. Pilot data, mismatched artifacts and incomplete matrices are rejected.
Construction inputs follow recorded parent-metadata hashes and unchanged
profile bytes, and must match the exact benchmark compiler metadata.

### Prioritized next work

1. Prioritize PGO with Microsoft linking tools. It is the demonstrated x64
   improvement; requalify the x64 backend runtime provenance before proposing
   a production rollout.
2. Complete the paired Arm64 study before choosing a common optimization policy
   or claiming an architecture-specific ThinLTO effect.
3. Keep Rust-side ThinLTO optional. The x64 final bootstrap took 59.12 minutes
   versus 43.06 for PGO alone (one construction run each), without demonstrated
   workload benefit. Its extra construction cost is not an IronRDP CI speedup.
4. Resolve the original parallel filesystem-test failure, then qualify full
   tools, distribution packaging and release CI. Serial correctness checks in
   this experiment do not replace that work.

## Compatibility and earlier setup diagnostics

The initial x64 compatibility probes completed:

| Input objects | Microsoft link.exe | Result |
|---|---|---|
| clang-cl native objects | Ordinary linking | Linked and executed successfully |
| clang-cl ThinLTO bitcode | Ordinary linking | Rejected as invalid/corrupt input |
| clang-cl ThinLTO bitcode | `/LTCG` | Rejected as invalid/corrupt input |
| cl.exe `/GL` objects | `/LTCG` | Linked and executed successfully |

These are format/compatibility results, not compiler-speed results.
[Evidence: initial x64 baseline job](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/37948218037/job/113879940009).
That run subsequently failed before compiler construction because the Rust
checkout was nested inside the harness's Cargo workspace. The corrected run
uses sibling checkouts. A short intermediate run was cancelled before expensive
training to include the already-known, dependency-preserving training lockfile
migration. Neither setup attempt contributes to performance measurements.

The next attempt exposed bootstrap splitting a space-containing absolute
linker path in `RUSTFLAGS`. The harness now selects `link.exe` from the
verified native MSVC environment, retaining the same executable rather than
changing linkers. CMake's linker and librarian identities are also checked.

In [run 37949623212](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/37949623212),
the Arm64 instrumented-rustc bootstrap command completed in 49.86 minutes,
but the post-build audit rejected CMake's linker identity before PGO training.
This is **not** a valid same-tools result; the remaining jobs were cancelled.
A local Arm64 reproduction showed that CMake discovers `lld-link.exe` and
`llvm-lib.exe` next to clang-cl even when Microsoft tools precede them on PATH.
The harness now supplies a `CMAKE_TOOLCHAIN_FILE` pinning both Microsoft tools
for every CMake invocation, including the build of the shipped rust-lld.
Every phase first configures, builds and runs a small CMake fixture and checks
tool hashes before starting the expensive bootstrap build. Final audits check
both LLVM and rust-lld CMake caches. A native local Arm64 fixture with Clang
20.1.3 and CMake 4.4.3 passed; CI must repeat it with the experiment's Clang
22.1.8. Local fixture timing is not part of the performance study.

[Run 37957091081](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/37957091081)
passed the Arm64 native-tool audits and completed the instrumented compiler
build in 49.74 minutes. Training then failed because `cargo run --bin collector`
had not built the separate `rustc-fake.exe` helper. The harness now explicitly
builds all collector binaries and verifies their presence before training;
native Arm64 local execution confirmed the helper can launch stage0 rustc.
Both baseline jobs independently failed building the optional profiler runtime
for bare WASM (`errno.h` unavailable). The configuration now disables that
runtime only for `wasm32-unknown-unknown`, retaining native profiler support.
No training crates, workload commands or optimization treatments were removed.
Collector-build time is recorded separately from profile collection.

An unsuccessful build will be reported as a failure, not as a zero improvement
or a successful optimized toolchain.

## Sources

* [MSVC LTCG](https://learn.microsoft.com/en-us/cpp/build/reference/ltcg-link-time-code-generation)
* [LLVM ThinLTO](https://clang.llvm.org/docs/ThinLTO.html)
* [Original review branch](https://github.com/marcpems/rust-arm64-compiler-ab/tree/review/windows-pgo-thinlto)
