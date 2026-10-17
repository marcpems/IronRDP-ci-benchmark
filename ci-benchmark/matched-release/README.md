# Matched Rust release cost and IronRDP benefit

## Release-only Microsoft-retained PGO + Rust ThinLTO scaling

The separate [scaling protocol](msvc-scaling-protocol.json) schedules x64/16,
ordinary Arm64/16 and high-core Arm64/32 first, then matching four-CPU
controls. A 16-CPU point on the high-core machine supplies a same-machine
4/16/32 curve. Seven cold full-release cells run serially within each
machine; independent machines may run concurrently. No IronRDP jobs are
scheduled. GB300 was registered but offline when this batch was requested.
An additional ordinary Arm64 eight-CPU cell was requested on 16 October,
after the four/sixteen comparison completed. It uses the same recipe and
qualification, extending that machine's curve to 4/8/16 without changing the
x64 or GB300 allocations. `matched-arm64-eight-scaling.yml` runs this cell
independently. If space is insufficient, only generated dependency/training
caches from the qualified 4/16 cells are relocated to C: with verified
checksums; sources, merged profiles, results and distribution archives stay
in place. That maintenance is separate from the eight-CPU release job.

The first eight-CPU preparation (`38870164332`) rejected an internal Cargo
checkout license symlink before copying or deleting anything. The replacement
(`38870376305`) preserved and checksum-verified the Cargo cache, but source
removal stopped on a read-only Git pack index. Neither attempt reached release
production. Recovery now reuses the exact relocation receipt, rechecks the full
retained copy and every remaining source entry, and resumes removal without
recopying a partially removed source. Only Windows read-only regular-file
deletion failures are retried after clearing that source file's read-only bit;
other permission errors and redirected entries remain fatal. Internal symlinks
are retained inside the preserved tree, and external symlinks remain rejected.
Cache maintenance has a separate 120-minute allowance; the release recipe,
measurement boundaries and 180 GiB free-space guard are unchanged.

On 16 October, removal of investigation data known to be obsolete was
authorized. `matched-arm64-obsolete-cleanup.yml` waits for the ordinary Arm64
release lock and refuses to run alongside surviving build processes. It
revalidates the qualified 4/16-CPU results, full distribution checksums and
merged profiles before deleting only their Cargo and rustc-perf training
caches, including verified relocated copies. These caches are not reused by
fresh-profile measurements. Sources, evidence, merged profiles, distributions
and failed-build diagnostics remain untouched. Per-cache disposal receipts
and a free-space report distinguish deletion from preservation, and subsequent
space preparation skips caches deliberately disposed of. No experiment root
or unqualified build is recursively removed by this cleanup.

Cleanup [38888150667](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38888150667)
completed after the eight-CPU measurement. It removed four obsolete cache
trees containing 8,357,881,526 file bytes (7.78 GiB), with both qualified
result identities and protected archives/profiles reverified. Observed free
space afterward was 219.22 GiB on C: and 167.51 GiB on D:. Drive-level free
space increased by 2.12 and 3.56 GiB respectively; these changes are not the
same quantity as the logical sizes of deleted files. D: remains 12.49 GiB
below the next fresh release's 180 GiB guard. Failed-build diagnostics and
all release evidence remain retained.

The additional cleanup pass
[38900486448](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38900486448)
removed another 12,536,036,749 file bytes from six Cargo/training caches:
the qualified Microsoft-PGO pilot `38532798400`, LLVM-PGO pilot `38542164879`,
and eight-CPU scaling release `38873093226`. `--additional` selects only these
three inspected roots, with each pilot's own exact recipe and allocation
checked before deletion. It does not treat the older PGO-only recipe as a
scaling control. Full release archives, profile hashes and result identities
were reverified; source checkouts and all failed-build trees remain retained.
The ordinary Arm64 inventory now reuses the bounded inspection workflow,
including top-level setup directories and evidence/training subdirectories,
without traversing redirected entries.
The follow-up pass `38901491141` confirmed all six caches were already
disposed of and made no further deletions. Its fresh D: reading was
195,308,638,208 free bytes (**181.90 GiB**), now 1.90 GiB above the release
guard. This is ordinary Arm64 storage, not the separately blocked GB300.

This recipe retains `clang-cl`, Microsoft `link.exe` and `lib.exe`, with
fresh PGO and **Rust-side cross-crate ThinLTO enabled**. Native LLVM ThinLTO
stays off because its bitcode is not supported by Microsoft `/LTCG`.
Earlier report rows labelled Microsoft-retained PGO had Rust cross-crate
ThinLTO off, so they are not reused as four-CPU controls. The distinct
`msvc-pgo-rust-thin` variant and study metadata prevent mixing these results.

CPU allocations mean logical processors, not necessarily physical cores:
the x64 machine has 8 physical cores / 16 logical CPUs. Bootstrap/Cargo/CMake
workers follow each allocation; training remains at four Cargo jobs and one
frontend thread, and LLVM link jobs stay at one across this scaling series.
Full distribution scope, fresh profiles, source pins, native tools and
qualification gates are unchanged. The workflow rejects inadequate space,
wrong runners and in-place reruns; completed artifacts are retained before
only that cell's verified disposable build directory is reclaimed.

The batch starts from `experiment/msvc-rust-thin-scaling` through
`matched-msvc-scaling.yml`. Each cell has its own 24-hour self-hosted deadline.
An offline runner can still hit GitHub's queue limit. Single-pass ratios will
be reported as measured scaling observations, not confidence intervals or
guaranteed GitHub-hosted performance. A 360-minute hosted budget is evaluated
against **whole-job** duration, not just compilation.

The initial GB300 cell in 38716997224 remained unassigned after the runner
returned online. It finally started at 10:46:53 UTC on 15 October, then
failed before checkout: Windows PowerShell's `.NET Environment.ProcessorCount`
reported only 8 CPUs (the smaller processor group), causing an incorrect
32-CPU capacity rejection. Fresh dispatch probe 38722680331 succeeded and
independently recorded that 8-CPU view. The original scheduling delay's
service-side cause is not established.

The replacement preflight uses the machine-wide CIM logical CPU count.
Measured builds use explicit Windows Job Object processor-group affinity on
multi-group machines at every allocation, not only at 64 CPUs. A real native
probe must execute on every selected CPU and reject every excluded CPU before
each GB300 build. `matched-gb300-scaling.yml` replaces only the failed GB300
32/16/4 chain; running x64 and ordinary Arm64 cells remain untouched.
The compiler recipe, source, worker counts and timing boundaries are unchanged.

Native probe 38722992402 passed all selected/excluded CPU checks at 32, 16 and
4 CPUs on GB300's `[64, 8]` processor groups. Replacement 38723101166 passed
capacity preflight, but GitHub reported loss of runner communication during
source/tool preparation at 11:03:32 UTC. GB300 was then offline; production
never started. This is distinct from the earlier preflight bug.

GB300 was online again at 11:57 UTC. Recovery probe 38731374184 received a
job, found no other runner workers or active build processes, and passed the
32/16/4 CPU-affinity checks. Three Git processes predated the failed release
and showed no CPU or I/O counter growth over 15 seconds; they were left
untouched. The GB300-only chain is restarted in a fresh run and build root,
not resumed in the disconnected job's partially prepared tree.

The ordinary Arm64/16 cell in 38716997224 failed at 11:25:48 UTC while rendering
the unstable book in the final distribution stage, after both PGO stages.
`rustbook` reported Windows error 183 ("already exists") creating the
`library-features` directory. The directory was present as a directory on
subsequent inspection. Isolated diagnostic 38728217117 used the retained
renderer and book input but fresh destinations, with the same 16-CPU affinity:
all eight attempts passed (two each with default or single-threaded Rayon on
D: ReFS and C: NTFS). This does not establish the original failure's cause,
nor prove a filesystem or concurrency fix. The failed release is excluded.

`matched-arm64-scaling.yml` schedules a fresh ordinary Arm64 16/4 chain,
without changing the compiler recipe or suppressing documentation. It does
not resume the failed tree or reuse its profiles. The original x64 chain
continues independently. Failed runs and diagnostic replays are not accepted
production measurements.

The fresh ordinary Arm64/16 release in 38728610658 completed and qualified:
production 6721.889759 seconds (112.03 minutes), extracted-distribution tests
3208.655321 seconds (53.48 minutes), and the whole successful job 11334 seconds
(188.90 minutes). Its source/tool identity, full manifest and PGO/Rust ThinLTO
audit passed. The matching four-CPU control has now also completed, as below.

