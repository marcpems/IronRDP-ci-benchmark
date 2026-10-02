# Windows x64 compiler optimization validation

## Scope fixed before measurement

Use Rust 1.94.1 at `e408947bfd200af42db322daf0fadfe7e26d3bd1`, the same Rust
LLVM 21.1.8 and rustc-perf revisions as the completed Arm64 experiment.
Build and evaluate natively on standard GitHub `windows-2025` runners, never
under x64 emulation on the local Arm64 machine. All writes stay in the user fork.

Windows x64 already configures both PGO stages. The treatment retains both and
adds LLVM ThinLTO and cross-crate Rust ThinLTO. Preserve x64's existing compiler
`codegen-units=1`; do not introduce unrelated compiler settings to chase parity.
Both Windows architectures should have effective frontend/backend PGO and both
ThinLTO modes, not necessarily identical architecture-specific release options.

Build two matched x64 packages: `pgo-control` (both PGO stages, no cross-crate
ThinLTO) and `optimized` (both PGO stages and both ThinLTO settings). Both use
the same native SDK, clang-cl 20.1.3, LLD and bitcode-capable librarian.
Both relink static LLVM for training and require nonzero X86TargetLowering
and InstCombine profile counters. This makes the matched contrast an additional
ThinLTO effect with effective PGO, not a claim about official x64 PGO coverage.
The official compiler remains the practical adoption reference.

Use byte-identical official native/WASM standard libraries in the evaluation
packages. Record compiler files, flags, actual LLVM profile use, profile hashes,
runner identity and build-stage wall times. Check native/WASM output and absence
of residual instrumentation before accepting an archive.

Evaluation will reuse the original IronRDP native command sequence and compiler
isolation suite: pinned product source, offline builds, original native Cargo
profiles, cold targets, one excluded warmup and three measured rounds on five
independent VMs, with paired compiler ordering. Capture process-tree CPU and
wall time; run original correctness commands outside the performance timers.
Freeze package hashes in the protocol before dispatching measurements. Do not
assume Arm64's 16% full-native or 18% graphics saving transfers to x64.

## Minimal upstream-facing scope

1. Release configuration: request `llvm.thin-lto=true`, `rust.lto=thin`, and
   compatible linker/librarian selection for Windows. Arm64 additionally enters
   the existing opt-dist PGO pipeline; x64 already does so.
2. [Static LLVM PGO patch](static-llvm-pgo.patch): keep shared-LLVM behavior;
   relink the training compiler against instrumented LLVM for static linkage.
3. [Bootstrap lookup patch](bootstrap-clang-runtime.patch): execute read-only
   clang runtime discovery during dry-run, required by the pinned bootstrap.

No rustc/LLVM implementation changes, new training corpus, allocator changes,
SDK replacement, disabled DIA support, or standalone LLVM tool pruning are
included. Runner setup, compiler-only packaging, profile evidence and benchmarks
are experiment infrastructure, not proposed upstream compiler changes.
Current upstream must be rechecked before submitting any patch; none is submitted
by this experiment. Full distribution and Arm64EC qualification remain separate.
