# Windows Arm64 Rust distribution feasibility

## Status and decision

**Investigation in progress; not release-qualified.** This report separates measured
upstream timings, a cold fork experiment, and conditional budget scenarios. Existing
Arm compiler performance wins are motivation, not evidence that a full distribution
fits CI. Neither the earlier trimmed package nor x64 profile reuse qualifies Arm64.

Source inspection date: **2026-10-02**. Current Rust main is
[`dba8825fe50879b22129271fb865944e384f7cce`](https://github.com/rust-lang/rust/tree/dba8825fe50879b22129271fb865944e384f7cce),
version **1.101.0**, not the experiment's **1.94.1**
[`e408947bfd200af42db322daf0fadfe7e26d3bd1`](https://github.com/rust-lang/rust/tree/e408947bfd200af42db322daf0fadfe7e26d3bd1).

## Current configured limits and scope

| Layer | Configuration / limit | Consequence |
|---|---|---|
| Arm64 ordinary compiler tests | Two `windows-11-arm` matrix jobs; shared workflow timeout **360 min/job** | A dist-only optimization does not require these jobs to retrain PGO |
| Arm64 distribution | `windows-11-arm`, **360 min/job**, plain `x.py dist bootstrap --include-default-paths` | Full tools, profiler, native + Arm64EC; currently no opt-dist |
| x64 distribution | `windows-2025-8core-32gb`, **360 min/job**, opt-dist | Existing PGO is not evidence that an Arm four-CPU job fits |
| GitHub-hosted hard limit | **360 min/job** | Raising only YAML cannot exceed it |
| Matrix / citool | Parallel jobs; at most **20 custom try jobs** unless `nolimit` | This is a job-count limit, not a shorter build timeout |
| Release promotion | Published simpleinfra production CodeBuild definition: **240 min** | Separate download/recompress/sign/manifest/smoke-test/publish budget, not another compiler rebuild |
| Fork experiment | **350 min** from first step for build subprocesses; **360 min** workflow | Ten-minute diagnostic reserve; reaching 350 is not proof of failure at exactly 360 |

Sources: [current jobs](https://github.com/rust-lang/rust/blob/dba8825fe50879b22129271fb865944e384f7cce/src/ci/github-actions/jobs.yml),
[workflow](https://github.com/rust-lang/rust/blob/dba8825fe50879b22129271fb865944e384f7cce/.github/workflows/ci.yml#L70-L115),
[citool](https://github.com/rust-lang/rust/blob/dba8825fe50879b22129271fb865944e384f7cce/src/ci/citool/src/jobs.rs),
[platform limits](https://docs.github.com/en/actions/reference/limits),
[production release module](https://github.com/rust-lang/simpleinfra/blob/3db50ee298dd74635f3196cac3d4c3c72f4597af/terraform/releases/environments.tf),
[CodeBuild deadline](https://github.com/rust-lang/simpleinfra/blob/3db50ee298dd74635f3196cac3d4c3c72f4597af/terraform/releases/impl/promote-release.tf#L30-L56).
These are versioned source settings, not an authenticated inspection of deployed AWS state.
No extra citool execution timeout was found in the inspected main workflow/build path.

The standard public Arm runner is documented as **4 CPU / 16 GB RAM / 14 GB SSD
workspace storage**. Actual free capacity must be measured: the successful Oct 2
upstream Arm job logged a **256 GiB C: volume / 124 GiB free before setup**, and
used image **windows-11-vs2026-arm64 20260924.168.1** despite its `windows-11-arm`
label. Do not substitute the documented storage allowance for measured free disk.
[Runner specifications](https://docs.github.com/en/actions/reference/runners/github-hosted-runners);
[exact image](https://github.com/actions/runner-images/blob/win11-vs2026-arm64/20260924.168/images/windows/Windows11-VS2026-Arm64-Readme.md).
Concurrency depends on the organization's plan/quota; the public YAML supplies no
Arm-specific guarantee. Jobs may queue; job durations below exclude queue wait.

## Measured upstream observations

Two successful **Oct 2, 2026 UTC** merge runs, not the older September sample:

| Run | Arm dist total / build | Arm test jobs total | x64 dist total / build | Workflow created-to-updated |
|---|---:|---:|---:|---:|
| [36967138610](https://github.com/rust-lang/rust/actions/runs/36967138610) (exact inspected main) | **117.93 / 106.33 min** | 118.98 / 143.82 min | 119.12 / 114.72 min | 181.35 min |
| [36953332403](https://github.com/rust-lang/rust/actions/runs/36953332403) | **121.47 / 108.48 min** | 117.53 / 149.50 min | 182.37 / 175.77 min | 183.77 min |

**Critical confound:** the first Arm distribution reports **97.92% sccache hits**:
3,446 C++ hits and **one C++ miss** (99.97%); Rust 196 hits/77 misses.
These are warm-cache release-build observations, **not cold LLVM build timings**.
Fresh PGO, changed optimization flags, and profile-use hashes invalidate assumptions
about retaining those hits. The fork experiment deliberately has no upstream
S3 credentials/cache. Cold versus warm costs cannot be attributed solely to PGO.

The first merge's last substantial job was `test-x86_64-mingw-1` (~180 min);
the second was x64 dist (~182 min). Arm dist was not the critical path. Conditional
scenario, **not a measured optimized result**: an Arm dist duration of 240 min
would fit six hours but move these ~181–184 min workflows to approximately 240 min,
subject to scheduling. Summing all jobs is not workflow latency.

Raw evidence: [Arm job](https://github.com/rust-lang/rust/actions/runs/36967138610/job/110713424955),
[compact log excerpts](evidence/upstream-arm-dist-excerpts.log),
[derived timing records](evidence/upstream-timings.json).
`summarize_upstream.py` reproduces the timing reduction from GitHub run/job API
responses (`GET repos/rust-lang/rust/actions/runs/{id}` and `/jobs?per_page=100`,
all pages). The branch-filtered API returned older September results during this
investigation; repository-wide discovery found the current runs. No population
percentiles or core-linear scaling are inferred from two observations.

## Fork experiment

Baseline full experiment:
[36991902911](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36991902911),
commit `e00e642302874b9605cecf022d8ef9cc3ac6de3c`.
Native-helper treatment:
[36993262359](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36993262359),
commit `b4737d330d8ff20ce0175bf84a3764972f390bc6`.
Initial setup-only run:
[36991037745](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36991037745).
The harness is isolated at branch `ci/arm-release-feasibility` in
`marcpems/IronRDP-ci-benchmark`; no existing compiler checkout/build/run is modified.

Both variants use Rust 1.94.1, LLVM
`00d23d10dc48c6bb9d57ba96d4a748d85d77d0c7` (21.1.8), native host clang-cl
20.1.3 (`woa64`), and stock installed MSVC/Windows SDK. The treatment trains
fresh profiles on rustc-perf `c0301bc44d175b9b2c5442b25049475c39d7700c`.
Only token-stream-stress's obsolete lockfile format is migrated; before/after
package graphs must match. No portable SDK, DIA-off setting, tool pruning,
borrowed profiles, or split build jobs are used.

Baseline: upstream-style full dist, no PGO/ThinLTO change. Treatment: rustc+LLVM
PGO, Rust `lto=thin`, LLVM `thin-lto=true`, native LLD for rustc, and opt-dist's
extracted-distribution tests. Baseline intentionally does not add those opt-dist
tests, matching the existing Arm dist job.

The setup equivalent omits upstream sccache, S3 publication, rustup uninstall,
and deletion of installed LLVM. These omissions and the older stable source are
explicit qualifications, not hidden upstream equivalence claims. Environment
variables reaching opt-dist are allowlisted, because it prints the environment.
Minute memory/commit/disk samples and stage progress stream to logs; preflight
artifacts upload before compilation; deadline handling reserves diagnostic time.
Profiles must show **nonzero AArch64TargetLowering and InstCombine execution**.

**Build results pending.** Initial preflight failed before any compiler build:
baseline stopped at 9m20s because top-level `configure` is a shell wrapper;
treatment stopped at 10m24s because patch context encountered checkout line-ending
differences. Python now invokes `src/bootstrap/configure.py`; Git line-ending
settings are established before checkout and patch application tolerates whitespace.
The corrected configure invocation was integration-tested against pinned source;
both minimal patches also pass application checks against pinned and current-main
source copies. No shared checkout was written. Setup-only failures are not compiler
build-time results, and neither job was canceled or rerun.

Initial preflight measured **Cobalt 100, 4 cores / 4 logical processors**, ~16 GiB
RAM, native ARM64 Python 3.13.15, image `win11-vs2026-arm64` 20260924.168.1,
and ~123.7 GiB free on a ~255.45 GiB C: volume before source setup. These are
machine observations, not compiler peak-memory/disk measurements.

In run 36991902911 the baseline reached its full build. Treatment failed after
**143.64 seconds building opt-dist**, before any PGO compiler build: bootstrap
tried to compile this native helper for Arm64EC too, but stage0 lacks its `core`.
The helper build is now explicitly restricted to native `--host`/`--target`;
final dist still includes both targets. Only the treatment is launched again;
the running baseline is neither restarted nor canceled. This is a necessary
Arm opt-dist integration detail, not a measured optimization timeout.

Run 36993262359 then built the native helper and rustc-perf successfully, but its
first PGO compiler stage stopped in **1.82 seconds**: enabling LLVM ThinLTO defaults
bootstrap to shared LLVM, which MSVC rejects. The treatment must explicitly keep
`llvm.link-shared=false` and use the native LLVM librarian for bitcode archives.
This is another early configuration failure, not an LLVM compile, six-hour limit,
or memory failure. No expensive PGO compiler stage has been restarted.

## Full distribution versus release qualification

The current successful upstream log packages native and Arm64EC standard libraries,
HTML/JSON docs and analysis, plus rustc, rustc-dev/rust-dev, rust-src, Cargo,
rust-analyzer, rustfmt, Clippy, Miri, LLVM tools, llvm-bitcode-linker, bootstrap,
combined `.tar.xz`, and Windows `.msi`. The pinned stable version's channel gates
can change the exact set. Merely packaging rustc/std/Cargo is not this scope.
`DIST_REQUIRE_ALL_TOOLS=1` and full default paths must remain enabled.

The [upload step](https://github.com/rust-lang/rust/blob/dba8825fe50879b22129271fb865944e384f7cce/src/ci/scripts/upload-artifacts.sh)
places distribution artifacts and metrics under the commit in `rust-lang-ci2`.
[promote-release](https://github.com/rust-lang/promote-release/blob/f699a3c4abdf090f09afb062794e5f5b7fd34d9f/src/lib.rs)
downloads those artifacts, recompresses, builds manifests/checksums, signs, smoke
tests rustup installation, and publishes. Additional PGO compiler hours belong to
**dist CI**, not a second release compiler-build budget. Artifact size/compression
changes can still affect the **240-minute promotion budget**; no promotion timing,
signing, publication, or installer qualification has been measured here.

Current main is not a drop-in extrapolation: its
[opt-dist Stage 1](https://github.com/rust-lang/rust/blob/dba8825fe50879b22129271fb865944e384f7cce/src/tools/opt-dist/src/main.rs#L239-L305)
profiles **rustdoc, Cargo and Clippy as well as rustc**, with additional training.
The static LLVM training stage still retains rustc; main also still lacks the
read-only runtime-discovery dry-run flag. A pinned 1.94.1 success would not prove
the larger main pipeline fits.

## Minimal changes and go/no-go gates

Exact candidate code diffs, kept separate from runner accommodations:
[static LLVM relink](patches/static-llvm-pgo.patch) and
[bootstrap runtime discovery](patches/bootstrap-clang-runtime.patch).
No compiler/LLVM implementation change is proposed.

Smallest next upstream change: fix static-LLVM training correctness and validate
nonzero backend profile coverage before enabling more optimization. Separately
qualify full main Arm64 opt-dist in a try job; do not silently enable it for every
ordinary compiler-test job. ThinLTO flags and switching Arm dist to opt-dist should
remain a separate adoption decision backed by time/memory/disk and correctness.
An Arm opt-dist job must also pass the native target when building the helper,
without narrowing the configured final distribution targets.

Go only after full component/Arm64EC/MSI coverage, valid fresh profiles, extracted
dist tests, adequate six-hour cold/miss and warm-cache headroom, current-main
reproduction, and release manifest/install/smoke validation. Ordinary compiler
tests must still pass; profile validity alone is not correctness qualification.

If a single job cannot fit, the smallest staged alternative is a separately
reviewed profile-generation job with exact source/tool/corpus provenance and
hash-verified profiles feeding full dist/tests. Every stage must independently
fit its deadline and resource limits; artifact transfer and longer workflow
latency count. Splitting does **not** make the original single-job design feasible,
and has not been measured by this experiment.