The dependent four-CPU cell stopped before checkout because D: had less than
180 GiB free, even after successful qualified-build cleanup. Read-only inventory
38755283083 found about 175 GiB free and 23.73 GiB in the earlier failed
documentation build. `matched-arm64-control.yml` preserves every file of that
specific failed build on C: with SHA256 verification before removing its D:
copy, then schedules only a fresh four-CPU control. Sources, profiles, logs and
qualified archives remain untouched; the 180 GiB guard is not relaxed.

GB300 run 38731573412 also lost runner communication, at 14:49:34 UTC during
the build/qualification step. It is excluded and its dependent 16/4 cells
were skipped. No completed GB300 scaling result is available from that run.

### Qualified CPU-scaling comparisons

The fresh ordinary Arm64 four-CPU control
[38756702383 / 116502060812](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38756702383/job/116502060812)
completed successfully on 16 October at 01:18:34 UTC. Comparison with
[the 16-CPU cell](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38728610658/job/116400524618)
checks identical source/tool identities and bootstrap configuration except
worker allocation, fresh profiles, actual CPU affinity, executed backend
profile counters, full manifests, explicit Rust PGO/ThinLTO flags and passed
extracted-distribution tests.

| Machine / allocation | Full production minutes | Successful whole-job minutes |
|---|---:|---:|
| Ordinary Arm64 / 4 CPUs | 507.79 | 606.70 |
| Ordinary Arm64 / 8 CPUs | 137.13 | 217.70 |
| Ordinary Arm64 / 16 CPUs | 112.03 | 188.90 |
| x64 / 4 logical CPUs | 726.81 | 851.18 |
| x64 / 16 logical CPUs, original | 610.70 | 720.22 |
| x64 / 16 logical CPUs, repeat | 916.98 | 1057.37 |

The [eight-CPU cell, 38873093226 / 116882096128](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38873093226/job/116882096128)
also passed the same provenance, configuration, profile, actual-affinity,
Rust PGO/ThinLTO and extracted-distribution checks. Production took
8227.535959 seconds, qualification 3275.982914 seconds, and the successful
whole job 13062 seconds. Retained-distribution verification and build-space
reclamation completed successfully. Relative to four CPUs, eight CPUs reduced
production time by **73.00%** (**3.70x**) and whole-job time by **64.12%**
(**2.79x**). Going from eight to sixteen CPUs reduced production time by a
further **18.30%** and whole-job time by **13.23%**.

On this Arm64 machine, 4 to 16 CPUs reduced production time by **77.94%**
(**4.53x** speedup), and successful whole-job time by **68.86%** (**3.21x**).
The 8- and 16-CPU jobs fit both the 360-minute hosted ceiling and a 300-minute
planning budget; the four-CPU job does not. These are self-hosted observations,
not measurements of GitHub larger runners or guaranteed hosted performance.
The four-to-eight and four-to-sixteen production speedups exceed their
CPU-count increases: fixed-order, single-pass results need repetition before
explaining or generalizing that effect. Whole-job figures exclude queue time, failed attempts and separate
recovery jobs; they are not total experiment cost.

The x64 16-logical-CPU release also qualified, but its job exceeded six hours.
Its fresh four-CPU control (job 116693884027) lost runner communication at
04:38:42 UTC on 16 October, during the combined build/qualification step.
GitHub then reported the x64 runner offline, and the job log was unavailable.
That incomplete control remains excluded. Its fresh replacement,
[38869758791 / 116880180878](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38869758791/job/116880180878),
qualified with **43608.363620 seconds (12h06m48s)** of full production,
3044.150801 seconds of extracted-distribution qualification and 51071 seconds
(14h11m11s) for the successful whole job. Independent evidence checks confirm
matching source/tools/runtime patches and configuration outside worker
allocation, actual four-CPU affinity, fresh merged profiles,
backend profile counters, Cranelift training, Rust PGO/ThinLTO flags and full qualification.
The maintenance receipt matches result SHA-256
`fc1567aba2a396eacb9939be5479f1344995b22b930dd93721b97db37ee0d303`.

Four to sixteen logical CPUs reduced x64 production by **15.97% (1.19x)**
and whole-job time by **15.39% (1.18x)** in these initial observations.
These are descriptive ratios, not a stable CPU-scaling estimate: the
matched sixteen-CPU repeat below reverses the ordering.
The measured four-CPU production time does not support the proposed 40-hour
linear projection. Opt-dist timers separate the production phases:

| Production phase | x64 / 4 CPUs, minutes | x64 / 16 CPUs, original minutes | x64 / 16 CPUs, repeat minutes |
|---|---:|---:|---:|
| Build instrumented rustc and LLVM | 78.69 | 52.67 | 77.58 |
| Gather rustc/rustdoc/clippy/Cranelift profiles | 209.99 | 207.30 | 359.39 |
| Build optimized rustc | 39.42 | 30.19 | 29.62 |
| Build instrumented LLVM | 76.95 | 49.48 | 74.00 |
| Gather/merge LLVM profiles | 146.61 | 139.16 | 197.56 |
| Final distribution build | 159.74 | 121.98 | 159.89 |
| Helper construction and remaining production overhead | 15.41 | 9.92 | 18.95 |
| **Total production** | **726.81** | **610.70** | **916.98** |

Profile gathering/merging totals **5h56m36s at four CPUs versus 5h46m28s at
the original sixteen-CPU run**, only 2.92% longer. These phases retain four
Cargo training jobs in both allocations; they are not raw compiler-build
time and do not receive a proportional increase in configured Cargo workers.
That does not imply constant wall time, as the repeat demonstrates.
All other production combined is 6h10m12s versus 4h24m14s, a 1.40x
speedup in the initial pair only. The sixteen-logical-CPU machine has eight
physical cores. These fixed-order observations cannot establish the cause
of the weak or reversed scaling.
All these cells use the new Microsoft-retained PGO plus Rust
cross-crate ThinLTO recipe; the older PGO-only pilots are not controls.

The requested [sixteen-CPU repeat, 38980060732 / 117263372781](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38980060732/job/117263372781)
completed and independently qualified. Production took **55019.005912 seconds
(15h16m59s)**, extracted qualification 3906.326522 seconds, and the successful
release job 63442 seconds (17h37m22s). Source pins, native tool identities,
normalized bootstrap configuration, runtime patch sources, actual sixteen-CPU
affinity and Rust PGO/ThinLTO flags match the original. Fresh profile hashes
and executed backend counters were checked again.
Its independent root is `E:\m80060732t16r1`; retained-distribution
maintenance matches result SHA-256
`67c0d5cac865040e4c5419707b8b3a09075283a5845192dec41e2317919a2cc9`.
Both sixteen-CPU observations are retained, not averaged into a replacement.

**The repeat took 50.15% longer than the original sixteen-CPU production run,
and 26.17% longer than the four-CPU control.** Gathering/merging increased
from 5h46m28s to **9h16m57s**, accounting for **68.72% of the additional
production time**. Rustc profile gathering alone increased from 5980.20 to
12218.10 seconds. Other production increased from 4h24m14s to 6h00m02s;
the slowdown is not confined to training. Fixed training jobs therefore
cannot be treated as fixed training duration. Qualification also took longer.
These are qualified release results, but the same-allocation variation is
larger than the initial apparent CPU benefit, so they do not support a
reliable x64 CPU-scaling curve or hosted-runner projection.

The cause is not established: matching recipe and affinity do not demonstrate
matching background load, CPU frequency/power, storage latency or cache
conditions. Before another expensive scaling pair, prioritize phase-aligned
CPU/frequency, memory and disk-I/O observations and isolated fresh rustc/LLVM
training replays. Then use counterbalanced full-release allocations under
stable conditions. No additional full x64 release was dispatched after this
requested repeat.

On 16 October the user requested another x64 16-CPU observation because the
first production time (610.70 minutes) appeared unexpectedly high.
`matched-x64-sixteen-repeat.yml` waits behind the current four-CPU job using
the same machine lock, then requires that exact job and local matched result
to have completed successfully before scheduling a fresh 16-CPU release.
The repeat retains the same recipe, source pins, full qualification and disk
guard, but uses a new workflow-run root and fresh profiles. Both 16-CPU results
are reported separately rather than replacing the first or selecting the
faster one. The protocol's extra x64 repeat is conditional, not a claim that
all cells have two repetitions; per-run VM/attempt identifiers remain unchanged.
A linear extrapolation from the first 16-CPU production time gives about
40h43m at four CPUs, but SMT, fixed-work stages and other nonlinear effects
made that a hypothesis, not a prediction; the completed control above disproves
that extrapolation for this run. The control retained its existing 24-hour
job limit and 1430-minute harness deadline.

