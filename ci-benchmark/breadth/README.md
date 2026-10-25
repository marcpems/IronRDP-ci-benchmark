# Windows breadth preparation — OS64766704

## Paired wall-clock hypothesis test

The requested follow-up tests this hypothesis: **the PGO-improved Rust toolchain
that reduced IronRDP build time also reduces wall-clock compilation time across
the frozen broader corpus**. The base is actual official Rust 1.94.1; the test
is the exact qualified local Rust 1.94.1 compiler used in the earlier repeated
IronRDP replay, not the newer 1.101 candidate-only pilot below.

Both use the same official Cargo and byte-identical official standard libraries.
This tests transfer of the demonstrated toolchain-replacement improvement:
the local production recipe combines PGO training repair with native-linking
changes. Official Rust already includes upstream optimizations; the contrast
must not be described as "PGO enabled versus PGO disabled" or as an isolated
causal estimate of profile quality.

The [frozen paired protocol](paired-protocol.json) uses five independent hosted
Windows jobs per project, four CPU/worker slots per job, and adjacent base/test
pairs in counterbalanced order for every scenario. One warmup round is excluded
by design; three measured rounds are retained. Original correctness runs for
both compilers in every warmup scenario outside the compile clock, with explicit
coverage required before measured rows are accepted. Source identities are
verified and comment edits restored in every cell. Successful cell target
directories are removed only after evidence is recorded, outside timing, to
bound disk usage; evidence is never removed.

Per-cell estimates average the three repetitions within each machine before
computing base/test effects across machines. Each scenario family also gets
an equal-project geometric-mean ratio, so the largest project cannot dominate.
Bootstrap draws preserve base/test pairing and all scenarios within a project's
machine; machines for different projects are independently sampled because
those jobs use separate runner VMs. Intervals are pointwise, conditional on
these fixed compiler artifacts, not simultaneous guarantees or PGO retraining
uncertainty. There is no combined full-build/incremental headline and no
post-result corpus selection, failed-row removal or slow-sample trimming.

The [paired workflow](../../.github/workflows/breadth-paired.yml) is separate
from the custom-runner pilot and does not consume its machine.
[The completed report](PAIRED-BREADTH-REPORT.md) presents the hypothesis,
wall-clock findings and conclusion first, then correctness and a scope-limited
summary. All 15 VMs, 450 measured cells and 350 original correctness commands
passed. Equal-project wall-clock reductions were **4.56% for check, 9.45% for
debug and 14.32% for release**; incremental-family effects were inconclusive.
These paired 1.94.1 results supersede the lack of comparative evidence for that
recipe, not the separate limitations of the newer 1.101 candidate-only pilot.

## Earlier candidate-only preparation

**Preparation, not broad-speedup evidence or a shipping recommendation.**
The ADO item is Started as of 25 October 2026; progress is recorded in comments,
not by rewriting its acceptance criteria. This branch was isolated from reporting
commit `e0941523`. The original preparation launched no runner workloads;
the separately scoped custom-runner candidate matrix below has now executed.

## Current-source custom-runner pilot

The user authorized progressing with the completed custom-runner artifacts
without waiting for the separate hosted-runner feasibility experiment.
[`custom-candidate.json`](custom-candidate.json) pins the completed
[PR validation run 40170434889](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/40170434889),
its exact source plus prerequisite patch, result/manifest identities, and
rustc/Cargo/std archive hashes. The original build directory is read-only;
the pilot installs fresh copies of the validated components.

