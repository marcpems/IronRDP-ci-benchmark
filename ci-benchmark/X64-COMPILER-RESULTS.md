# Compiler isolation: optimized Windows x64 compiler

Paired stock-to-optimized toolchain replacement; cold artifacts, controlled Cargo profile.
Equal-weight VM means after averaging rounds; 95% paired VM-cluster bootstrap intervals.
CPU = user + kernel process-tree seconds; setup and correctness checks are excluded.

| Component | Metric | Linux stock | Windows stock | Windows optimized | Reduction (95% interval) |
|---|---|---:|---:|---:|---|
| graphics-project-1 | wall_seconds | 130.06 | 271.19 | 191.65 | 29.3% (27.5% to 31.2%) |
| graphics-project-1 | cpu_seconds | 130.01 | 266.79 | 187.59 | 29.7% (28.0% to 30.8%) |
| graphics-project-4 | wall_seconds | 52.91 | 112.58 | 78.60 | 30.2% (28.7% to 31.5%) |
| graphics-project-4 | cpu_seconds | 196.06 | 411.20 | 282.15 | 31.4% (30.3% to 32.3%) |
| yuv-native-codegen-1 | wall_seconds | 91.83 | 171.39 | 113.70 | 33.7% (32.0% to 35.1%) |
| yuv-native-codegen-1 | cpu_seconds | 91.81 | 169.46 | 112.61 | 33.5% (31.9% to 34.9%) |
| yuv-native-codegen-4 | wall_seconds | 33.97 | 73.19 | 47.96 | 34.5% (32.5% to 36.5%) |
| yuv-native-codegen-4 | cpu_seconds | 123.44 | 258.44 | 167.65 | 35.1% (33.9% to 36.1%) |
| yuv-native-metadata-1 | wall_seconds | 1.68 | 2.89 | 2.75 | 4.7% (2.2% to 7.1%) |
| yuv-native-metadata-1 | cpu_seconds | 1.68 | 2.87 | 2.71 | 5.5% (3.3% to 7.6%) |
| yuv-native-metadata-4 | wall_seconds | 1.67 | 2.92 | 2.75 | 5.6% (2.3% to 8.8%) |
| yuv-native-metadata-4 | cpu_seconds | 1.67 | 2.90 | 2.74 | 5.5% (2.2% to 8.8%) |
| yuv-wasm-codegen-1 | wall_seconds | 44.25 | 82.49 | 55.31 | 32.9% (28.7% to 35.6%) |
| yuv-wasm-codegen-1 | cpu_seconds | 44.24 | 81.57 | 53.93 | 33.9% (31.9% to 35.5%) |
| yuv-wasm-codegen-4 | wall_seconds | 16.41 | 34.38 | 22.57 | 34.4% (33.0% to 35.6%) |
| yuv-wasm-codegen-4 | cpu_seconds | 59.08 | 122.75 | 78.48 | 36.1% (34.6% to 37.4%) |
| yuv-wasm-metadata-1 | wall_seconds | 1.00 | 1.77 | 1.68 | 5.3% (3.6% to 7.0%) |
| yuv-wasm-metadata-1 | cpu_seconds | 0.99 | 1.74 | 1.66 | 4.7% (2.2% to 7.0%) |
| yuv-wasm-metadata-4 | wall_seconds | 1.00 | 1.76 | 1.62 | 7.8% (6.5% to 9.0%) |
| yuv-wasm-metadata-4 | cpu_seconds | 1.00 | 1.74 | 1.61 | 7.7% (6.3% to 8.7%) |

## Additional ThinLTO versus matched effective-PGO control

| Component | Metric | PGO control | PGO + ThinLTO | Reduction (95% interval) |
|---|---|---:|---:|---|
| graphics-project-1 | wall_seconds | 207.64 | 191.65 | 7.7% (6.5% to 8.9%) |
| graphics-project-1 | cpu_seconds | 205.26 | 187.59 | 8.6% (8.2% to 9.1%) |
| graphics-project-4 | wall_seconds | 86.05 | 78.60 | 8.7% (7.1% to 9.8%) |
| graphics-project-4 | cpu_seconds | 311.70 | 282.15 | 9.5% (8.8% to 10.1%) |
| yuv-native-codegen-1 | wall_seconds | 128.74 | 113.70 | 11.7% (10.9% to 12.5%) |
| yuv-native-codegen-1 | cpu_seconds | 127.51 | 112.61 | 11.7% (10.9% to 12.5%) |
| yuv-native-codegen-4 | wall_seconds | 57.35 | 47.96 | 16.4% (11.0% to 22.6%) |
| yuv-native-codegen-4 | cpu_seconds | 189.84 | 167.65 | 11.7% (11.0% to 12.4%) |
| yuv-native-metadata-1 | wall_seconds | 2.91 | 2.75 | 5.3% (3.3% to 7.3%) |
| yuv-native-metadata-1 | cpu_seconds | 2.88 | 2.71 | 6.0% (4.1% to 7.8%) |
| yuv-native-metadata-4 | wall_seconds | 2.91 | 2.75 | 5.5% (2.8% to 7.9%) |
| yuv-native-metadata-4 | cpu_seconds | 2.90 | 2.74 | 5.5% (3.2% to 7.6%) |
| yuv-wasm-codegen-1 | wall_seconds | 61.41 | 55.31 | 9.9% (6.3% to 12.2%) |
| yuv-wasm-codegen-1 | cpu_seconds | 60.77 | 53.93 | 11.3% (10.5% to 12.1%) |
| yuv-wasm-codegen-4 | wall_seconds | 26.72 | 22.57 | 15.5% (11.2% to 21.4%) |
| yuv-wasm-codegen-4 | cpu_seconds | 88.97 | 78.48 | 11.8% (10.9% to 12.6%) |
| yuv-wasm-metadata-1 | wall_seconds | 1.78 | 1.68 | 5.6% (3.1% to 8.1%) |
| yuv-wasm-metadata-1 | cpu_seconds | 1.75 | 1.66 | 5.4% (2.8% to 7.6%) |
| yuv-wasm-metadata-4 | wall_seconds | 1.86 | 1.62 | 12.5% (5.5% to 21.9%) |
| yuv-wasm-metadata-4 | cpu_seconds | 1.78 | 1.61 | 9.7% (5.6% to 14.7%) |

Prior Arm64 graphics-workload reference: 18.0% CPU / 18.8% wall reduction versus an LLD control.
This experiment measures the practical official-to-optimized replacement instead.
Interval overlap is not proof of equal effects. Native, common and WASM are separate workloads,
not stages to add into one CI total. Cargo activity intervals do not uniquely attribute CPU costs.
