# Incremental Rust-only ThinLTO over repaired x64 PGO

Updated 30 October 2026. **No meaningful incremental IronRDP wall-time benefit
was observed in this pilot.** This measures building IronRDP using an
already-built compiler, not building Rust or application runtime.

| Three measured rounds, mean per five-command block | Repaired PGO | Same + Rust-only ThinLTO | Reduction |
|---|---:|---:|---:|
| IronRDP offline wall | 812.586s | 812.961s | **-0.05%** (0.375s slower) |
| Descendant CPU | 3141.375s | 3130.063s | **0.36%** |

Reduction is `100 * (1 - sum(treatment) / sum(baseline))`; negative means
slower. Paired wall reductions were **0.69%, 0.05%, -0.88%**. CPU reductions
were **0.72%, 0.32%, 0.04%**. These mixed sub-percent wall observations do not
establish a useful gain or a statistically established regression.

## What changed, and what did not

- Rust source `4da678aada4683607acbd67a8da37a320c791f93`, LLVM
  `aab11ee0ea5ea9a1d462ad0bc1fae9d9bb643019`, plus the exact common
  `builtins_locator.run_in_dry_run()` prerequisite.
- Only `rust.lto = "thin-local"` versus `"thin"` changed. Both retained
  one Rust codegen unit, Clang 20.1.3, Microsoft `link.exe`/`lib.exe`, and
  **native LLVM ThinLTO off**. Source/configuration/native-tool/SDK and
  header/library identities were checked.
- Identical frozen rustc and LLVM PGO profiles came from qualified training
  [40170434889](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/40170434889).
  Both compilers were built fresh on standard hosted Windows x64; neither
  used cached native objects. Compiler-cache hit rate: **N/A, not enabled**.
- This tests the effective repaired-PGO condition. It is not a rebuilt,
  fully qualified combination of the open upstream PRs; their cache
  workaround does not affect a build with no compiler-cache service.

The previous **7.6%** x64 result added **both Rust and LLVM ThinLTO with LLVM
linking tools**. It is a different intervention and is not contradicted by,
or transferable to, this Microsoft-linked Rust-only result.

## Consumer measurement and correctness

Pinned IronRDP `0c5419eca6bf53563056ed252f537bca67862705`; one hosted Windows
consumer VM, four-LP inherited affinity, one excluded warmup per arm and
three measured rounds. Arm ordering alternated AB/BA/AB/BA including warmup.
Every block started with a fresh target directory, shared across its five
original offline, frozen commands: xtask bootstrap, workspace test compilation,
native TLS, gateway native TLS and gateway native TLS plus smartcard.
Dependencies, setup, transfers and correctness execution were outside timing.

Both arms used identical stage0 Cargo and retained their own built standard
library. All 43 rlib/import-library files matched byte-for-byte; the std DLL
differed only in 24 bytes of linker timestamps/debug identifiers. Runtime
code/data matched, each unchanged PDB bound to its own DLL, and no library was
transplanted or patched. Raw package checksums remained mandatory.

Both arms passed native correctness: **3,604 workspace tests**, plus **1 TLS,
10 gateway and 13 smartcard tests**, with zero failures and six ignored
workspace tests. Workspace `--tests` respects the pinned manifests'
`test = false` declarations and excludes doctests. Compiler smoke checks also
passed. The final set has **30 successful timed commands**, excluding the
two warmup blocks.

## Qualification and interpretation limits

**One build pair and one consumer VM, not a population confidence interval.**
These are experimental stage2 compiler/sysroot packages: **not complete
distribution qualification**, not doctest coverage, and not a production
recommendation. The pinned source's compiler-private-tool LTO handling and
stack behavior require separate full-release work; related upstream
[Rust #128947](https://github.com/rust-lang/rust/pull/128947) remains a distinct
effort. No new stack, DLL, MIR or runtime-search-path patch was introduced.

Compiler-only build wall was **3828.440s baseline / 3646.557s ThinLTO** on
separate hosted builders. These are provenance/overhead receipts, **not an
isolated Rust-production saving**: there is no repeated same-machine
production comparison, fresh training, full tools/docs/MSI or extracted
distribution suite in this pilot.

## Recovery history and evidence

Both compilers succeeded in producer
[41058649059](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/41058649059).
The initial consumer rejected nondeterministic DLL/PDB metadata before timing.
Subsequent consumer-only attempts exposed a missing correctness-only `PUBLIC`
variable and a harness mistake forcing manifest-disabled browser tests to run
natively via `--lib --bins`. These failures are preserved. The final recovery
used `--tests`, restored the real `PUBLIC` directory only for correctness, and
changed neither compiler package, source, profiles nor timed commands.

Successful consumer
[41076640207](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/41076640207)
completed **17:17:42 UTC**, at harness
`be5fa8759eefdcd518a9c398f11fc43f8968bdfc`. Independent verification rehashed
packages and checked inputs, profile use, affinity, all command receipts,
compiled-artifact messages, CPU accounting and native test outcomes, then
recomputed the percentages.

[Persistent compact evidence](x64-rust-thin-incremental-evidence.zip) includes
raw timing/correctness outputs, producer receipts, exact protocol amendments,
failure records, the verifier and per-file hashes. Frozen original protocol
fields remain historical; the recorded continuation amendment supersedes the
whole-DLL identity rule and erroneous correctness target selection.
The custom NVMe sizing runner was not used or interrupted.
