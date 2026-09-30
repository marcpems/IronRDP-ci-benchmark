# Measured native Cargo command breakdown

Wall seconds, median [min-max]. Complete successful native sequences only.
Unit-seconds are overlapping elapsed intervals, not CPU-seconds.

| Command | linux-arm64 | linux-x64 | windows-arm64 | windows-x64 |
|---|---:|---:|---:|---:|
| xtask-bootstrap | 2.25 [2.13-2.29], n=3 | 2.49 [2.26-2.69], n=3 | 6.06 [3.78-13.05], n=3 | 7.92 [6.48-12.63], n=3 |
| workspace-tests | 326.28 [313.55-332.24], n=3 | 432.21 [384.49-451.39], n=3 | 543.04 [520.50-570.74], n=3 | 790.08 [606.37-967.15], n=3 |
| native-tls-tests | 9.28 [8.97-9.56], n=3 | 10.86 [9.46-10.98], n=3 | 16.54 [15.29-17.07], n=3 | 17.40 [13.64-21.19], n=3 |
| gateway-native-tls-tests | 45.26 [42.97-45.31], n=3 | 57.18 [50.52-57.73], n=3 | 73.71 [70.03-75.42], n=3 | 94.21 [73.83-119.28], n=3 |
| gateway-smartcard-tests | 40.33 [38.86-40.80], n=3 | 50.63 [46.32-51.63], n=3 | 72.64 [69.34-73.37], n=3 | 94.56 [72.35-116.95], n=3 |
| native-total | 424.25 [406.48-429.36], n=3 | 555.03 [493.07-572.74], n=3 | 714.95 [678.94-746.69], n=3 | 1008.89 [774.10-1231.04], n=3 |

## linux-arm64 replicate 1

Native complete: True

| Command | Wall | Compiler only | Build scripts only | Overlap | Outside units | Unit-seconds | Units | System CPU % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xtask-bootstrap | 2.29 | 2.05 | 0.00 | 0.04 | 0.20 | 3.48 | 8 | 75.2 |
| workspace-tests | 326.28 | 240.44 | 0.00 | 85.28 | 0.56 | 1282.61 | 739 | 94.7 |
| native-tls-tests | 9.56 | 9.28 | 0.00 | 0.07 | 0.21 | 27.64 | 25 | 85.0 |
| gateway-native-tls-tests | 45.31 | 44.92 | 0.00 | 0.09 | 0.30 | 151.37 | 122 | 93.6 |
| gateway-smartcard-tests | 40.80 | 40.47 | 0.00 | 0.03 | 0.30 | 134.27 | 63 | 95.4 |

### Longest workspace-test units

| Package | Target | Origin | Unit seconds | Sole-active seconds |
|---|---|---|---:|---:|
| ironrdp-testsuite-core 0.0.0 |  test "integration_tests_core" (test) | workspace | 74.05 | 0.00 |
| yuv 0.8.16 |  | dependency | 66.31 | 0.00 |
| aws-lc-sys 0.42.0 |  build script (run) | dependency | 59.64 | 0.00 |
| ironrdp-testsuite-extra 0.1.0 |  test "integration_tests_extra" (test) | workspace | 48.34 | 0.00 |
| ironrdp-daemon 0.1.0 |  | workspace | 42.05 | 0.00 |
| ironrdp-daemon 0.1.0 |  lib (test) | workspace | 30.87 | 3.77 |
| x11rb-protocol 0.13.2 |  | dependency | 28.54 | 0.00 |
| sspi 0.21.3 |  | dependency | 27.75 | 0.00 |
| ironrdp-pdu 0.9.0 |  | workspace | 23.58 | 0.00 |
| ironrdp 0.17.0 |  example "server" | workspace | 23.15 | 0.00 |
| zstd-sys 2.0.16+zstd.1.5.7 |  build script (run) | dependency | 21.37 | 0.00 |
| picky 7.0.0-rc.25 |  | dependency | 19.95 | 0.00 |

## linux-arm64 replicate 2

Native complete: True

