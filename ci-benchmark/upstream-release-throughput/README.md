# Quality-preserving upstream-equivalent Windows release study

This study uses only standard GitHub-hosted `windows-2025` and `windows-11-arm`
runners. It never dispatches to either custom timing runner.

## Fixed recipe

Rust source is the unmodified upstream revision
`76c90957b7e422c4b9c45192b0197214d7de5a54` (9 October 2026), not the experimental
compiler fork. The workflow uses upstream's sccache, Clang, WIX, Ninja and
submodule-install scripts and invokes `src/ci/scripts/run-build-from-ci.sh`.
The release configuration and command are taken from upstream
`src/ci/github-actions/jobs.yml`. Source and tool identities are recorded.

- x64 uses upstream's complete `opt-dist windows-ci` production pipeline:
  fresh PGO training, full distribution and its extracted-distribution tests.
- Arm64 uses upstream's non-PGO distribution recipe, including Arm64EC.
  The common extracted-distribution suite is additionally run after production,
  identically for every Arm64 setting, and separately timed.
- `DIST_TRY_BUILD=0`, all required tools, docs, MSI, backend selection, compiler
  codegen units, optimization defaults, and balanced XZ compression are fixed.
- No training crates, training scenarios or tests are removed. There are no
  Rust/LLVM source patches, no alternative linkers and no compression changes.

Standard x64 has four logical CPUs rather than upstream's eight-core/32GB
release runner. Each job has a fresh local sccache instead of upstream's
private remote cache. These differences are explicit; the study is equivalent
in release recipe and output requirements, not identical infrastructure.
The upstream CI orchestration, not a reconstructed compiler-only command,
remains inside the primary measurement.

## First feasibility matrix

Each architecture runs three independent fresh hosted jobs:

| Setting | Only experimental change | Hypothesis |
|---|---|---|
| baseline | None | Upstream defaults on standard hosted hardware |
| jobs6 | `build.jobs=6` on four CPUs | Modest oversubscription may overlap dependency/I/O waits; could also lose time or exhaust memory |
| link1 | `llvm.link-jobs=1` | Limiting simultaneous LLVM links may reduce memory pressure and contention; could also lengthen the link tail |

The default four-CPU process allowance is identical across all three settings.
No extra processors are being purchased or substituted. Upstream's fixed
four-job PGO training remains unchanged. This pilot can reject bad scheduling
choices; it cannot establish a reliable percentage saving from one VM each.
Successful candidates require repeated matched runs and a comparison of full
artifact-name sets, configurations, tools, source pins and completed tests.

## Measurement and acceptance

Retain complete recipe wall time and process-tree CPU, peak job memory,
bootstrap exclusive phase timings, setup-step durations, qualification logs,
the actual distribution archives, and their names/sizes/hashes. The main x64
command includes upstream's qualification; report bootstrap distribution and
training scopes separately rather than calling everything compilation.

No result is accepted without successful full recipe execution, preserved
configuration requirements, the complete required distribution, and successful
qualification. Archive hashes alone are not an expectation of bitwise
reproducibility across independently trained PGO builds; differences must be
interpreted with the recorded configuration and test evidence.

Hosted jobs still have a six-hour hard cap. The recipe has a 340-minute
job-relative safety boundary to leave evidence-upload time; additional Arm64
qualification uses the existing 350-minute boundary. A timeout is an incomplete
observation, never a claimed speedup or a reason to reduce training/test coverage.
If production cannot finish, a separately specified pipeline split is needed
before claiming full-release timing results.

Publication to the harness's main experiment branch does not launch this study.
`experiment/upstream-release-throughput-pilot` or ordinary explicit dispatch
starts the six-cell standard-hosted matrix. The continuation branch and dispatch
input described below start only its three x64 continuation cells.

The first pilot is
[38291808264](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38291808264),
from harness `f5825c51364b439745070882778e026b4c382dde`. All six jobs were
confirmed assigned to GitHub-hosted runners with the intended standard labels,
and all reached the measured upstream release command. This is a launch record,
not a successful qualification or a performance conclusion.

