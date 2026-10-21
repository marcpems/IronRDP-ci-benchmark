# Windows breadth preparation — OS64766704

**Preparation, not broad-speedup evidence or a shipping recommendation.**
The ADO item remains Proposed. This branch was isolated from reporting commit
`e0941523`; no workflows, builds on shared runners, pushes or ADO edits were made.

The accepted existing result is the
[fresh IronRDP replay](../X64-PGO-FRESH-REPLAY.md): 18.019% lower offline wall time
(95% 14.958–20.842%) on five independent Windows VMs. It combines training repair
and native linking changes, adds no ThinLTO, and is not a generated-code runtime
or arbitrary-project guarantee. The selected shipping candidate is **unset**.
Failed profile-only run
[39584578532](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39584578532)
is not an eligible source. A replacement must independently complete qualification.

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
overrides. A real local Windows smoke runs two tiny Python processes and verifies
that the 64 MiB command's peak is not carried into the next fresh Job.
No Rust project was built: Rust/Cargo were unavailable on PATH. These tests
validate harness behavior, **not** the proposed corpus's Windows buildability.
The completed local check passed all 11 new tests plus three existing native
order/environment-control tests. A separate persisted meter smoke observed
73,068,544 versus 5,820,416 peak committed Job bytes for the allocation and empty
commands respectively; these values are diagnostic meter evidence, not Rust
performance. A second complete audit reproduced byte-identical JSON
(`efba3b3c321c86b279a0844cd0745eece22da1d0e33d3c8f7f5243d1a1074d9b`).

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
The local proposal did **not** execute these preparation commands.

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

Maintainer decisions, the causal comparison and reviewed static-LLVM repair are
still prerequisites. Runtime/code-size benchmarks and all regression thresholds
require explicit agreement; **no numeric acceptance thresholds are invented**.
Exact treated components and PGO configuration must be explicit: newer opt-dist
can also treat tools, so “PGO candidate” is not sufficiently precise.

1. Agree these roots/versions/features, overlap policy and correctness scope.
   Decide semantic-edit, runtime, binary-size and compatibility cases separately.
2. After a successful causal run and repair qualification, pin actual official,
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
