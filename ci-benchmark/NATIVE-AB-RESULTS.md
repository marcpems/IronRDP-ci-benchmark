# Original IronRDP CI: optimized Windows Arm64 compiler

Paired stock-to-optimized toolchain replacement; cold artifacts, original Cargo profiles.
Equal-weight VM means after averaging rounds; 95% paired VM-cluster bootstrap intervals.
CPU = user + kernel process-tree seconds; setup and correctness checks are excluded.

| Component | Metric | Linux stock | Windows stock | Windows optimized | Reduction (95% interval) |
|---|---|---:|---:|---:|---|
| xtask-bootstrap | wall_seconds | 2.24 | 4.06 | 3.69 | 8.9% (4.2% to 14.2%) |
| xtask-bootstrap | cpu_seconds | 6.18 | 10.89 | 9.51 | 12.6% (11.4% to 13.9%) |
| workspace-tests | wall_seconds | 319.47 | 540.08 | 460.60 | 14.7% (14.1% to 15.3%) |
| workspace-tests | cpu_seconds | 1202.47 | 2035.84 | 1722.51 | 15.4% (14.9% to 15.9%) |
| native-tls-tests | wall_seconds | 9.07 | 17.24 | 13.43 | 22.1% (21.1% to 23.0%) |
| native-tls-tests | cpu_seconds | 30.10 | 47.78 | 38.50 | 19.4% (18.9% to 20.0%) |
| gateway-native-tls-tests | wall_seconds | 43.62 | 74.45 | 60.24 | 19.1% (17.5% to 20.4%) |
| gateway-native-tls-tests | cpu_seconds | 161.46 | 273.36 | 222.46 | 18.6% (17.6% to 19.6%) |
| gateway-smartcard-tests | wall_seconds | 39.77 | 73.82 | 58.03 | 21.4% (20.2% to 22.6%) |
| gateway-smartcard-tests | cpu_seconds | 149.04 | 262.77 | 215.95 | 17.8% (16.6% to 19.0%) |
| common | wall_seconds | 42.33 | 69.78 | 57.06 | 18.2% (17.5% to 18.9%) |
| common | cpu_seconds | 148.13 | 244.57 | 198.73 | 18.7% (17.7% to 19.8%) |
| wasm | wall_seconds | 77.51 | 134.63 | 112.61 | 16.4% (15.4% to 17.3%) |
| wasm | cpu_seconds | 288.43 | 495.14 | 409.62 | 17.3% (16.9% to 17.8%) |
| native-total | wall_seconds | 414.16 | 709.64 | 595.99 | 16.0% (15.4% to 16.7%) |
| native-total | cpu_seconds | 1549.24 | 2630.64 | 2208.94 | 16.0% (15.4% to 16.6%) |

Prior graphics-workload reference: 18.0% CPU / 18.8% wall reduction versus an LLD control.
This experiment measures the practical official-to-optimized replacement instead.
Interval overlap is not proof of equal effects. Native, common and WASM are separate workloads,
not stages to add into one CI total. Cargo activity intervals do not uniquely attribute CPU costs.
