# Matched Rust release cost and IronRDP benefit

This new study replaces cross-version comparisons with actual full distribution
builds and downstream measurements of their resulting compilers. The
[protocol](protocol.json) is preregistered; amendments below are declared before
replacement runs, with every pilot excluded from final estimates.

Three configurations per native architecture share Rust commit
`7db17d9b5bbe6b16be2dc86b4bfae81d6e1ae238`, LLVM, clang-cl, SDK selection, full
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

## Fresh-profile qualification outcome

Run 38172717639 passes complete baseline qualification on both architectures.
The x64 baseline takes 9,308.65 seconds for production and 11,065 seconds for
the complete job; Arm64 takes 6,947.20 and 9,389 seconds respectively. These
remain single excluded pilot observations, not population estimates.

Arm64 MSVC-PGO completes production in 16,118.67 seconds, but its fresh profiles
expose another overflow in the same nested-expression regression. The other
22,097 UI cases pass. The actual unqualified compiler archive
(`rustc-nightly-aarch64-pc-windows-msvc.tar.xz`, SHA-256
`7d26046aca16a6d3fa17800758fede8e99b41f4060fd814d0bf52c5915140bae`)
reproduces locally. Native unwinding shows a 2,880-byte general expression frame
plus a 400-byte scope wrapper per nested arm. The scope-only repair is therefore
insufficient, despite passing its original-profile diagnostic.

The follow-up source also separates `if` lowering from the large dispatcher.
The new diagnostic consumes the fresh failing profiles from run 38172717639,
whose parent source is `ab0afc7ee6827da442070b034830b5d69a9b537c`. Original
diagnostic runs remain pinned to their historical workflow commits; no old
success is reclassified as fresh-profile qualification.

The x64 MSVC-PGO pilot times out during final distribution assembly. Both LLVM
pilots in run 38158053450 also time out, despite reaching final production:
x64 is still linking LLVM tools and Arm64 is building Rustdoc. All three hit
the 350-minute safety boundary; they are unfinished observations, not completed
costs. GitHub's six-hour hosted-job limit cannot be extended by setting a larger
workflow timeout. A multi-job recipe and explicit elapsed-pipeline/total-runner
accounting are required before replacement production measurements.

## Separate self-hosted Arm64 experiment

At the user's request, `MARCPE-D4-Arm64` was validated through an actual
Actions job before scheduling releases. This is not the local CLI computer
(`MARCPE-C2-1`); no local SDK installation paths are assumed. The preflight
checks native MSVC/SDK linking, builds the Rust MIR compiler component, and
compiles the pinned IronRDP core library and runs its native TLS integration
tests. A Cargo success with no compiled artifacts or no executed tests is
rejected; `ironrdp-core` itself disables unit-test targets.

[Preflight 38224862582](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38224862582)
passes all these checks, including the native TLS integration test. Bootstrap
explicitly selects `aarch64-pc-windows-msvc`; autodetection previously selected
an existing GNU toolchain. The recorded runner CPU is NVIDIA RTX Spark N1X,
with 20 cores and 20 logical processors. Neither earlier validation attempt
alone established the complete gate: one selected the wrong Rust host and
the other used a no-op Cargo test target.

With that gate passed, `experiment/matched-release-selfhost-arm64-pilot`
selects only native self-hosted Arm64 jobs, serializing the baseline,
Microsoft-retained PGO and LLVM-option full releases on that machine. Every
cell has a new physical source, Cargo-home, runtime and temporary directory;
compiler/profile caches are not shared. The existing four-CPU process affinity
and four build jobs remain in effect. Actual CPU identity/count, runner name
and native-tool hashes are retained. The self-hosted deadline is 530 minutes,
leaving ten minutes for evidence upload before a 540-minute workflow timeout.
Hosted jobs remain at their original 350/360-minute limits.

[Pilot 38225557840](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38225557840)
was launched from harness `16468b3a87f03946b19d0f81f0064b3082a99fc0`, with
Rust `7db17d9b5bbe6b16be2dc86b4bfae81d6e1ae238`. Its first job was confirmed
executing on the intended runner. Launch is not successful release qualification.

Self-hosted evidence explicitly records `runner_class=self-hosted-arm64`.
The hosted-study analyzer rejects it: these times must be reported as a separate
machine-specific comparison, never combined with hosted x64 or Arm64 samples.
Neither preflight nor a diagnostic reused-profile success qualifies a full
release; fresh training and the complete distribution checks remain required.

## Separate self-hosted x64 experiment

The subsequently registered `MARCPE-TEST01-X64` runner uses the same preflight,
now shared in `matched-selfhost.yml` and `validate_selfhost.py`. The
`experiment/matched-x64-selfhost-validate` branch selects native x64 Python,
MSVC and an explicitly pinned `x86_64-pc-windows-msvc` bootstrap host.
The same real compilation and executed-test gates apply.

