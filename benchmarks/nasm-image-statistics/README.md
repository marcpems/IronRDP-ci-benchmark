# NASM installation on two Windows Arm runner images

## Result

128 fresh-runner jobs completed successfully, with up to 16 running concurrently.
Eight earlier instrumentation canaries also passed but are excluded from the
statistical cohort. All main jobs used one of the two requested image versions;
none were excluded, failed, or removed as outliers.

**The default-storage comparison does not establish a median slowdown on the
newer image. The ReFS-configured comparison shows a slowdown signal, but the
data do not establish that ReFS itself caused it.**

These are NASM command timings, not complete release-build times.

| Actual image version | Storage setup | Jobs | Median | 10th percentile | 90th percentile |
|---|---|---:|---:|---:|---:|
| `20261013.183.4` | Default | 37 | 28.70 s | 24.50 s | 38.79 s |
| `20261018.189.1` | Default | 27 | 31.02 s | 25.51 s | 63.38 s |
| `20261013.183.4` | ReFS candidate | 32 | 27.73 s | 25.59 s | 29.80 s |
| `20261018.189.1` | ReFS candidate | 32 | 53.27 s | 26.05 s | 98.26 s |

The 10th/90th percentiles describe the distribution of individual measurements;
they are not confidence intervals for the median.

### Image contrasts

10,000 bootstrap replicates resampled complete balanced scheduling blocks.
Intervals below are nominal 95% percentile intervals, not simultaneous
multiple-comparison intervals.

| Comparison: newer minus older image | Median difference | 95% interval | Relative difference | 95% interval |
|---|---:|---:|---:|---:|
| Default storage (primary) | +2.32 s | -2.82 to +12.90 s | +8.1% | -9.3% to +44.0% |
| ReFS candidate (secondary) | +25.53 s | +1.51 to +33.00 s | +92.1% | +5.4% to +118.3% |

The primary interval includes zero: this is not evidence of equivalence, nor
does it rule out a substantial slowdown. The secondary contrast is positive,
but should not be generalized into an image-wide regression.

Exploratory direct storage comparisons provide an important caution:

- On the older image, ReFS minus default is -0.97 s, with interval
  -3.62 to +0.43 s.
- On the newer image, ReFS minus default is +22.24 s, with interval
  -1.25 to +31.29 s.
- The difference between those two storage effects is +23.21 s, with interval
  -0.04 to +32.55 s.

These intervals include zero. A significant contrast in one storage group
and an inconclusive contrast in another is not, by itself, proof of an
image-by-storage interaction. No extra samples were requested to chase a
significance threshold.

## Where the elapsed time went

For the ReFS-configured jobs:

| Phase, median | Older image | Newer image |
|---|---:|---:|
| Command start to Chocolatey banner | 11.21 s | 21.84 s |
| Banner to package ready | 7.16 s | 11.44 s |
| Package ready to installer start | 6.25 s | 12.59 s |
| NASM installer execution | 2.16 s | 4.00 s |
| Finishing | 0.80 s | 1.07 s |

Phase medians do not necessarily sum to the median total. The explicitly
logged download/package-ready interval, a subset of the second row, was
1.01 s versus 1.43 s. This interval includes processing at its boundaries and
does not capture every repository lookup or network wait.

Most of the larger elapsed-time difference appears before the actual NASM
installer runs. It is not explained by the logged package-transfer interval
alone.

### Whole-machine resource observations

| Metric, median, ReFS group | Older image | Newer image |
|---|---:|---:|
| Busy CPU time, summed across four processors | 18.29 CPU-s | 23.41 CPU-s |
| Average utilization across four processors | 15.75% | 11.83% |
| Physical disk bytes read | 144.77 MiB | 158.24 MiB |
| Network bytes received | 12.09 MiB | 19.10 MiB |

The extra elapsed time is much larger than the increase in CPU work, and
the machine is not saturating all four processors. This does not exclude
single-thread CPU bottlenecks. The pattern is consistent with additional
waiting or background contention, rather than simply more computation or a
slower NASM payload download. Byte counts alone cannot identify which resource
was responsible for that waiting.

**Disk-latency telemetry is not used.** Sixteen jobs produced impossible
negative latency deltas, consistent with raw counter rollover/reset. The
original counter snapshots were not retained, so these values cannot be
reliably repaired. All latency fields, including positive ones, are excluded
from the analysis; the original values remain in the archived measurements
for transparency. The future workflow removes this unreliable measurement.
The independently measured command timings and nonnegative CPU/byte counters
are retained.