The Arm64 `link1` cell completed the upstream distribution build, but the
measurement wrapper rejected the still-running sccache server and its Windows
console host before qualification could run. This is a harness lifecycle
failure, not an accepted release sample or a compiler failure. The superseded
pilot was cancelled to avoid continuing known-invalid measurements.

The wrapper now runs `sccache --stop-server` after the unchanged upstream
command, preserving build failures and treating shutdown failures explicitly.
A local reproduction with the exact upstream sccache binary reproduced the
old `sccache.exe`/`conhost.exe` leak; the repaired wrapper exited successfully
with no remaining descendants. No unknown background processes are allowlisted.
The measured command includes this small final cache-shutdown overhead.
Future failed builds retain any produced distributions for diagnosis, clearly
labelled unqualified. Compiler source, output settings and tests are unchanged.

## Repaired pilot results

[Run 38302741082](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38302741082)
used harness `b41cbca7cdf2a2365e75b881f5b6e9139d03a0a4`.
All six jobs have finished. The three Arm64 cells passed; all three x64 cells
reached the 340-minute job-relative safety deadline during the final build.
The previous cache-daemon lifecycle failure did not recur in the completed
Arm64 commands. The superseded run is confirmed cancelled.

### Arm64: qualified, but no demonstrated scheduling win

Times below are minutes. Production excludes setup, artifact uploads and the
additional extracted-distribution suite; the whole-job column includes them.

| Setting | Production | Additional tests | Whole job | Production vs baseline | Average CPU / 4 CPUs | Peak job memory |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 152.68 | 27.43 | 192.67 | reference | 68.66% | 4.86 GiB |
| jobs6 | 155.34 | 27.86 | 198.53 | +1.74% | 70.10% | 6.84 GiB |
| link1 | 154.10 | 28.14 | 196.18 | +0.93% | 68.59% | 4.80 GiB |

All three use the same runner image and tool hashes, identical 22-file artifact
name sets, and identical parsed configurations after removing only the declared
scheduling knob and its recorded configure arguments. All required manifests
and extracted-distribution tests passed. Balanced XZ, Arm64EC, docs and tools
remain enabled. Independent archive hashes need not match.

One VM per cell does not distinguish small differences from host noise. Neither
candidate demonstrated a whole-release improvement; six jobs used about 41%
more peak memory without improving wall time. There is no basis to recommend
either change for Arm64 from this pilot.

The baseline's exclusive bootstrap breakdown is:

| Component | Minutes |
|---|---:|
| LLVM and LLD | 53.15 |
| Tools | 31.19 |
| Distribution assembly and compression | 29.89 |
| Compiler, standard library and backends | 25.70 |
| Documentation | 6.96 |
| Other bootstrap scopes | 4.22 |
| Remaining recipe overhead, including bootstrap-unattributed time | 1.57 |

These are wall-clock scopes, including linking and waits, not raw compilation
CPU. Process-tree accounting measured 2.75 effective cores across the production
command. This is about 69% of this four-CPU runner, not the approximately 20%
machine-wide utilization seen when a four-CPU cap was used on a 20-CPU machine.

### x64: complete PGO stages, incomplete release

All three cells completed both upstream PGO stages, then timed out while
building the final optimized distribution. No distribution or final extracted
tests completed, so none is an accepted release sample.

| Setting | Rust/tool PGO stage (min) | LLVM PGO stage (min) | Sum of completed PGO stages (min) |
|---|---:|---:|---:|
| baseline | 225.99 | 100.79 | 326.78 |
| jobs6 | 205.04 | 84.43 | 289.47 |
| link1 | 219.98 | 99.75 | 319.73 |

These stages include building instrumented compilers, training and profile
processing; they are not training-only times. The six-job cell reached the
final-build boundary earlier, with an 11.4% lower sum of PGO-stage times than
baseline. Subsequent hardware inspection found that this compared an Intel
Xeon Platinum 8573C with an AMD EPYC 7763: the difference cannot be attributed
to the six-job setting, even for those completed stages. It is **not** a measured
full-release speedup. The x64 standard runner has half the logical CPUs of
upstream's release runner and lacks its private remote cache.