| Command | Wall | Compiler only | Build scripts only | Overlap | Outside units | Unit-seconds | Units | System CPU % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xtask-bootstrap | 2.25 | 1.99 | 0.00 | 0.05 | 0.21 | 3.39 | 8 | 75.7 |
| workspace-tests | 332.24 | 246.31 | 0.00 | 85.38 | 0.55 | 1307.06 | 739 | 94.9 |
| native-tls-tests | 9.28 | 9.02 | 0.00 | 0.06 | 0.20 | 26.97 | 25 | 86.2 |
| gateway-native-tls-tests | 45.26 | 44.86 | 0.00 | 0.10 | 0.30 | 150.32 | 122 | 92.7 |
| gateway-smartcard-tests | 40.33 | 39.99 | 0.00 | 0.03 | 0.31 | 133.00 | 63 | 95.2 |

### Longest workspace-test units

| Package | Target | Origin | Unit seconds | Sole-active seconds |
|---|---|---|---:|---:|
| ironrdp-testsuite-core 0.0.0 |  test "integration_tests_core" (test) | workspace | 74.20 | 0.00 |
| yuv 0.8.16 |  | dependency | 67.55 | 0.00 |
| aws-lc-sys 0.42.0 |  build script (run) | dependency | 59.25 | 0.00 |
| ironrdp-testsuite-extra 0.1.0 |  test "integration_tests_extra" (test) | workspace | 49.00 | 0.00 |
| ironrdp-daemon 0.1.0 |  | workspace | 43.10 | 0.00 |
| ironrdp-daemon 0.1.0 |  lib (test) | workspace | 30.64 | 3.02 |
| x11rb-protocol 0.13.2 |  | dependency | 29.67 | 0.00 |
| sspi 0.21.3 |  | dependency | 29.01 | 0.00 |
| ironrdp 0.17.0 |  example "server" | workspace | 23.40 | 0.00 |
| ironrdp-pdu 0.9.0 |  | workspace | 23.39 | 0.00 |
| zstd-sys 2.0.16+zstd.1.5.7 |  build script (run) | dependency | 21.37 | 0.00 |
| picky 7.0.0-rc.25 |  | dependency | 19.92 | 0.00 |

## linux-arm64 replicate 3

Native complete: True

| Command | Wall | Compiler only | Build scripts only | Overlap | Outside units | Unit-seconds | Units | System CPU % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xtask-bootstrap | 2.13 | 1.91 | 0.00 | 0.04 | 0.18 | 3.22 | 8 | 74.5 |
| workspace-tests | 313.55 | 230.81 | 0.00 | 82.23 | 0.51 | 1230.99 | 739 | 94.7 |
| native-tls-tests | 8.97 | 8.75 | 0.00 | 0.03 | 0.19 | 26.14 | 25 | 84.5 |
| gateway-native-tls-tests | 42.97 | 42.60 | 0.00 | 0.08 | 0.29 | 140.81 | 122 | 93.2 |
| gateway-smartcard-tests | 38.86 | 38.55 | 0.00 | 0.02 | 0.29 | 124.46 | 63 | 94.5 |

### Longest workspace-test units

| Package | Target | Origin | Unit seconds | Sole-active seconds |
|---|---|---|---:|---:|
| ironrdp-testsuite-core 0.0.0 |  test "integration_tests_core" (test) | workspace | 69.43 | 0.00 |
| yuv 0.8.16 |  | dependency | 65.21 | 0.00 |
| aws-lc-sys 0.42.0 |  build script (run) | dependency | 58.71 | 0.00 |
| ironrdp-testsuite-extra 0.1.0 |  test "integration_tests_extra" (test) | workspace | 45.58 | 0.00 |
| ironrdp-daemon 0.1.0 |  | workspace | 40.71 | 0.00 |
| x11rb-protocol 0.13.2 |  | dependency | 27.83 | 0.00 |
| sspi 0.21.3 |  | dependency | 27.51 | 0.00 |
| ironrdp-daemon 0.1.0 |  lib (test) | workspace | 27.22 | 4.45 |
| ironrdp-pdu 0.9.0 |  | workspace | 22.33 | 0.00 |
| ironrdp 0.17.0 |  example "server" | workspace | 21.97 | 0.00 |
| zstd-sys 2.0.16+zstd.1.5.7 |  build script (run) | dependency | 21.33 | 0.00 |
| picky 7.0.0-rc.25 |  | dependency | 19.25 | 0.00 |