These counters cover the entire VM, including Windows background activity and
all physical disks. They do not isolate Chocolatey, distinguish C: from D:,
or prove that storage, antivirus, network services, or an image component
caused the slowdown. A CPU/disk/network percentage attribution would require
process-level tracing; it cannot be recovered from these aggregate counters.

## Runner labels are not separate hardware treatments

127 main observations reported Cobalt 100 and one reported Cobalt 200; all had
four logical processors. Both labels used the `win11-vs2026-arm64` image family. All installations
reported Chocolatey 2.7.4 and NASM 3.2.0.

The Cobalt 200 observation was a newer-image ReFS job that completed in
25.16 s. It was retained in the primary analysis. An explicit Cobalt-100-only
sensitivity analysis changes the newer-image ReFS median to 54.22 s and the
image contrast to +26.49 s (95% interval +3.84 to +33.30 s). Thus that single,
faster hardware sample does not explain the slowdown signal. See
`sensitivity-cobalt100.json`.

| Label | Image | Default jobs / median | ReFS jobs / median |
|---|---|---:|---:|
| `windows-11-arm` | Older | 18 / 31.04 s | 16 / 27.93 s |
| `windows-11-vs2026-arm` | Older | 19 / 28.37 s | 16 / 27.59 s |
| `windows-11-arm` | Newer | 14 / 31.16 s | 16 / 39.35 s |
| `windows-11-vs2026-arm` | Newer | 13 / 29.63 s | 16 / 55.81 s |

Those smaller subdivisions are descriptive. They do not establish a
label-specific performance difference.

## Method and limitations

- Main run: [39579652894][main], workflow commit `b58cae7a`.
  The full SHA is recorded in `summary.json` and every measurement.
  The workflow itself is available through the run.
- Canary run: [39579207024][canary], eight jobs used only to validate the
  instrumentation.
- 32 nominal scheduling blocks each contained both labels and both storage
  modes. Order within each block was shuffled with seed `20261021`.
  GitHub controls actual start order and VM/image assignment; a matrix block
  is not a guarantee of simultaneous execution.
- Image versions were recorded on the actual VM. A third image would have
  been excluded without installing NASM or changing its disks.
- The count-driven rule was 128 initial jobs, with at most one additional
  balanced batch if an image/storage cell had fewer than 25 successes and
  both images remained available. The smallest cell had 27, so no top-up
  was performed. The rule did not depend on the effect size or interval.
- The command was the production `choco install nasm`, on a fresh hosted VM.
  A stopwatch and timestamped output milestones measured it. Progress
  output was filtered, and machine counters were read before and after.
  Instrumentation and output handling differ from the original uninstrumented
  production step, so absolute timings should not be merged with that pilot.
- CPU deltas use Windows `GetSystemTimes`. Disk bytes and counts use raw
  physical-disk performance counters. The attempted average-latency counters
  failed data-quality checks and are not interpreted. Network byte deltas sum active
  non-loopback/non-tunnel interfaces.
- Resource snapshots straddle the command and include some instrumentation
  overhead and background activity; only command time is the primary outcome.
- The ReFS variant uses the previously tested guarded candidate preparation:
  workspace and Cargo home on D:, compiler temp on D:, no existing-volume
  reformatting, no antivirus exclusions, and no agent reconfiguration.
  Chocolatey and NASM retain their default C: installation locations.
- The image assignment is observational, not randomized or pinnable through
  these labels. Boot state, host contention and time variation remain
  possible confounders. Bootstrap intervals describe uncertainty in this
  cohort, not a guarantee about all GitHub runners.
- This experiment does not rerun Cargo compilation and does not demonstrate
  a full release-build improvement. The decision not to open the upstream
  performance PR is unchanged.

## Reproduce the analysis

`measurements.json` preserves all 128 artifacts plus GitHub job outcomes,
step timestamps and links. `summary.json` contains the estimates, resource
summaries, subgroup counts and confidence intervals. `analysis-plan.json`
records the comparison and sampling rules specified before the main results
were read. The direct storage and interaction estimates are explicitly
exploratory additions.

Python's standard library is sufficient for offline reanalysis:

```powershell
python .\benchmarks\nasm-image-statistics\analyze.py --data .\benchmarks\nasm-image-statistics\measurements.json
```

This writes `nasm-summary-offline.json` and `nasm-measurements-offline.json`
beside the script. The seed and all 10,000 bootstrap draws are deterministic.
Live collection also accepts a run ID and requires authenticated `gh`;
`GH_EXECUTABLE` can specify its executable path.

The fork-only measurement workflow is `.github/workflows/nasm-image-statistics.yml`
on `perf/windows-arm-nasm-statistics`. A fresh push to that branch runs another
128-job batch; no release or upstream PR is created.

[main]: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39579652894
[canary]: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39579207024