The first conditional repeat attempt,
[38941287737](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38941287737),
passed the qualified-four gate but its release job `117225327513` failed
the unchanged 180 GiB free-space preflight before production. The four-CPU
maintenance receipt recorded 176043859968 bytes (163.95 GiB) free on E: after
retaining the full distribution and removing its build tree. This is a
storage-blocked attempt, not a compiler failure or another timing sample.
`matched-x64-space.yml` uses the bounded inventory under the same x64 machine
lock to inspect experiment-owned caches before a fresh repeat.
The repeat gate can now preserve only Cargo/training caches from the exact
qualified x64 four-/sixteen-CPU cells and, if needed, the two completed
optimized pilots in `38406317769`. It uses the shared lossless relocation
helper, explicit x64 runner identity and all four merged-profile checks
(rustc, rustdoc, Clippy and LLVM), before and after relocation. Rust/runtime sources, evidence,
full distributions, profiles and interrupted-build diagnostics remain in
place. Copies on C: are checksum/link-verified before source-cache removal;
the unchanged 180 GiB E: guard must pass before the fresh release starts.
The broad x64 inventory `38976448853` exceeded its 30-minute job limit
without uploading its incremental report. The next repeat gate,
`38977555520`, passed process isolation but rejected the profile manifest
before any relocation: the new guard incorrectly expected a separate fifth
Cranelift profile. The actual producer and downloaded qualified evidence
both contain four merged profiles. The corrected guard requires exactly those
four hashes; independently checked Cranelift backend evidence remains unchanged.
Neither failed maintenance attempt contributes a production timing sample.
Future x64 inventories are restricted to the two cache directories in those
four exact qualified releases, rather than recursively scanning every legacy
experiment and repeatedly counting overlapping parent trees.
The corrected gate in `38980060732` succeeded after preserving seven cache
trees (14745376698 logical file bytes) on C:, with all four completed-result
hashes matching the independently retained evidence. It moved both caches
from each initial scaling cell and the LLVM pilot, plus the Microsoft pilot's
Cargo cache; all data was retained, not discarded. E: then had
194796802048 bytes (181.42 GiB) free. This separate maintenance job is
excluded from the repeat's production and successful release-job timings.

`matched-remaining-scaling.yml` queues only the missing x64/4 and GB300/32/16/4
cells. Independent readiness jobs wait for each runner to reconnect, verify
the previously failed job and retained provenance, check for surviving work,
and upload interrupted-run evidence before allowing fresh release roots.
They do not kill processes or relax the disk guard. Existing qualified cells
are not rebuilt. GitHub's 24-hour queue limit still applies; offline hosts
cannot be restarted or repaired through an unassigned Actions job.

On 16 October the x64 runner reconnected and its isolation check passed.
The first reconnection artifact upload failed because its files spanned
incompatible upload roots; staging the report and interrupted logs beneath
one physical root fixed that failure (verified by 38869537727). E: had only
about 169 GiB free. `matched-x64-scaling-control.yml` therefore preserves the
interrupted build on C: using the same checksum/junction-checked relocation,
then runs only the missing four-CPU control from fresh sources and profiles.
This recovery requires a successful same-run reconnection report. The
interrupted training logs are diagnostic evidence, not accepted timings.

GB300 reconnected on 16 October, but the 32-CPU cell in `38869810910`
failed disk preflight before compilation; its 16/4-CPU dependents were skipped.
The following read-only inventory (`38893912254`) also lost runner
communication. After the runner was restarted, bounded inspections
`38897182002` and `38897351896` succeeded with no surviving experiment worker.
Unrelated Python services were identified and left untouched.
`matched-gb300-space.yml` now records metadata incrementally and limits each
directory scan to 45 seconds, explicitly marking incomplete sizes as lower
bounds rather than using them as totals. D: still had about 76.5 GiB free,
roughly 104 GiB below the unchanged release guard. The two retained failed
build directories total approximately 57 GiB; reclaiming those alone cannot
enable a release. No GB300 data was removed, and no replacement 32-CPU
production run was started without sufficient storage. Additional space is
required before the 32-first scaling chain can resume.

After the user's subsequent GB300 disk cleanup, the old failed run's local
provenance was missing, so readiness attempt `38902759407` stopped without
starting production. The GB300 workflow now explicitly retrieves its
previously preserved evidence from `38869810910`, verifies that historical
receipt/provenance, and still performs fresh live process and storage checks.
The corrected chain
[38903042998](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38903042998)
passed readiness with 226,830,721,024 bytes free on D: (about 211.3 GiB)
and no surviving experiment processes. Its 32-CPU job `116979807783` passed
the unchanged capacity, 180 GiB and fresh-root guards and started setup.
The order remains 32, then 16, then 4 CPUs; no timings from this new chain
are accepted until full production and qualification finish.
That 32-CPU job subsequently lost runner communication at 13:48:33 UTC
on 16 October, about 54 minutes into the combined build/qualification step.
GitHub marked it failed and the dependent 16/4 jobs were skipped. The runner
was reported offline; the job log and new release evidence were unavailable.
This attempt is excluded from scaling results. The disconnect cause remains
unproven, and the new interrupted root `D:\m03042998t32r1` must be inspected
for surviving work and retained evidence before any further restart.

On 17 October, after the requested x64 repeat qualified, GB300 was still
offline. The reconnection gate now additionally verifies failed job
`116979807783` / run `38903042998`, requires the latest root's local matching
provenance, and checks for surviving processes referencing either interrupted
root. The older archived receipt is historical evidence only and cannot
substitute for inspecting this latest interruption. The uploaded reconnection
report identifies both failures and stages the latest local logs. Missing or
mismatched latest evidence blocks the chain rather than silently falling back.
Only the remaining GB300 32/16/4 cells are queued; no completed x64 or ordinary
Arm64 cells are repeated. An offline runner cannot execute even the readiness
check, and GitHub's 24-hour queue-expiry limit still applies.

The [maintainer-focused optimization brief](Rust-Compiler-Optimization-Maintainer-Brief.docx)
adds a short goal and TL;DR, the same measured comparison without runner names,
and an adoption proposal. It separates observed PGO benefits from the combined
LLVM-linker/ThinLTO treatment, and models larger-runner whole-job times against
GitHub's 360-minute limit with a 300-minute planning target. These are conditional
production-speedup scenarios, not measured hosted scaling or promised timings
for particular CPU counts. The original one-page report remains unchanged.

## Completed x64, ordinary Arm64 and GB300 pilots

The fresh x64 replay [38636440191](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38636440191)
passed all five timed compilation commands and all four original correctness
commands for every actual released compiler. The strict analyzer accepted the
complete round, including identical correctness-only NTFS temporary overrides.
No results from failed runs are reused.

The ordinary Arm64 replay [38695519744](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38695519744)
also passed the complete paired round and strict analysis. Its replay step
took 62m 20s; the whole job took 1h 59m 42s, completing at 08:56:35 UTC on
15 October 2026. All nine self-hosted releases and all three downstream
comparisons are now qualified; the repeated standard-hosted study is not.

The [one-page combined Word report](Self-Hosted-Rust-Release-Pilots.docx) and
[machine-readable results](selfhost-pilot-results.json) now include all three
machines, with their separate qualification histories. Word pagination was checked
after rendering. Production excludes setup, verification and uploads; the
results also retain whole-job and cleanup durations and all five native
compilation components.

| Machine / recipe | Full production minutes | Increase vs no PGO | IronRDP seconds | Compile saving |
|---|---:|---:|---:|---:|
| x64 / 4 CPUs / no PGO | 134.1 | Reference | 737.35 | Reference |
| x64 / 4 CPUs / Microsoft PGO | 548.1 | +308.66% | 555.78 | 24.62% |
| x64 / 4 CPUs / LLVM PGO + ThinLTO | 787.3 | +486.97% | 526.00 | 28.66% |
| Ordinary Arm64 / 4 CPUs / no PGO | 180.1 | Reference | 1348.55 | Reference |
| Ordinary Arm64 / 4 CPUs / Microsoft PGO | 431.9 | +139.85% | 1018.93 | 24.44% |
| Ordinary Arm64 / 4 CPUs / LLVM PGO + ThinLTO | 656.4 | +264.52% | 972.70 | 27.87% |
| GB300 / 64 CPUs / no PGO | 138.5 | Reference | 200.28 | Reference |
| GB300 / 64 CPUs / Microsoft PGO | 182.6 | +31.84% | 157.30 | 21.46% |
| GB300 / 64 CPUs / LLVM PGO + ThinLTO | 203.3 | +46.79% | 156.28 | 21.97% |

