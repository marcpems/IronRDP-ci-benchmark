# Is one 32-vCPU Windows Arm64 runner enough for Rust?

**For the complete Rust project: no. For one Windows Arm64 MSVC optimized
distribution build at a time: a credible candidate, not yet qualified. For all
upstream Windows Arm64 CI demand with reliable latency: do not promise it.**

The [per-build proposal](BALANCED-PROPOSAL.md) recommends **one runner per build**,
not necessarily **one runner for the whole fleet**. Here concurrency is exactly
**one**: 32 vCPUs are used within a job, not 32 simultaneous jobs. Catalog 32 vCPUs
and 128-GB RAM are not 32 guaranteed physical cores. If the available machine
instead has 32 physical cores, its clocks, memory, disk, OS support and measured
throughput must replace these assumptions; the hosted tariff is only a comparator.

| Question | Assessment |
|---|---|
| Correctness and coverage | Native MSVC Arm64 dist, Arm64EC outputs and native tests are feasible in principle, subject to the existing PGO/static-relink/full-tools qualification gates. Hardware alone proves no correctness or optimization parity. |
| Per-job limit | Modeled optimized **135.8-minute central / 247.4-minute adverse** single jobs fit 360; **380-minute combined stress does not**. Two sequential jobs retain full work and fit at **405 minutes total / 231 longest**. These are not measured 32-vCPU optimized results. |
| Aggregate MSVC distribution capacity | At sampled demand, budgeting every attempted build to completion requires **115% / 209%** of one runner's available time (central/adverse). Keeping historical cancellation deadlines lowers central occupancy to **81%**, but this is conditional and exceeds a 70% headroom target. |
| Reliable turnaround and availability | A single runner has no failure redundancy. Bursts, maintenance, replacement and loss of a profile/build tree delay every following build. It is not a reliable near-two-hour service merely because each isolated build takes two hours. |
| All Windows Arm64 / cross-platform CI | Consolidating native tests and LLVM-MinGW dist makes the load substantially larger. Linux, macOS, Windows x64/i686 and other target-specific qualification remain elsewhere. |

**Recommendation:** retain ordinary CI and LLVM-MinGW on their existing runners.
Use the 32-vCPU machine for optimized MSVC Arm64 dist, but provide **overflow/
replacement capacity** before treating it as the sole production resource. The
full-attempt central budget calls for **two concurrent 32-vCPU runner slots** at
70% utilization; the adverse budget calls for three (four at 20% growth).
This is simpler than a profile-production DAG rewrite. It is a capacity estimate,
not a queue-latency guarantee. If only one machine is available, admit that the
full-demand/headroom target is not established; do not silently omit try builds,
merge qualification, tools, Arm64EC, training or optimization coverage.

### Measured outcome added October 2, 16:10 UTC