The [pilot workflow](../../.github/workflows/breadth-candidate-pilot.yml) uses
`MARCPE-TEST01-X64`, sixteen logical processors, isolated NTFS source/build/test
paths and the existing dedicated-runner concurrency guard. The initial fd
full-check, incremental no-op and incremental comment-edit passed in
[run 40185382041](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/40185382041),
including 125 unit and 88 integration tests in both debug and release per cell.
The workflow now covers all three frozen projects and all five scenarios below,
with one project at a time to avoid competing for the shared 16-slot machine.
Project failures do not cancel the other projects. Each cell retains the original
unfiltered correctness commands outside measurement; Alacritty additionally runs
its terminal no-default-features check. Nushell remains `nu-parser` only.
Each project has a separate fresh root, Cargo cache and named evidence artifact.
Dependencies are fetched and checksum-verified before offline commands;
official Cargo 1.99.1 and candidate rustc/rustdoc/standard libraries are explicit
and hashed. The original attempt using candidate Cargo 1.101 passed full-check
and all 125 unit tests, but integration tests could not find `fd.exe`: the pinned
fd helper assumes the old `debug/deps` test location, whereas Cargo stabilized a
new build layout in 1.100. The pilot uses pinned official Cargo 1.99.1 rather than
patching the workload, relocating test binaries or skipping tests. This is an
explicit common-tool choice, not a hidden fallback or a rustc codegen regression.
Actual successful Cargo JSON artifacts are reconciled with the current training
audit. Metadata preserves each project's feature flags rather than enabling
all workspace features. Failures and source-restoration evidence are retained.

This is **candidate-only correctness and harness validation**, not a paired
performance study or continuation of the old four-processor timing series.
The original 1.94.1 manifest below remains historical; the current candidate uses
a separate current-source corpus/audit. It also trains additional tools, so the
old LLVM-only treatment description does not apply. No accepted matched control
or exact-revision official compiler is currently pinned. In particular,
cancelled storage run 40036080644 has no qualified control distribution, and its
"control" label is a filesystem control, not a PGO treatment contrast.
Runtime throughput, code-size gates and a broad shipping decision remain outside
this initial pilot.

Local checks for the pilot:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = '.github\scripts'
python -m unittest test_breadth test_breadth_candidate_pilot test_breadth_candidate_report test_breadth_selectors -v
actionlint .github\workflows\breadth-candidate-pilot.yml
```

For a complete multi-project run, download all three `breadth-candidate-pilot-*`
artifacts into separate same-named subdirectories, then reproduce the compact
report:

```powershell
python .github\scripts\breadth_candidate_report.py `
  --evidence <download-root> --output <candidate-observations.json>
```

The report requires every selected project/scenario, identical frozen manifests
and installed tool hashes, matching cell evidence and the exact successful
original correctness commands. Missing/failed evidence is an error, not a partial
success report. It preserves every input file hash and distinguishes artifact
records from distinct packages. Comparative effects, confidence intervals and
aggregate weights are explicitly null: a single-candidate matrix cannot estimate
them. A complete candidate report still recommends **no-go for broad performance
or shipping qualification** until the external qualification gates are met.

### Completed candidate matrix and recommendation

[Run 40185924144](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/40185924144)
executed revision `230fb1df4ec02a7118447dc76f3131d3fd8ca97b` on 25 October 2026.
All **15 cells and 35 original correctness commands passed**, serialized on
`MARCPE-TEST01-X64` (8 physical cores, 16 logical processors). No hosted feasibility
result was needed. Project jobs took 6m27s (fd), 9m57s (Alacritty) and 13m51s
(Nushell); these include setup and correctness, not just measured compilation.

[Raw evidence](raw-40185924144.zip) contains all 276 captured files, including
stdout/stderr, source and tool identities, package inventories, measurements and
resolved artifact audits. Its SHA-256 is
`68670f899006561e0c6ab7574515ccf0ca650b6167f86598bf69da5430c59a4c`.
The [reproducible compact report](candidate-observations-40185924144.json) binds
each raw file by hash. Extract the archive and run the report command above to
reproduce it. Raw evidence is committed here, independent of Actions retention.

Single-run wall seconds, **not speedups or qualified comparative estimates**:

| Project | Check | Debug build | Release build | Incremental no-op | Comment edit |
|---|---:|---:|---:|---:|---:|
| fd | 5.892 | 8.740 | 27.787 | 0.161 | 1.635 |
| Alacritty workspace | 15.577 | 22.962 | 32.764 | 0.294 | 3.103 |
| Nushell `nu-parser` | 31.212 | 35.982 | 36.807 | 0.354 | 0.834 |

