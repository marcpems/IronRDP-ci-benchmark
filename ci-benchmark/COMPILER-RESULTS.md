# Compiler validation measurements

Cells: median wall seconds / median CPU seconds (user + kernel). n=3 per cell.
CPU time sums concurrent threads/processes and is not wall time.

| Workload | Logical CPUs | Linux x64 | Windows x64 | Linux Arm64 | Windows Arm64 |
|---|---:|---:|---:|---:|---:|
| graphics-project | 1 | 133.31 / 133.27 | 265.66 / 261.48 | 122.14 / 122.05 | 212.14 / 205.55 |
| graphics-project | 4 | 56.48 / 210.26 | 113.56 / 409.64 | 35.99 / 126.36 | 60.92 / 212.09 |
| yuv-native-metadata | 1 | 1.67 / 1.67 | 3.06 / 2.80 | 1.65 / 1.65 | 2.82 / 2.75 |
| yuv-native-metadata | 4 | 1.72 / 1.72 | 2.82 / 2.81 | 1.71 / 1.71 | 3.02 / 2.97 |
| yuv-native-codegen | 1 | 91.10 / 91.08 | 173.47 / 169.39 | 75.97 / 75.95 | 107.37 / 106.31 |
| yuv-native-codegen | 4 | 35.08 / 127.09 | 74.77 / 258.92 | 20.09 / 68.74 | 31.72 / 106.67 |
| yuv-wasm-metadata | 1 | 1.00 / 0.99 | 1.71 / 1.72 | 1.16 / 1.16 | 2.10 / 2.03 |
| yuv-wasm-metadata | 4 | 0.97 / 0.97 | 1.65 / 1.64 | 1.17 / 1.17 | 2.14 / 2.11 |
| yuv-wasm-codegen | 1 | 43.41 / 43.40 | 82.54 / 80.91 | 48.48 / 48.46 | 70.26 / 68.78 |
| yuv-wasm-codegen | 4 | 16.75 / 60.49 | 35.07 / 122.98 | 13.05 / 44.40 | 20.16 / 69.02 |

## Windows/Linux ratios

| Workload | CPUs | x64 wall | x64 CPU | Arm64 wall | Arm64 CPU |
|---|---:|---:|---:|---:|---:|
| graphics-project | 1 | 1.993x | 1.962x | 1.737x | 1.684x |
| graphics-project | 4 | 2.011x | 1.948x | 1.693x | 1.678x |
| yuv-native-metadata | 1 | 1.826x | 1.672x | 1.705x | 1.664x |
| yuv-native-metadata | 4 | 1.641x | 1.638x | 1.770x | 1.738x |
| yuv-native-codegen | 1 | 1.904x | 1.860x | 1.413x | 1.400x |
| yuv-native-codegen | 4 | 2.132x | 2.037x | 1.579x | 1.552x |
| yuv-wasm-metadata | 1 | 1.719x | 1.728x | 1.811x | 1.756x |
| yuv-wasm-metadata | 4 | 1.700x | 1.686x | 1.837x | 1.809x |
| yuv-wasm-codegen | 1 | 1.901x | 1.864x | 1.449x | 1.419x |
| yuv-wasm-codegen | 4 | 2.094x | 2.033x | 1.545x | 1.554x |

## Single-to-four CPU wall speedup

Median of the three within-run speedups (same runner for each pair).

| Workload | Linux x64 | Windows x64 | Linux Arm64 | Windows Arm64 |
|---|---:|---:|---:|---:|
| graphics-project | 2.384x | 2.352x | 3.469x | 3.460x |
| yuv-native-metadata | 0.975x | 1.084x | 0.989x | 0.976x |
| yuv-native-codegen | 2.630x | 2.348x | 3.644x | 3.391x |
| yuv-wasm-metadata | 1.004x | 1.109x | 0.981x | 0.993x |
| yuv-wasm-codegen | 2.626x | 2.551x | 3.649x | 3.485x |

## Compiler-own CPU share in project builds

| Platform | CPUs | Compiler CPU median | Share of all process-tree CPU |
|---|---:|---:|---:|
| linux-x64 | 1 | 131.39 | 98.54% |
| linux-x64 | 4 | 207.91 | 98.85% |
| windows-x64 | 1 | 258.64 | 98.92% |
| windows-x64 | 4 | 405.89 | 99.06% |
| linux-arm64 | 1 | 119.30 | 97.71% |
| linux-arm64 | 4 | 123.50 | 97.83% |
| windows-arm64 | 1 | 202.12 | 98.42% |
| windows-arm64 | 4 | 208.91 | 98.46% |
