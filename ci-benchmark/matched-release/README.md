# Matched Rust release cost and IronRDP benefit

This new study replaces cross-version comparisons with actual full distribution
builds and downstream measurements of their resulting compilers. The
[protocol](protocol.json) is preregistered; amendments below are declared before
replacement runs, with every pilot excluded from final estimates.

Three configurations per native architecture share Rust commit
`ab0afc7ee6827da442070b034830b5d69a9b537c`, LLVM, clang-cl, SDK selection, full
distribution scope and four-logical-CPU standard GitHub runner class:

| Configuration | PGO | Native linking | LLVM / Rust cross-crate ThinLTO |
|---|---|---|---|
| Baseline | None | Microsoft link.exe / lib.exe | Off / off |
| MSVC retained | Fresh full opt-dist profiles | Same Microsoft tools | Off / off |
| LLVM option | Fresh full opt-dist profiles | lld-link / llvm-lib | On / on |

The baseline is an explicit no-PGO control, **not the existing shipped x64 PGO
recipe**. The study estimates the full cost of each optimization recipe against
that control; it must not be labelled the incremental change to today's x64
upstream release pipeline. Fresh profiles differ across production jobs, so
the LLVM contrast measures the complete recipe, not LTO in isolation.

The pilot runs one job per configuration/architecture. If all six complete,
the full study runs three independent cold build jobs per cell. Pilot results
are excluded. Hardware identity, tool hashes, full output manifest and all
failures are retained. No prior compiler-only timings fill missing cells.

The production timer includes helper construction, full tool/frontend/backend
PGO collection and full distribution assembly. All variants then run the same
extracted-distribution test suite. GitHub's actual job duration additionally
includes initial setup, runtime preparation, tests and uploads, and will be
reported separately from production time and queue wait. Upload duration
depends on retained evidence and is not a pure compiler cost.

Full distribution retains docs, tools, installer and Arm64EC where applicable.
No fresh-profile job consumes a previous job's profiles or cached LLVM. The
350-minute safety boundary permits diagnostics before GitHub's six-hour cap.
A timeout is an unfinished lower bound, never a successful completion time.
Any split-job alternative requires a declared protocol amendment and separate
elapsed-path/runner-time accounting.

The exact resulting distribution compilers will be compared on IronRDP's five
original native offline Cargo commands, using a common baseline Cargo/std
within each matched set. One warmup and three measured rounds run on each
benchmark VM, with compiler-order counterbalancing and original correctness
commands outside timing. These measurements cannot be borrowed from the old
source/version or the compiler-only study.

The requested final deliverable is a one-page Word comparison of full release
cost increases and IronRDP compilation savings, expressed against their stated
baselines. No document claiming completed measurements is produced before the
required datasets and qualification checks are available.

## Pilot repair, declared before replacement runs

[Pilot 38122240736](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38122240736)
failed all six cells. None supplies a completed release duration. The original
protocol used Rust `07bb50a774b11375032aacc16fd9a70f090f8642`.

The replacement uses short physical checkout, runtime and evidence roots on
every runner (`C:\mr` or `D:\mr`), not drive aliases that path canonicalization
can expand. Local native Arm64 reproductions confirmed that an existing
270-character archive path fails with Microsoft link.exe while the same archive
at 100 characters links, and that MSVC's relative header include fails with a
211-character source path but succeeds at 130 characters. The AWS-LC header
exists in the published dependency archive; this is not a missing dependency.
Cargo home, temporary files and qualification extraction also use the short root.

The Arm64 LLVM pilot independently failed on Rustdoc's DLL-data references.
Cargo passes `-Clinker-plugin-lto` when compiling ThinLTO dependencies; that mode
assumes static linking and omits Windows DLL-import annotations. Compiler-private
tools instead import data from `rustc_driver`. The new common Rust source
overrides that dependency mode with
`-Clinker-plugin-lto=no -Cembed-bitcode=yes` for MSVC-target compiler-private tools
and codegen backends at cross-crate-LTO stages. It does **not** disable Rust's
in-process ThinLTO. A three-crate atomic-static DLL reproducer fails before the
override, then links and runs after it. The exact added Rust regression fixtures
also link and run locally with both link.exe and lld-link and both Thin/FatLTO.

The source amendment applies to all cells; its conditional flags do not change
the no-cross-crate-LTO baseline/MSVC-PGO recipes. Full tools, docs, installer,
fresh profiles, correctness requirements and timing boundaries remain unchanged.
Local diagnostic successes are not substitutes for the replacement hosted pilot.
Downstream replays likewise use short physical workload, compiler, Cargo-home
and temporary roots uniformly across variants, before any benchmark pilot or
measured replay. No existing downstream timing is rescaled to account for paths.

[Replacement attempt 38133710688](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38133710688)
was stopped after x64 setup could not move the checkout from the workspace's
D: volume to the system C: volume. No production timing from that attempt is
accepted. The short root is now selected on the **workspace volume**, with an
atomic directory rename instead of a cross-volume PowerShell move. The same
rule applies to downstream benchmarks.

Pilot 38133940060 reached complete Arm64 baseline distribution assembly
(22 files, including the required components) in 6911.61 production seconds.
Qualification then passed 22,097 UI cases and failed one, E0152, solely because
its expected diagnostic normalizes paths under Rust's build root. The harness
had extracted the compiler outside that root. Extraction now uses upstream
opt-dist's `build/unpacked-dist` layout; neither the expected diagnostic nor the
test selection is changed. That pilot observation is not a qualified release-job
duration and remains excluded. Subsequent failed jobs preserve any distribution
files under explicitly **unqualified** artifact names, never as accepted inputs
to the downstream benchmark.

