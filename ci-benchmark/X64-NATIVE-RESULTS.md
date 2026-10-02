# Original IronRDP CI: optimized Windows x64 compiler

Paired stock-to-optimized toolchain replacement; cold artifacts, original Cargo profiles.
Equal-weight VM means after averaging rounds; 95% paired VM-cluster bootstrap intervals.
CPU = user + kernel process-tree seconds; setup and correctness checks are excluded.

| Component | Metric | Linux stock | Windows stock | Windows optimized | Reduction (95% interval) |
|---|---|---:|---:|---:|---|
| xtask-bootstrap | wall_seconds | 2.24 | 4.72 | 3.54 | 24.9% (17.8% to 29.6%) |
| xtask-bootstrap | cpu_seconds | 6.81 | 13.46 | 9.82 | 27.0% (25.6% to 28.8%) |
| workspace-tests | wall_seconds | 384.34 | 746.67 | 568.63 | 23.8% (21.9% to 25.4%) |
| workspace-tests | cpu_seconds | 1473.33 | 2813.19 | 2130.67 | 24.3% (22.4% to 25.8%) |
| native-tls-tests | wall_seconds | 9.76 | 17.43 | 14.00 | 19.7% (15.8% to 24.2%) |
| native-tls-tests | cpu_seconds | 34.03 | 52.45 | 40.65 | 22.5% (20.7% to 24.0%) |
| gateway-native-tls-tests | wall_seconds | 51.00 | 94.36 | 72.43 | 23.2% (21.3% to 24.8%) |
| gateway-native-tls-tests | cpu_seconds | 194.51 | 356.10 | 268.53 | 24.6% (22.6% to 26.3%) |
| gateway-smartcard-tests | wall_seconds | 45.59 | 94.23 | 72.04 | 23.6% (20.8% to 26.1%) |
| gateway-smartcard-tests | cpu_seconds | 176.99 | 355.53 | 259.41 | 27.0% (24.1% to 29.7%) |
| common | wall_seconds | 56.05 | 111.53 | 78.42 | 29.7% (25.6% to 33.3%) |
| common | cpu_seconds | 205.66 | 394.38 | 279.43 | 29.1% (26.2% to 31.6%) |
| wasm | wall_seconds | 93.77 | 174.40 | 134.69 | 22.8% (21.1% to 24.3%) |
| wasm | cpu_seconds | 359.98 | 647.11 | 501.33 | 22.5% (20.8% to 24.1%) |
| native-total | wall_seconds | 492.93 | 957.41 | 730.64 | 23.7% (21.7% to 25.3%) |
| native-total | cpu_seconds | 1885.68 | 3590.73 | 2709.08 | 24.6% (22.5% to 26.1%) |

## Additional ThinLTO versus matched effective-PGO control

| Component | Metric | PGO control | PGO + ThinLTO | Reduction (95% interval) |
|---|---|---:|---:|---|
| xtask-bootstrap | wall_seconds | 3.71 | 3.54 | 4.4% (0.0% to 7.9%) |
| xtask-bootstrap | cpu_seconds | 10.56 | 9.82 | 7.0% (4.6% to 8.8%) |
| workspace-tests | wall_seconds | 615.66 | 568.63 | 7.6% (7.0% to 8.2%) |
| workspace-tests | cpu_seconds | 2293.03 | 2130.67 | 7.1% (6.9% to 7.3%) |
| native-tls-tests | wall_seconds | 15.41 | 14.00 | 9.2% (3.6% to 16.5%) |
| native-tls-tests | cpu_seconds | 44.20 | 40.65 | 8.0% (6.3% to 10.5%) |
| gateway-native-tls-tests | wall_seconds | 78.62 | 72.43 | 7.9% (7.4% to 8.4%) |
| gateway-native-tls-tests | cpu_seconds | 291.79 | 268.53 | 8.0% (7.4% to 8.5%) |
| gateway-smartcard-tests | wall_seconds | 77.72 | 72.04 | 7.3% (6.5% to 8.3%) |
| gateway-smartcard-tests | cpu_seconds | 282.00 | 259.41 | 8.0% (6.9% to 9.3%) |
| common | wall_seconds | 85.74 | 78.42 | 8.5% (7.8% to 9.3%) |
| common | cpu_seconds | 306.08 | 279.43 | 8.7% (8.0% to 9.5%) |
| wasm | wall_seconds | 144.53 | 134.69 | 6.8% (5.3% to 8.6%) |
| wasm | cpu_seconds | 536.79 | 501.33 | 6.6% (5.7% to 7.6%) |
| native-total | wall_seconds | 791.12 | 730.64 | 7.6% (7.1% to 8.0%) |
| native-total | cpu_seconds | 2921.58 | 2709.08 | 7.3% (7.0% to 7.5%) |

Prior Arm64 graphics-workload reference: 18.0% CPU / 18.8% wall reduction versus an LLD control.
This experiment measures the practical official-to-optimized replacement instead.
Interval overlap is not proof of equal effects. Native, common and WASM are separate workloads,
not stages to add into one CI total. Cargo activity intervals do not uniquely attribute CPU costs.