All no-op cells compiled zero artifacts; each comment edit compiled exactly one
artifact. The report also records command-tree CPU and fresh-Job peak committed
memory for every cell. There is no rustc-exclusive CPU or RSS claim.

fd ran 213 tests per debug/release command. Alacritty ran 259 workspace debug,
128 terminal no-default-feature and 258 workspace release tests, including
doctests. Nushell ran 258 tests per debug/release command; **two upstream-ignored
tests remain ignored**, `multi_test_parse_number` and `test_parse_any`. No new
filter or ignore was introduced. Thus "original correctness passed" does not
mean every upstream-ignored test was executed, nor that full Nushell or Alacritty
GUI behavior was validated.

Full-check observed/compiled distinct-package counts were 64 (fd), 130
(Alacritty) and 111 (Nushell), with exact backend/frontend training fixture-lock
overlap of 33/24, 63/53 and 42/35 respectively. These are not whole-lock or
artifact-record counts and do not prove dependency-disjointness.

**Recommendation: no-go for broad performance or shipping qualification; go only
for progressing this frozen candidate corpus to an approved paired study.**
The candidate passed the declared build and original-test coverage, but there
are no matched-control or official-comparator measurements, no independent-runner
effect estimates, and no runtime-throughput or code-size regression bounds.
No aggregate, confidence interval or maintainer-approved threshold is invented.