## linux-x64 replicate 1

Native complete: True

| Command | Wall | Compiler only | Build scripts only | Overlap | Outside units | Unit-seconds | Units | System CPU % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xtask-bootstrap | 2.69 | 2.41 | 0.00 | 0.05 | 0.23 | 4.09 | 8 | 80.6 |
| workspace-tests | 451.39 | 319.57 | 0.00 | 131.17 | 0.65 | 1778.88 | 741 | 96.7 |
| native-tls-tests | 10.86 | 10.55 | 0.00 | 0.08 | 0.23 | 31.92 | 25 | 90.2 |
| gateway-native-tls-tests | 57.18 | 56.73 | 0.00 | 0.13 | 0.32 | 193.43 | 119 | 95.9 |
| gateway-smartcard-tests | 50.63 | 50.27 | 0.00 | 0.03 | 0.33 | 169.00 | 63 | 97.9 |

### Longest workspace-test units

| Package | Target | Origin | Unit seconds | Sole-active seconds |
|---|---|---|---:|---:|
| yuv 0.8.16 |  | dependency | 133.23 | 0.00 |
| ironrdp-testsuite-core 0.0.0 |  test "integration_tests_core" (test) | workspace | 91.73 | 0.00 |
| aws-lc-sys 0.42.0 |  build script (run) | dependency | 89.10 | 0.00 |
| ironrdp-testsuite-extra 0.1.0 |  test "integration_tests_extra" (test) | workspace | 61.83 | 0.00 |
| ironrdp-daemon 0.1.0 |  | workspace | 57.63 | 0.00 |
| sspi 0.21.3 |  | dependency | 43.25 | 0.00 |
| x11rb-protocol 0.13.2 |  | dependency | 38.95 | 0.00 |
| ironrdp-daemon 0.1.0 |  lib (test) | workspace | 36.28 | 5.27 |
| libopus_sys 0.3.3 |  build script (run) | dependency | 34.74 | 0.00 |
| ironrdp-pdu 0.9.0 |  | workspace | 33.35 | 0.00 |
| ironrdp 0.17.0 |  example "server" | workspace | 29.10 | 0.00 |
| zstd-sys 2.0.16+zstd.1.5.7 |  build script (run) | dependency | 28.34 | 0.00 |

## linux-x64 replicate 2

Native complete: True

| Command | Wall | Compiler only | Build scripts only | Overlap | Outside units | Unit-seconds | Units | System CPU % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xtask-bootstrap | 2.26 | 2.02 | 0.00 | 0.05 | 0.19 | 3.42 | 8 | 82.6 |
| workspace-tests | 384.49 | 271.71 | 0.00 | 112.33 | 0.45 | 1516.15 | 741 | 96.3 |
| native-tls-tests | 9.46 | 9.22 | 0.00 | 0.06 | 0.18 | 28.36 | 25 | 90.4 |
| gateway-native-tls-tests | 50.52 | 50.15 | 0.00 | 0.11 | 0.26 | 166.98 | 119 | 96.6 |
| gateway-smartcard-tests | 46.32 | 45.97 | 0.00 | 0.03 | 0.32 | 154.02 | 63 | 97.9 |

### Longest workspace-test units