On x64 the LLVM recipe saves another 29.78 seconds per five-command sequence
relative to Microsoft PGO (5.36% faster), but costs another 239.16 production
minutes. On GB300 the respective differences are 1.02 seconds and 20.70 minutes.
On ordinary Arm64 LLVM saves another 46.22 seconds over Microsoft PGO (4.54%
faster), at another 224.50 production minutes.
These are single paired pilot observations, not established repeatable
advantages. Machines are not pooled; four-CPU x64 and 64-CPU GB300 are not an
architecture-controlled comparison. Ordinary four-CPU Arm64 remains separate,
and the repeated standard-hosted study remains incomplete.

## Qualified ordinary four-CPU Arm64 releases

LLVM release [38542164879](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38542164879)
completed successfully on `MARCPE-D4-Arm64`, including full distribution and
extracted-suite qualification. Production was 39,385.06 seconds (10h 56m 25s);
the whole job was 45,598 seconds (12h 39m 58s). The selected baseline and
Microsoft-PGO releases are 38225557840 and 38532798400, respectively.
All three match the pinned source/submodules, native tool hashes, exact
runner, four-worker bootstrap settings and full archive coverage, including
Arm64EC. The selection is recorded in `selfhost-arm64-pilot-runs.json`.

| Recipe | Production seconds | Increase vs no PGO |
|---|---:|---:|
| No PGO | 10,804.58 | Reference |
| Microsoft PGO | 25,914.76 | +139.85% |
| LLVM PGO + ThinLTO | 39,385.06 | +264.52% |

The ordinary Arm64 replay branch is
`experiment/matched-release-selfhost-arm64-benchmark-pilot`. It requires
`MatchedStandardArm64`, checks the exact runner name and NTFS temporary
filesystem for correctness, and shares the ordinary release concurrency lock. It uses the
same five offline commands, four original correctness commands, common
baseline Cargo/std and fresh targets as the existing pilots. GB300 retains
its separate labels, selection and 64-worker policy. The accepted ordinary
Arm64 results are included above, without substituting any GB300 measurements.

Initial replay 38695414694 stopped at filesystem preflight before downloading
archives or compiling: ordinary Arm64's D: is also ReFS. The replacement uses
the already qualified x64 arrangement: correctness-only TEMP/TMP on explicitly
checked C: NTFS, identically for all three recipes. Timed builds, Cargo home
and cold targets stay on D:. This change is recorded in the replay index and
checked by the analyzer; GB300 and hosted defaults remain unchanged.

## Excluded x64 replay history

The second x64 replay, 38601292855, also exhausted LLVM distribution download
retries before measurements. Subsequent x64 setup downloads the release
evidence only and copies archives from each selected release's local
`retained-dist`. Every archive is SHA-256 checked against the downloaded
manifest both before and after copying. Missing or mismatched archives fail
explicitly; there is no partial-download fallback. The normal compiler/source/
tool qualification checks remain in place. This changes setup transport only:
workload targets and Cargo home remain fresh, and no interrupted build is reused.
GB300 archive transport is unchanged.

The first retained-archive setup (38628375935) exposed the download action's
single-match layout: each evidence artifact was extracted directly into `a`,
not into its artifact-name directory. The setup failed before archive staging
or measurements. Each x64 evidence download now has an explicit per-variant
destination. The replacement starts in a fresh root; the overwritten evidence
from that failed setup is never reused.

Run 38629796046 then reached staging but exposed Windows PowerShell 5's JSON
array pipeline behavior: the array wrapper created one nested manifest entry.
Direct assignment now preserves scalar entries for iteration. The corrected
iteration was exercised against all three actual manifests under Windows
PowerShell 5.1 (19/20/20 entries), rather than only parsing the script syntax.
Neither setup failure reached compilation measurements.

Run 38630900550 revealed that `Get-FileHash` is unavailable in the runner's
PowerShell environment. Archive verification now uses streaming .NET SHA-256,
with deterministic disposal of the file and hash handles. The exact helper
passed a known SHA-256 test vector under Windows PowerShell 5.1; no hashing
gate was removed.

Run 38632084070 passed archive staging and all five baseline compile commands,
then failed `filesystem_controls_query_the_opened_file_handle` on
`STATUS_INVALID_DEVICE_REQUEST`. Diagnostic 38636102151 confirmed E: is ReFS:
`fsutil objectid create` rejects it with "An NTFS volume is required", while
the same disposable-file probe succeeds on C: (NTFS). This is not the GB300
UDP failure. Subsequent x64 replays place only correctness-process TEMP/TMP
in a fresh, explicitly checked C: NTFS directory, consistently for all recipes.
Timed compilation, target directories and Cargo home remain on E:. The exact
correctness overrides are recorded and validated separately; hosted and GB300
defaults remain unchanged. No test is skipped, no assertion is weakened, and
the failed partial baseline is excluded.

## x64 replay download interruption

All three x64 release recipes qualified. The first downstream replay,
38588758754, failed during setup: downloading the 1.72 GB LLVM distribution
artifact exhausted five retries. No compilation measurements or correctness
tests started. The evidence and maintenance artifacts downloaded successfully;
the failure is not a compiler or correctness result. Fresh replacements used
unchanged qualification gates and fresh benchmark directories.
The failed setup is excluded, and no partial download is treated as verified.

This new study replaces cross-version comparisons with actual full distribution
builds and downstream measurements of their resulting compilers. The
[protocol](protocol.json) is preregistered; amendments below are declared before
replacement runs, with every pilot excluded from final estimates.

Three configurations per native architecture share Rust commit
`7db17d9b5bbe6b16be2dc86b4bfae81d6e1ae238`, LLVM, clang-cl, SDK selection, full
distribution scope and four-logical-CPU standard GitHub runner class:

| Configuration | PGO | Native linking | LLVM / Rust cross-crate ThinLTO |
|---|---|---|---|
| Baseline | None | Microsoft link.exe / lib.exe | Off / off |
| MSVC retained | Fresh full opt-dist profiles | Same Microsoft tools | Off / off |
| LLVM option | Fresh full opt-dist profiles | lld-link / llvm-lib | On / on |

The baseline is an explicit no-PGO control, **not the existing shipped x64 PGO
recipe**. The study estimates the full cost of each optimization recipe against
that control; it must not be labelled the incremental change to today's x64
upstream release pipeline. Fresh profiles differ across production jobs, so
the LLVM contrast measures the complete recipe, not LTO in isolation.

The pilot runs one job per configuration/architecture. If all six complete,
the full study runs three independent cold build jobs per cell. Pilot results
are excluded. Hardware identity, tool hashes, full output manifest and all
failures are retained. No prior compiler-only timings fill missing cells.

The production timer includes helper construction, full tool/frontend/backend
PGO collection and full distribution assembly. All variants then run the same
extracted-distribution test suite. GitHub's actual job duration additionally
includes initial setup, runtime preparation, tests and uploads, and will be
reported separately from production time and queue wait. Upload duration
depends on retained evidence and is not a pure compiler cost.

Full distribution retains docs, tools, installer and Arm64EC where applicable.
No fresh-profile job consumes a previous job's profiles or cached LLVM. The
350-minute safety boundary permits diagnostics before GitHub's six-hour cap.
A timeout is an unfinished lower bound, never a successful completion time.
Any split-job alternative requires a declared protocol amendment and separate
elapsed-path/runner-time accounting.

The exact resulting distribution compilers will be compared on IronRDP's five
original native offline Cargo commands, using a common baseline Cargo/std
within each matched set. One warmup and three measured rounds run on each
benchmark VM, with compiler-order counterbalancing and original correctness
commands outside timing. These measurements cannot be borrowed from the old
source/version or the compiler-only study.

The requested final deliverable is a one-page Word comparison of full release
cost increases and IronRDP compilation savings, expressed against their stated
baselines. No document claiming completed measurements is produced before the
required datasets and qualification checks are available.

## Pilot repair, declared before replacement runs

[Pilot 38122240736](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38122240736)
failed all six cells. None supplies a completed release duration. The original
protocol used Rust `07bb50a774b11375032aacc16fd9a70f090f8642`.

The replacement uses short physical checkout, runtime and evidence roots on
every runner (`C:\mr` or `D:\mr`), not drive aliases that path canonicalization
can expand. Local native Arm64 reproductions confirmed that an existing
270-character archive path fails with Microsoft link.exe while the same archive
at 100 characters links, and that MSVC's relative header include fails with a
211-character source path but succeeds at 130 characters. The AWS-LC header
exists in the published dependency archive; this is not a missing dependency.
Cargo home, temporary files and qualification extraction also use the short root.

