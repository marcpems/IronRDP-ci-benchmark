# Official versus repaired x64 LLVM profiles

## Qualified result

**Changing only the LLVM profile reduced offline IronRDP compilation wall time
by 13.73%, saving 97.61 seconds per five-command native block.** Both compilers
were rebuilt with the same source, Microsoft native linking tools, official
Rust-side PGO profile and optimization settings. The control used the official
shipping LLVM profile; it was **not the untouched official shipping binary**.

| Endpoint | Official LLVM profile | Repaired LLVM profile | Reduction |
|---|---:|---:|---:|
| Native compilation wall time | 711.049 s | 613.436 s | **13.73%** |
| Native compilation CPU time | 2769.458 s | 2381.292 s | **14.02%** |
| Workspace test compilation wall time | 554.219 s | 476.849 s | **13.96%** |

These are means of three measured rounds on one self-hosted i9-11900 runner,
using four-worker affinity and fresh target directories. One warmup per
compiler was excluded in advance. All **30 measured commands**, 10 warmup
commands and **eight original correctness commands** succeeded; both full Rust
distributions separately passed the unmodified upstream extracted-distribution
tests. The completed replay is
[39635843303](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39635843303).

| Measured round | Official profile | Repaired profile | Wall reduction |
|---|---:|---:|---:|
| 1 | 719.845 s | 613.625 s | 14.76% |
| 2 | 707.895 s | 616.093 s | 12.97% |
| 3 | 705.406 s | 610.591 s | 13.44% |

The **12.97-14.76% range is observed paired-round variation, not a confidence
interval**. This is one compiler-build pair and one machine, not replicated
training/builds or independent hosted VMs. It isolates switching the entire
LLVM profile file, not the contribution of individual missing functions.
Do not subtract this 13.73% from the earlier five-VM 18.0% toolchain benefit:
those studies have different controls, hardware and scope.

### Native-command breakdown

| Command group | Official profile | Repaired profile | Wall reduction |
|---|---:|---:|---:|
| xtask bootstrap | 3.323 s | 2.905 s | 12.57% |
| Workspace tests, compilation only | 554.219 s | 476.849 s | 13.96% |
| Native TLS tests, compilation only | 12.198 s | 10.970 s | 10.06% |
| Gateway native TLS tests, compilation only | 70.798 s | 62.442 s | 11.80% |
| Gateway smartcard tests, compilation only | 70.511 s | 60.270 s | 14.52% |

### CI wall-clock interpretation

For a consumer CI job with this five-command block on its critical path and
unchanged other work, the measured saving is approximately **1m38s per build**.
If unchanged overhead is `H` seconds, the corresponding whole-job reduction fraction is
`97.613 / (711.049 + H)`. **13.73% is not a measured whole-IronRDP-CI reduction**;
parallel jobs and other critical-path work can change the end-to-end effect.

Producing the full compiler distribution with existing profiles took
**4506.154 to 4337.160 seconds**, an observed **168.994-second / 3.75% reduction**
in this one ordered pair. No profile training is included. The control's
qualification was recovered in a separate job, so **there is no matched fresh
whole-compiler-CI comparison from this experiment**. The earlier two-pair
training-inclusive result (+2.71% production / +4.00% whole job) remains a
separate recipe comparison, not contradicted or replaced by this result.

For transparency, the final self-hosted **experiment** job took 5979 seconds:

| Activity | Wall time |
|---|---:|
| Thirty measured native compilation commands | 3973.456 s |
| Ten excluded warmup compilation commands | 1316.096 s |
| Eight untimed original correctness commands | 57.742 s |
| Other work inside the benchmark step | 138.707 s |
| Setup, input transfer, upload and other work outside that step | 493.000 s |

The residual inside the step includes toolchain preparation, dependency fetching,
instrumentation overhead and cleanup; it is not assigned to compilation.
This eight-block benchmarking job is not a representative single-toolchain CI job.
Build telemetry had no invalid counter samples, at least 8076 MiB available
RAM and at least 1794.56 GiB free on the ReFS build volume across the two builds.

## Direct official-profile finding