| Package | Target | Origin | Unit seconds | Sole-active seconds |
|---|---|---|---:|---:|
| yuv 0.8.16 |  | dependency | 109.59 | 0.00 |
| ironrdp-testsuite-core 0.0.0 |  test "integration_tests_core" (test) | workspace | 84.54 | 0.00 |
| aws-lc-sys 0.42.0 |  build script (run) | dependency | 78.60 | 0.00 |
| ironrdp-testsuite-extra 0.1.0 |  test "integration_tests_extra" (test) | workspace | 56.50 | 0.00 |
| ironrdp-daemon 0.1.0 |  | workspace | 51.60 | 0.00 |
| sspi 0.21.3 |  | dependency | 35.17 | 0.00 |
| ironrdp-daemon 0.1.0 |  lib (test) | workspace | 35.00 | 4.27 |
| x11rb-protocol 0.13.2 |  | dependency | 34.03 | 0.00 |
| libopus_sys 0.3.3 |  build script (run) | dependency | 27.90 | 0.00 |
| ironrdp-pdu 0.9.0 |  | workspace | 26.83 | 0.00 |
| ironrdp 0.17.0 |  example "server" | workspace | 26.62 | 0.00 |
| zstd-sys 2.0.16+zstd.1.5.7 |  build script (run) | dependency | 22.91 | 0.00 |

## linux-x64 replicate 3

Native complete: True

| Command | Wall | Compiler only | Build scripts only | Overlap | Outside units | Unit-seconds | Units | System CPU % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xtask-bootstrap | 2.49 | 2.22 | 0.00 | 0.05 | 0.22 | 3.85 | 8 | 83.3 |
| workspace-tests | 432.21 | 301.41 | 0.00 | 130.22 | 0.58 | 1713.85 | 741 | 96.5 |
| native-tls-tests | 10.98 | 10.69 | 0.00 | 0.07 | 0.22 | 32.14 | 25 | 89.8 |
| gateway-native-tls-tests | 57.73 | 57.27 | 0.00 | 0.14 | 0.32 | 196.32 | 119 | 96.4 |
| gateway-smartcard-tests | 51.63 | 51.28 | 0.00 | 0.03 | 0.32 | 172.87 | 63 | 97.9 |

### Longest workspace-test units

| Package | Target | Origin | Unit seconds | Sole-active seconds |
|---|---|---|---:|---:|
| yuv 0.8.16 |  | dependency | 121.56 | 0.00 |
| ironrdp-testsuite-core 0.0.0 |  test "integration_tests_core" (test) | workspace | 93.40 | 0.00 |
| aws-lc-sys 0.42.0 |  build script (run) | dependency | 87.70 | 0.00 |
| ironrdp-testsuite-extra 0.1.0 |  test "integration_tests_extra" (test) | workspace | 60.90 | 0.00 |
| ironrdp-daemon 0.1.0 |  | workspace | 58.17 | 0.00 |
| ironrdp-daemon 0.1.0 |  lib (test) | workspace | 44.05 | 0.99 |
| x11rb-protocol 0.13.2 |  | dependency | 39.74 | 0.00 |
| sspi 0.21.3 |  | dependency | 38.96 | 0.00 |
| libopus_sys 0.3.3 |  build script (run) | dependency | 35.16 | 0.00 |
| ironrdp-pdu 0.9.0 |  | workspace | 29.77 | 0.00 |
| ironrdp 0.17.0 |  example "server" | workspace | 28.72 | 0.00 |
| zstd-sys 2.0.16+zstd.1.5.7 |  build script (run) | dependency | 26.70 | 0.00 |

## windows-arm64 replicate 1

Native complete: True

| Command | Wall | Compiler only | Build scripts only | Overlap | Outside units | Unit-seconds | Units | System CPU % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xtask-bootstrap | 13.05 | 12.43 | 0.00 | 0.14 | 0.48 | 24.54 | 8 | 21.7 |
| workspace-tests | 570.74 | 258.37 | 0.00 | 308.93 | 3.44 | 2240.52 | 691 | 91.7 |
| native-tls-tests | 16.54 | 16.02 | 0.00 | 0.00 | 0.52 | 36.85 | 15 | 74.6 |
| gateway-native-tls-tests | 73.71 | 72.51 | 0.00 | 0.43 | 0.77 | 243.47 | 123 | 93.2 |
| gateway-smartcard-tests | 72.64 | 71.70 | 0.00 | 0.12 | 0.82 | 230.82 | 77 | 91.1 |

### Longest workspace-test units