The Arm64 LLVM pilot independently failed on Rustdoc's DLL-data references.
Cargo passes `-Clinker-plugin-lto` when compiling ThinLTO dependencies; that mode
assumes static linking and omits Windows DLL-import annotations. Compiler-private
tools instead import data from `rustc_driver`. The new common Rust source
overrides that dependency mode with
`-Clinker-plugin-lto=no -Cembed-bitcode=yes` for MSVC-target compiler-private tools
and codegen backends at cross-crate-LTO stages. It does **not** disable Rust's
in-process ThinLTO. A three-crate atomic-static DLL reproducer fails before the
override, then links and runs after it. The exact added Rust regression fixtures
also link and run locally with both link.exe and lld-link and both Thin/FatLTO.

The source amendment applies to all cells; its conditional flags do not change
the no-cross-crate-LTO baseline/MSVC-PGO recipes. Full tools, docs, installer,
fresh profiles, correctness requirements and timing boundaries remain unchanged.
Local diagnostic successes are not substitutes for the replacement hosted pilot.
Downstream replays likewise use short physical workload, compiler, Cargo-home
and temporary roots uniformly across variants, before any benchmark pilot or
measured replay. No existing downstream timing is rescaled to account for paths.

[Replacement attempt 38133710688](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38133710688)
was stopped after x64 setup could not move the checkout from the workspace's
D: volume to the system C: volume. No production timing from that attempt is
accepted. The short root is now selected on the **workspace volume**, with an
atomic directory rename instead of a cross-volume PowerShell move. The same
rule applies to downstream benchmarks.

Pilot 38133940060 reached complete Arm64 baseline distribution assembly
(22 files, including the required components) in 6911.61 production seconds.
Qualification then passed 22,097 UI cases and failed one, E0152, solely because
its expected diagnostic normalizes paths under Rust's build root. The harness
had extracted the compiler outside that root. Extraction now uses upstream
opt-dist's `build/unpacked-dist` layout; neither the expected diagnostic nor the
test selection is changed. That pilot observation is not a qualified release-job
duration and remains excluded. Subsequent failed jobs preserve any distribution
files under explicitly **unqualified** artifact names, never as accepted inputs
to the downstream benchmark.

The MSVC-PGO pilot also completed production on both architectures: 13,700.72
seconds on x64 and 16,499.84 seconds on Arm64. Both hit the same E0152 harness
issue. Arm64 additionally failed `expr/if/expr-stack-overflow.rs` with
`0xc00000fd` (compiler stack overflow). This is a real qualification failure,
not just output normalization, and must not be waived or hidden by increasing
the qualification process's stack limit.

The retained earlier compiler-only Arm64 baseline and PGO compilers both pass
that exact source test locally; they used different profiles and are not proof
that the failed full-release compiler is sound. The failed pilot did not retain
its distribution archive, which is why subsequent failures now retain
unqualified binaries. A separate `experiment/matched-release-stack-diagnostic`
branch runs only Arm64/MSVC-PGO, rebuilding a compiler with the failed job's
hash-verified Rust/LLVM profiles, unchanged compiler source and matching native
tools. It preserves the compiler and PDBs, then runs the nested-expression test
with the default stack limit and a separate phase-tracing invocation. This
profile-reuse diagnostic is **not** a fresh release build or a timing sample,
does not produce `result.json`, and cannot feed the matched analysis.
Its source remains pinned to `a2bb36e3594a73a806ad9d2bf2694fcd977c3261`
independently of later release-recipe amendments.

## LLVM feasibility amendment

Both LLVM cells in pilot 38133940060 reached the global 350-minute safety
boundary without a distribution. On x64 the initial frontend training-tools
build was still incomplete. Arm64 completed the frontend stage in 14,414.18
seconds and was still constructing the backend-instrumented compiler. Neither
observation is a completed release duration, and neither establishes an
IronRDP benefit. Their censored durations cannot be substituted into a
percentage-cost comparison.

The revised opt-dist recipe disables LLVM ThinLTO on intermediate LLVM builds
that are discarded before distribution: initial frontend preparation, its
static-LLVM reuse during frontend PGO optimization, and backend instrumentation.
It retains static LLVM, the selected linkers/librarians, and the configured Rust
LTO throughout. The final distribution still enables LLVM ThinLTO for the LLVM
option. Baseline/MSVC-PGO already have LLVM ThinLTO disabled, so this does not
introduce a different native-tool choice there.

The unit regression covers static/shared LLVM, both Windows architectures and
full/fast training modes, including the absence of a final-distribution LTO
override. Hosted feasibility remains unproven: the dedicated
`experiment/matched-release-llvm-pilot` branch runs only the two LLVM pilot cells
to test the revised recipe while the independent Arm64 stack failure is
diagnosed. It does not replace the required qualified six-cell pilot or supply
measured samples. All final comparison cells must share the same source revision.
That two-cell feasibility run is
[38158053450](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38158053450),
pinned to Rust `29d50151dcdd6e5b885920bc535047b380006900`, before the MIR repair below.

## Default-stack MIR diagnosis and repair

[Diagnostic 38155374593](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38155374593)
reproduced the Arm64 overflow with both the original and phase-traced invocations.
The retained compiler archive has SHA-256
`b55e9c49be303b870ce74a50733d82313ed5f93fee767b1bce18c90839067756`.
After verifying source, parent profile hashes, native tools and archive identity,
the same compiler also failed locally at the unchanged default stack limit.

Phase tracing passes parsing and type checking. Native ARM64 unwinding locates
the failure in MIR construction, with `expr_into_dest` retaining two 1,744-byte
frames per nested `else if`: a scope wrapper and the expression itself. The
existing regression contains 5,205 arms. Reduced-stack tests of older compilers
were debugger controls only; they failed earlier in parsing and are not evidence
about this full-profile failure.

The common Rust source now handles scope wrappers separately from the large,
non-inlined expression dispatcher. Scope cleanup, coverage instrumentation and
block-context behavior are preserved, and no stack limit or test expectation is
relaxed. Native bootstrap type-checking and pinned formatting checks pass.
The `experiment/matched-release-repair-stack-diagnostic` branch explicitly
rebuilds this repaired source with the original profiles to check the failure
quickly. Its provenance marks the source/profile difference; it remains
unqualified and cannot supply a release or downstream timing. Success there
still requires new fresh-profile production and full qualification before any
measurement matrix is accepted.

The repaired compiler in
[diagnostic 38167588581](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38167588581)
passes both default-stack probes on the native hosted runner and also passes
locally, without a stack override. Its archive SHA-256 is
`b44fa872890b176b192be585996af00fc5e66a0acaaf7deff0c2dcefd8f698e5`.
Seven existing scope/drop and coverage fixture configurations emit byte-identical
MIR before and after the repair. The four executable configurations also pass
their runtime assertions, covering match-arm scopes and temporary destruction
under both abort and unwind panic strategies. The other three cover tail
expressions and branch coverage instrumentation.

With that diagnostic gate passed, `experiment/matched-release-msvc-pilot` runs
the four baseline/MSVC-retained full-release pilot cells on this common source
while LLVM feasibility is investigated separately. These jobs use fresh profiles
where applicable and the complete qualification suite. They remain excluded
pilots, not substitutes for the three-repetition measurement matrix.

## Fresh-profile qualification outcome

Run 38172717639 passes complete baseline qualification on both architectures.
The x64 baseline takes 9,308.65 seconds for production and 11,065 seconds for
the complete job; Arm64 takes 6,947.20 and 9,389 seconds respectively. These
remain single excluded pilot observations, not population estimates.

Arm64 MSVC-PGO completes production in 16,118.67 seconds, but its fresh profiles
expose another overflow in the same nested-expression regression. The other
22,097 UI cases pass. The actual unqualified compiler archive
(`rustc-nightly-aarch64-pc-windows-msvc.tar.xz`, SHA-256
`7d26046aca16a6d3fa17800758fede8e99b41f4060fd814d0bf52c5915140bae`)
reproduces locally. Native unwinding shows a 2,880-byte general expression frame
plus a 400-byte scope wrapper per nested arm. The scope-only repair is therefore
insufficient, despite passing its original-profile diagnostic.

The follow-up source also separates `if` lowering from the large dispatcher.
The new diagnostic consumes the fresh failing profiles from run 38172717639,
whose parent source is `ab0afc7ee6827da442070b034830b5d69a9b537c`. Original
diagnostic runs remain pinned to their historical workflow commits; no old
success is reclassified as fresh-profile qualification.

The x64 MSVC-PGO pilot times out during final distribution assembly. Both LLVM
pilots in run 38158053450 also time out, despite reaching final production:
x64 is still linking LLVM tools and Arm64 is building Rustdoc. All three hit
the 350-minute safety boundary; they are unfinished observations, not completed
costs. GitHub's six-hour hosted-job limit cannot be extended by setting a larger
workflow timeout. A multi-job recipe and explicit elapsed-pipeline/total-runner
accounting are required before replacement production measurements.

