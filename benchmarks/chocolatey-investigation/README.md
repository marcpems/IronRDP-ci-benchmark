# Chocolatey startup and NASM setup investigation

## Conclusions

The investigation located the large delays in Chocolatey startup and embedded
Windows PowerShell initialization, but did **not** identify the underlying Windows
wait or establish that a particular image update caused it. No configuration
tweak tested here reliably recovered the time.

The practical alternative for IronRDP is to omit NASM for the native
`aarch64-pc-windows-msvc` target. All six omission builds of `ironrdp-agent`
succeeded, including archive checks, executable `--help`, and persisted Rust
caches. The six controls also succeeded. All four viewer builds, with and without
NASM, failed with the same existing `libopus_sys` unresolved symbols
`__imp_floor` and `__imp_lrintf`. This is not a claim of a working viewer release
or a passing Rust test suite.

These are fork-only experiments. Production workflows and shared dependency
actions remain unchanged. Linux was not modified or tested. No security settings
were weakened, and no upstream PR was created.

## Runs and methodology

| Purpose | Run | Jobs |
|---|---|---:|
| Initial process diagnostic attempt | [39593822541](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39593822541) | 8 |
| Corrected process/configuration diagnostics | [39594193280](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39594193280) | 8 |
| Exploratory recovery comparison | [39594438199](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39594438199) | 32 |
| Independent TEMP-path follow-up | [39595578818](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39595578818) | 32 |
| Defender performance traces | [39594813812](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39594813812) | 4 |
| Native Arm release comparison | [39594198946](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39594198946) | 16 |

The initial diagnostic attempt failed during post-installation inventory because
an assumed `choco.exe.config` path did not exist. The corrected attempt resolves
the executable on PATH and explicitly records absent executable configuration.
Only the corrected attempt is included in the diagnostic analysis.

All successful diagnostic, recovery, confirmation, and trace jobs used the two
requested images. All 16 build jobs also resolved to those images. All observed
CPUs in these campaigns were Cobalt 100 with four logical processors.

Profiled/debug executions are kept separate from unprofiled performance trials.
Fresh-runner timing variants are shuffled across nominal blocks and both runner
labels. Actual image assignment is observational, not controlled by the labels.
The 128-job earlier experiment is not pooled with these follow-ups.

## What changed between the images

Four corrected diagnostic jobs used each image. Their 30 recorded Chocolatey
feature flags and cache-location setting were identical. Both reported
Chocolatey 2.7.4, the same PATH-launcher SHA-256, embedded PowerShell enabled,
and the same registered .NET Framework release value. These observations do not
establish equality of every possible machine or Chocolatey setting.

The *loaded binaries* reveal servicing changes that the generic ".NET Framework
4.8.1" installed-software entry does not:

| Component | `20261013.183.4` | `20261018.189.1` |
|---|---|---|
| Windows build | 26200.9457 | 26200.9711 |
| Loaded CLR | 4.8.9345.0 | 4.8.9363.0 |
| Embedded Windows PowerShell assembly | 10.0.26100.9457 | 10.0.26100.9711 |
| Outer PowerShell | 7.6.6 | 7.6.7 |
| Defender platform | 4.18.25080.5 | 4.18.26090.9 |
| Defender engine | 1.1.26080.3 | 1.1.26090.9 |

Chocolatey hosts Windows PowerShell 5.1 on .NET Framework, not the outer
PowerShell 7/.NET Core runtime. The PowerShell 7 or .NET SDK update cannot simply
be assumed responsible. Both images loaded native-image versions of `mscorlib`
and `System.Management.Automation`; the evidence does not support a blanket
claim that their NGen images are missing.

The PATH command is a launcher at `C:\ProgramData\Chocolatey\bin\choco.exe`
(version 0.12.1.0); it starts the actual Chocolatey 2.7.4 executable at
`C:\ProgramData\Chocolatey\choco.exe`. The recorded configuration hash is of the
launcher, not the main executable. Architecture API readings and module
inventories are retained, but are not used to claim a causal emulation penalty.

