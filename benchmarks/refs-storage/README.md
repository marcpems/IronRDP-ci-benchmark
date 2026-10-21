# Windows Arm ReFS release-build experiment

## Decision: retain the experiment; do not open an upstream PR

The guarded storage setup works, but these measurements do not establish a
consistent, significant end-to-end speedup. Before testing, the acceptance
threshold was set at a repeated median reduction of at least 10% in Arm
build-job wall time, including provisioning and cache overhead. The results
do not meet that threshold consistently across the two runner labels.

The clean candidate is on [`perf/windows-arm-refs`][candidate]. The experiment
reuses the existing `marcpems/IronRDP-ci-benchmark` fork; it does not change its
default branch or publish releases. No upstream PR was created.

## Corrected cold-cache measurements

[Run 39574497666, attempt 1][cold] built `ironrdp-agent` from upstream commit
`860cf6ccb1359e15034cfbf402a308e3ad21b341`. There were three independent fresh
runners for each label/variant combination: 12 jobs, all successful, all cache
misses. All 12 cache entries were independently confirmed through GitHub's
cache API, at approximately 395 MB each.

| Runner label | Default median job | ReFS median job | Reduction | Default median compile | ReFS median compile |
|---|---:|---:|---:|---:|---:|
| `windows-11-arm` | 481 s | 431 s | 10.4% | 343 s | 326 s |
| `windows-11-vs2026-arm` | 488 s | 466 s | 4.5% | 360 s | 328 s |

Job time is the GitHub job's `completed_at - started_at`, including setup,
checkout, dependency installation, cache handling, compilation, packaging,
artifact upload, validation and post-job steps. It excludes queue time.
It is not the duration of the complete six-platform release/publish workflow.
In particular, no claim is made that the release workflow's critical path
improves. Linux jobs were neither modified nor included in the experiment.

The samples used two image versions, `20261013.183.4` and `20261018.189.1`,
both identifying as `win11-vs2026-arm64`. Runner labels did not pin an image.
The small sample count, image rollout and variable dependency-installation
time prevent strong statistical or fleet-wide claims.

## Cache restore verification

[Attempt 2][warm] reran the same 12 jobs and succeeded. However, only seven
jobs had exact cache hits: five default-storage jobs and two ReFS jobs.
The other five missed because their environment-derived cache keys changed
with the runner image. It would be misleading to label all of attempt 2
as a warm-cache comparison.

The two actual ReFS cache hits verified the full save/restore cycle,
restored dependencies, built and ran the binary, verified archive checksums,
and confirmed the workspace, Cargo home and compiler temp paths still used
the ReFS drive. Their total job times were 318 s and 217 s. One warm sample
per label is insufficient to establish a repeated warm-cache speedup.
No cache save/restore failure warnings were found in the corrected runs.

## Release compatibility and unchanged jobs

[Run 39574562225][released] used commit
`11a0810cfbbabd8b8023875a05e3041216d4b01b`, the source of both published
`ironrdp-agent-v0.1.0` and `ironrdp-viewer-v0.1.0` tags.

- The Windows x64 agent and viewer release jobs passed, including archive and
  binary smoke checks. The storage step was skipped.
- The Arm agent passed with both storage variants: 382 s default versus
  353 s ReFS (7.6% improvement, one sample only).
- The Arm viewer failed identically with both variants: `libopus_sys` linker
  errors for `__imp_floor` and `__imp_lrintf` (`LNK2019` / `LNK1120`).
  The initial current-source builds also failed at the viewer link step.
  This is baseline behavior, not a demonstrated storage regression, but it
  prevents a completely green Arm release validation.

No Rust source, lockfile, Linux/macOS behavior, x64 configuration or release
publication logic was changed. A structural YAML comparison confirmed that
removing the new guarded preparation step reproduces the original release
workflow exactly.

## Storage behavior and safety

The new step requires GitHub-hosted Windows Arm64, verifies the operating
system architecture, and leaves existing `D:` assignments untouched. It
initializes a disk only when exactly one eligible, online, writable raw NVMe
disk exists with zero partitions, at least 50 GiB capacity, and neither boot
nor system status. The workspace must be empty and ordinary, and an existing
Cargo home must also be an ordinary directory.

The new partition is formatted as a ReFS Dev Drive using Windows defaults.
No existing volume is reformatted, no partition is resized, and no antivirus
exclusions or filter-policy overrides are applied. The real runner logs
confirmed a trusted developer volume protected by the antivirus filter.

The workspace moves behind a junction to `D:\workspace`. Cargo home moves
behind a junction to `D:\cargo-home`, with `CARGO_HOME` explicitly pointing
at that physical path. `TEMP` and `TMP` become `D:\build-temp`. The running
agent, `GITHUB_WORKSPACE`, `RUNNER_TEMP` and Rust toolchain are not reconfigured.
Missing or ambiguous eligible storage produces a logged no-op; operational
failures propagate.

`Test-StorageGuards.ps1` extracts the actual candidate step from the workflow
and tests 22 cases with mocked storage/filesystem reads and an initialization
sentinel. It never initializes a disk. Run it with Arm64 PowerShell:

```powershell
.\benchmarks\refs-storage\Test-StorageGuards.ps1
```

The test covers occupied `D:` assignments, absent/ambiguous/initialized disks,
boot/system/offline/read-only/non-NVMe disks, partition-inventory disagreement,
capacity, nonempty/linked workspaces, invalid Cargo homes and error propagation.
The candidate passed actionlint and PowerShell parsing.

## Rejected initial implementation

[Run 39572966152][initial] is deliberately excluded from performance claims.
Moving only Cargo's source-cache subdirectories left cache paths relative to
the old workspace on `C:`. GNU tar resolved the junction's parents on `D:`,
so saves failed with `Cannot stat` despite successful agent job conclusions.
Its apparently faster post-job times were not valid savings.

The corrected candidate moves all Cargo-home data and explicitly sets its
physical path, preserving configuration and installed binaries while making
cache archives address the right drive. Cache persistence and actual restores
were checked rather than relying on green job conclusions.

## Evidence and reproduction

`results.json` contains the 38 job records across all four run attempts,
including step timings and job URLs. Image versions and actual cache-hit
states are recorded for both repeated-build attempts. `cache-inventory.json`
is a snapshot of the corrected campaign's cache entries.

The self-contained fork-only workflows are:

- `.github/workflows/refs-benchmark.yml` on `perf/windows-arm-refs-benchmark`
- `.github/workflows/refs-release-validation.yml` on
  `perf/windows-arm-refs-release-validation`

They reuse the candidate release steps with fixed upstream source commits,
isolated per-run/label/package/variant/sample cache namespaces, unique
artifacts, and additional validation. They do not publish release assets.
Push a new commit to the corresponding experiment branch for fresh cache
namespaces; rerun that run to exercise its saved caches. Always inspect the
actual cache-hit state and image version before comparing warm timings.
The existing runs can be rerun with `gh run rerun RUN_ID --repo
marcpems/IronRDP-ci-benchmark`, subject to cache retention and runner changes.

[candidate]: https://github.com/marcpems/IronRDP-ci-benchmark/tree/perf/windows-arm-refs
[initial]: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39572966152
[cold]: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39574497666/attempts/1
[warm]: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39574497666/attempts/2
[released]: https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39574562225
