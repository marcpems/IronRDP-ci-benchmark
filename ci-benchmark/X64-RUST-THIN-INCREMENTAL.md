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

## Why this differs from the earlier 7.6% result

The 30 October forensic review found an **attribution gap in the original
expectation**, not evidence that the earlier gain was invented or that the
new treatment silently failed to enable ThinLTO. Expecting a significant
Rust-only improvement from a combined Rust-plus-LLVM result was stronger
than the evidence supported. A feasible same-Microsoft-tools configuration
is not, by itself, a demonstrated performance improvement.

The [recomputed audit](x64-rust-thin-gap-audit.json) revisits all 15 historical
measured pairs and all three new pairs, the original build configurations,
profile hashes, actual final-driver compiler commands and packaged PE code.

| Controlled comparison | Earlier study | New pilot |
|---|---|---|
| Rust compiler being built | 1.94.1, `e408947bf` | 1.101.0-nightly, `4da678aad` |
| LLVM backend being built | 21.1.8 | 23.1.3 |
| Rust cross-crate ThinLTO | Off -> on | Off -> on |
| Native C++ LLVM ThinLTO | **Off -> on** | **Off in both arms** |
| Native linker/librarian | **LLD/llvm-lib in both arms** | Microsoft link/lib in both arms |
| PGO profiles | Identical within that pair | Identical within this pair, but different from the historical pair |
| Consumer environment | Windows 2025; five independent four-LP VMs | Windows 2022; one four-LP VM |
| Cargo and stdlib | Common official 1.94.1 components | Common stage0 Cargo; own, runtime-identical stdlibs |
| IronRDP source and dependency lock | Same pinned source/lock as the new pilot | Same as historical study |
| Recomputed wall reduction | **7.64484%** | **-0.04615%** |
| Recomputed CPU reduction | **7.27333%** | **0.36011%** |

**Important correction:** the historical matched 7.6% contrast did not switch
linkers between its control and treatment. Both already used LLD. The linker
differs **between studies**, and in the broader shipping-to-optimized
comparison. It would be wrong to explain the matched 7.6% as merely changing
from Microsoft linking to LLD.

The old wall gain appears on all five VMs: **6.51-8.16%**. Two used the same
AMD EPYC 7763 CPU model as the new consumer and gave **7.80% and 7.83%**.
That makes a different CPU model alone an inadequate explanation. These are
not the same physical VMs or OS/toolchain images.

### Was the new treatment actually applied?

Yes, the effective final-driver invocation, not just `bootstrap.toml`,
contains **`-Zdylib-lto -Clto=thin -Cembed-bitcode=yes`** in the treatment.
The baseline has none of those overrides. Both use `-C codegen-units=1` and
the exact same `-Cprofile-use` path/profile bytes. Bootstrap's pinned
[`apply_dylib_lto`](https://github.com/rust-lang/rust/blob/4da678aada4683607acbd67a8da37a320c791f93/src/bootstrap/src/core/build_steps/compile.rs#L1287-L1313)
explicitly supplies these flags to override Cargo's dylib defaults. The
earlier `-C embed-bitcode=no` printed by Cargo is followed by the effective
`-Cembed-bitcode=yes`; it is not evidence that ThinLTO was disabled.

The final command's output suffix matches the driver in each shipped package:
`rustc_driver-4d4a0159589fd330.dll` versus
`rustc_driver-07ae6c6f31e26882.dll`. Their executable `.text` sections differ,
not just timestamps: **129,169,044 versus 135,284,708 virtual bytes**
(4.73% larger with ThinLTO). Each `rustc.exe` contains its own distinct driver
DLL name. This rejects the simple "identical compiler/no-op setting" explanation.
Larger code is a possible optimization trade-off, not proof of an
instruction-cache regression; no hardware-counter profile was collected.

The consumer passes each arm's absolute compiler path through `RUSTC`, and
the Windows process launcher passes that environment to Cargo. The common
Cargo executable does not select the baseline compiler for both arms.
Fresh targets, matching compiled-artifact counts, package hashes and
alternating order also check out. There was no measured-command loaded-module
trace, so this is static package/code-path evidence rather than a claim of
directly observed DLL loads for every invocation.

### Could other CI work hide a large compiler improvement?

There is no sign of that in the receipts. Setup/transfers/correctness are
outside the timer, the workload consumes approximately **3.87 / 3.85 of four
CPU equivalents**, and CPU improves only 0.36%, not the historical 7.27%.
The dominant workspace compilation is also flat:

| Original native command | Baseline wall, seconds | Rust-only ThinLTO wall, seconds | Wall reduction | CPU reduction |
|---|---:|---:|---:|---:|
| xtask bootstrap | 3.795 | 3.832 | -0.97% | -0.39% |
| Workspace test compilation | 625.092 | 625.018 | **0.01%** | **0.35%** |
| Native TLS test compilation | 15.949 | 15.951 | -0.01% | -0.19% |
| Gateway native TLS compilation | 84.367 | 84.781 | -0.49% | 0.85% |
| Gateway smartcard compilation | 83.382 | 83.380 | 0.00% | 0.03% |

Thus a large improvement in the main step is not being cancelled by setup
or another measured step. Small effects remain uncertain with one consumer
VM; these observations do not establish universal zero benefit or a regression.
The earlier failed correctness attempts did not alter compiler packages or
timed commands, so their fixes do not explain this difference.

### What remains unexplained, and the discriminating experiment

The leading **untested explanation** is that native LLVM ThinLTO, or its
interaction with Rust ThinLTO, supplied much of the earlier combined gain.
Rust-side ThinLTO cannot apply cross-module optimization to the already-native
LLVM objects used in the new pilot. PGO and one codegen unit already optimize
the baseline strongly, but that is not a measured explanation for the gap:
the historical control also had effective PGO and one codegen unit.

Compiler/backend version, profiles, native link layout and OS/Cargo changes
are additional cross-study differences. The existing experiments cannot
allocate the missing gain among them; **subtracting -0.05% from 7.6% would
not measure an LLVM-only benefit**.

The highest-information next experiment is a fixed-source, fixed-profile,
LLD-linked **2x2**: neither cross-crate LTO mode, Rust-only, LLVM-only, both.
Replay all four on the same independent hosted consumers and preserve the
Microsoft-linked pair as the adoption reference. This separates LLVM's
contribution from Rust's and their interaction; only then bridge versions if
the old combined gain still does not reproduce. A repeat of the present
Microsoft-linked pair on additional VMs can establish repeatability, but
cannot by itself explain the historical combined effect. No additional
benchmark has been launched for this forensic review.

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