Repeating the unchanged single-job x64 workflow is not a viable completion
strategy. A continuation needs separately specified job boundaries that retain
all fresh PGO training, profiles, final build and tests, with transfer/restore
overhead reported separately. Merely increasing the YAML timeout cannot bypass
the hosted six-hour limit. The original pilot did not implement this split.

Machine-readable evidence is in [pilot2-results.json](pilot2-results.json):
job and step durations, accepted Arm64 process accounting, manifests and
exclusive phases, and explicitly incomplete x64 stage observations.

## Bounded x64 continuation

The continuation mode completes the missing final-build/qualification work
without rerunning or shortening the already completed PGO training. It is a
feasibility continuation, not a replacement measurement of the original
single-job recipe and not yet an automated fresh-training multi-job pipeline.

Push `experiment/upstream-release-throughput-continuation`, or dispatch with
`continue_x64_pilot=true`, to run only baseline/jobs6/link1 on standard
`windows-2025` runners. Each cell downloads its own evidence from run
38302741082. The original five merged profiles cover LLVM, rustc (also used for
Cargo), rustdoc, Clippy and Cranelift. No profile is exchanged across settings.

Before building, the driver verifies pinned SHA256 hashes of all five profiles,
the original configuration, provenance, failure record and training log against
[pilot2-profiles.json](pilot2-profiles.json). It requires both PGO stages to have
completed, the same Rust revision, setting, native paths, runner image and
build-tool identities, and exactly the final command recorded by upstream
`opt-dist`. Drift fails explicitly rather than silently using another cohort.

The fresh runner repeats the official upstream preparation and final
distribution command with all six upstream `pgo.*.use` settings, but omits
`--keep-stage 0` because no previously compiled stage0 build artifacts are
restored. Bootstrap's keep-stage path assumes those artifacts already exist;
retaining it on a fresh runner would skip required builds. All compiler stages
are instead rebuilt as needed, without lowering their optimization settings.
The distribution is followed by
the existing extracted-distribution helper. Its eleven test paths, Cranelift
sysroot assembly and `COMPILETEST_ENABLE_DIST_TESTS=1` match the pinned upstream
`opt-dist` test recipe. Compression, full tool/docs/MSI outputs, and compiler
optimization settings are unchanged. The generated production configuration
must match the original pilot's parsed configuration exactly. Rust/LLVM source
and training code are not modified.

Only profiles are transferred: no partial LLVM objects, warm compiler cache or
stage0 build objects are restored. Thus final-build cost can differ from an
in-process continuation. Final distribution and tests are reported separately,
with `full_release_timing_complete=false`; earlier training, repeated setup,
profile download, uploads and the discarded timed-out build tail must not be
hidden in a claimed full-release speedup. A successful continuation establishes
output qualification and final-stage feasibility. Reliable end-to-end savings
still require a matched, repeatable split pipeline with all overhead accounted
for.

The three-cell continuation was launched as
[38356308993](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38356308993),
from harness `d2ed87af57cdb0b2824d80151d2343d2ff1ab3ca`. This records the launch,
not successful final-build qualification or an end-to-end speedup.

### First continuation: all qualified, CPU models confound timing

Run 38356308993 completed all three final distributions and their extracted
tests successfully. The same 20 artifact names, tool hashes, runner image and
production configuration (except the declared scheduling settings) were
verified. Each test log reports 25,648 passed, zero failed, 739 ignored and
541 filtered tests across ten summaries, with identical counts across cells.
Profiles remain the original per-setting profiles, not a common profile shared
across settings.

However, `windows-2025` assigned three different CPU models. Equal runner
labels, image versions and four-logical-CPU allowances do **not** establish
equal processor performance.

| Setting | Reported CPU model | Final production (min) | Extracted tests (min) | Whole continuation job (min) | Average CPU / 4 CPUs |
|---|---|---:|---:|---:|---:|
| baseline | AMD EPYC 7763 | 195.53 | 21.50 | 223.07 | 77.91% |
| jobs6 | Intel Xeon Platinum 8573C | 180.06 | 19.93 | 206.17 | 77.20% |
| link1 | Intel Xeon 6973P-C | 153.19 | 16.69 | 175.07 | 75.24% |

