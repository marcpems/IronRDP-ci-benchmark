# NASM omission with the merged ReFS setup

The apparent slowdown in the initial two-job comparison did not reproduce as
a systematic NASM-omission effect. All 24 repeated agent builds passed. Omitting
NASM reduced mean complete-job time by 40.25 seconds, with a nominal-block
bootstrap 95% interval of 26-57 seconds saved. Compilation itself showed no
clear penalty from omission.

## ReFS was included in both comparisons

The original two-job check and this replication both checked out upstream
`bf5d4a47a3006290f3804695de1980247fdc6829`, which descends from the merged
ReFS PR, `579979ea` ([#2186](https://github.com/Devolutions/IronRDP/pull/2186)).
Their storage step is identical to the upstream release workflow's merged
step, including populated-workspace preservation.

Every job verified ReFS on D:, the workspace junction to `D:\workspace`, and
`CARGO_HOME=D:\cargo-home`. TEMP/TMP also used the merged D: configuration.
The source was deliberately held constant with yesterday's comparison;
subsequent upstream source changes were not mixed into this experiment.

## What happened in the original pair

[Original run](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39649163283)
and [retained metadata](https://github.com/marcpems/IronRDP-ci-benchmark/blob/cdfa75a2/benchmarks/nasm-pr-validation/results.json).
Both jobs used image `20261018.189.1` and Cobalt 100.

| Stage | With NASM | Without NASM | Difference |
|---|---:|---:|---:|
| Job setup | 3 s | 4 s | +1 s |
| ReFS preparation | 13 s | 33 s | +20 s |
| Checkout | 8 s | 19 s | +11 s |
| NASM installation | 30 s | 0 s | -30 s |
| Rust cache setup | 15 s | 32 s | +17 s |
| Build step | 307 s | 339 s | +32 s |
| Complete job | 415 s | 467 s | +52 s |

The omission runner was already **32 seconds behind before the NASM stage**.
That delay cannot have been caused by skipping NASM.

The cache discrepancy was almost entirely before the action printed
`Cache Configuration`, not during a cache download. Both caches were cold.
In [rust-cache v2.9.1](https://github.com/Swatinem/rust-cache/tree/v2.9.1/src),
that preceding phase discovers toolchain versions, obtains workspace
metadata, and reads/hashes manifests and configuration. The logs do not
subdivide that phase sufficiently to identify its individual slow operation.

Both logs contain the same 364 `Compiling` entries and 336 crate downloads.
The logged crate-download spans were 5.10 and 5.42 seconds. The
first-compilation-to-finish spans were 296.73 and 328.98 seconds, respectively;
there was no expanded Rust dependency set or substantial extra download delay.

These observations identify where the extra time went, but not the original
VM's physical-host bottleneck. Those ephemeral machines are gone, and their
host-level scheduling, storage contention, and CPU-frequency traces were not
recorded. Matching image and CPU model does not guarantee identical throughput.

## Fixed-size replication

[Run 39747378333](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39747378333)
followed the committed [plan](plan.json): eight nominal scheduling blocks,
three variants, and at most 12 simultaneous jobs. Variant order within each
block was shuffled with a fixed seed. There were no result-dependent top-ups
or failed-job exclusions.

All jobs used `windows-11-arm`, four logical processors, Cobalt 100, the High
performance power plan, isolated cold caches, and unchanged security settings.
Eight jobs installed NASM, eight omitted it, and eight omitted it but waited
30 seconds to test a startup-settling explanation.

| Metric | With NASM | Without NASM | Without NASM + 30 s wait |
|---|---:|---:|---:|
| Successful jobs | 8/8 | 8/8 | 8/8 |
| Mean complete-job time | 469.0 s | 428.8 s | 452.1 s |
| Median complete-job time | 463.5 s | 427.5 s | 450.0 s |
| Mean NASM installation | 29.9 s | 0 s | 0 s |
| Mean Cargo elapsed time | 332.1 s | 327.6 s | 322.9 s |
| Mean Rust cache setup | 15.1 s | 15.3 s | 14.4 s |
| Mean guest CPU busy during build | 94.1% | 93.8% | 94.0% |

The complete-job mean reduction was **40.25 seconds / 8.6%**; the median
reduction was **36 seconds / 7.8%**. These instrumented jobs include common
diagnostic overhead. About 30 seconds is the eliminated installation;
the remainder includes variation in other stages, including a 3-second mean
difference in host-information collection. Do not attribute every saved
second to the removal or promise the exact percentage for production runs.

With 10,000 nominal-block bootstrap resamples:

- Omission minus baseline, mean job: **-40.25 s**, interval **[-57, -26]**.
- Omission minus baseline, mean Cargo: **-4.50 s**, interval **[-17.34, +8.40]**.
- Omission minus baseline, mean cache setup: **+0.13 s**, interval **[-2, +2]**.
- Waiting minus immediate omission, mean job: **+23.38 s**, interval
  **[+9.75, +37]**.
- Waiting minus immediate omission, mean Cargo: **-4.71 s**, interval
  **[-15.43, +5.05]**.

There is no clear compilation benefit from adding the delay, and it makes the
whole job slower. There is likewise no reproduced cache-initialization penalty
from omitting NASM.

### Image distribution and limitations

Image assignment was observed, not controlled. Counts for older/newer images
were 3/5 for baseline, 4/4 for omission, and 5/3 for the delay control.
The small image-specific subsets are descriptive:

| Image | Baseline n / mean job | Omission n / mean job |
|---|---:|---:|
| `20261013.183.4` | 3 / 471.0 s | 4 / 442.3 s |
| `20261018.189.1` | 5 / 467.8 s | 4 / 415.3 s |

The whole-job direction is the same within both images. Eight observations
per variant and nominal, rather than guaranteed simultaneous/machine-matched,
blocks still limit generalization. No universal image or physical-host cause
is established.

## Compilation and correctness checks

All 24 builds compiled the same **427 Cargo units with identical features**,
with zero fresh units. The native `aws-lc-sys` configuration remained
`aarch64-pc-windows-msvc`, `Building with: CC`, and `clang-cl` in every variant.
There is no evidence of a NASM-dependent fallback to a different build path.

Per-unit timings show overlapping variation in native dependency compilation,
Rust code generation, and the final agent build. For example, the agent library
unit ranged from 23.26 to 38.33 seconds without NASM. Unit durations overlap
because compilation is parallel; they must not be summed as wall-clock time.
The approximately 94% guest CPU activity indicates a busy compilation workload,
not a long idle network wait. These counters include all guest processes and
cannot independently identify hypervisor contention or attribute all CPU time
to rustc.

Both omission variants asserted NASM absence. Packaging, checksums, executable
`--help`, and ReFS-path checks passed in all 24 jobs. All **24 approximately
395 MB caches** were independently confirmed through GitHub's cache API.
This campaign tested the agent, not a new viewer build; earlier viewer linker
failures remain a separate issue.

The evidence supports removing the unused NASM installation, retaining the
merged ReFS setup, and not adding an artificial wait. The original two-job
result was an unrepresentative comparison, not proof that NASM omission slows
the build.

## Retained data and reproduction

`measurements.json` contains job metadata, cache inventory, host/CPU observations,
native compiler configuration, and all per-unit Cargo timing records.
`summary.json` is derived without contacting GitHub:

```powershell
python .\benchmarks\nasm-refs-replication\analyze.py `
  --output "$env:TEMP\nasm-replication-summary.json"
```

The fork-only workflow retains the raw HTML timing reports as artifacts.
No release workflow or upstream PR was changed by this investigation.
