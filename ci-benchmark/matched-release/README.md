# Matched Rust release cost and IronRDP benefit

This new study replaces cross-version comparisons with actual full distribution
builds and downstream measurements of their resulting compilers. The
[protocol](protocol.json) is fixed before pilot outcomes.

Three configurations per native architecture share Rust commit
`a2bb36e3594a73a806ad9d2bf2694fcd977c3261`, LLVM, clang-cl, SDK selection, full
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
