# Same-tools Windows compiler results

Architecture scope: aarch64-pc-windows-msvc.
No results for omitted architectures are implied.

Compiler build run: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38056115559
Benchmark run: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38063669491

Native clang-cl, link.exe and lib.exe were held constant. Both PGO variants used
byte-identical profiles. Each architecture has five independent VMs and three
measured rounds per compiler, following one excluded warmup.

Correctness commands run outside timing. Protocol amendment: Before the replacement full study: serialize correctness test harnesses after an incomplete x64 study and separate 600-run diagnostics. Parallel diagnostics showed a different filesystem-notification failure under PGO-only; all 300 serial runs passed. The original DELETE_PENDING cause remains unproven. Timed compilation remains four-way parallel and unchanged; discard the entire incomplete study, not only its failed VM.

| Architecture | Variant | Native wall (s) | Native CPU (s) |
|---|---|---:|---:|
| aarch64-pc-windows-msvc | baseline | 668.71 | 2429.52 |
| aarch64-pc-windows-msvc | pgo | 539.61 | 1935.85 |
| aarch64-pc-windows-msvc | pgo-rust-thin | 540.40 | 1944.92 |

Positive reductions mean faster compilation; negative values mean slower.
Intervals resample paired whole VMs, not individual Cargo commands.

| Architecture | Contrast | Wall reduction | Wall 95% interval | CPU reduction | CPU 95% interval |
|---|---|---:|---:|---:|---:|
| aarch64-pc-windows-msvc | baseline->pgo | 19.31% | 18.39% to 20.27% | 20.32% | 19.91% to 20.81% |
| aarch64-pc-windows-msvc | pgo->pgo-rust-thin | -0.15% | -2.59% to 1.86% | -0.47% | -1.93% to 0.46% |
| aarch64-pc-windows-msvc | baseline->pgo-rust-thin | 19.19% | 17.77% to 20.29% | 19.95% | 19.25% to 20.48% |

## Offline Cargo command breakdown

The first five commands form the native total. Common-package and WASM
compilation are separate secondary controls, not part of that total.

| Architecture | Command | Baseline (s) | PGO (s) | PGO + Rust ThinLTO (s) |
|---|---|---:|---:|---:|
| aarch64-pc-windows-msvc | xtask-bootstrap | 4.22 | 3.56 | 3.57 |
| aarch64-pc-windows-msvc | workspace-tests | 503.57 | 410.98 | 410.05 |
| aarch64-pc-windows-msvc | native-tls-tests | 17.26 | 12.94 | 12.93 |
| aarch64-pc-windows-msvc | gateway-native-tls-tests | 73.65 | 56.87 | 57.13 |
| aarch64-pc-windows-msvc | gateway-smartcard-tests | 70.02 | 55.27 | 56.73 |
| aarch64-pc-windows-msvc | common | 66.46 | 51.88 | 52.79 |
| aarch64-pc-windows-msvc | wasm | 133.47 | 102.36 | 103.08 |

Process-tree CPU seconds include user and kernel time across descendants;
they are not wall seconds or an additive breakdown of wall time.

| Architecture | Command | Baseline CPU (s) | PGO CPU (s) | PGO + Rust ThinLTO CPU (s) |
|---|---|---:|---:|---:|
| aarch64-pc-windows-msvc | xtask-bootstrap | 10.26 | 8.51 | 8.58 |
| aarch64-pc-windows-msvc | workspace-tests | 1868.65 | 1501.47 | 1507.11 |
| aarch64-pc-windows-msvc | native-tls-tests | 45.32 | 34.25 | 34.37 |
| aarch64-pc-windows-msvc | gateway-native-tls-tests | 259.27 | 200.75 | 201.71 |
| aarch64-pc-windows-msvc | gateway-smartcard-tests | 246.02 | 190.87 | 193.15 |
| aarch64-pc-windows-msvc | common | 225.60 | 175.95 | 176.77 |
| aarch64-pc-windows-msvc | wasm | 471.55 | 366.38 | 367.58 |

These are offline Cargo compilation measurements, not end-to-end CI times.
Setup, downloads, uploads, and correctness runs are outside the timed totals.
The toolchains are compiler-only experiments, not qualified releases.
This newer source is not a matched comparison against the earlier Rust 1.94.1 study.

## Toolchain construction

| Architecture | Phase | Bootstrap wall (min) | Resume stage0/bootstrap (min) | Collector build (min) | Training wall (min) | Profile merge (min) | Bootstrap CPU (min) |
|---|---|---:|---:|---:|---:|---:|---:|
| aarch64-pc-windows-msvc | baseline | 53.65 | 0.00 | 0.00 | 0.00 | 0.00 | 180.26 |
| aarch64-pc-windows-msvc | rustc-profile | 50.00 | 0.00 | 2.63 | 27.28 | 2.84 | 170.33 |
| aarch64-pc-windows-msvc | llvm-profile | 77.87 | 1.52 | 2.70 | 16.40 | 2.01 | 228.85 |
| aarch64-pc-windows-msvc | pgo | 49.92 | 0.00 | 0.00 | 0.00 | 0.00 | 169.35 |
| aarch64-pc-windows-msvc | pgo-rust-thin | 53.04 | 0.00 | 0.00 | 0.00 | 0.00 | 179.65 |

Bootstrap-command time includes stage0 acquisition, bootstrap compilation, LLVM
and Rust compilation. It is not a pure offline compiler CPU measurement.
Collector construction, training and profile merging are separately recorded. Source/tool setup and
artifact transfers are excluded from this table. Jobs rebuild prerequisites
independently; their summed time is not the workflow critical path.

For a resumed phase, the bootstrap column belongs to the original compiler-build run.
The resume column records only stage0/bootstrap preparation in the later training run;
the original compiler build is not counted a second time.

| Architecture | Phase | Compiler-build run | Training/artifact run |
|---|---|---|---|
| aarch64-pc-windows-msvc | baseline | 38056115559 | 38056115559 |
| aarch64-pc-windows-msvc | rustc-profile | 38001265175 | 38001265175 |
| aarch64-pc-windows-msvc | llvm-profile | 38031778830 | 38037822491 |
| aarch64-pc-windows-msvc | pgo | 38056115559 | 38056115559 |
| aarch64-pc-windows-msvc | pgo-rust-thin | 38056115559 | 38056115559 |