The [corrected cold Arm64 treatment](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36994829038/job/110799044364)
ended **failure after 350.57 minutes** at the harness's **350-minute safety
deadline**, not a compiler error or demonstrated exact 360-minute timeout.
Stage1 took **250.35 minutes**; Stage2 instrumented LLVM was interrupted while
linking after **~85.43 minutes**. Only the frontend profile exists: LLVM training,
final full dist and extracted qualification tests were not reached.
See the [measured-outcome addendum](BALANCED-PROPOSAL.md#measured-outcome-addendum--october-2-1610-utc)
and [maintained feasibility report](https://github.com/marcpems/IronRDP-ci-benchmark/blob/ci/arm-release-feasibility/arm-feasibility/FEASIBILITY.md).
This supplies **no completed optimized-build cost, 360-minute fit or native32
measurement**. The 141.82-minute stock baseline, sampled annual history and all
conditional capacity/cost model values remain unchanged; no new builds are proposed.

## Observed frequency, not “one nightly equals one compiler build”

**Read-only sample:** CI workflows created **2026-09-18 00:00 UTC through
2026-10-02 00:00 UTC, end exclusive**, two complete weeks, collected October 2.
The recent week was widened to the preceding week to check release-week and
cancellation effects. Daily pagination avoids the Actions search result ceiling;
each returned creation date and full page count is checked. No status filter
excludes failures/cancellations. All push runs' job-attempt histories were read;
28 PR controls (first successful and cancelled PR each day) were inspected.
Channel is read from **`src/ci/channel` at each push's exact source SHA**, not
guessed from the common `automation/bors/auto` branch.

| Workflow invocation type | Runs | Success | Failure | Cancelled |
|---|---:|---:|---:|---:|
| Auto/merge | 163 | 76 | 59 | 28 |
| Try | 260 | 180 | 49 | 31 |
| Try-perf | 328 | 328 | 0 | 0 |
| PR | 1,882 | 1,139 | 369 | 374 |
| **Total** | **2,633** | **1,723** | **477** | **433** |

These are **workflow conclusions, not Arm compiler conclusions**. Of 163 auto
runs, 158 materialized an MSVC Arm dist job; early matrix/setup failures can
prevent it. A failed matrix can still have a successful Arm dist artifact.

| Actual native Windows Arm64 job class | Scheduled attempts | Reached build step | Success / failure / cancelled | Measured SUM wall minutes |
|---|---:|---:|---:|---:|
| MSVC distribution, including Arm64EC outputs | **162** (158 auto + 4 custom try) | **142** | **90 / 0 / 72** | **14,330.7** |
| Two native MSVC test shards | 344 (316 auto + 28 try) | 300 | 188 / 14 / 142 | 32,467.1 |
| Separate Arm64 LLVM-MinGW distribution | 160 (158 auto + 2 try) | 139 | 87 / 1 / 72 | 14,021.6 |

The 162 MSVC dist jobs use **162 distinct source SHAs**; channel counts are
**153 nightly, 8 beta, 1 stable**. Successful jobs were **83 / 6 / 1** by
channel. There are **zero Actions rerun attempts** in the sampled push histories;
PR metadata records 14 additional run attempts, outside the default native
Windows Arm dist workload. New bors invocations after failed/cancelled merges
are still counted as new work, not deduplicated as “the same PR.” Rollups of many
PRs still make one job per target, not one build per constituent PR.
Cancelled MSVC jobs consumed **3,591.7 measured runner minutes**; **20 of the
162 scheduled jobs never reached the build step**. Cancellation is real paid
work when a runner was occupied, but is not automatically a full compiler build.

Weekly MSVC demand was **80 then 82 scheduled attempts**, with **68 then 74
reaching compilation**, and **44 then 46 successful jobs**. This annualizes to:

* **4,171–4,276 scheduled attempts/year**, two-week rate **4,224**;
* **3,546–3,859 compilation-started attempts/year**, two-week rate **3,702**;
* **2,294–2,399 successful dist jobs/year**, two-week rate **2,346**—not all
  release-qualified whole-matrix builds.

These are extrapolated **sample rates**, not an authoritative yearly requirement.
Two adjacent weeks cannot establish seasonality, release-cycle tails, future
policy, exceptional stable patches, runner changes or a population p95.
The preceding week had no stable dist; the newer week had one. Do not forecast
26 stable releases/year from that one observation. Native PR absence is supported
by the pinned default matrix and all 28 controls, not an exhaustive assertion
about every possible PR editing its own workflow.

### Nightly, beta, stable and retries

The [pinned CI workflow](https://github.com/rust-lang/rust/blob/dba8825fe50879b22129271fb865944e384f7cce/.github/workflows/ci.yml)
runs on PRs and bors auto/try/try-perf; it is not simply a nightly build scheduler.
The [job matrix](https://github.com/rust-lang/rust/blob/dba8825fe50879b22129271fb865944e384f7cce/src/ci/github-actions/jobs.yml)
uses Linux jobs for default PR CI and Linux quick distributions for default try;
custom try requests can select native Windows Arm jobs. Auto pushes exercise
the broader matrix and source channel. Rollups, re-bors attempts, beta/stable
backports and stable rebuild source commits therefore contribute compiler work.

[Production promotion configuration](https://github.com/rust-lang/simpleinfra/blob/3db50ee298dd74635f3196cac3d4c3c72f4597af/terraform/releases/environments.tf)
schedules nightly/beta at 00:00 UTC; stable is manually selected.
[Promotion implementation](https://github.com/rust-lang/promote-release/blob/f699a3c4abdf090f09afb062794e5f5b7fd34d9f/src/lib.rs)
downloads **existing commit-addressed CI artifacts**; it does not rebuild rustc.
Thus **do not add 365 nightly + 365 beta compiler rebuilds** to observed CI.
Several channel promotions, 21 component files, native/Arm64EC packages and MSI
from one MSVC dist are not independent compiler builds.
The [release process](https://forge.rust-lang.org/release/process.html) describes
stable changes/rebuild PRs and re-publication of their newly built artifacts.
The source-change CI belongs in compiler demand; re-running promotion alone does
not. Promotion's separate **240-minute** timeout and AWS/storage/signing costs
remain outside this machine's bill.

## Annual compute and capacity

[GitHub native Arm64 pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing)
and [hardware](https://docs.github.com/en/actions/reference/runners/larger-runners)
were **reverified October 2**: **`windows_32_core_arm`, $0.098/minute,
32 vCPU / 128 GB / 1,200 GB SSD**. Larger runners require the eligible organization
plan, are billed for public repositories, and do not consume included free minutes.
No x64 price or guaranteed physical core equivalence is substituted.

Assumptions: **365 days = 525,600 calendar minutes**; reserve **5%** for
maintenance/unavailability → **499,320 available minutes**; plan no more than
**70%** utilization → **349,524 scheduled-work minutes** for healthy headroom.
Those reserves are engineering choices, not a measured availability SLA.

`Nyear = sample attempts × 365 / 14`

`Mrequired = Nyear × SUM(job wall minutes per attempt)`

`Ccompute = $0.098 × Nyear × SUM(ceil(each job's minutes))`

`utilization = Mrequired / 499,320`

**No second retry multiplier** is applied to observed attempt rates: they already
include cancellations and any observed reruns. If future failure/retry frequency
or extra setup changes, add that workload explicitly. In contrast, a target of
`N` *qualified outputs* needs the separate success/failure accounting in the
[per-build model](BALANCED-PROPOSAL.md#comparable-latency-billed-sum-and-successful-build-cost);
it is not interchangeable with `N` scheduled attempts.

| Annual workload | Attempts/year | Central optimized 135.8 min | Adverse optimized 247.4 min | Central / adverse utilization |
|---|---:|---:|---:|---:|
| Hypothetical one candidate attempt daily; **not full upstream CI** | 365 | **$4,865** | **$8,871** | 9.9% / 18.1% |
| Observed compilation-started rate, every attempt budgeted full | 3,702 | **$49,342** | **$89,977** | 100.7% / 183.4% |
| Observed scheduled rate, every attempt budgeted full | **4,224** | **$56,292** | **$102,650** | **114.8% / 209.2%** |
| Scheduled rate + 20% growth/retry-policy sensitivity | 5,068 | **$67,550** | **$123,180** | 137.8% / 251.1% |

The full scheduled central row requires **573,459 wall / 574,406 rounded billed
minutes** annually. Adverse requires **1,044,807 / 1,047,446**. These are required
work/cost **on sufficient capacity**, not throughput one saturated machine can
deliver. Full-budget cancelled attempts are deliberately conservative, not a
claim that all historical cancellations actually took 135.8 or 247.4 minutes.

**Baseline and severe-tail checks:** retaining the measured **141.82-minute stock
four-CPU** duration as an *unscaled billing yardstick* gives **$58,775/year** at
the full scheduled rate; it is neither an optimized result nor a measurement on
32 vCPUs. The modeled **405.1-minute two-job stress** case needs **1,710,931 wall
minutes / $168,047/year**, about five runner slots at the 70% target. Splitting
fits per-job limits but does not create annual capacity on a single machine.
See [all baseline/central/adverse/stress rows](ANNUAL-TABLES.md) and
[machine-readable arithmetic](annual-results.json).

### Cancellation-aware sensitivity, not free capacity guaranteed by failures

A second FCFS replay retains each observed **external cancellation timestamp**:
expired queued work is not started; running work stops at that deadline;
successful historical requests receive the full modeled optimized duration.
It charges actual modeled occupied minutes and rounds each consumed job portion.
This produces **406,662 minutes / $39,986/year / 81.4%** central occupancy, versus
**597,423 / $58,711 / 119.6%** adverse. Thus a defensible conditional MSVC compute
planning span is roughly **$40k–$56k central**, or **$59k–$103k adverse**, before
growth and exclusions—not confidence bounds.

It is unsafe to promise capacity based on failures elsewhere cancelling 72/162
requests. The replay fixes old cancellation decisions while altering the Arm
schedule; actual future decisions and retries may differ. Adverse replay also
discards more work before service, not magically producing more successful
artifacts. A 365-attempt scenario is only ~$5k–$9k, but replacing merge-time dist
with that schedule would change upstream CI coverage/policy and is **not proposed**.

### Queue, peak demand and single-point failure

Observed daily scheduled MSVC demand ranges **6–17**, average **11.6**.
At 135.8 minutes, the peak day's work alone is **38.5 runner-hours**. For this
sample rate, one machine must average **≤118.2 occupied minutes/request** merely
to fit 95% availability, or **≤82.8** to preserve 70% headroom; neither is a
validated optimized throughput.

Replaying **all scheduled requests to completion**, with an empty initial queue,
no maintenance and no extra retries, gives central **19.4-hour median /
31.1-hour p95 wait** over the sample. This backlog is a consequence of >100%
offered load, not a measured GitHub queue. Retaining fixed cancellations instead
gives central median wait zero but **maximum ~180 minutes**—already several hours
before the build duration is added. Both replays are conditional, not guarantees.
Even a simple burst of three builds needs about **6.8 hours** to finish on one
runner, with the third waiting **4.5 hours** before its ~2.3-hour build.

Keep per-job 350-minute operational deadline / 360-minute hard limit. A two-job
fallback works sequentially on the same machine; a four-job DAG's *parallel*
elapsed estimate does **not** apply with concurrency one—charge its full SUM.
Prioritize release-critical source commits over discretionary work without
changing required qualification; retain cancellation semantics and reserve
replacement/overflow capacity. A hardware failure, image regression or long
repair otherwise blocks all Windows Arm64 artifacts; “95% annually available”
does not imply timely service on release day.

## What remains elsewhere

Native Windows Arm64 can execute the two MSVC test shards and the separate
**`dist-aarch64-llvm-mingw`** job (Arm64 gnullvm plus i686 target in current
configuration). That GNU/LLVM ABI distribution is **not** an MSVC/Arm64EC package
duplicate, and its shared-LLVM/codegen policy must not inherit the MSVC static
PGO settings blindly.

Moving those jobs is an explicit additional scope change. Their sampled rates
annualize to **8,969 test-shard attempts + 4,171 LLVM-MinGW dist attempts**.
Even an **unmeasured optimistic 45 minutes each** adds **591,300 wall minutes /
$57,947** annually, before the MSVC optimized dist work. At 90/135 minutes each
it adds roughly **$115,895/$173,842**. These are sizing sensitivities, not
native32 test measurements. Keeping these ordinary jobs on existing standard
public runners avoids that new paid compute and preserves parallel test latency.

Linux glibc/musl, macOS host/SDK/ABI tests, x86 Windows host behavior, other
platform dist builders, Miri/GCC/alternative-codegen configurations and broader
qualification still require their appropriate environments. Cross-compiling a
target or emulating x64 on Arm is not a substitute for native platform test
coverage. A single Arm machine cannot replace Rust's whole CI/release system.

## Active billing versus a dedicated machine

**525,600 × $0.098 = $51,508.80/year** is the *continuous-active hosted-rate
equivalent*. It is **not** an annual reservation or self-hosted purchase/TCO
quote. GitHub documents no charge for an idle larger-runner configuration;
concurrency one is a cap on job execution, not a promise of a permanently warm,
dedicated physical machine. Work above 525,600 minutes requires more capacity,
even if the required annual cost exceeds $51,509.

Self-hosting needs an actual quote for acquisition/amortization or VM rent,
Windows-on-Arm/virtualization licensing, power, networking, monitoring, staffing,
spares and replacement. For a quoted annual fixed cost `A`, variable annual
cost `V`, compare `A+V` with the hosted active bill **at equivalent delivered
throughput and redundancy**, not at equal nominal core count.

Storage/cache/network are excluded from the numeric compute bill and can matter:
the cold full-dist payload was **1.297 GiB** (21 files, one build). At `B`
successful stored builds/year and `R` retained days, mean payload storage is
`1.297 × B × R/365 GiB`; one upload per build is `1.297 × B GiB/year`.
At the observed ~2,346 successes/year and seven-day retention that is roughly
**58 GiB stored / 3.0 TiB transferred per year**, before downloads, diagnostics,
profiles, caches or the separate gnullvm outputs. Instrumented LLVM/cache
bundles can exceed distribution payloads. Add the actual artifact/S3/network
tariffs, plan fees and tax; hosted job SSD is not free persistent artifact
storage. Cache hits must not be required to fit cold-build capacity.

## Evidence and reproduction

* [September 18–24 inventory](data/annual-history-2026-09-18-2026-09-25.json)
  and [September 25–October 1 inventory](data/annual-history-2026-09-25-2026-10-02.json):
  creation times, branches, conclusions, attempts, per-source channel,
  native job timings and URLs; all matrix names retained for inspected runs.
* Example [beta dist](https://github.com/rust-lang/rust/actions/runs/36182966322/job/108229851717),
  [stable dist](https://github.com/rust-lang/rust/actions/runs/36464947395/job/109072975454),
  [separate native LLVM-MinGW job](https://github.com/rust-lang/rust/actions/runs/36081388361/job/107904221771).
* Read-only collector: `collect_annual_history.py --start YYYY-MM-DD --end YYYY-MM-DD`
  (end exclusive). Pagination is date bounded; every push attempt is inspected.
* Offline: `python .\ci-benchmark\build-time\annual_capacity.py`.
  Tests: `python -m unittest discover -s .\ci-benchmark\build-time -p "test_*.py"`.

This report did not wait for treatment runs, launch builds, provision
hardware, change CI, or publish upstream. The optimization duration model remains
unvalidated by a completed native32 full-production measurement.
