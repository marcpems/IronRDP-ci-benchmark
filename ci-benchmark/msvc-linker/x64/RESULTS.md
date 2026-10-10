# Same-tools Windows compiler results

Architecture scope: x86_64-pc-windows-msvc.
No results for omitted architectures are implied.

Compiler build run: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38021536352
Benchmark run: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38056790312

Native clang-cl, link.exe and lib.exe were held constant. Both PGO variants used
byte-identical profiles. Each architecture has five independent VMs and three
measured rounds per compiler, following one excluded warmup.

Correctness commands run outside timing. Protocol amendment: Before the replacement full study: serialize correctness test harnesses after an incomplete x64 study and separate 600-run diagnostics. Parallel diagnostics showed a different filesystem-notification failure under PGO-only; all 300 serial runs passed. The original DELETE_PENDING cause remains unproven. Timed compilation remains four-way parallel and unchanged; discard the entire incomplete study, not only its failed VM.

| Architecture | Variant | Native wall (s) | Native CPU (s) |
|---|---|---:|---:|
| x86_64-pc-windows-msvc | baseline | 786.91 | 2914.24 |
| x86_64-pc-windows-msvc | pgo | 637.54 | 2346.16 |
| x86_64-pc-windows-msvc | pgo-rust-thin | 640.89 | 2355.11 |

Positive reductions mean faster compilation; negative values mean slower.
Intervals resample paired whole VMs, not individual Cargo commands.

| Architecture | Contrast | Wall reduction | Wall 95% interval | CPU reduction | CPU 95% interval |
|---|---|---:|---:|---:|---:|
| x86_64-pc-windows-msvc | baseline->pgo | 18.98% | 15.78% to 21.55% | 19.49% | 17.25% to 21.78% |
| x86_64-pc-windows-msvc | pgo->pgo-rust-thin | -0.53% | -3.67% to 2.40% | -0.38% | -2.14% to 0.98% |
| x86_64-pc-windows-msvc | baseline->pgo-rust-thin | 18.56% | 15.92% to 22.04% | 19.19% | 15.80% to 22.30% |

## Offline Cargo command breakdown

The first five commands form the native total. Common-package and WASM
compilation are separate secondary controls, not part of that total.

| Architecture | Command | Baseline (s) | PGO (s) | PGO + Rust ThinLTO (s) |
|---|---|---:|---:|---:|
| x86_64-pc-windows-msvc | xtask-bootstrap | 3.81 | 3.15 | 3.22 |
| x86_64-pc-windows-msvc | workspace-tests | 606.17 | 491.42 | 497.36 |
| x86_64-pc-windows-msvc | native-tls-tests | 15.20 | 12.68 | 12.41 |
| x86_64-pc-windows-msvc | gateway-native-tls-tests | 82.02 | 66.69 | 64.83 |
| x86_64-pc-windows-msvc | gateway-smartcard-tests | 79.70 | 63.61 | 63.07 |
| x86_64-pc-windows-msvc | common | 82.06 | 66.38 | 65.64 |
| x86_64-pc-windows-msvc | wasm | 148.81 | 118.86 | 117.38 |

Process-tree CPU seconds include user and kernel time across descendants;
they are not wall seconds or an additive breakdown of wall time.

| Architecture | Command | Baseline CPU (s) | PGO CPU (s) | PGO + Rust ThinLTO CPU (s) |
|---|---|---:|---:|---:|
| x86_64-pc-windows-msvc | xtask-bootstrap | 11.18 | 9.08 | 9.12 |
| x86_64-pc-windows-msvc | workspace-tests | 2265.39 | 1837.90 | 1845.33 |
| x86_64-pc-windows-msvc | native-tls-tests | 44.94 | 35.11 | 34.90 |
| x86_64-pc-windows-msvc | gateway-native-tls-tests | 303.72 | 237.25 | 238.14 |
| x86_64-pc-windows-msvc | gateway-smartcard-tests | 289.01 | 226.82 | 227.63 |
| x86_64-pc-windows-msvc | common | 295.04 | 235.96 | 234.84 |
| x86_64-pc-windows-msvc | wasm | 557.20 | 443.01 | 438.03 |

These are offline Cargo compilation measurements, not end-to-end CI times.
Setup, downloads, uploads, and correctness runs are outside the timed totals.
The toolchains are compiler-only experiments, not qualified releases.
This newer source is not a matched comparison against the earlier Rust 1.94.1 study.

## Toolchain construction

| Architecture | Phase | Bootstrap wall (min) | Collector build (min) | Training wall (min) | Profile merge (min) | Bootstrap CPU (min) |
|---|---|---:|---:|---:|---:|---:|
| x86_64-pc-windows-msvc | baseline | 46.01 | 0.00 | 0.00 | 0.00 | 156.81 |
| x86_64-pc-windows-msvc | rustc-profile | 74.02 | 2.64 | 23.07 | 1.45 | 260.65 |
| x86_64-pc-windows-msvc | llvm-profile | 95.21 | 2.92 | 17.68 | 3.24 | 315.27 |
| x86_64-pc-windows-msvc | pgo | 43.06 | 0.00 | 0.00 | 0.00 | 151.10 |
| x86_64-pc-windows-msvc | pgo-rust-thin | 59.12 | 0.00 | 0.00 | 0.00 | 206.55 |

Bootstrap-command time includes stage0 acquisition, bootstrap compilation, LLVM
and Rust compilation. It is not a pure offline compiler CPU measurement.
Collector construction, training and profile merging are separately recorded. Source/tool setup and
artifact transfers are excluded from this table. Jobs rebuild prerequisites
independently; their summed time is not the workflow critical path.
