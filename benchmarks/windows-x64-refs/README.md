# Windows x64 NTFS versus resized ReFS

The storage change worked, but this experiment does not establish a reliable whole-job speedup for the `windows-2022` runner pool or its NVMe-backed subset.
All 16 cold agent builds succeeded, and GitHub confirmed 16 saved cache entries.
The overall mean improved by 37 seconds (6.6%), but the nominal-block bootstrap interval includes a slowdown.
An upstream x64 change is not justified by these measurements alone.

## Complete-job results

The [fixed experiment][run] compared eight stock NTFS jobs with eight jobs that shrank D: to Windows' supported minimum, created ReFS R:, and relocated the workspace, Cargo home and temporary directories.
Times include runner setup, storage preparation, checkout, NASM, compilation, packaging, common diagnostics and post-job cache saving; queue time is excluded.

| Metric | Stock NTFS | Resized ReFS | ReFS minus NTFS |
|---|---:|---:|---:|
| Mean job | 563.625 s | 526.625 s | -37.000 s (-6.6%) |
| Median job | 585.000 s | 564.000 s | -21.000 s (-3.6%) |
| Mean Cargo elapsed | 462.950 s | 442.275 s | -20.675 s |
| Mean cache setup | 18.375 s | 14.125 s | -4.250 s |
| Mean cache-save step | 43.625 s | 22.000 s | -21.625 s |

The 95% bootstrap interval for the mean job difference is **[-125.4, +38.1] seconds**.
The corresponding Cargo interval is [-102.4, +46.4] seconds.
Cache saving was more consistently faster, with an interval of [-31.1, -14.4] seconds.
The ReFS preparation step took 8-10 seconds, averaging 8.75 seconds, and is already included in the job totals.
Cache saving includes compression and upload, not just filesystem operations.

These are instrumented cold-build jobs, not a promise of production savings.
This comparison measures the combined filesystem and directory-relocation change; it does not isolate ReFS from moving Cargo home and compiler temporary files off C:.
Warm-cache performance and cache restoration were not measured.

## Hardware matters

Every job used image `20261012.333.1`, but the label supplied different CPU models and disk layouts.
Both variants received four NVMe and four SAS-presented virtual disks; their CPU distributions differed.

| CPU and presented disk bus | NTFS count / mean job | ReFS count / mean job |
|---|---:|---:|
| EPYC 9V45, NVMe | 1 / 412.00 s | 2 / 403.00 s |
| EPYC 9V74, NVMe | 3 / 509.00 s | 2 / 543.00 s |
| EPYC 7763, SAS | 3 / 652.33 s | 4 / 580.25 s |
| EPYC 9V74, SAS | 1 / 613.00 s | 0 / unavailable |

The NVMe-only averages were 484.75 seconds for NTFS and 473.00 seconds for ReFS, a nominal 11.75-second (2.4%) improvement.
That subset is not CPU-balanced: the 9V74 subset became slower with ReFS while the smaller 9V45 subset was slightly faster.
The larger observed benefit came from the SAS-presented machines, particularly EPYC 7763, rather than a demonstrated NVMe win.
These small hardware subsets are descriptive, not separately powered comparisons or matched physical hosts.
The earlier six-job peek overstated the overall advantage because it included a SAS control but only NVMe ReFS jobs.

## Preservation and limitations

The [preparation helper][helper] refuses non-hosted/non-x64 execution, occupied R:, boot/system/read-only disks and unsupported layouts.
It supports the observed 150 GiB MBR data disk and 220 GiB GPT NVMe data disk, preserving the latter's reserved partition.
It resizes only D: and formats only the newly created partition.
It copies directories before replacing them with junctions and retains their original contents as backups.
NASM installation, source revision, build flags, paging policy and security settings are not changed.

Separate [MBR checks][mbr-check] and [GPT-compatible checks][gpt-check] passed agent and viewer release builds, archive checksums, executable smoke checks and cache saving.
Pre-job fixture checks covered existing files, hidden attributes, junctions, symbolic links, protected partition layouts, paging settings, runner environment-file commands and a 512 MiB write through the relocated runner temporary directory.
The first two ReFS attempts in the [initial checks][initial-check] safely rejected the GPT reserved partition before modifying storage; an [eight-host read-only inventory][inventory] identified the additional supported layout.
Both initial NTFS controls succeeded.

Shrinking literally to the minimum has an important cost on SAS-presented hosts: D: retains its 2944 MiB pagefile but only about **54.6 MiB free**, restricting future pagefile growth.
The agent samples reported no pagefile usage; a separate viewer check reached 238 MiB of pagefile usage within the existing allocation.
On the NVMe layout, the pagefile was on C: and the reduced D: retained about 2998.7 MiB free.
No pagefile was moved, disabled or reconfigured.

Windows Server 2022 exposes ordinary ReFS here, not the ReFS Dev Drive mode used in the Windows Arm experiment.
All 16 hosts reported `AntivirusEnabled=true` and `RealTimeProtectionEnabled=false`; the workflow does not set protection preferences or exclusions.
The initial local analysis incorrectly required the Arm experiment's real-time-protection state, despite all hosted builds succeeding.
The analyzer now checks that the reported states agree across all samples and includes that state in its output.
These results do not establish performance with real-time protection enabled.

## Evidence and reproduction

The [protocol][plan] and [workflow][workflow] were committed before the timing run as `4c4cb0a7`.
The source checkout was pinned to `b9d140003323f3ae3cd22f91be556e58ed43322e`.
There were eight nominal scheduling blocks, randomized matrix ordering with seed `20261022`, at most eight concurrent jobs and no performance-dependent top-ups.
GitHub controls actual scheduling and hardware assignment; nominal blocks do not pair physical machines.
The analysis uses 10,000 fixed-seed nominal-block bootstrap resamples.

All 16 jobs compiled the same 434 Cargo units/features, with zero fresh units.
NASM remained installed in every job, reporting version 3.02.
GitHub's API confirmed 16 cache entries of approximately 433-434 MB each.
Cache keys were isolated by run ID, attempt, block and variant.

[Measurements][measurements] retain the job/step timings, cache metadata, host observations, preparation reports and Cargo timing data.
[Summary][summary] contains all observations, hardware subsets and bootstrap results.
Recompute it using Python's standard library:

```powershell
python .\benchmarks\windows-x64-refs\analyze.py
```

The generator additionally requires PyYAML.
It regenerates the workflow and protocol from the checked-in release workflow and preparation helper; it does not execute disk commands.
Do not run the preparation helper on a local machine.

[run]: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39792941867
[mbr-check]: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39789292390
[gpt-check]: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39791007852
[initial-check]: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39788742300
[inventory]: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39790554133
[helper]: Prepare-Storage.ps1
[plan]: plan.json
[workflow]: ../../.github/workflows/windows-x64-refs-replication.yml
[measurements]: measurements.json
[summary]: summary.json
