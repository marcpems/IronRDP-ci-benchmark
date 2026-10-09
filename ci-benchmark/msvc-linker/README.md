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

Not yet available. Build, training, compatibility, and IronRDP results will be
reported only after the corresponding jobs complete. An unsuccessful build
will be reported as a failure, not as a zero improvement or a successful
optimized toolchain.

## Sources

* [MSVC LTCG](https://learn.microsoft.com/en-us/cpp/build/reference/ltcg-link-time-code-generation)
* [LLVM ThinLTO](https://clang.llvm.org/docs/ThinLTO.html)
* [Original review branch](https://github.com/marcpems/rust-arm64-compiler-ab/tree/review/windows-pgo-thinlto)
