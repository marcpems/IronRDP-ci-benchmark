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
Both use profiles from a compiler relinked against static instrumented LLVM
and require nonzero X86TargetLowering and InstCombine profile counters.
This makes the matched contrast an additional
ThinLTO effect with effective PGO, not a claim about official x64 PGO coverage.
The official compiler remains the practical adoption reference.

The PGO control completed on `windows-2025` in run **36946671654** (5h26m).
The concurrent all-in-one ThinLTO/training job exceeded its 350-minute limit
before completing Stage 1. No treatment artifact or performance sample from
that cancelled job is accepted. The replacement treatment build uses the
control's **identical, checksum-pinned frontend and LLVM profiles**, with the same
source, clang, MSVC and SDK. This avoids repeating training within one hosted-job
time limit and makes the ThinLTO contrast tighter. It is not a measurement of
fresh-profile optimized release production time.

The replacement treatment completed successfully in
[run 36973674727](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36973674727):
**3h49m total**, including **225.8 minutes** for its profile-use compiler build.
Archive contents, actual profile use, native/WASM smoke output and matching
control/treatment profiles and target libraries were verified. The opt-in
installer and both workload suites passed the four-job
[pilot 36995063052](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36995063052),
including all original native correctness commands for all three Windows variants.
Pilot samples are excluded. The full
[20-job run 37001433534](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/37001433534)
passed: original native compilation improves **23.7% wall / 24.6% CPU** against
official Rust, and **7.6% wall / 7.3% CPU** against the matched effective-PGO
control. The latter isolates added ThinLTO with identical profiles; the former
is a practical toolchain replacement, not proof of missing official PGO.
See [native results](X64-NATIVE-RESULTS.md),
[compiler-isolation results](X64-COMPILER-RESULTS.md), and the
[combined interpretation](COMBINED-REPORT.md#original-x64-ci-validation).
Immutable artifact checksums are in [the native protocol](x64-native-protocol.json)
and [the compiler protocol](x64-compiler-protocol.json).

Use byte-identical official native/WASM standard libraries in the evaluation
packages. Record compiler files, flags, actual LLVM profile use, profile hashes,
runner identity and build-stage wall times. Check native/WASM output and absence
of residual instrumentation before accepting an archive.

Evaluation reused the original IronRDP native command sequence and compiler
isolation suite: pinned product source, offline builds, original native Cargo
profiles, cold targets, one excluded warmup and three measured rounds on five
independent VMs, with paired compiler ordering. Capture process-tree CPU and
wall time; run original correctness commands outside the performance timers.
Package hashes were frozen in the protocols before dispatching measurements.
The measured x64 effects above replace estimates based on Arm64.

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