After validation, `experiment/matched-release-selfhost-x64-pilot` selects
only the three x64 full-release variants, with the same fresh directories,
four-CPU affinity and 530/540-minute safety/job limits as the Arm64 experiment.
Its concurrency group is separate from Arm64, so the machines can work
independently while serializing jobs on each machine. Evidence identifies
`runner_class=self-hosted-x64`, and the hosted analyzer rejects it.
Existing Arm64 runs remain pinned to their original workflow revisions.

[x64 preflight 38230661502](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38230661502)
passes the native executable, compiler-component and IronRDP compile/test gates.
The machine records an Intel Core i9-11900, eight cores and 16 logical
processors, MSVC 14.44.35207 and Windows SDK 10.0.26100.0. The native bootstrap
reports `x86_64-pc-windows-msvc`.
[x64 pilot 38231778023](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38231778023)
was then launched from harness `a304bc7f5bfd07fa3bdc9a301da0b42ed8d1c9b6`
with the same Rust source pin as the Arm64 pilot. These are separate-machine
feasibility runs, not a controlled comparison of processor architectures.

The first x64 pilot fails during runtime preparation, before Rust production:
MSVC's approved `vctip.exe` descendant reports an 8.3 executable path, which
did not match the long-path allowlist. Process accounting now canonicalizes
both sides, still allowing only the exact approved executable and counting
its CPU. Real Windows regression tests exercise a short-path child and reject
an unapproved child; no telemetry policy is changed on the persistent machine.

The later cells also expose a workflow interpolation error: a replica suffix
turned `$variantCode` into the undefined variable `$variantCode1`. Bracing the
PowerShell variable restores separate variant/replica roots; a regression
executes the rendered naming expression for all nine combinations. Existing
roots are not reused or deleted. The running Arm64 baseline is preserved,
but subsequent Arm64 variants need the corrected workflow before retrying.

## GB300 high-parallel Arm64 track

The user separately authorized `GB300-Arm64` with label `HighCoreCount` and
accepted a fixed 64-CPU configuration. The native preflight exercises an
actual 64-CPU Windows Job Object before releases are scheduled. The initial
preflight exposed that one legacy processor-group mask cannot cover the
requested CPUs. The high-core path uses `JobObjectGroupInformationEx` with
explicit masks across groups, reads back the kernel configuration, and runs a
probe on every selected CPU while requiring excluded CPUs to reject affinity
requests. The four-CPU measurement path keeps its original single-group policy.
The release branch `experiment/matched-release-selfhost-arm64-highcore-pilot`
selects only Arm64 and that label, with an additional exact runner-name gate.
Its concurrency group is independent of the four-CPU runs.

All three variants use 64 build workers and inherited 64-CPU process-tree
affinity, including runtime preparation, compiler construction and distribution
qualification. Cargo and standalone CMake build parallelism are explicitly 64;
LLVM permits two simultaneous link jobs. Variants run sequentially with fresh
directories so they do not contend with each other. The full distribution,
Arm64EC, compiler codegen settings, training workload and qualification tests
are unchanged. In particular, the pinned PGO collector retains its four Cargo
jobs and single frontend thread: training does not promise 64-way scaling.

Provenance identifies `self-hosted-arm64-highcore`, build/affinity/link limits
and training concurrency. These observations cannot enter the hosted analyzer
or be pooled with either four-CPU machine. Fresh qualified distributions and
separate downstream high-core IronRDP replays are still required before a
release-cost versus compilation-saving conclusion is possible.

[GB300 preflight 38247985162](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38247985162)
passes native compiler/SDK execution, the Rust compiler-component check and
IronRDP compilation/integration testing. Recorded CPU: Grace A02P, 72 cores
and 72 logical processors; MSVC 14.51.36231 and SDK 10.0.26100.0.
Windows exposes groups of 64 and eight processors. The affinity probe
successfully executes on all 64 selected group-zero CPUs and rejects every
one of the eight excluded group-one CPUs. The initial preflight's legacy
mask failure is not a hardware-capacity failure.

[GB300 pilot 38248685449](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38248685449)
was launched from harness `308cc96caf359fd76fc3c4c0eec945bbf0a901cb`,
using the common Rust source `7db17d9b5bbe6b16be2dc86b4bfae81d6e1ae238`.
These remain excluded feasibility pilots until full release qualification.

The first GB300 pilot exhausts D: during the LLVM portion of baseline
production, before any distribution is completed. The other two variants
then fail while downloading Actions. The user cleared space and authorized
a restart. Subsequent high-core jobs record starting capacity and require
at least 180 GiB (193.3 decimal GB) free before each variant as a safety floor,
not an upper bound on storage use. Retries use new run-specific directories,
never the failed partial build as a cold measurement.