The raw final-production differences are -7.91% and -21.65%, respectively.
Neither is an established scheduling benefit: processor models differ, there
is only one sample per setting, and each setting retains its independently
trained PGO profiles. Even the separately run tests, which use the same
four-job scheduling across settings, are materially faster on the candidate
machines. Do not recommend `llvm.link-jobs=1` as a 22% release optimization
from this table.

Baseline exclusive bootstrap wall time was 79.39 minutes in LLVM/LLD,
43.88 in tools, 42.39 in the compiler/standard library/backends,
23.65 in assembly/compression, 2.69 in docs and 2.10 in other scopes.
Remaining recipe and unattributed overhead was about 1.43 minutes.
These remain wall scopes, not raw compilation CPU. Process-tree CPU averages
3.12 effective logical cores; peak job memory was 6.50 GiB, compared with
8.91 GiB for jobs6 and 6.56 GiB for link1.

These results establish that complete optimized x64 outputs and qualification
fit on standard runners when the final build is continued separately. They
do not establish a fresh-training end-to-end release duration or a safe
performance recommendation. Do not sum the earlier PGO stages and this cold
rebuild and present that as an observed single-job release.

Evidence is in [continuation1-results.json](continuation1-results.json).
The immediate priority is CPU-model-matched observations before attributing
any savings to scheduling, followed by repeatable fresh-training split-pipeline
accounting. Balanced compression and existing output/test requirements remain
fixed.

One repeat three-cell continuation cohort,
[38381817405](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38381817405),
was dispatched at the same harness revision and with the same per-setting
profile hashes. This checks repeatability and seeks overlapping CPU-model
observations; standard-runner placement does not guarantee them. Its results
must be grouped by reported CPU model rather than blindly averaged across
hardware. No custom runners are used.

### Repeat continuation: no scheduling win established

Run 38381817405 also qualified all three distributions. Each setting retained
its first-cohort source, configuration, tool hashes, image, profile hashes,
20 output names and identical qualification counts.

| Setting | Reported CPU model | Final production (min) | Extracted tests (min) |
|---|---|---:|---:|
| baseline | AMD EPYC 9V45 | 125.62 | 14.46 |
| jobs6 | AMD EPYC 9V74 | 191.77 | 20.54 |
| link1 | AMD EPYC 7763 | 205.35 | 22.04 |

There is now one cross-cohort CPU-model match: on EPYC 7763, baseline took
195.53 minutes and link1 took 205.35 minutes, **5.03% longer**, not faster.
This is not proof of a regression: it still compares different VMs and
independently trained profiles, with only one observation per setting on
that CPU model. It does not support the apparent 21.65% link1 improvement
from the first, hardware-mixed cohort.

More importantly, the **unchanged baseline**, including identical PGO profiles,
took 195.53 minutes on its first VM and 125.62 on its repeat VM: an observed
35.75% reduction without any scheduling change. That is VM/hardware-associated
variation, not a measured isolated CPU-model speedup. Averaging all six
continuations without accounting for hardware would produce a misleading
answer.

Evidence and the exact comparison scopes are in
[continuation2-results.json](continuation2-results.json). No further independent
VM repeats have been launched after this cohort.

### Current recommendation and remaining work

Keep upstream's scheduling defaults: these pilots do not justify changing
`build.jobs` to six or `llvm.link-jobs` to one. Arm64 showed no improvement in
its qualified full-recipe pilot; x64 has no established causal scheduling win.
Do not change compression or remove tests to obtain a better number.

The next useful investigation is a same-VM crossover with identical PGO
profiles and fresh build/cache directories, rather than another randomly
placed full-build cohort. Start with LLVM/LLD, the largest baseline final-build
wall scope, so both settings can fit within the hosted six-hour limit. Use
opposite execution orders on separate VMs to expose order effects. Such results
would be component measurements, not whole-release savings.

Only a promising controlled change should advance to repeated full-output
qualification and a fresh-training split pipeline. That pipeline must account
for repeated setup, profile/state transfers, any rebuilt stages, packaging and
tests; the current cold final-stage continuations are not that measurement.
Neither the controlled crossover nor the fresh-training split pipeline has
been implemented or launched in this study.