| Package | Target | Origin | Unit seconds | Sole-active seconds |
|---|---|---|---:|---:|
| aws-lc-sys 0.42.0 |  build script (run) | dependency | 156.32 | 0.00 |
| ironrdp-testsuite-core 0.0.0 |  test "integration_tests_core" (test) | workspace | 108.86 | 0.00 |
| yuv 0.8.16 |  | dependency | 108.62 | 0.00 |
| libopus_sys 0.3.3 |  build script (run) | dependency | 89.56 | 0.00 |
| windows 0.62.2 |  | dependency | 80.11 | 0.00 |
| ironrdp-testsuite-extra 0.1.0 |  test "integration_tests_extra" (test) | workspace | 73.40 | 0.00 |
| ironrdp-daemon 0.1.0 |  | workspace | 66.44 | 0.00 |
| ironrdp-activex 0.1.0 |  lib (test) | workspace | 62.55 | 0.00 |
| sspi 0.21.3 |  | dependency | 45.66 | 0.00 |
| ironrdp-daemon 0.1.0 |  lib (test) | workspace | 43.60 | 4.15 |
| ironrdp-pdu 0.9.0 |  | workspace | 37.53 | 0.00 |
| picky 7.0.0-rc.25 |  | dependency | 35.32 | 0.00 |

## windows-arm64 replicate 2

Native complete: True

| Command | Wall | Compiler only | Build scripts only | Overlap | Outside units | Unit-seconds | Units | System CPU % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xtask-bootstrap | 3.78 | 3.05 | 0.00 | 0.17 | 0.56 | 5.90 | 8 | 80.4 |
| workspace-tests | 520.50 | 324.59 | 0.00 | 194.37 | 1.54 | 2067.83 | 691 | 96.6 |
| native-tls-tests | 15.29 | 14.78 | 0.00 | 0.00 | 0.51 | 34.95 | 15 | 77.6 |
| gateway-native-tls-tests | 70.03 | 68.86 | 0.00 | 0.43 | 0.74 | 237.07 | 123 | 95.1 |
| gateway-smartcard-tests | 69.34 | 68.35 | 0.00 | 0.12 | 0.87 | 220.20 | 77 | 91.4 |

### Longest workspace-test units

| Package | Target | Origin | Unit seconds | Sole-active seconds |
|---|---|---|---:|---:|
| aws-lc-sys 0.42.0 |  build script (run) | dependency | 117.25 | 0.00 |
| yuv 0.8.16 |  | dependency | 104.09 | 0.00 |
| ironrdp-testsuite-core 0.0.0 |  test "integration_tests_core" (test) | workspace | 102.90 | 0.00 |
| windows 0.62.2 |  | dependency | 80.45 | 0.00 |
| ironrdp-testsuite-extra 0.1.0 |  test "integration_tests_extra" (test) | workspace | 69.44 | 0.00 |
| ironrdp-daemon 0.1.0 |  | workspace | 62.93 | 0.00 |
| ironrdp-activex 0.1.0 |  lib (test) | workspace | 59.33 | 0.00 |
| ironrdp-daemon 0.1.0 |  lib (test) | workspace | 57.85 | 0.00 |
| libopus_sys 0.3.3 |  build script (run) | dependency | 54.94 | 0.00 |
| sspi 0.21.3 |  | dependency | 42.08 | 0.00 |
| ironrdp-pdu 0.9.0 |  | workspace | 38.14 | 0.00 |
| picky 7.0.0-rc.25 |  | dependency | 32.73 | 0.00 |

## windows-arm64 replicate 3

Native complete: True

| Command | Wall | Compiler only | Build scripts only | Overlap | Outside units | Unit-seconds | Units | System CPU % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xtask-bootstrap | 6.06 | 5.43 | 0.00 | 0.13 | 0.50 | 10.68 | 8 | 55.3 |
| workspace-tests | 543.04 | 339.67 | 0.00 | 201.74 | 1.63 | 2155.68 | 691 | 96.2 |
| native-tls-tests | 17.07 | 16.52 | 0.00 | 0.00 | 0.55 | 36.95 | 15 | 74.6 |
| gateway-native-tls-tests | 75.42 | 74.19 | 0.00 | 0.42 | 0.81 | 249.29 | 123 | 93.7 |
| gateway-smartcard-tests | 73.37 | 72.35 | 0.00 | 0.12 | 0.90 | 232.81 | 77 | 91.4 |