The MSVC-PGO pilot also completed production on both architectures: 13,700.72
seconds on x64 and 16,499.84 seconds on Arm64. Both hit the same E0152 harness
issue. Arm64 additionally failed `expr/if/expr-stack-overflow.rs` with
`0xc00000fd` (compiler stack overflow). This is a real qualification failure,
not just output normalization, and must not be waived or hidden by increasing
the qualification process's stack limit.

The retained earlier compiler-only Arm64 baseline and PGO compilers both pass
that exact source test locally; they used different profiles and are not proof
that the failed full-release compiler is sound. The failed pilot did not retain
its distribution archive, which is why subsequent failures now retain
unqualified binaries. A separate `experiment/matched-release-stack-diagnostic`
branch runs only Arm64/MSVC-PGO, rebuilding a compiler with the failed job's
hash-verified Rust/LLVM profiles, unchanged compiler source and matching native
tools. It preserves the compiler and PDBs, then runs the nested-expression test
with the default stack limit and a separate phase-tracing invocation. This
profile-reuse diagnostic is **not** a fresh release build or a timing sample,
does not produce `result.json`, and cannot feed the matched analysis.
Its source remains pinned to `a2bb36e3594a73a806ad9d2bf2694fcd977c3261`
independently of later release-recipe amendments.

## LLVM feasibility amendment

Both LLVM cells in pilot 38133940060 reached the global 350-minute safety
boundary without a distribution. On x64 the initial frontend training-tools
build was still incomplete. Arm64 completed the frontend stage in 14,414.18
seconds and was still constructing the backend-instrumented compiler. Neither
observation is a completed release duration, and neither establishes an
IronRDP benefit. Their censored durations cannot be substituted into a
percentage-cost comparison.

The revised opt-dist recipe disables LLVM ThinLTO on intermediate LLVM builds
that are discarded before distribution: initial frontend preparation, its
static-LLVM reuse during frontend PGO optimization, and backend instrumentation.
It retains static LLVM, the selected linkers/librarians, and the configured Rust
LTO throughout. The final distribution still enables LLVM ThinLTO for the LLVM
option. Baseline/MSVC-PGO already have LLVM ThinLTO disabled, so this does not
introduce a different native-tool choice there.

The unit regression covers static/shared LLVM, both Windows architectures and
full/fast training modes, including the absence of a final-distribution LTO
override. Hosted feasibility remains unproven: the dedicated
`experiment/matched-release-llvm-pilot` branch runs only the two LLVM pilot cells
to test the revised recipe while the independent Arm64 stack failure is
diagnosed. It does not replace the required qualified six-cell pilot or supply
measured samples. All final comparison cells must share the same source revision.
That two-cell feasibility run is
[38158053450](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38158053450),
pinned to Rust `29d50151dcdd6e5b885920bc535047b380006900`, before the MIR repair below.

## Default-stack MIR diagnosis and repair

[Diagnostic 38155374593](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38155374593)
reproduced the Arm64 overflow with both the original and phase-traced invocations.
The retained compiler archive has SHA-256
`b55e9c49be303b870ce74a50733d82313ed5f93fee767b1bce18c90839067756`.
After verifying source, parent profile hashes, native tools and archive identity,
the same compiler also failed locally at the unchanged default stack limit.

Phase tracing passes parsing and type checking. Native ARM64 unwinding locates
the failure in MIR construction, with `expr_into_dest` retaining two 1,744-byte
frames per nested `else if`: a scope wrapper and the expression itself. The
existing regression contains 5,205 arms. Reduced-stack tests of older compilers
were debugger controls only; they failed earlier in parsing and are not evidence
about this full-profile failure.

The common Rust source now handles scope wrappers separately from the large,
non-inlined expression dispatcher. Scope cleanup, coverage instrumentation and
block-context behavior are preserved, and no stack limit or test expectation is
relaxed. Native bootstrap type-checking and pinned formatting checks pass.
The `experiment/matched-release-repair-stack-diagnostic` branch explicitly
rebuilds this repaired source with the original profiles to check the failure
quickly. Its provenance marks the source/profile difference; it remains
unqualified and cannot supply a release or downstream timing. Success there
still requires new fresh-profile production and full qualification before any
measurement matrix is accepted.

The repaired compiler in
[diagnostic 38167588581](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38167588581)
passes both default-stack probes on the native hosted runner and also passes
locally, without a stack override. Its archive SHA-256 is
`b44fa872890b176b192be585996af00fc5e66a0acaaf7deff0c2dcefd8f698e5`.
Seven existing scope/drop and coverage fixture configurations emit byte-identical
MIR before and after the repair. The four executable configurations also pass
their runtime assertions, covering match-arm scopes and temporary destruction
under both abort and unwind panic strategies. The other three cover tail
expressions and branch coverage instrumentation.

With that diagnostic gate passed, `experiment/matched-release-msvc-pilot` runs
the four baseline/MSVC-retained full-release pilot cells on this common source
while LLVM feasibility is investigated separately. These jobs use fresh profiles
where applicable and the complete qualification suite. They remain excluded
pilots, not substitutes for the three-repetition measurement matrix.
