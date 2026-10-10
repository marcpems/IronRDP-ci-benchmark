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

Audited Arm64 and x64 baseline compiler packages are now available from
[run 37965170591](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/37965170591).
Both architectures now have successful frontend PGO training. Arm64 required
two profiling-runtime repairs; [run 38001265175](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38001265175)
passed eight repeated online-merge checks and all nine frontend workloads.
x64 LLVM/backend training also succeeded in
[run 38009549235](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38009549235).
Arm64's rebuilt Clang runtime now passes hosted checks, but compiler bootstrap
then crashes while stage 1 compiles `yoke`. A diagnostic retry will preserve
that compiler. Independently, x64 is progressing to a fresh control and both
final optimized compiler builds. Diagnostic profiles from different runtime
revisions are not a matched performance comparison.
See [the runtime diagnostic report](RUNTIME-DIAGNOSTICS.md).
No optimized compiler comparison or IronRDP performance results are available.

[Run 38021536352](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38021536352)
successfully built and packaged all three x64 compiler variants, including
Rust-side ThinLTO with Microsoft linking tools. The x64 pilot now runs
independently while Arm64 remains under investigation. It is a one-VM,
one-round feasibility check, not the five-VM performance study. Runtime source
hashes must match across all final compiler variants in addition to the
existing source, native-tool, profile and archive checks.

The x64 pilot in
[run 38025384632](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38025384632)
completed all seven compilation commands and four original native test commands
for each compiler. Native totals were 1,063.93 seconds for baseline, 851.68 for
PGO, and 876.03 for PGO plus Rust ThinLTO. These are **one-VM, one-round pilot
observations**, not performance conclusions or evidence that ThinLTO helps.
The workflow was unsuccessful overall because an unconditional matrix include
accidentally appended an Arm64 job to the x64-only scope. Runner/host selection
now derives from each selected architecture without adding matrix cells.
The separate five-VM x64 study excludes these pilot measurements.

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