### Longest workspace-test units

| Package | Target | Origin | Unit seconds | Sole-active seconds |
|---|---|---|---:|---:|
| aws-lc-sys 0.42.0 |  build script (run) | dependency | 119.49 | 0.00 |
| ironrdp-testsuite-core 0.0.0 |  test "integration_tests_core" (test) | workspace | 109.77 | 0.00 |
| yuv 0.8.16 |  | dependency | 107.70 | 0.00 |
| windows 0.62.2 |  | dependency | 81.70 | 0.00 |
| ironrdp-testsuite-extra 0.1.0 |  test "integration_tests_extra" (test) | workspace | 75.21 | 0.00 |
| ironrdp-daemon 0.1.0 |  | workspace | 67.13 | 0.00 |
| ironrdp-activex 0.1.0 |  lib (test) | workspace | 63.57 | 0.00 |
| ironrdp-daemon 0.1.0 |  lib (test) | workspace | 61.38 | 0.00 |
| libopus_sys 0.3.3 |  build script (run) | dependency | 54.04 | 0.00 |
| sspi 0.21.3 |  | dependency | 44.11 | 0.00 |
| ironrdp-pdu 0.9.0 |  | workspace | 38.85 | 0.00 |
| ironrdp 0.17.0 |  example "server" | workspace | 34.79 | 0.00 |

## windows-x64 replicate 1

Native complete: True

| Command | Wall | Compiler only | Build scripts only | Overlap | Outside units | Unit-seconds | Units | System CPU % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xtask-bootstrap | 6.48 | 5.89 | 0.00 | 0.12 | 0.47 | 11.19 | 8 | 72.7 |
| workspace-tests | 967.15 | 660.73 | 0.00 | 305.18 | 1.24 | 3817.11 | 693 | 98.5 |
| native-tls-tests | 21.19 | 20.66 | 0.00 | 0.00 | 0.53 | 49.97 | 15 | 82.9 |
| gateway-native-tls-tests | 119.28 | 118.14 | 0.00 | 0.37 | 0.77 | 409.26 | 123 | 98.9 |
| gateway-smartcard-tests | 116.95 | 116.08 | 0.00 | 0.09 | 0.78 | 393.71 | 77 | 98.4 |

### Longest workspace-test units

| Package | Target | Origin | Unit seconds | Sole-active seconds |
|---|---|---|---:|---:|
| yuv 0.8.16 |  | dependency | 302.55 | 0.00 |
| aws-lc-sys 0.42.0 |  build script (run) | dependency | 216.56 | 0.00 |
| ironrdp-testsuite-core 0.0.0 |  test "integration_tests_core" (test) | workspace | 210.95 | 0.00 |
| ironrdp-testsuite-extra 0.1.0 |  test "integration_tests_extra" (test) | workspace | 144.28 | 0.00 |
| ironrdp-daemon 0.1.0 |  | workspace | 131.98 | 0.00 |
| ironrdp-activex 0.1.0 |  lib (test) | workspace | 118.71 | 0.00 |
| windows 0.62.2 |  | dependency | 114.70 | 0.00 |
| sspi 0.21.3 |  | dependency | 84.45 | 0.00 |
| ironrdp-daemon 0.1.0 |  lib (test) | workspace | 83.90 | 4.92 |
| libopus_sys 0.3.3 |  build script (run) | dependency | 70.13 | 0.00 |
| ironrdp-pdu 0.9.0 |  | workspace | 65.64 | 0.00 |
| ironrdp 0.17.0 |  example "server" | workspace | 63.50 | 0.00 |

## windows-x64 replicate 2

Native complete: True

