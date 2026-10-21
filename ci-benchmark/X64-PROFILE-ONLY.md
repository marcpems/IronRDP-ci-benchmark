# Official versus repaired x64 LLVM profiles

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

## Preregistered causal experiment

**Status: scheduled and running; no profile-only performance result yet.**
Run [39584578532](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39584578532)
uses harness commit `b175183e4fbf0cfd8be02dde9dc223bb37c84c34`.
Its readiness job passed and the official-profile release job started.

Two clean complete Rust distributions use the same source path and revisions,
clang-cl 20.1.3, Microsoft linker/librarian, official Rust-side PGO profile,
16 build workers, Rust `thin-local`, and no LLVM ThinLTO. Only the supplied
LLVM profile changes: official versus the repaired profile from accepted run
[39456859889](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39456859889).
No new training runs are needed. Both distributions include the existing
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

After both releases qualify, the same runner measures the five original
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

Workflow: [x64-profile-only.yml](../.github/workflows/x64-profile-only.yml).
Artifacts: `x64-profile-{official,repaired}-{evidence,dist}` and
`x64-profile-replay`. Large artifacts have 30-day retention; compact final
evidence will accompany the qualified report.