The initial 200 GiB floor rejected a later reading of 206.2 decimal GB
(192.1 GiB). At the user's explicit request, it was lowered to 180 GiB to
proceed with the available space. This accepts greater disk-exhaustion risk;
each subsequent variant still checks remaining space, and retained build
directories are not silently removed.

## Standard self-hosted Arm64 baseline qualification

The baseline job in run 38225557840 passes full distribution qualification
on `MARCPE-D4-Arm64`, using Rust `7db17d9b5bbe6b16be2dc86b4bfae81d6e1ae238`.
Production takes 10,804.58 seconds; the complete job takes 16,677 seconds
(08:45:42 to 13:23:39 UTC). This is one excluded pilot, not a repeated estimate.
The production interval includes full distribution construction, not just
offline compiler CPU work.

The two subsequent optimized cells fail before building. The generic Arm64
labels allow one to land on the newly registered GB300, where the exact-name
gate correctly rejects it; the other hits the old directory interpolation
bug. The standard runner now has the additional `MatchedStandardArm64` label,
required by its validation and release workflows. The
`experiment/matched-release-selfhost-arm64-optimized-pilot` branch retries
only Microsoft-PGO and LLVM/ThinLTO with corrected routing and fresh roots,
preserving rather than rebuilding the qualified baseline.

## GB300 baseline utilization evidence

Run 38282254692 completes and qualifies its 64-CPU baseline. The production
interval is 8,309.48 seconds. Windows Job Object accounting reports
21,365.30 CPU-seconds, averaging 2.57 active CPUs over production despite
the verified 64-CPU affinity. This confirms the user's low-utilization
observation; configured worker count is not achieved average parallelism.

The production invocation in `build/metrics.json` lasts 8,244.14 seconds.
Summing its exclusive (child-excluded) step durations avoids double counting:
distribution assembly/packaging is 6,132.72 seconds (102.21 minutes, about
74% of production), tool construction 780.27 seconds, compiler/standard-library
steps 467.39 seconds, LLVM/LLD 254.05 seconds, documentation generation
465.53 seconds and vendoring 136.96 seconds. Remaining time includes bootstrap
startup and small orchestration steps. These categories are wall time, not
raw CPU time or purely offline compilation.

Within packaging, the combined distribution/MSI step takes 3,032.78 seconds
and the two documentation packaging steps take 2,564.49 seconds combined.
The completed logs therefore locate the dominant elapsed-time cost in
packaging/assembly rather than failure to select 64 compile workers.
They do not yet separate compression CPU from file I/O or other packaging
costs; changing the required distribution scope would invalidate this comparison.

## Recovery after nine-hour self-hosted limits

Both four-CPU x64 optimized jobs in run 38236237914 hit the 530-minute
safety boundary. Microsoft-PGO reached final Clippy construction; the LLVM
option was linking LLVM tools in its final PGO-use build. Neither result is
a completed release cost. Subsequent self-hosted jobs use a 1,440-minute
(24-hour) workflow budget and a 1,430-minute internal deadline, preserving
ten minutes for uploads. This is headroom, not an expected duration.
Hosted limits are unchanged.

The `selfhost-x64-optimized-pilot` and
`selfhost-arm64-highcore-optimized-pilot` branch suffixes restart only the
missing optimized variants. All training and build directories are fresh;
successful baselines remain separately identified pilot observations.
Recovery of historical baselines uses the separate
`matched-selfhost-recovery.yml` workflow (`experiment/matched-selfhost-reclaim`).
It validates the exact qualified source/run/runner identity and every archive
against the complete distribution manifest, moves the archives to the same
experiment's `retained-dist`, preserves bootstrap metrics, and removes only
that experiment's `r/build` subdirectory. Source, evidence and PGO profiles
remain. No failed build is reused as a cold build.

New successful self-hosted cells perform the same reclamation **after**
distribution/evidence uploads so the following variant can use the available
space. This maintenance is outside the recorded production interval but
inside whole-job wall time; the separate `*-maintenance` artifact records
its start/end and before/after free bytes. Whole-job comparisons must disclose
this added maintenance rather than attributing it to compiler production.
The 180 GiB high-core startup floor remains unchanged.

## Separate release-throughput investigation

The [local throughput report](../release-throughput/README.md) explains the
four-CPU utilization ceiling, breaks down completed hosted baseline jobs, and
records paired local LLVM-parallelism and installer-compression experiments.
Neither custom timing runner was used for those new experiments. Their
component speedups do not replace full-release or downstream compiler timings.
