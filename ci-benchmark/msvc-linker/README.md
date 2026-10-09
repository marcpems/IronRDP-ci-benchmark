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

Compiler build and IronRDP performance results are not yet available.
[The current compiler workflow](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/37949154663)
is generating the toolchains and profiles.

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

An unsuccessful build will be reported as a failure, not as a zero improvement
or a successful optimized toolchain.

## Sources

* [MSVC LTCG](https://learn.microsoft.com/en-us/cpp/build/reference/ltcg-link-time-code-generation)
* [LLVM ThinLTO](https://clang.llvm.org/docs/ThinLTO.html)
* [Original review branch](https://github.com/marcpems/rust-arm64-compiler-ab/tree/review/windows-pgo-thinlto)