Pinned installed-software manifests:

- [Older image](https://github.com/actions/runner-images/blob/releases/win11-vs2026-arm64/20261013/images/windows/Windows11-VS2026-Arm64-Readme.md)
- [Newer image](https://github.com/actions/runner-images/blob/releases/win11-vs2026-arm64/20261018/images/windows/Windows11-VS2026-Arm64-Readme.md)

## Where the time goes

Three slow newer-image diagnostic installations took 63.75, 80.27, and 91.63
seconds, all on **default storage**. The other newer-image diagnostic took
26.49 seconds on ReFS. Thus slow execution is not confined to ReFS.

On those three slow instances:

- Command launch to Chocolatey's banner took 31.33-35.29 seconds. The main
  Chocolatey process had consumed approximately 1.94-2.89 CPU-seconds by then.
- Calling the embedded PowerShell host to its initialized-host message took
  9.12-23.95 seconds, with approximately 0.42-0.69 additional main-process
  CPU-seconds.
- Initialized host to installer start took another 2.49-5.23 seconds.

The fast newer-image diagnostic's corresponding host initialization took
3.20 seconds and approximately 0.55 CPU-seconds. Across all eight diagnostics,
main Chocolatey process CPU time was approximately 7.77-9.66 seconds, despite
installation wall times of 26.49-91.63 seconds. Sampled CPU boundaries are
approximate. Logical process I/O is not physical disk latency.

This establishes substantial waiting rather than a proportionate increase in
Chocolatey's own CPU work. It does not distinguish filesystem/filter waits,
page faults, scheduling, runtime synchronization, or other external waits.
Warm `choco --version` calls had per-job medians of 2.20-2.41 seconds; they are
different commands and not proof that a free warm-up would fix installation.

The [NASM 3.2.0 Chocolatey package](https://community.chocolatey.org/api/v2/package/nasm/3.2.0)
bundles its installers. Its script inventories Start Menu entries, selects the
embedded installer, runs it, and cleans up. There is no second installer
download in that script. The long package-setup gap contains embedded host
initialization; it cannot all be attributed to Start Menu enumeration.

Inspected package SHA-256:
`9a72ba9d6f6f0dc2a5598ec160366b2bdd925a23e229dfb5d854f63c0f2a2160`.

Chocolatey [2.7.4 startup source](https://github.com/chocolatey/choco/blob/2.7.4/src/chocolatey.console/Program.cs)
also performs bootstrap, logging, configuration, container, and licensing work
before printing its banner. "Before banner" is not solely executable loading.

## Defender traces

Four bounded 120-second recordings used Microsoft's
[`New-MpPerformanceRecording`](https://learn.microsoft.com/powershell/module/defenderperformance/new-mpperformancerecording)
and `Get-MpPerformanceReport`. Only parsed summaries were uploaded; raw ETL
files were deleted on their ephemeral runners.

| Image | Storage | Installation | Recorded real-time scan duration |
|---|---|---:|---:|
| Older | Default | 41.12 s | 0.133 s |
| Older | ReFS | 33.43 s | 0.103 s |
| Newer | Default | 26.26 s | 0.177 s |
| Newer | ReFS | 60.31 s | 0.252 s |

Raw report durations are 100-nanosecond units, matching their FILETIME
start/end differences; the entire recordings span approximately 120 seconds.
Durations may overlap and are not equivalent to critical-path elapsed time.
The reports are predominantly AMSI events and have different coverage between
platform versions. Recorded scan time is far too small to explain the long
installation in these traces, but this is not a comprehensive exclusion of
every antivirus/filter interaction. Defender real-time protection and tamper
protection remained enabled.

## Recovery trials

The first 32-job comparison tested original storage, full ReFS preparation,
ReFS with original C: TEMP/TMP restored, and ReFS with direct invocation of
the main Chocolatey executable. Everything else in the installation probe was
unchanged. All 32 jobs succeeded.

On the newer image, the exploratory ReFS medians were 44.24 seconds for the
original candidate, 26.43 seconds with C: TEMP/TMP, and 50.27 seconds with
direct invocation. The C:-TEMP cell contained only three observations.
That apparent improvement was therefore followed by a separate, fixed-size
32-job experiment with its [analysis plan](temp-confirmation-plan.json)
committed before launch. There were no top-ups.

The follow-up did **not** confirm a useful TEMP-path improvement:

| Image | D: TEMP/TMP, n / median | C: TEMP/TMP, n / median | C: minus D: |
|---|---:|---:|---:|
| Older | 9 / 27.63 s | 12 / 28.10 s | +0.48 s |
| Newer | 7 / 31.55 s | 4 / 29.26 s | -2.29 s |

Nominal scheduling-block bootstrap 95% intervals are -3.63 to +4.71 seconds
on the older image and -10.22 to +80.84 seconds on the newer image. The newer
image cells did not meet the prespecified minimum of eight each, so that
primary comparison remains descriptive. A newer-image C:-TEMP installation
still took **108.80 seconds**, including 48.02 seconds before the banner.
Neither TEMP restoration nor launcher bypass is recommended as a demonstrated
fix for the slowdown. No external-PowerShell, certificate-policy, Defender
exclusion, or runtime-cache modification is proposed.

## Avoiding an unnecessary dependency

The exact crates were downloaded from crates.io and verified against the
checksums in the pinned source's `Cargo.lock`:

- `openh264-sys2` 0.9.7: `build.rs`, `NasmConfiguration::find`, returns `None`
  for architectures other than x86/x86-64 before attempting NASM.
- `aws-lc-sys` 0.42.0: selects Windows aarch64 sources and the Clang toolchain
  for native Arm; its NASM/prebuilt-NASM paths concern x86-family assembly.
- `libopus_sys` 0.3.3 uses its CMake build path. Both release variants reach
  the same existing viewer link failure.

All 16 builds used upstream source
`860cf6ccb1359e15034cfbf402a308e3ad21b341`, the original release flags, fresh
variant-specific cache keys, and default storage. Omission jobs explicitly
asserted that NASM was absent from PATH and the usual installation directories.
All 12 successful agent jobs persisted approximately 395 MB Rust caches,
verified using GitHub's cache API rather than job success alone.

| Runner label | Controls, n / median job | Without NASM, n / median job | Observed change |
|---|---:|---:|---:|
| `windows-11-arm` | 3 / 565 s | 3 / 460 s | -18.6% |
| `windows-11-vs2026-arm` | 3 / 498 s | 3 / 474 s | -4.8% |

The removed dependency step took **24-125 seconds** in the six agent controls.
Job durations include setup, archive creation, and cache post-steps, but exclude
queueing. These small whole-job comparisons are not causal speedup estimates:
five of six controls used the newer image, versus two of six omission jobs.
Compiler and image changes confound the difference beyond the eliminated step.

A production omission should be gated on the **build target**, not just the
host CPU: an Arm host cross-compiling for x64 may still need NASM. A targeted
input to the shared dependency action can preserve existing callers and leave
Linux/x64 behavior unchanged. That production change has not been made here.
The original upstream PR confidence/performance gate remains unmet, and the
pre-existing viewer release failure is still unresolved.

## Reproduction and retained evidence

`measurements.json` retains corrected process/module samples, timestamped
diagnostic events, configuration snapshots, all 64 unprofiled timing samples,
four Defender summaries, and all 16 GitHub build-job records.
Credential-related debug lines were redacted before artifact upload.
`build-details.json` contains image/CPU identities, absence checks, and linker
errors. `cache-inventory.json` records actual persisted cache entries.

Reproduce the summary offline:

```powershell
python .\benchmarks\chocolatey-investigation\analyze.py `
  --data .\benchmarks\chocolatey-investigation\measurements.json `
  --output "$env:TEMP\chocolatey-summary.json"
```

The five `chocolatey-*.yml`/`nasm-omission.yml` experiment workflows are retained
on this branch with branch-specific push triggers. Findings commits use
`[skip ci]`; publishing evidence does not relaunch these campaigns.