The exact candidate production recipe at `adfdd487` unconditionally trains and
requires five PGO profiles; it has no no-PGO control mode or dispatch parameter.
A matched control needs a separately implemented and qualified production path.
The actual [official nightly dated 2026-10-25](https://static.rust-lang.org/dist/2026-10-25/channel-rust-nightly.toml)
uses Rust `12433c307b5a497388ffe2f4e49dbf1ab8c71fa0`, not candidate
`4da678aada4683607acbd67a8da37a320c791f93`; treating it as a same-revision control
would confound source changes. Maintainer agreement on root-only holdout,
shipping treatment and runtime/size thresholds remains a prerequisite. No
training-corpus tuning was performed, and the ADO research item remains Started.

The accepted existing result is the
[fresh IronRDP replay](../X64-PGO-FRESH-REPLAY.md): 18.019% lower offline wall time
(95% 14.958–20.842%) on five independent Windows VMs. It combines training repair
and native linking changes, adds no ThinLTO, and is not a generated-code runtime
or arbitrary-project guarantee. The selected shipping candidate is **unset**.
The [historical profile-only comparison](https://github.com/marcpems/IronRDP-ci-benchmark/blob/experiment/x64-pgo-comparison/ci-benchmark/X64-PROFILE-ONLY.md)
has since completed with a 13.73% IronRDP-only result. It does not qualify the
current upstream candidate or demonstrate benefit on these held-out projects.
Failed profile-only run
[39584578532](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39584578532)
is not an eligible source. Candidate distributions for this study still need
explicit selection and qualification.

## Concrete candidate corpus

[`corpus.json`](corpus.json) pins Git revisions, exact lockfile bytes, package and
feature selection, source-edit locations, commands, correctness scope and proposed
weights. These are intentionally stable snapshots, not claims about current HEAD.

| Project | Pinned revision | Scope and role |
|---|---|---|
| [fd v10.2.0](https://github.com/sharkdp/fd/tree/b19136871310b01500b4f09eadd7387b8476be47) | `b19136871310b01500b4f09eadd7387b8476be47` | All features; Windows CLI and clap derive consumer; release fat LTO/CGU=1 |
| [Alacritty v0.15.1](https://github.com/alacritty/alacritty/tree/0c405d53e74ace2980fc5e6c6d5b710c144bc075) | `0c405d53e74ace2980fc5e6c6d5b710c144bc075` | Four-crate workspace; Windows desktop, local derive macro and graphics/terminal codegen |
| [Nushell 0.103.0](https://github.com/nushell/nushell/tree/c98642647878b4f66fb7e38388a3973071b0e27b) | `c98642647878b4f66fb7e38388a3973071b0e27b` | `nu-parser` only; parser/protocol types and rstest; not full shell/plugins |

For each project, the five proposed scenarios are fresh-target `check`, debug
`build`, release `build`, debug incremental no-op, and debug incremental
comment-only source edit. Thus the initial suite is **15 distinct cells**, not
five IronRDP commands replicated under new names. The latter two seed a fresh
target with the same compiler/environment outside timing. Comment-only edits
exercise compiler invalidation/reuse, not general semantic-edit performance.
Full and incremental scenarios are separate endpoints.

fd and Alacritty have **their own** release LTO settings. Preserve them and report
them; “no added ThinLTO” in the earlier compiler-production recipe does not mean
these application builds have no LTO. No artificial opt-level/CGU/debug overrides
are added by the new probe.

Windows-rs `5888c8c472ab9b35c3159c2912bb045dc3020a82` and image
`f337e27aadaae8b86484429bc6020fef8a019c95` are **reserves**, not runnable frozen
members: neither has a committed root Cargo.lock. Windows-rs was inspected
sparsely, not prepared as a complete workspace. Do not silently generate evolving
dependencies or add either to the aggregate. They need separately agreed features,
a complete checkout, frozen generated lock and renewed overlap audit.

## Training disjointness: root holdout only

The audit reads **Git blobs at Rust 1.94.1**, not the newer working checkout:

- Rust [`e408947bfd200af42db322daf0fadfe7e26d3bd1`](https://github.com/rust-lang/rust/blob/e408947bfd200af42db322daf0fadfe7e26d3bd1/src/build_helper/src/lib.rs).
- LLVM `00d23d10dc48c6bb9d57ba96d4a748d85d77d0c7`.
- rustc-perf [`c0301bc44d175b9b2c5442b25049475c39d7700c`](https://github.com/rust-lang/rustc-perf/tree/c0301bc44d175b9b2c5442b25049475c39d7700c/collector/compile-benchmarks).

Exact LLVM selectors (Debug/Opt, Full): **syn-2.0.101, cargo-0.87.1,
serde-1.0.219, ripgrep-14.1.1, regex-automata-0.4.8, clap_derive-4.5.32,
hyper-1.6.0**. Exact rustc selectors (Check/Debug/Opt, All):
**externs, ctfe-stress-5, cargo-0.87.1, token-stream-stress, match-stress,
tuple-stress, diesel-2.2.10, bitmaps-3.2.1, serde-1.0.219-new-solver**.
There are 15 distinct selected fixture directories. In particular, proposing
ripgrep, syn, serde or clap_derive as completely held-out benchmarks is incorrect.

[`training-audit.json`](training-audit.json) contains the complete machine-readable
intersections, source URLs, fixture manifests and lock hashes:

| Candidate lock | Packages in whole lock | Exact LLVM lock reuse | Exact rustc lock reuse | LLVM / rustc reused names |
|---|---:|---:|---:|---:|
| fd | 114 | 53 | 45 | 84 / 87 |
| Alacritty | 278 | 95 | 82 | 122 / 114 |
| Nushell workspace | 794 | 225 | 189 | 291 / 251 |

Exact identity means name, version, source and checksum agree. For example,
`memchr 2.7.4` and several `windows-sys` versions recur in all three lockfiles.
`proc-macro2 1.0.86` recurs for fd, and `quote 1.0.37` for the other two.
Name-only reuse additionally discloses different versions and copied training
roots lacking registry provenance.

**These are conservative lock intersections, not counts of actually compiled
Windows dependencies.** They include unused features, non-Windows/dev packages,
and, especially for `nu-parser`, unselected workspace packages. The
[collector](https://github.com/rust-lang/rustc-perf/blob/c0301bc44d175b9b2c5442b25049475c39d7700c/collector/src/compile/execute/mod.rs)
sets `RUSTC_REAL` to the instrumented training compiler for dependency builds too;
only profiling the final benchmark invocation does not establish transitive
holdout. A target/feature-resolved metadata and training-log audit remains needed.
Selectors describe intended training membership; this audit alone does not prove
every selected fixture actually contributed counters to an official profile.
The historical token-stream-stress lock-format migration preserved package
records, so it does not change these intersections.

The three selected roots are not selected training roots, but **none is proven
dependency-disjoint**. Maintainers must agree whether root holdout with explicit
dependency reuse satisfies the experiment. If strict transitive disjointness is
required, this proposal is blocked; do not relabel these projects or tune training
against them. Keep any tuning validation corpus separate.

Reproduce the audit (Python 3.11+, Git, no Cargo required):

```powershell
python .github\scripts\breadth_audit.py `
  --manifest ci-benchmark\breadth\corpus.json `
  --rust <rust-git-checkout-containing-the-pinned-commit> `
  --perf <clean-pinned-rustc-perf-checkout> `
  --corpus <parent-of-fd-alacritty-nushell-windows-rs-image-checkouts> `
  --output <new-audit.json>
```

Clone with `git -c core.autocrlf=false clone ...` and detach at each exact SHA.
The audit rejects changed revisions, dirty sources and changed pinned locks.
Sparse rustc-perf needs all 15 selected fixture directories. No submodule updates
or modifications in the shared Rust source checkout are necessary.

### Resolved dependency reconciliation

[`breadth_resolved_audit.py`](../../.github/scripts/breadth_resolved_audit.py)
adds an opt-in audit of captured Cargo metadata and, when available, Cargo JSON
artifact records. It keeps selected-root graph reachability, observed artifacts,
newly compiled artifacts and reused fresh artifacts separate. It pins input
hashes and reconciles identities against the frozen source lock and all pinned
training fixture locks, rather than comparing names or parsing opaque Cargo IDs.
Malformed, failed or incomplete artifact captures fail closed.

The 25 October fd metadata-only run selected **73 reachable packages including
the root**, with exact identity reuse of **33 LLVM fixture-lock packages and
24 rustc fixture-lock packages**. These differ from the original entire-lock
53/45 counts because reachability excludes unused locked packages. They are
still conservative resolution counts: dev edges, host build dependencies and
workspace feature unification are not a command's compilation-unit graph.
No compilation records were captured; observed/compiled scopes are **null**,
not zero. Neither set of counts proves actual contributions to training profiles,
dependency-disjointness, buildability or a performance benefit.

To reproduce from retained inputs, use the pinned rustc-perf checkout and a new
output path. `capture.json` identifies project/scenario/source/target, exact
selected root package IDs and the successful metadata command receipt, including
its declared `filter_platform`. Its tool identities and preparation-only status
are preserved. Hashes bind supplied bytes; they do not authenticate the receipt's
execution history.

```powershell
python .github\scripts\breadth_resolved_audit.py `
  --manifest ci-benchmark\breadth\corpus.json `
  --training-audit ci-benchmark\breadth\training-audit.json `
  --perf <pinned-rustc-perf-checkout> `
  --lock <pinned-fd-checkout>\Cargo.lock `
  --metadata <study-root>\input-preparation-20261025\metadata-complete.stdout `
  --capture <study-root>\input-preparation-20261025\capture.json `
  --resolved-only --output <new-audit.json>
```

`--resolved-only` is explicit and produces `resolved-not-observed`; missing
build evidence never silently becomes successful build evidence. For an eventual
qualified run, regenerate metadata with the accepted common Cargo and supply
the corresponding successful build capture rather than reusing these 1.93.0
input-preparation receipts.

For artifact mode, replace `--resolved-only` with `--messages <Cargo-JSON-stdout>`.
The capture must additionally contain the matching Cargo command and successful
exit status, for example:

```json
"cargo": {
  "command": ["cargo", "check", "--all-features", "--frozen", "--message-format=json", "--target", "x86_64-pc-windows-msvc"],
  "exit_code": 0
}
```

Record the actual scenario/project argument order. The metadata receipt needs
its `command`, `exit_code: 0` and declared `filter_platform`; preserve tool versions
and hashes too. Optional receipt source revision, lock hash, source status and
stdout hash are checked when supplied. Fresh artifacts are not new compilations,
and a package can have both fresh and newly compiled targets in the same capture.

## Smoke harness and validation

[`breadth_probe.py`](../../.github/scripts/breadth_probe.py) is a **single-cell,
non-qualifying smoke harness**, not an approved matrix runner or shipping gate.
It reuses `process_metrics.py` and native environment/telemetry helpers:

- Source revision, clean tracked/untracked tree, exact lock and executable hashes
  are required. Original source bytes are restored on success and failure.
- Cargo JSON must contain successful `build-finished`. Full/edit scenarios need
  rebuilt artifacts; no-op requires fresh artifacts and **zero** rebuilt ones.
  A successful no-op is never rejected just because nothing compiled.
- Fresh targets separate full scenarios. Incremental seeding and unfiltered
  correctness tests are separately logged outside the measured row.
- All tests run, not merely `--no-run`. fd's all-feature tests and Alacritty's
  terminal no-default-feature check follow the pinned CI choices; release tests
  are proposed additional checks. `nu-parser` tests do not validate the whole
  Nushell product. GUI behavior, runtime throughput and output size remain untested.
- A **fresh Windows Job per command** supplies actual peak committed Job memory
  and largest-process committed peak. This is not RSS. The old meter's shared-job
  peak is lifetime cumulative, so it must not be presented as a per-command peak
  or differenced. CPU is whole command-tree CPU, not rustc-exclusive CPU.
- Failures retain logs and a failed record; no slow samples are removed.

Focused validation:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = '.github\scripts'
python -m unittest test_breadth -v
```

The tests cover no-op artifact semantics, failed/missing Cargo completion,
lock identity distinctions, full/edit cache rejection, source restoration after
failure, correctness failure, existing target/output rejection and environment
overrides. Resolved-audit tests additionally cover selected-root reachability,
registry/Git/path identities, pinned training blobs, capture provenance and
resolved-only versus observed/fresh/compiled scopes. A real local Windows smoke
runs two tiny Python processes and verifies
that the 64 MiB command's peak is not carried into the next fresh Job.
No Rust project was built: Rust/Cargo were unavailable on PATH. These tests
validate harness behavior, **not** the proposed corpus's Windows buildability.
The completed local check passed all 11 new tests plus three existing native
order/environment-control tests. A separate persisted meter smoke observed
73,068,544 versus 5,820,416 peak committed Job bytes for the allocation and empty
commands respectively; these values are diagnostic meter evidence, not Rust
performance. A second complete audit reproduced byte-identical JSON
(`efba3b3c321c86b279a0844cd0745eece22da1d0e33d3c8f7f5243d1a1074d9b`).
On 25 October, the extended breadth suite and existing native probe suite passed
all **36 tests** together (`python -m unittest test_breadth test_native_ci_probe -v`).

Before a coordinated smoke, prepare offline dependencies **outside timing** in
a dedicated per-study Cargo home. With a vetted direct Cargo executable:

```powershell
$env:CARGO_HOME = '<study-root>\cargo-home'
# For each complete, clean, pinned checkout:
& '<common-cargo.exe>' fetch --locked --target x86_64-pc-windows-msvc
# Capture the selected target's dependency graph and each scenario's feature choice:
& '<common-cargo.exe>' tree --locked --offline --target x86_64-pc-windows-msvc `
  --edges normal,build,dev --all-features  # fd; use --workspace for Alacritty, -p nu-parser for Nushell
```

Archive the Cargo home/vendor source bundle, package checksums, graph outputs and
their SHA-256 manifest. Preserve `.cargo` configuration files and ensure inherited
user/ancestor config does not silently inject flags. Verify all frozen scenario
commands offline during a pilot; `fetch` success is not that verification.
No fetch, tool installation or artifact extraction belongs inside measurement.
The initial proposal did **not** execute these preparation commands. On
25 October, fd's exact pinned lock was fetched into a dedicated study Cargo home
and `metadata --locked --offline --format-version 1 --filter-platform
x86_64-pc-windows-msvc --all-features` completed with the source and lock unchanged.
Existing ARM64 Cargo/rustc 1.93.0 were used for this **input preparation only**;
they are not the study's x64 Rust 1.94.1 compilers. No workload was built or tested.
The first offline attempt failed on missing `anyhow`; a target-filtered fetch
then still left metadata needing `windows_aarch64_msvc 0.48.5`. An unfiltered
`fetch --locked` supplied the remaining manifests and the offline retry passed.
Both failed attempts are retained, not discarded. Thus target-filtered fetch
success alone must not be treated as complete metadata preparation.
Alacritty and Nushell have not yet received the equivalent preparation.
[`fd-input-preparation.json`](fd-input-preparation.json) pins the exact commands,
tool/executable identities, metadata hash and the 113 cached crate archives'
34,203,510-byte input inventory hash. All archives were matched against the exact
`Cargo.lock` checksums, with none missing or extra. Raw receipts, metadata and archive hashes
are retained under the recorded local study root, not remotely published.

Example single-cell invocation after qualified-artifact selection and coordination:

```powershell
python .github\scripts\breadth_probe.py `
  --manifest ci-benchmark\breadth\corpus.json --project fd --scenario incremental-noop `
  --source <clean-fd-checkout> --output <new-study-directory-outside-source> `
  --cargo <common-official-cargo.exe> --cargo-sha256 <exact-sha256> `
  --compiler <verified-rustc.exe> --compiler-sha256 <exact-sha256> `
  --rustdoc <explicit-correctness-rustdoc.exe> --rustdoc-sha256 <exact-sha256> `
  --non-qualifying-smoke
```

The probe never upgrades its output to qualified evidence. An eventual matrix
driver must also validate the complete distribution/provenance/profile hashes,
common Cargo and byte-identical std, native tools, meter self-tests, runner image,
CPU/storage conditions, trial ordering and complete matrix. Executable hashes
alone do not validate companion DLLs, std or profiles. Reuse the strict
[fresh replay validator](../analyze_x64_pgo_replay.py) patterns, but do **not**
feed these rows to its IronRDP-specific five-command summation.
The correctness rustdoc is explicit and hashed rather than silently selected from
PATH; agree whether it is candidate-built or common, and report that choice.
A common official rustdoc does not establish candidate codegen correctness of
doctests. Normal test binaries use the explicitly selected rustc.

## Proposed interpretation and next bounded execution

Maintainer decisions, accepted candidate artifacts and reviewed static-LLVM repair
are still prerequisites. The historical causal comparison is complete but is not
automatic qualification of the current source or this corpus.
Runtime/code-size benchmarks and all regression thresholds
require explicit agreement; **no numeric acceptance thresholds are invented**.
Exact treated components and PGO configuration must be explicit: newer opt-dist
can also treat tools, so “PGO candidate” is not sufficiently precise.

1. Agree these roots/versions/features, overlap policy and correctness scope.
   Decide semantic-edit, runtime, binary-size and compatibility cases separately.
2. After candidate selection and repair qualification, pin actual official,
   same-revision control and candidate distributions, profiles and provenance;
   validate common Cargo/std and native tooling. Preserve failed attempts.
3. Prepare/freeze dependency inputs and reconcile target-resolved overlap.
4. Coordinate **one new standard x64 VM**, initially fd full-check and both
   incremental scenarios for each qualified variant, one round and unfiltered
   correctness. Stop on failures; this is a harness pilot, not confidence evidence.
   No shared x64/Arm64/GB300 runner should be occupied by this preparation.
5. Only after pilot/maintainer approval, run the preregistered independent-VM
   matrix. Report every project/scenario/contrast, including regressions. Average
   rounds within VM; use equal-project geometric-mean ratios separately in each
   of the five scenario families, with paired whole-VM bootstrap intervals.
   Do not pool repeated rounds as independent machines, trim slow samples, sum
   full and incremental times, or let the largest workspace dominate weighting.
6. Investigate material regressions before changing the corpus/training. A broad
   go/no-go needs actual correctness, runtime/size gates and quantified regressions
   accepted by maintainers; today's outcome is **no qualification decision**.
