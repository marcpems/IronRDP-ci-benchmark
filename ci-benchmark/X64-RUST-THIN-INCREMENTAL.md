# Incremental Rust-only ThinLTO: hosted pilot

This is a **limited experimental compiler/sysroot pilot**, not a qualified full
release or an actual rebuilt combined-PR shipped artifact. No performance result
exists until `thin-incremental-consumer-evidence/index.json` has `complete: true`.
Production receipts deliberately retain `complete: false`; `build_complete`
means only that the compiler package passed its build/audit/smoke gates.

## Fixed inputs and intervention

The adjacent JSON protocol pins Rust `4da678a`, LLVM `aab11ee`, rustc-perf
`208d929`, all five frozen profiles, the training provenance, and IronRDP
`0c5419e`. Training run **40170434889**, artifact **12593394360**, completed the
repaired full pipeline with 25,648 upstream extracted tests. We consume only its
profile bytes and evidence, **not its compiled objects or distribution**.
The exact previously qualified `builtins_locator.run_in_dry_run()` prerequisite
is common to both arms, checked against helper Git blob `6aa5fc0b`.
There are no new Rust source edits, runtime-search-path changes, stack changes,
DLL changes, or MIR/codegen patches.

Both arms build fresh stage2 rustc and native stdlib at the same `D:\ri\r` path.
Only `rust.lto = "thin-local"` versus `"thin"` changes. Rust CGU=1, Clang
20.1.3, Microsoft `link.exe`/`lib.exe`, LLVM ThinLTO=off, PGO profile bytes,
four-LP affinity and build workers remain fixed. Compiler caches are disabled:
hit rate is **N/A**, not an observed 0%. Each build includes ordinary bootstrap
stages, but no cross-arm compiler-object or LLVM archive reuse.
Rust #165138/sccache #2962 cache fixes are semantically irrelevant with no cache;
this measures the effective repaired-PGO condition, not cache throughput.

The hosted builds may have different MSVC/SDK binaries from the historical
profile producer. Both are rebuilt with matching current native tools, never
compared against the historical binary. The original profile producer's tool
identity remains in the receipts, and its Clang executable hashes must match.
The two builders and consumer must match MSVC/SDK versions, native tool hashes,
all INCLUDE/LIB file hashes, Microsoft tool DLLs, and hosted image version.
Any mismatch rejects the pair before timing.

## Deliberate pilot limitations

The pinned source's compiler-private tool LTO handling still uses Cargo profiles.
Rust #128947 proposes a workaround for Cargo #14575 plus increased compiler
stack size; enabling the config alone is not demonstrated to produce a qualified
full tool distribution. This pilot avoids those tools, **does not apply their
proposed patches**, and does not claim their tests passed. Default compiler
stack size remains unchanged; a stack failure is preserved rather than hidden.
Full-release qualification is a separate prerequisite for product conclusions.

Both packages retain their own newly built native stdlib; their complete native
library manifests must be identical. No stdlib transplantation is allowed.
The common Cargo is the pinned bootstrap stage0 Cargo, with identical hashes
required across builders. This packaging is experimental, not installation
guidance for users. Clippy, rustdoc, Cranelift and Cargo PGO profiles are retained
and verified as provenance but not used to build this compiler-only pilot.

## Endpoint and acceptance

One independently allocated hosted consumer VM runs native correctness
commands for both arms outside timing, then one warmup plus three measured rounds
in AB/BA/AB/BA order. Every block has a fresh target directory, shared only across
its original five commands:

1. `cargo build -p xtask`
2. `cargo test --workspace --no-run`
3. `cargo test -p ironrdp-tls --test native_tls --features native-tls --no-run`
4. `cargo test -p ironrdp-mstsgu --test http_auth --features native-tls --no-run`
5. `cargo test -p ironrdp-mstsgu --test http_auth --features native-tls,smartcard --no-run`

Timed commands append `--frozen --timings --message-format=json`, use offline
Cargo, disabled incrementality, dev debug=0, four workers and inherited four-LP
process-tree affinity. Dependencies are fetched beforehand. Primary endpoint:
sum of these five command wall times; process-tree CPU is secondary. It is not
application runtime. Correctness, fetch, setup, compiler production, packaging
and transfers are outside those totals, with separate receipts where measured.
Only successful commands, positive compiled-artifact counts, unchanged lockfile,
validated CPU meter, complete pair identities and all correctness gates permit
`complete: true`. Failures remain uploaded; no population confidence intervals
are claimed from this one-build-pair, one-consumer-VM pilot.
Correctness removes `--no-run`; the workspace command additionally selects
`--lib --bins --tests`. Doctests are explicitly excluded because this pilot has
no rustdoc. Feature-specific integration-test commands retain their original
target selection. This is native unit/integration qualification, not complete
IronRDP documentation or full compiler-distribution qualification.

## Resources and safety

Only standard `windows-2022` hosted x64 jobs run. There is no self-hosted job,
dispatch, cleanup or dependency on active sizing run **41054163612**; no use of
its `matched-x64-selfhost` lock or pending slot.

Prior hosted allocation run 39135351977 had 157,839,081,472 free bytes and 16 GiB
RAM. Its training completed in approximately 4h40, but whole-workspace archival
timed out. This design instead imports ~79 MB of existing profile evidence and
exports only compiler/sysroot packages. Fresh fixed-profile compiler-only builds
avoid retraining and full release tools/docs/MSI. The 305-minute absolute build
budget and six-hour jobs are bounded feasibility attempts, **not predicted
completion times**. A 90-GiB free-space gate rejects unsuitable allocations.
No heavy local build is required.

The branch-scoped push workflow starts two compiler jobs and a dependent consumer.
If resources, stack behavior, profile audit or identity checks fail, no benchmark
result is accepted. A resource-blocked retry must stay hosted, or wait outside
GitHub's self-hosted queue for fresh authorization after sizing completes; never
dispatch into a competing pending concurrency slot.