## Separate self-hosted Arm64 experiment

At the user's request, `MARCPE-D4-Arm64` was validated through an actual
Actions job before scheduling releases. This is not the local CLI computer
(`MARCPE-C2-1`); no local SDK installation paths are assumed. The preflight
checks native MSVC/SDK linking, builds the Rust MIR compiler component, and
compiles the pinned IronRDP core library and runs its native TLS integration
tests. A Cargo success with no compiled artifacts or no executed tests is
rejected; `ironrdp-core` itself disables unit-test targets.

[Preflight 38224862582](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38224862582)
passes all these checks, including the native TLS integration test. Bootstrap
explicitly selects `aarch64-pc-windows-msvc`; autodetection previously selected
an existing GNU toolchain. The recorded runner CPU is NVIDIA RTX Spark N1X,
with 20 cores and 20 logical processors. Neither earlier validation attempt
alone established the complete gate: one selected the wrong Rust host and
the other used a no-op Cargo test target.

With that gate passed, `experiment/matched-release-selfhost-arm64-pilot`
selects only native self-hosted Arm64 jobs, serializing the baseline,
Microsoft-retained PGO and LLVM-option full releases on that machine. Every
cell has a new physical source, Cargo-home, runtime and temporary directory;
compiler/profile caches are not shared. The existing four-CPU process affinity
and four build jobs remain in effect. Actual CPU identity/count, runner name
and native-tool hashes are retained. The self-hosted deadline is 530 minutes,
leaving ten minutes for evidence upload before a 540-minute workflow timeout.
Hosted jobs remain at their original 350/360-minute limits.

[Pilot 38225557840](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38225557840)
was launched from harness `16468b3a87f03946b19d0f81f0064b3082a99fc0`, with
Rust `7db17d9b5bbe6b16be2dc86b4bfae81d6e1ae238`. Its first job was confirmed
executing on the intended runner. Launch is not successful release qualification.

Self-hosted evidence explicitly records `runner_class=self-hosted-arm64`.
The hosted-study analyzer rejects it: these times must be reported as a separate
machine-specific comparison, never combined with hosted x64 or Arm64 samples.
Neither preflight nor a diagnostic reused-profile success qualifies a full
release; fresh training and the complete distribution checks remain required.

## Separate self-hosted x64 experiment

The subsequently registered `MARCPE-TEST01-X64` runner uses the same preflight,
now shared in `matched-selfhost.yml` and `validate_selfhost.py`. The
`experiment/matched-x64-selfhost-validate` branch selects native x64 Python,
MSVC and an explicitly pinned `x86_64-pc-windows-msvc` bootstrap host.
The same real compilation and executed-test gates apply.

After validation, `experiment/matched-release-selfhost-x64-pilot` selects
only the three x64 full-release variants, with the same fresh directories,
four-CPU affinity and 530/540-minute safety/job limits as the Arm64 experiment.
Its concurrency group is separate from Arm64, so the machines can work
independently while serializing jobs on each machine. Evidence identifies
`runner_class=self-hosted-x64`, and the hosted analyzer rejects it.
Existing Arm64 runs remain pinned to their original workflow revisions.

[x64 preflight 38230661502](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38230661502)
passes the native executable, compiler-component and IronRDP compile/test gates.
The machine records an Intel Core i9-11900, eight cores and 16 logical
processors, MSVC 14.44.35207 and Windows SDK 10.0.26100.0. The native bootstrap
reports `x86_64-pc-windows-msvc`.
[x64 pilot 38231778023](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38231778023)
was then launched from harness `a304bc7f5bfd07fa3bdc9a301da0b42ed8d1c9b6`
with the same Rust source pin as the Arm64 pilot. These are separate-machine
feasibility runs, not a controlled comparison of processor architectures.

The first x64 pilot fails during runtime preparation, before Rust production:
MSVC's approved `vctip.exe` descendant reports an 8.3 executable path, which
did not match the long-path allowlist. Process accounting now canonicalizes
both sides, still allowing only the exact approved executable and counting
its CPU. Real Windows regression tests exercise a short-path child and reject
an unapproved child; no telemetry policy is changed on the persistent machine.

The later cells also expose a workflow interpolation error: a replica suffix
turned `$variantCode` into the undefined variable `$variantCode1`. Bracing the
PowerShell variable restores separate variant/replica roots; a regression
executes the rendered naming expression for all nine combinations. Existing
roots are not reused or deleted. The running Arm64 baseline is preserved,
but subsequent Arm64 variants need the corrected workflow before retrying.

## GB300 high-parallel Arm64 track

The user separately authorized `GB300-Arm64` with label `HighCoreCount` and
accepted a fixed 64-CPU configuration. The native preflight exercises an
actual 64-CPU Windows Job Object before releases are scheduled. The initial
preflight exposed that one legacy processor-group mask cannot cover the
requested CPUs. The high-core path uses `JobObjectGroupInformationEx` with
explicit masks across groups, reads back the kernel configuration, and runs a
probe on every selected CPU while requiring excluded CPUs to reject affinity
requests. The four-CPU measurement path keeps its original single-group policy.
The release branch `experiment/matched-release-selfhost-arm64-highcore-pilot`
selects only Arm64 and that label, with an additional exact runner-name gate.
Its concurrency group is independent of the four-CPU runs.

All three variants use 64 build workers and inherited 64-CPU process-tree
affinity, including runtime preparation, compiler construction and distribution
qualification. Cargo and standalone CMake build parallelism are explicitly 64;
LLVM permits two simultaneous link jobs. Variants run sequentially with fresh
directories so they do not contend with each other. The full distribution,
Arm64EC, compiler codegen settings, training workload and qualification tests
are unchanged. In particular, the pinned PGO collector retains its four Cargo
jobs and single frontend thread: training does not promise 64-way scaling.

Provenance identifies `self-hosted-arm64-highcore`, build/affinity/link limits
and training concurrency. These observations cannot enter the hosted analyzer
or be pooled with either four-CPU machine. Fresh qualified distributions and
separate downstream high-core IronRDP replays are still required before a
release-cost versus compilation-saving conclusion is possible.

[GB300 preflight 38247985162](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38247985162)
passes native compiler/SDK execution, the Rust compiler-component check and
IronRDP compilation/integration testing. Recorded CPU: Grace A02P, 72 cores
and 72 logical processors; MSVC 14.51.36231 and SDK 10.0.26100.0.
Windows exposes groups of 64 and eight processors. The affinity probe
successfully executes on all 64 selected group-zero CPUs and rejects every
one of the eight excluded group-one CPUs. The initial preflight's legacy
mask failure is not a hardware-capacity failure.

[GB300 pilot 38248685449](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38248685449)
was launched from harness `308cc96caf359fd76fc3c4c0eec945bbf0a901cb`,
using the common Rust source `7db17d9b5bbe6b16be2dc86b4bfae81d6e1ae238`.
These remain excluded feasibility pilots until full release qualification.

The first GB300 pilot exhausts D: during the LLVM portion of baseline
production, before any distribution is completed. The other two variants
then fail while downloading Actions. The user cleared space and authorized
a restart. Subsequent high-core jobs record starting capacity and require
at least 180 GiB (193.3 decimal GB) free before each variant as a safety floor,
not an upper bound on storage use. Retries use new run-specific directories,
never the failed partial build as a cold measurement.

The initial 200 GiB floor rejected a later reading of 206.2 decimal GB
(192.1 GiB). At the user's explicit request, it was lowered to 180 GiB to
proceed with the available space. This accepts greater disk-exhaustion risk;
each subsequent variant still checks remaining space, and retained build
directories are not silently removed.

## Standard self-hosted Arm64 baseline qualification

The baseline job in run 38225557840 passes full distribution qualification
on `MARCPE-D4-Arm64`, using Rust `7db17d9b5bbe6b16be2dc86b4bfae81d6e1ae238`.
Production takes 10,804.58 seconds; the complete job takes 16,677 seconds
(08:45:42 to 13:23:39 UTC). This is one excluded pilot, not a repeated estimate.
The production interval includes full distribution construction, not just
offline compiler CPU work.

The two subsequent optimized cells fail before building. The generic Arm64
labels allow one to land on the newly registered GB300, where the exact-name
gate correctly rejects it; the other hits the old directory interpolation
bug. The standard runner now has the additional `MatchedStandardArm64` label,
required by its validation and release workflows. The
`experiment/matched-release-selfhost-arm64-optimized-pilot` branch retries
only Microsoft-PGO and LLVM/ThinLTO with corrected routing and fresh roots,
preserving rather than rebuilding the qualified baseline.

