# Incremental Rust-only ThinLTO: hosted pilot

This is a **limited experimental compiler/sysroot pilot**, not a qualified full
release or an actual rebuilt combined-PR shipped artifact. No performance result
exists until `thin-incremental-consumer-evidence/index.json` has `complete: true`.
Production receipts deliberately retain `complete: false`; `build_complete`
means only that the compiler package passed its build/audit/smoke gates.

**Continuation amendment:** run 41058649059 built both compilers successfully,
then rejected the pair before any consumer timing because the original whole-file
stdlib identity rule included Microsoft linker/debug metadata. The frozen
`x64-rust-thin-continuation.json` supersedes only that rule, as detailed below.

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

## Completion collection

`monitor_x64_rust_thin.py` is a single attached, read-only waiting helper with
a maximum twelve-hour deadline, two-minute polling, bounded network retries,
and pinned run/head/attempt/workflow identity. It downloads all terminal study
artifacts, retains failures and raw failed-job logs, and invokes the separate
`verify_x64_rust_thin.py` verifier only after remote success. Neither script
dispatches, cancels, reruns, or changes any runner.

The verifier hashes the actual packaged compiler/Cargo/stdlib files, checks
paired source/config/profile/native-tool receipts, verifies all five command
receipts and raw compiled-artifact messages, checks correctness and the CPU meter,
and recomputes each paired wall/CPU reduction. The principal descriptive summary
is `100 * (1 - sum(treatment) / sum(baseline))`; individual paired reductions and
their arithmetic mean are also retained. Percentage display uses decimal
arithmetic rounded half-up to two decimals. Warmups never enter these summaries.
No confidence interval or full-release qualification is inferred.

Example (from the isolated worktree; supply the exact launched head):

```powershell
python .github\scripts\monitor_x64_rust_thin.py `
  --gh D:\copilot\tools\gh\bin\gh.exe `
  --run-id 41058649059 --head 35b5f2e6ed7eb00f73aded41eeb23a1a8a4211ab `
  --attempt 1 --hours 12 --interval 120 `
  --output ..\thin-incremental-evidence\completion-41058649059
```

The destination must be new so a retry cannot overwrite original failure evidence.
`monitor-failure.json` is an explicit rejection, never a performance result.

## Metadata-only stdlib identity repair

The original packages have 45 native stdlib files. All 43 rlib/import-library
files are byte-identical. `std-e2f0fb81520f5a3a.dll` differs in exactly 24 bytes:
COFF/debug-directory timestamps and the CodeView RSDS GUID. Zeroing only those
specified metadata fields in an in-memory comparison produces the identical
SHA-256 `2e005ec7c8bd1d8c104acf582451de23eb65b5c325e2c6f22d7d383bbfddf079`.
Every remaining DLL byte, including runtime code/data and Rust metadata, matches.
The PDBs have nondeterministic debug-stream layouts; they are not claimed
byte-identical. Each unchanged PDB must bind to its own DLL's timestamp, GUID and
age. PDB files are excluded only from the runtime-input equality criterion.

The repair does **not** modify either DLL/PDB, transplant stdlib components,
rebuild a compiler, change stack/source/config/profile inputs, or relax native
tool identity. A dedicated consumer-only workflow uses SHA-pinned original
package/metadata files. Raw package checksums remain mandatory. New tests reject
a one-byte nonmetadata DLL change and an incorrectly bound PDB; the separate
collector verifies the actual DLL byte differences against independently frozen
offsets and canonical hash. This is a declared correction to an overly strict
acceptance gate, not evidence that the first run passed.

The original failure, both successful compiler receipts/packages and the exact
runtime-identity comparison are retained under
`D:\copilot\thin-incremental-evidence\completion-41058649059`.
The consumer continuation branch is `experiment/x64-rust-thin-consumer`; it has
only a standard hosted Windows consumer job and cannot rebuild compilers or
occupy any self-hosted concurrency slot.