Rust 1.94.1 publishes the actual profile-use inputs in
[its Windows x64 reproducibility bundle](https://static.rust-lang.org/dist/reproducible-artifacts-1.94.1-x86_64-pc-windows-msvc.tar.xz).
The published SHA-256 matches
`7c1aabaabd49f6b59b0ca2211b7b7dc737cba0b3accf63542527f89cf7641793`;
its source metadata identifies Rust commit
`e408947bfd200af42db322daf0fadfe7e26d3bd1`.
At that commit, bootstrap's `ReproducibleArtifacts` implementation in
`src/bootstrap/src/core/build_steps/dist.rs` copies the configured
`rust_profile_use` and `llvm_profile_use` files into this package.

Inspection with the official 1.94.1 LLVM tools
(`21.1.8-rust-1.94.1-stable`) gives:

| LLVM profile | X86TargetLowering functions / active | InstCombine functions / active |
|---|---:|---:|
| Official shipping | 0 / 0 | 6 / 0 |
| Previously rebuilt upstream recipe | 0 / 0 | 6 / 0 |
| Repaired local recipe | 255 / 167 | 873 / 597 |

Commands: `llvm-profdata show --function=X86TargetLowering --counts FILE`
and the corresponding `--function=InstCombine` command. An active function
has at least one nonzero block counter. The exact official reader SHA-256
is `33d15da94a4209094191d5fab5de5bb34c801c33ad0a08180f9b1891375f54a6`.
The profile and archive hashes are pinned in
[`x64-profile-only-protocol.json`](x64-profile-only-protocol.json).

This directly establishes the specific missing coverage in the official
published LLVM profile. It does **not** establish that all official PGO is
ineffective or that this gap alone explains the earlier 18% toolchain benefit.

## Protocol and execution history

**Status: complete; both compilers and the downstream replay qualified.** Continuation
[39611328907](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39611328907)
used harness `599cf40bdfcaec3aca1cec43e1027630357a1ccf`. The preserved control
and fresh repaired build both passed their common-input gates and upstream
correctness tests. Production took 4506.154 seconds for the official-profile
control and 4337.160 seconds for repaired-profile production. These are
compiler-production timings, **not** IronRDP compile times.

The first replay attempt never reached measurements: downloading both complete distribution
bundles (about 3 GB) to the self-hosted runner failed after five retries.
The successful replay-only workflow used a standard hosted Windows runner to stage
just the two compiler archives and result/manifest files, about 165 MiB total.
Their exact hashes and original release run are pinned in
[`x64-profile-replay-input.json`](x64-profile-replay-input.json).
The self-hosted runner then measured those unchanged compilers; neither
production nor compiler qualification was repeated.
Replay-only run
[39635843303](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39635843303)
uses harness `32d5658dd4508b17519aff38a3306fdba3e50366`.

Replacement production run
[39595776289](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39595776289)
used harness `23ef5e31d9c4ad2ab48a8b0b7ec5ad381e95dea8`. Its official-profile
distribution build succeeded in 4506.15 seconds but was incorrectly rejected
by an added Cranelift-archive requirement. The pinned upstream
`CraneliftCodegenBackend::run` explicitly omits that component on stable/beta;
the previously accepted 1.94.1 manifests likewise contain no Cranelift archive.
The check now reuses the existing stable-distribution validator.

The retained distribution passed qualification without another compiler build in
[run 39608556774](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39608556774):
87.17 seconds to build the test helper and 542.26 seconds for the unmodified
upstream extracted-distribution tests. Archive hashes remained unchanged.
That run failed only when `upload-artifact` could not find a common root for
evidence on D: and readiness on C:. The upload layout now stages readiness
alongside the evidence on D:.

The continuation preserved the successful production and qualification evidence,
uploaded the verified archives, then started the repaired build from a fresh
checkout at the **same** D: source path. Original ownership and a separate
continuation ownership marker gate cleanup. No control build or test rerun is
needed. The paired replay subsequently completed using the preserved artifacts.

Original production provenance, raw logs, measurement, configuration and metrics
are hash-pinned in
[`x64-profile-qualification-input.json`](x64-profile-qualification-input.json).
Qualification used separate output and run identities, verified native tools,
profiles and test implementation, and checked archive hashes before and after
the upstream tests. Continuation metadata records its orchestration run separately
from `production_run_id` and `qualification_run_id`; it does not overwrite or
relabel either failed Actions job.
CI accounting must identify the split production/qualification
runs; a resumed job is not a fresh whole-CI timing sample.

Initial run [39584578532](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39584578532),
harness `b175183e4fbf0cfd8be02dde9dc223bb37c84c34`, completed its official-profile
full distribution successfully in 4495.89 seconds, then stopped before
correctness qualification. Its guard rejected 56 hash-mismatch diagnostics,
all for `main` entry points in standalone `llvm/tools` or `llvm/utils`
executables, not functions in the LLVM libraries linked into rustc. The
official profile contains multiple `main` records, including a one-counter
record with count 501, matching the discarded count in those diagnostics.

The corrected guard retains and reports these narrowly identified standalone
tool-entry collisions. Missing Rust profile use, LLVM library mismatches,
non-`main` function mismatches, and unclassified warnings still reject a build.
Both variants use the same guard. The original attempt remains excluded and
preserved; the replacement control was also a fresh build, not reused objects.

Two clean complete Rust distributions use the same source path and revisions,
clang-cl 20.1.3, Microsoft linker/librarian, official Rust-side PGO profile,
16 build workers, Rust `thin-local`, and no LLVM ThinLTO. Only the supplied
LLVM profile changes: official versus the repaired profile from accepted run
[39456859889](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39456859889).
No new training was run. Both distributions include the existing
full tools/docs/MSI scope.

Qualification calls the pinned, **unmodified** upstream `opt-dist` `tests.rs`
implementation. A common dispatch-only change exposes that test entry point
without retraining. The common bootstrap clang-runtime discovery patch remains;
no treatment-specific compiler implementation or training patch is applied.
Exact configuration, profile hashes, native CMake settings, raw logs,
distribution manifests, production timing and telemetry are retained.

The reset runner was inventoried by
[readiness run 39583339394](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39583339394):
i9-11900, 8 physical / 16 logical CPUs, about 31.7 GiB RAM.
The D: ReFS volume is a 2 TB `NVMe HFS002TFM9X189N-SKhynix` SSD,
with about 1.83 TiB free. E: and G: are on the older Toshiba HDD and are
not used for compilation. C: remains NTFS and supplies correctness-test
temporary directories. The host and filesystem are explicitly gated again
by each job; no formatting or machine policy changes are performed.

After both releases qualified, the same runner measured the five original
offline native IronRDP compilation commands. Both compilers use identical
official Cargo and native standard libraries. Each compiler has one excluded
warmup and three measured rounds, alternating order, fresh target directories,
and four-worker CPU affinity. Original correctness tests run outside timing.

The endpoint is the difference between mean three-round native totals.
Report paired-round differences and their range, **not** a confidence interval
over independent VMs: this is one machine and one compiler-build pair.
Build time, qualification, and whole Actions job time are separate endpoints.
Cross-study build-time changes cannot be attributed to PGO because the runner
was reset and its storage changed.

## Evidence and reproduction

The [numerical report](X64-PROFILE-ONLY.json) includes component means, paired
rounds, compiler-production timings, experiment-job accounting and per-file
evidence hashes. The [compact evidence ZIP](x64-profile-only-evidence.zip)
permanently preserves the original measurement JSON, meter self-test, compiler
metadata/manifests, profile-use audits, production metrics/telemetry and job
records. It also includes the official-profile audit.

From the repository root, reproduce the numerical report with Python 3.13:

```powershell
Expand-Archive ci-benchmark\x64-profile-only-evidence.zip -DestinationPath profile-evidence
python ci-benchmark\analyze_x64_profile_only.py profile-evidence --output profile-result.json
```

Extraction and reanalysis reproduce the published JSON byte-for-byte.
Full distribution binaries, merged profiles and verbose logs remain in Actions
with 30-day retention; the compact archive reproduces the numbers, not the binaries.

Initial workflow: [x64-profile-only.yml](../.github/workflows/x64-profile-only.yml).
Final replay: [x64-profile-replay.yml](../.github/workflows/x64-profile-replay.yml).
Artifacts: `x64-profile-{official,repaired}-{evidence,dist}` and
`x64-profile-replay`.
