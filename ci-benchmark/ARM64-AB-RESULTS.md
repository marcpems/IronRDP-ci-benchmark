# Arm64 compiler optimization A/B

Times are equal-weight means across VMs after averaging measured rounds within each VM.
Intervals are paired Windows / independent Linux VM-cluster bootstrap percentiles.
Warmups are excluded; no slow-run trimming. CPU = user + kernel seconds.

| Endpoint | CPUs | Metric | Linux official | Windows official | MSVC baseline | LLD control | Optimized |
|---|---:|---|---:|---:|---:|---:|---:|
| graphics-project | 1 | cpu_seconds | 122.347 | 201.853 | 201.678 | 203.530 | 165.208 |
| graphics-project | 1 | wall_seconds | 122.394 | 206.351 | 206.768 | 207.820 | 169.846 |
| graphics-project | 4 | cpu_seconds | 127.344 | 213.608 | 215.310 | 214.339 | 175.742 |
| graphics-project | 4 | wall_seconds | 35.691 | 60.767 | 60.853 | 60.930 | 49.487 |
| yuv-native-codegen | 1 | cpu_seconds | 74.231 | 109.815 | 109.812 | 109.580 | 90.044 |
| yuv-native-codegen | 1 | wall_seconds | 74.247 | 110.900 | 110.789 | 111.292 | 91.160 |
| yuv-native-codegen | 4 | cpu_seconds | 69.558 | 107.989 | 107.948 | 107.277 | 88.732 |
| yuv-native-codegen | 4 | wall_seconds | 20.476 | 32.281 | 32.188 | 32.230 | 26.386 |
| yuv-native-metadata | 1 | cpu_seconds | 1.645 | 2.969 | 2.948 | 3.002 | 2.233 |
| yuv-native-metadata | 1 | wall_seconds | 1.646 | 3.006 | 2.994 | 3.053 | 2.271 |
| yuv-native-metadata | 4 | cpu_seconds | 1.672 | 3.014 | 3.019 | 3.074 | 2.315 |
| yuv-native-metadata | 4 | wall_seconds | 1.673 | 3.040 | 3.035 | 3.120 | 2.329 |
| yuv-wasm-codegen | 1 | cpu_seconds | 48.146 | 70.200 | 70.574 | 70.944 | 58.835 |
| yuv-wasm-codegen | 1 | wall_seconds | 48.157 | 70.900 | 71.259 | 71.959 | 59.478 |
| yuv-wasm-codegen | 4 | cpu_seconds | 44.902 | 69.735 | 69.834 | 69.745 | 57.592 |
| yuv-wasm-codegen | 4 | wall_seconds | 13.053 | 20.602 | 20.604 | 20.640 | 16.877 |
| yuv-wasm-metadata | 1 | cpu_seconds | 1.163 | 2.138 | 2.144 | 2.171 | 1.611 |
| yuv-wasm-metadata | 1 | wall_seconds | 1.164 | 2.167 | 2.180 | 2.266 | 1.640 |
| yuv-wasm-metadata | 4 | cpu_seconds | 1.169 | 2.212 | 2.199 | 2.231 | 1.665 |
| yuv-wasm-metadata | 4 | wall_seconds | 1.169 | 2.225 | 2.218 | 2.257 | 1.687 |

## Primary graphics / four-CPU contrasts

**cpu_seconds:** optimization-only saving 18.0% (95% interval 16.1% to 19.4%).
Rebuilt MSVC / official ratio: 1.008; 90% interval 0.994 to 1.023; equivalence gate: True.
Optimization contrast closes **44.7%** of the contemporary official Windows/Linux gap (95% interval 38.0% to 50.6%).
Historical-gap equivalent: 44.7%, conditional on the measured relative saving transferring to the earlier runner sample.

**wall_seconds:** optimization-only saving 18.8% (95% interval 16.6% to 20.6%).
Rebuilt MSVC / official ratio: 1.001; 90% interval 0.984 to 1.020; equivalence gate: True.
Optimization contrast closes **45.6%** of the contemporary official Windows/Linux gap (95% interval 37.8% to 53.4%).
Historical-gap equivalent: 46.0%, conditional on the measured relative saving transferring to the earlier runner sample.