After the interrupted Microsoft-PGO attempt, the
`experiment/matched-release-selfhost-arm64-msvc-only-pilot` branch schedules
only that missing recipe using the current 24-hour job budget. It shares the
ordinary Arm64 concurrency lock, so it waits for an active LLVM job instead
of cancelling or competing with it. The baseline and active LLVM cell are
not restarted, and the retry uses a fresh run-specific build root.

The older ordinary Arm64 LLVM job 114980960970 in run 38255849700 hit its
530-minute internal safety deadline at 18:12:52 UTC on 13 October
(`subprocess.TimeoutExpired` in the full opt-dist command). Its job ended at
18:15:04 UTC after evidence upload; it is not a qualified release cost.
The queued Microsoft-only replacement 38431443964 then started. The
`experiment/matched-release-selfhost-arm64-llvm-pilot` branch schedules one
fresh LLVM replacement behind it with the current 24-hour job limit and
ordinary-runner concurrency lock. Interrupted outputs are not reused as
cold-build inputs, and the qualified baseline remains untouched.

## GB300 baseline utilization evidence

Run 38282254692 completes and qualifies its 64-CPU baseline. The production
interval is 8,309.48 seconds. Windows Job Object accounting reports
21,365.30 CPU-seconds, averaging 2.57 active CPUs over production despite
the verified 64-CPU affinity. This confirms the user's low-utilization
observation; configured worker count is not achieved average parallelism.

The production invocation in `build/metrics.json` lasts 8,244.14 seconds.
Summing its exclusive (child-excluded) step durations avoids double counting:
distribution assembly/packaging is 6,132.72 seconds (102.21 minutes, about
74% of production), tool construction 780.27 seconds, compiler/standard-library
steps 467.39 seconds, LLVM/LLD 254.05 seconds, documentation generation
465.53 seconds and vendoring 136.96 seconds. Remaining time includes bootstrap
startup and small orchestration steps. These categories are wall time, not
raw CPU time or purely offline compilation.

Within packaging, the combined distribution/MSI step takes 3,032.78 seconds
and the two documentation packaging steps take 2,564.49 seconds combined.
The completed logs therefore locate the dominant elapsed-time cost in
packaging/assembly rather than failure to select 64 compile workers.
They do not yet separate compression CPU from file I/O or other packaging
costs; changing the required distribution scope would invalidate this comparison.

## Recovery after nine-hour self-hosted limits

Both four-CPU x64 optimized jobs in run 38236237914 hit the 530-minute
safety boundary. Microsoft-PGO reached final Clippy construction; the LLVM
option was linking LLVM tools in its final PGO-use build. Neither result is
a completed release cost. Subsequent self-hosted jobs use a 1,440-minute
(24-hour) workflow budget and a 1,430-minute internal deadline, preserving
ten minutes for uploads. This is headroom, not an expected duration.
Hosted limits are unchanged.

The `selfhost-x64-optimized-pilot` and
`selfhost-arm64-highcore-optimized-pilot` branch suffixes restart only the
missing optimized variants. All training and build directories are fresh;
successful baselines remain separately identified pilot observations.
Recovery of historical baselines uses the separate
`matched-selfhost-recovery.yml` workflow (`experiment/matched-selfhost-reclaim`).
It validates the exact qualified source/run/runner identity and every archive
against the complete distribution manifest, moves the archives to the same
experiment's `retained-dist`, preserves bootstrap metrics, and removes only
that experiment's `r/build` subdirectory. Source, evidence and PGO profiles
remain. No failed build is reused as a cold build.

New successful self-hosted cells perform the same reclamation **after**
distribution/evidence uploads so the following variant can use the available
space. This maintenance is outside the recorded production interval but
inside whole-job wall time; the separate `*-maintenance` artifact records
its start/end and before/after free bytes. Whole-job comparisons must disclose
this added maintenance rather than attributing it to compiler production.
The 180 GiB high-core startup floor remains unchanged.

Self-hosted downstream replay uses an explicit JSON mapping from each variant
to its release-run ID (`matched_release_probe.py --release-runs FILE`).
It requires matching qualified source, runner name, resource class, logical
CPU count, build worker/affinity counts and native tool hashes; it still
extracts the actual checksummed distributions and shares baseline Cargo/std.
The high-core replay sets both Cargo workers and measured affinity to 64.
Four-worker behavior remains the default for other native probes.
The older qualified x64 baseline predates the `build_jobs` metadata field:
its archived `bootstrap.toml` explicitly records four workers. Self-hosted
replay verifies the archived configuration for every variant, binds its hash
into benchmark provenance, and records when that file supplies the legacy
worker-count evidence. It never silently assumes a missing worker count.
Hosted replay still requires a single release run and rejects self-hosted
artifacts. Separate self-hosted index metadata must not enter the hosted
18-job analyzer, and pilot observations remain excluded from its final estimates.
`matched-selfhost-ironrdp.yml` schedules the two available self-hosted machine
classes separately, using the same per-machine concurrency locks as release
construction. Its `selfhost-<machine>-pilot-runs.json` selection files are
committed only after all selected distributions qualify; a missing selection
fails rather than silently selecting an old run. No benchmark is launched
merely by adding this workflow.

The separate `analyze_selfhost_matched.py` accepts only complete, qualified
pilot compiler sets with exact per-variant job/archive provenance and a
complete paired native replay. It reports observed production/job increases
and IronRDP savings, with no confidence interval from a single observation.
Its one-page Word layout explicitly labels the results preliminary, retains
the distinction from the hosted preregistration, and shows the full GitHub
cleanup-step time alongside whole-job time. Release artifacts are organized
under one `--releases` subdirectory per runner class; each benchmark index is
passed separately with `--index`. The renderer's two-machine layout is checked
using Word pagination, not assumed from document dimensions.

### Fresh 24-hour retries

The GB300 baseline's 22 distribution files were checksum-preserved at
`D:\m82254692b1\retained-dist` by
[recovery 38367095934](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38367095934).
The observed free space rose from 163.16 to 192.85 decimal GB. Removing only
the inspected build cache of successful preflight 38247985162 in
[recovery 38367787711](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38367787711)
then brought free space to 194.03 GB, above the unchanged 180 GiB floor.
Preflight evidence and baseline source/evidence were retained.

Fresh optimized-only runs from harness
`d400690ed8276c28a3a302a9044288e75da04cd9` are:

- [GB300 38368036985](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38368036985):
  passed its storage/runner gate and started source preparation.
- [x64 38368289662](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38368289662):
  started source checkout after successful baseline archive preservation and
  reclamation. Its free space rose from 380.00 to 411.97 GB; the 19 baseline
  distribution files remain at `E:\m36237914b1\retained-dist`.

Launch alone is not a completed release timing. The ordinary Arm64 runner was
offline at launch, then returned and started its previously queued LLVM cell
at 09:22:47 UTC on 13 October. That older cell retains its nine-hour budget;
its missing Microsoft-PGO cell is not replaced with GB300 data.

The x64 Microsoft-PGO retry was cancelled at 11:34:47 UTC during training.
Its logs record `KeyboardInterrupt` and `STATUS_CONTROL_C_EXIT`, not the
24-hour timeout or a demonstrated compiler defect. The initiator is unknown.
Evidence was preserved; LLVM job 115275351619 started afterward. No automatic
replacement of the cancelled Microsoft-PGO job was launched.

### Qualified GB300 Microsoft-PGO pilot

Job 115197808134 in run 38368036985 subsequently completed successfully.
It used fresh profiles, the same Rust revision, the same native tool hashes
and the same 64-worker/64-CPU resource class as its qualified baseline.

| GB300 recipe | Full production seconds | Whole job seconds | Production increase |
|---|---:|---:|---:|
| Controlled no-PGO baseline | 8,309.483881 | 10,083 | reference |
| Microsoft-retained PGO | 10,955.446016 | 12,912 | +31.84% |

The whole-job increase is 28.06%; this additionally includes post-upload
build-space cleanup, which was outside the historical baseline job. The
extracted-distribution suite passed in 1,181.04 seconds. The PGO distribution
retains all 22 baseline artifact names and adds the expected
`reproducible-artifacts-nightly-aarch64-pc-windows-msvc.tar.xz` profile bundle.
Upstream bootstrap creates that bundle when PGO-use profiles are present;
it is not an omitted baseline tool or an unannounced reduced output scope.
These are single pilot observations. No new IronRDP saving is claimed yet.

The following LLVM job 115281290625 failed before preparation at the unchanged
180 GiB gate: only 148.37 decimal GB remained. Completed build-space reclamation
had already preserved the PGO archives at `D:\m68036985m1\retained-dist`.
Read-only inventory 38393790110 confirmed approximately 148.48 GB free, about
44.79 GB below the gate. The inspected remaining Cargo/training caches and old
failed build cannot by themselves recover that shortfall. No further storage
limit reduction or source-repository deletion was performed.

