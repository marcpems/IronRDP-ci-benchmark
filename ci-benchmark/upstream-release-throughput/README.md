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
Only `experiment/upstream-release-throughput-pilot` or explicit dispatch starts
the standard-hosted matrix.

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
baseline. This is a single-run lead worth investigating, **not** a measured
full-release speedup. The x64 standard runner has half the logical CPUs of
upstream's release runner and lacks its private remote cache.

Repeating the unchanged single-job x64 workflow is not a viable completion
strategy. A continuation needs separately specified job boundaries that retain
all fresh PGO training, profiles, final build and tests, with transfer/restore
overhead reported separately. Merely increasing the YAML timeout cannot bypass
the hosted six-hour limit. No such split has been implemented or launched.

Machine-readable evidence is in [pilot2-results.json](pilot2-results.json):
job and step durations, accepted Arm64 process accounting, manifests and
exclusive phases, and explicitly incomplete x64 stage observations.