| Command | Wall | Compiler only | Build scripts only | Overlap | Outside units | Unit-seconds | Units | System CPU % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xtask-bootstrap | 12.63 | 4.38 | 0.00 | 0.16 | 8.09 | 7.91 | 8 | 85.9 |
| workspace-tests | 790.08 | 536.10 | 0.00 | 246.41 | 7.57 | 3089.29 | 693 | 97.5 |
| native-tls-tests | 17.40 | 16.94 | 0.00 | 0.00 | 0.46 | 40.68 | 15 | 82.8 |
| gateway-native-tls-tests | 94.21 | 93.19 | 0.00 | 0.36 | 0.66 | 313.73 | 123 | 98.4 |
| gateway-smartcard-tests | 94.56 | 93.77 | 0.00 | 0.08 | 0.71 | 322.72 | 77 | 98.7 |

### Longest workspace-test units

| Package | Target | Origin | Unit seconds | Sole-active seconds |
|---|---|---|---:|---:|
| yuv 0.8.16 |  | dependency | 240.87 | 0.00 |
| aws-lc-sys 0.42.0 |  build script (run) | dependency | 172.83 | 0.00 |
| ironrdp-testsuite-core 0.0.0 |  test "integration_tests_core" (test) | workspace | 170.61 | 0.00 |
| ironrdp-testsuite-extra 0.1.0 |  test "integration_tests_extra" (test) | workspace | 115.61 | 0.00 |
| ironrdp-daemon 0.1.0 |  | workspace | 105.60 | 0.00 |
| ironrdp-activex 0.1.0 |  lib (test) | workspace | 94.94 | 0.00 |
| windows 0.62.2 |  | dependency | 94.89 | 0.00 |
| sspi 0.21.3 |  | dependency | 71.62 | 0.00 |
| ironrdp-daemon 0.1.0 |  lib (test) | workspace | 64.38 | 5.56 |
| ironrdp-pdu 0.9.0 |  | workspace | 56.14 | 0.00 |
| ironrdp 0.17.0 |  example "server" | workspace | 50.24 | 0.00 |
| libopus_sys 0.3.3 |  build script (run) | dependency | 49.49 | 0.00 |

## windows-x64 replicate 3

Native complete: True

| Command | Wall | Compiler only | Build scripts only | Overlap | Outside units | Unit-seconds | Units | System CPU % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xtask-bootstrap | 7.92 | 7.50 | 0.00 | 0.09 | 0.33 | 13.73 | 8 | 43.5 |
| workspace-tests | 606.37 | 287.93 | 0.00 | 317.57 | 0.87 | 2397.23 | 693 | 90.2 |
| native-tls-tests | 13.64 | 13.17 | 0.00 | 0.00 | 0.47 | 30.62 | 15 | 79.9 |
| gateway-native-tls-tests | 73.83 | 72.90 | 0.00 | 0.23 | 0.70 | 252.63 | 123 | 98.6 |
| gateway-smartcard-tests | 72.35 | 71.65 | 0.00 | 0.05 | 0.65 | 247.15 | 77 | 98.6 |

### Longest workspace-test units

| Package | Target | Origin | Unit seconds | Sole-active seconds |
|---|---|---|---:|---:|
| libopus_sys 0.3.3 |  build script (run) | dependency | 170.07 | 0.00 |
| yuv 0.8.16 |  | dependency | 157.86 | 0.00 |
| aws-lc-sys 0.42.0 |  build script (run) | dependency | 136.39 | 0.00 |
| ironrdp-testsuite-core 0.0.0 |  test "integration_tests_core" (test) | workspace | 126.15 | 0.00 |
| vswhom-sys 0.1.3 |  build script (run) | dependency | 76.95 | 0.00 |
| ironrdp-daemon 0.1.0 |  | workspace | 75.14 | 0.00 |
| ironrdp-testsuite-extra 0.1.0 |  test "integration_tests_extra" (test) | workspace | 74.50 | 2.67 |
| ironrdp-activex 0.1.0 |  lib (test) | workspace | 73.46 | 0.00 |
| ironrdp-daemon 0.1.0 |  lib (test) | workspace | 73.00 | 0.00 |
| windows 0.62.2 |  | dependency | 65.92 | 0.00 |
| sspi 0.21.3 |  | dependency | 48.24 | 0.00 |
| ironrdp-pdu 0.9.0 |  | workspace | 38.05 | 0.00 |