After additional user-provided space, the
`experiment/matched-release-selfhost-arm64-highcore-llvm-pilot` branch retries
only the missing LLVM cell. It retains the 180 GiB startup gate, 64 workers,
24-hour job budget, fresh source/profile/build directories and full qualification.
The successful baseline and Microsoft-PGO cells are not rebuilt.

### Complete GB300 pilot set and downstream replay

LLVM PGO + ThinLTO job 115297414553 in run 38397813994 qualified successfully.
Production took 12,197.582781 seconds (203.29 minutes), 46.79% above the
controlled baseline. The whole job took 14,169 seconds, including post-upload
cleanup; extracted-distribution qualification passed in 1,172.15 seconds.
It retains all 22 baseline archive names plus the same expected PGO profile
bundle as the Microsoft-PGO recipe.

`selfhost-arm64-highcore-pilot-runs.json` selects the three qualified runs:
baseline 38282254692, Microsoft PGO 38368036985 and LLVM PGO + ThinLTO
38397813994. Their actual qualification records, source pins, native tool
hashes, archive-name coverage and archived 64-worker bootstrap configurations
were checked before selection. The separate high-core benchmark branch
replays these released compilers with shared baseline Cargo/std and 64 Cargo
workers/CPU affinity. This is one paired pilot round, not the repeated hosted
study. Release costs alone do not establish downstream IronRDP savings.

The actual paired replay is
[38431290827](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38431290827),
launched from harness `e852f146c9ad84d4d38a4d3f015461a1fec9f114`.
Its launch is not yet a completed downstream result.

That replay subsequently failed correctness, so it is excluded rather than
used to claim a compile saving. Baseline completed all correctness commands;
Microsoft-PGO compiled all five measured commands, then
`e2e::egfx_moves_onto_the_udp_tunnel_with_soft_sync` timed out at `e2e.rs:1335`
waiting for the server connection to end after tunnel closure. LLVM replay
was not reached. The automatic report generator stopped without publishing
a report. `matched-udp-diagnostic.yml` rebuilds the unchanged workload with
each retained released compiler and executes the exact test three times per
compiler, recording every outcome. These are diagnostic repetitions, never
retries accepted into the failed benchmark or replacements for full correctness.

Isolated diagnostic 38438214909 completed all nine test executions successfully
(three per compiler). This does not establish the cause of the full-suite
failure or prove compiler equivalence. The next bounded diagnostic runs all
five build commands followed by all four original correctness commands for
every compiler, with the benchmark's 64-CPU Windows Job Object accounting.
It keeps fresh per-compiler targets and records failures without silently
retrying or excluding a test. The first isolated diagnostic did not use
that accounting context, so its success alone cannot validate the benchmark.

Full-sequence diagnostic 38440022998 passed all five build commands and all
four original correctness commands for each of the three released compilers
under the 64-CPU accounting context. No workload source or timeout was changed.
The original UDP timeout remains unexplained; these passes do not establish
a repaired defect or prove the failure was unrelated to the compiler.
After these two bounded diagnostics, one new complete paired pilot replay is
scheduled with fresh targets and all correctness gates unchanged. No successful
block from the failed run is reused. Any resulting report must disclose the
excluded first replay and unresolved intermittent correctness failure.

### Actual GB300 release-cost versus IronRDP result

Fresh paired replay
[38441909371](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38441909371)
completed successfully with all original correctness commands passing for each
released compiler. The strict self-hosted analyzer validated the selected release
jobs, checksummed archive/configuration provenance, common Cargo/std, native
tool identities, command coverage and CPU/worker class.

| Recipe | Production minutes | Production increase | IronRDP native compile seconds | Compile saving |
|---|---:|---:|---:|---:|
| Controlled no-PGO | 138.49 | reference | 200.275 | reference |
| Microsoft-retained PGO | 182.59 | +31.84% | 157.300 | 21.46% |
| LLVM PGO + ThinLTO | 203.29 | +46.79% | 156.281 | 21.97% |

The LLVM recipe is only 1.019 seconds faster than Microsoft PGO in this one
paired observation, while its production takes another 20.70 minutes. This
does not establish a repeatable advantage for ThinLTO. These are complete
recipe contrasts, not an isolated LTO treatment with identical profiles.

The [one-page Word report](GB300-Rust-Release-Pilot.docx) includes whole-job
costs, cleanup-policy differences and the correctness caveat. Its final,
actual-data document was rendered with Word and verified to occupy exactly
one page. [Machine-readable results](gb300-pilot-results.json) include the
five-command compilation breakdown and qualification history. The failed
first replay and both diagnostic runs are not timing samples in this report.
The unexplained initial UDP correctness timeout remains a limitation, not
a defect claimed fixed by rerunning. One pilot does not satisfy the repeated
hosted protocol or support pooling with ordinary Arm64 or x64.

The reconciled production breakdown in [gb300-release-costs.json](gb300-release-costs.json)
sums exclusive bootstrap scopes across all production invocations, including
intermediate instrumented builds. The remainder is explicitly outside bootstrap
(training workloads, profile processing and orchestration), not called raw
compilation. Each column reconciles to its observed production interval.

| Production wall minutes | No PGO | Microsoft PGO | LLVM PGO + ThinLTO |
|---|---:|---:|---:|
| Assembly/compression | 102.21 | 102.91 | 103.38 |
| Compiler/std/backends | 7.79 | 13.14 | 17.09 |
| LLVM/LLD | 4.23 | 14.56 | 21.88 |
| Tools | 13.00 | 18.28 | 21.59 |
| Documentation | 7.76 | 7.48 | 10.51 |
| Other/bootstrap unattributed | 2.41 | 2.07 | 2.13 |
| Outside-bootstrap production | 1.09 | 24.16 | 26.71 |

Assembly/compression remains about 102-103 minutes in all three recipes.
PGO adds training and compiler-building cost without materially shortening
that dominant baseline component. These scopes include linking and waiting;
they are wall-time categories, not process CPU measurements.

## x64 runner connectivity diagnostics

Following the user's observation of repeated 100-second HTTP timeouts and
listener relaunches, `experiment/matched-x64-runner-diagnostics` runs a
read-only investigation on the exact x64 runner. It reports installed runner
version, service state, proxy-presence flags, sanitized listener event categories
and stack-method names, and DNS/HTTPS transport checks to GitHub hosts discovered
in the logs. Raw diagnostic logs, credentials, proxy values and URL query strings
are not uploaded. It uses the release concurrency lock, installs nothing and
does not change firewall, TLS, proxy, service or timeout settings.
Successful short HTTPS probes do not prove that long-poll/job-renewal connections
remain reliable during a multi-hour build.

[Diagnostic 38404765834](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38404765834)
completed successfully. The installed runner is 2.337.0, with no registered
Actions Windows service or explicit proxy/HTTP-timeout override detected.
Both cancelled jobs' listener logs contain repeated broker HTTP timeouts,
dispatcher shutdown/job cancellation, and fatal stacks through
`BrokerHttpClient.GetRunnerMessageAsync` / `BrokerMessageListener.GetNextMessageAsync`
at their termination times. This identifies runner-control-channel failure,
not manual cancellation or a demonstrated compiler defect.
DNS and three short HTTPS probes per discovered GitHub endpoint succeeded at
transport level; unauthenticated service roots returned expected 400/404 responses.
That does not identify why long polls time out.

The installed version's `VssUtil.GetHttpRequestSettings` supports
`GITHUB_ACTIONS_RUNNER_HTTP_TIMEOUT=300` as a reversible mitigation to test.
Its default is 100 seconds, independently of workflow build limits.
The setting must be inherited when launching the listener; setting it only in
a workflow step cannot configure the parent process. No override or listener
restart was applied by the diagnostic workflow. Multi-hour stability remains
unverified and expensive x64 retries remain paused.

After the user reported repairing the runner and authorized restarting, fresh
optimized-only run 38406317769 started on 13 October at 13:36:25 UTC with
harness `3037a03df7a9cee3b624fc5443f697037127941e`. It preserves the qualified
baseline, uses fresh roots and serializes the two optimized jobs. The runner
briefly reported offline during the build but later returned online; this
does not yet establish multi-hour reliability or qualified release success.

## Separate release-throughput investigation

The [local throughput report](../release-throughput/README.md) explains the
four-CPU utilization ceiling, breaks down completed hosted baseline jobs, and
records paired local LLVM-parallelism and installer-compression experiments.
Neither custom timing runner was used for those new experiments. Their
component speedups do not replace full-release or downstream compiler timings.
