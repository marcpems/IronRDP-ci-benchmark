# Balanced Windows Arm64 compiler-production proposal

**Decision, 2026-10-02:** prefer **one native Windows Arm64 32-vCPU / 128-GB
larger runner per build**, fresh rustc+LLVM PGO, and **ThinLTO only on the final shipping
Rust/LLVM compiler** initially. This keeps the existing serial bootstrap pipeline
and full distribution instead of adding a four-job protocol. Funding is not the
constraint: choose latency, headroom and maintainability first. This is a
**conditional proposal, not a measured optimized build or upstream-ready patch**.

The planning sensitivity is **136 minutes / $13.68 compute per completed qualified
build**, versus **182 minutes / $9.39** on native 16-vCPU. The 32-vCPU choice is
near the existing two-hour warm job; it is not guaranteed. A constrained scaling
case takes **247 minutes**, and combined stress assumptions exceed 360.
**Fallback: two sequential jobs, fresh profile producer → final compiler/full
dist/qualification**, before considering four-job parallelism.

The eventual upstream-sized change is confined to **Arm64 dist**: select the
configured larger-runner label and use the Arm-capable opt-dist entrypoint, with
stage-local LTO settings and mandatory static relinks. Keep
`llvm.link-shared=false`, native bitcode-capable LLVM librarian/LLD, and build
opt-dist helpers for the native host only; the final dist still includes Arm64EC.
Do not apply final ThinLTO globally to every training stage. Keep
`DIST_REQUIRE_ALL_TOOLS=1` and the existing channel's full output policy.

## Can one machine cover a year of upstream work?

**Not reliably as the sole runner.** “One runner per build” above is not a
one-machine fleet guarantee. The new [capacity and annual-cost assessment](ANNUAL-CAPACITY.md)
inspects **2,633 CI invocations over September 18–October 1 UTC**:
**162 MSVC Arm64 distribution attempts**, 344 native test jobs and 160 separate
Arm64 LLVM-MinGW dist jobs. Promotion reuses CI artifacts; it does not add
365 nightly and 365 beta compiler rebuilds.

With **concurrency one**, 95% assumed availability and the current **$0.098/min**
native32 rate, annualizing those MSVC attempts gives:

| Scope / conditional accounting | Attempts/year | Central optimized compute/year | Adverse compute/year |
|---|---:|---:|---:|
| One candidate attempt daily, **not full upstream CI** | 365 | $4,865 | $8,871 |
| Sampled scheduled rate, budget each attempt in full | ~4,224 | **$56,292** | **$102,650** |
| Same arrivals, retain historical cancellation deadlines | ~4,224 | **$39,986** | **$58,711** |

The full-attempt central/adverse workloads require **115%/209%** of one runner's
available minutes; even cancellation-aware central occupancy is **81%**, above
a 70% headroom target. These are modeled cost/capacity sensitivities, not yearly
forecasts or measured native32 builds. Prefer a primary runner with overflow/
replacement capacity; central full-attempt planning needs **two runner slots**.
Keep ordinary CI elsewhere. Linux/macOS/x86 coverage cannot be replaced by this
machine. A **$51,508.80** continuous-active hosted-rate equivalent is not a
self-hosted annual TCO quote, and idle larger-runner configuration is not billed.
See [sample provenance, queues, retries, storage and yearly tables](ANNUAL-CAPACITY.md).

## Verified availability and price—not x64 substitutions

Official pages checked October 2:
[hardware](https://docs.github.com/en/actions/reference/runners/larger-runners),
[Arm64 pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing),
[public standard runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).
The [August 20 image announcement](https://github.blog/changelog/2026-08-20-windows-11-arm64-vs2026-image-generally-available/)
explicitly confirms Windows 11 Arm64 VS2026 on standard **and larger** runners.

| Native Windows Arm64 option | RAM / SSD catalog | USD / wall minute | Access |
|---|---|---:|---|
| Standard public, 4 CPU | 16 GB / documented 14 GB workspace allowance | **$0 compute** | Existing public runner; actual baseline free disk was ~124 GiB |
| Larger, 16 vCPU | 64 GB / 600 GB | **$0.050**, `windows_16_core_arm` | Organization/enterprise on Team or Enterprise Cloud |
| Larger, 32 vCPU | 128 GB / 1200 GB | **$0.098**, `windows_32_core_arm` | Same; not included/free even for public repositories |

These are catalog vCPUs, **not promised physical cores or equal per-core speed**.
No private account entitlement, image provisioning, regional capacity or queue SLA
was verified. An organization administrator must enable the correct Arm64 image,
runner group, repository access and billing; use its configured label, not an
invented `windows-11-arm-32core` public label. A personal fork cannot assume access.
No paid infrastructure was provisioned. The unrelated x64 16/32 prices
($0.082/$0.162) and private standard 2-core price are **not used**.

If organization/capacity access is unavailable, use the existing standard-runner
split as a timeout-safe staging option, or obtain a supported native Windows
Arm64 self-hosted quote. Self-hosting adds hardware/VM provisioning, supported
Windows-on-Arm drivers/image, applicable Windows desktop/virtualization licensing,
SDK/tool rights, patching, isolation, ephemeral cleanup, monitoring and spare
capacity. A Linux Arm VM or x64 Windows SKU is not evidence of a licensed native
Windows Arm64 16/32-vCPU offering. No unsupported SKU or self-hosted rate is assumed.

## Evidence and revised accounting

The [completed cold baseline report](https://github.com/marcpems/IronRDP-ci-benchmark/blob/95eb8b6f792e7851c8e4be7b47edacd5aa21c32b/arm-feasibility/FEASIBILITY.md)
records [green baseline job 110789801580](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36991902911/job/110789801580):
**141.82 minutes total; 132.44 minutes `x.py dist`**. The enclosing workflow was
red from an earlier treatment setup failure. Exclusive bootstrap minutes:
LLVM/LLD **50.84**, rustc/std **22.94**, tools **25.52**, docs **5.51**,
packaging **22.50**, vendoring **3.75**. Retained non-core work is therefore
`141.82 - 50.84 - 22.94 = 68.04`, including a **53.53-minute output tail**.
Native/Arm64EC std is replaced inside the modeled compiler core, not dropped.
Vendoring/setup/unassigned time is already retained, not added twice.

This cold no-PGO Rust **1.94.1 / LLVM 21.1.8** run is not a matched optimization
control for the **1.100-era warm-cache September** jobs in [README](README.md).
It omitted upstream S3/sccache and publication; upstream integration can add time.
Use the 50.84-minute seed LLVM anchor, **not** a cold/PGO conversion factor.
All optimized-stage rates remain assumptions. The old
[250–260 / 405–415 / 670–680 scenarios](PGO-LTO-PROJECTION.md) remain historical
assumptions; this new cold-accounting variant gives **411 / 644 minutes** for its
planning/stress four-CPU serial cases, not new measured bounds.

The [x64 fresh-PGO control](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36946671654)
took ~5h26; the [~3h49 ThinLTO treatment](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36973674727)
reused its profiles. Neither is fresh Arm64 production or an ISA scaling ratio.
The corrected Arm treatment's terminal outcome is recorded below from the
feasibility owner's handoff; no run was restarted or awaited by this analysis.
Parent x64 run 37001433534 was not queried or modified here.

### Measured-outcome addendum — October 2, 16:10 UTC

[Corrected cold Arm64 treatment 36994829038, job 110799044364](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36994829038/job/110799044364)
completed **failure at 2026-10-02 16:10:03 UTC**, **350.57 minutes total**.
The harness reported **`safety_deadline_hit=true` at 350 minutes from the first
step**: this was not a compiler error or an observed exact 360-minute timeout.
The [maintained feasibility report](https://github.com/marcpems/IronRDP-ci-benchmark/blob/ci/arm-release-feasibility/arm-feasibility/FEASIBILITY.md)
owns the detailed evidence.

* Initial instrumented rustc+LLVM: **193.86 minutes**, including **154.08 minutes
  exclusive LLVM**; frontend training **35.33**, frontend-PGO rebuild **21.15**;
  **Stage1 total 250.35 minutes**. The LLVM subset is not added again.
* Stage2 instrumented LLVM began **14:44:11.618 UTC** and was still linking at
  interruption **16:09:37 UTC**, after **~85.43 minutes**. Last Ninja output was
  **3843/3904 tasks**, not a remaining-time estimate or proof of near completion.
* Only **`rustc-pgo.profdata`** was produced. LLVM training, final profile-use
  dist/tools/docs/MSI/Arm64EC and extracted tests were **not reached**; there is
  no LLVM profile or backend-coverage qualification and no completed optimized
  release cost.
* Sampled whole-machine peaks: physical **7.51 GiB**, commit **7.80 GiB**;
  minimum free disk **29.52 GiB**. No sampled resource exhaustion was observed;
  this does not bound unsampled spikes or unreached final-stage requirements.

The **141.82-minute cold stock baseline remains valid**. The treatment did not
complete within its operational budget; whether it could fit exactly 360 minutes
is unmeasured. It is not a native32 measurement or validation of the proposed
final-only-LTO policy. Existing model inputs, annual demand and conditional cost/
capacity values are **unchanged**, not recalibrated from this incomplete run.

## Comparable latency, billed SUM and successful-build cost

**Conditional planning inputs, balanced scaling, no optimized-stage cache hit:**

| Layout | Arm elapsed | SUM runner wall | SUM rounded job minutes | Longest job | Compute / attempt → qualified |
|---|---:|---:|---:|---:|---:|
| Public 4 CPU, serial | 410.9 | 410.9 | 411 | 410.9; invalid | $0 → no completed build within cap |
| Public 4 CPU, four jobs | 385.9 | 473.4 | 475 | 176.5 | $0 → $0 compute only |
| Native 16, one job | 182.0 | 182.0 | 183 | 182.0 | $9.15 → **$9.39** |
| **Native 32, one job** | **135.8** | **135.8** | **136** | **135.8** | **$13.33 → $13.68** |
| Native 32, two serial jobs | 151.8 | 151.8 | 153 | 86.1 | $14.99 → $15.39 |
| Native 32, four jobs | 156.6 | 198.3 | 200 | 65.7 | $19.60 → $20.12 |

All amounts are USD, compute only, before tax, subscription, artifact/cache
storage and operations. Standard public usage consumes runner resources but is
not billed compute. Paid compute is **SUM(ceil(each job wall minutes)) × its
native Arm rate**, not elapsed critical path and not core-minutes.
These are the **Arm production component** of qualified-build cost; unchanged
ordinary/all-platform CI and promotion charges must be added for a whole-release
invoice. Their runner classes/rates are not normalized or invented here.
The original four-job central estimate (~385 elapsed / 475 runner / 185 longest)
used a different retained budget. The revised row is not another benchmark.

Cost/qualified assumes **95% eventual-attempt qualification success** and failed
attempts consuming **half each job**, neither measured:
`Cqualified = Csuccess + (1-q)/q × Cfailed`.
Whole-pipeline retries are charged conservatively; exact immutable successful
producer reuse can lower retry cost, but correlated failures can raise it.
Qualification includes correct profiles, complete packages and required tests,
not merely an exit-zero compiler. Deterministic invalid profiles have `q=0`:
there is **no finite qualified-build cost**, regardless of cheap runner time.
Infeasible over-cap jobs are not assigned a successful-build price.
The [generated table](BALANCED-TABLES.md) and [JSON](balanced-results.json) include
80/95/99% success sensitivities; fixed per-build costs must be added separately.

32-vCPU is not the cheapest compute: at equal reliability it beats 16-vCPU on
price only if billed minutes fall below `0.050/0.098 = 51.0%` of the 16-vCPU
minutes. Here it saves ~46 minutes for ~$4.29 more per qualified build. Choose it
for the two-hour target and headroom, **not because funding forces a compromise**.
For self-hosting, let monthly fully loaded fixed cost be `A`, variable cost per
qualified build `V` (power/cloud time, retries, licenses not in `A`, operations),
and monthly qualified throughput `N`: break-even is
`A/N + V < Chost`, or `N > A/(Chost-V)` when `Chost>V`.
Require enough capacity and equivalent reliability; an unpriced host is not free.

## Scaling, memory, cache and transfers

The [tested offline model](balanced_model.py) uses per-stage Amdahl-like scaling:
`t(n) = t(4) × [s + (1-s)/(1+(n/4-1)e)] × m`.
Balanced assumptions: efficiency `e=.8`; serial fractions compile `.10`,
training/qualification `.30`, tools `.15`, docs `.30`, packaging `.55`; `m=1`.
Source/setup/support do not shrink. The constrained case uses `.55` efficiency,
higher serial fractions and a **1.25× memory/I/O penalty** on scalable stages.
These are independent hypotheses, **not calibration or confidence intervals**.
Doubling 16→32 cannot halve setup, training bottlenecks, serial links or packaging.
Larger RAM may avoid paging, but no peak-memory requirement has been measured.

All layouts retain fresh training and mandatory static relinks. Serial jobs
transfer no intermediate build trees. Two jobs transfer profiles/provenance;
the final job recompiles from pinned source. Four jobs additionally need usable
compiler/object/native prerequisites, not just a static-linked executable.
Planning transfers assume six minutes per handoff, split equally between charged
producer upload/compression and consumer download/extraction; consumer setup ten
minutes. Stress uses ten/fifteen. JSON also tests **20-minute handoffs / 15-minute
setup**. These are budgets, not measured artifact sizes/throughput.
An assumed five-minute queue per dependency level adds **5/10/15 minutes** to
one/two/four-job critical paths without pretending idle queue is billed compute.

Cold misses determine acceptance. A separate hypothetical **80% exact
instrumented-LLVM hit / ten-minute restore** mixture does not remove fresh
profiles, static relinks or final profile-use rebuilds. No hit rate is measured;
compression, storage and cache maintenance still cost money/time. Cache keys
must bind source, targets, clang/SDK, flags, paths and instrumentation identity;
profiles bind corpus/modes/compiler identity too. Never equate warm stock C++
hits with optimized-stage hits. Smaller work on 32-vCPU can make a large restore
barely worthwhile. Additional tool-specific PGO and tool ThinLTO costs (`E/U` in
the [original model](PGO-LTO-PROJECTION.md)) remain **unknown and unbudgeted**,
not claimed free or covered by these scenario ceilings.

## Acceptance gates and fallback order

1. **Qualification first.** Match the chosen Linux policy's rustc/LLVM PGO and
   final ThinLTO coverage, not Linux hardware or guaranteed Linux performance.
   Pin source/SDK/image/corpus; verify final flags/profile hashes, no unacceptable
   function mismatches, and nonzero **AArch64TargetLowering + InstCombine**
   execution after a real static relink. Validate transient non-LTO training
   quality with retained downstream controls. Full tools, supported LLVM targets,
   native+Arm64EC libraries/docs, profiler, dev archives, MSI, manifests and
   install/test gates remain; channel-gated tools follow that channel.
2. **One 32-vCPU job is the first candidate, not an unconditional rollout.**
   Provisional release gate: matched cold and warm complete builds, every observed
   job ≤**300 minutes** (60-minute hard-limit headroom); target median ≤**150**
   and eventual p95 ≤**180 minutes** for “near two hours.” Collect at least ten
   cold/warm pairs for screening, then enough sustained production data to estimate
   p95; ten pairs are not statistical proof. No profile/cache hit may be required
   to fit. Keep subprocess deadline **350**, workflow limit **360**.
   Record peak committed memory and disk; require ≥**20% measured free headroom**
   and no sustained paging, not assumed RAM proportionality.
3. **Use two serial jobs if cold/tail time approaches 300 or fails the cap.**
   This preserves stage order and needs only one profile/provenance boundary.
   Combined constrained/stress native32: serial **380 minutes fails**, two jobs
   **405 elapsed / 231 longest** fit with **129 minutes** hard-limit headroom,
   ~$**40.84** qualified compute. It sacrifices the two-hour target explicitly.
   Native16 is viable if measured ≤180 minutes with equivalent headroom, or if
   32-vCPU access is unavailable—not merely to save a few dollars.
4. **Four jobs only for measured necessity.** Ordinary `needs`: frontend and LLVM
   builders overlap → backend static relink/training → final. No mid-job messaging,
   no reserved waiting runner. Use only if two-job producers exceed 300 or measured
   overlap recovers ≥20 minutes net after transfers without qualification loss.
   On the planning native32 case it is **slower and dearer** than one job.
   Standard four-CPU four-job staging fits modeled per-job stress limits but takes
   ~599 minutes; free compute is not a near-two-hour solution.
5. **Do not silently reduce optimization/output coverage.** Frontend-only PGO or
   ThinLTO-only are explicit lower-coverage fallbacks ([subset comparison](PGO-LTO-PROJECTION.md#3-subsets-smaller-changes-may-fit-without-the-full-bundle)),
   not “Linux-equivalent” delivery. Independent profile producers, training shards
   and tools/docs fan-out add provenance/merge complexity; defer until measurements
   justify them. If quality or timing gates fail, retain the qualified stock path.

**[360 minutes is per hosted job](https://docs.github.com/en/actions/reference/limits),
not the merge critical path.** Ordinary test CI stays
unchanged and runs alongside dist. Approximate merge eligibility is
`max(other platform/test finish, Arm start + qualified Arm path) + final gates`;
successful splitting alone does not make that max smaller. With the recent
~181–184-minute other-job frontier, the modeled 136+5-minute path need not extend
the merge, while 247+5 adds roughly 68–71 minutes, subject to start offsets.
The **240-minute promotion** process separately downloads, recompresses, signs
and publishes these artifacts; **it does not rebuild the compiler**. Its elapsed
cost and schedule wait remain unknown and are not included in compiler prices.

## Reproduce / scope

`python .\ci-benchmark\build-time\balanced_model.py` and
`python .\ci-benchmark\build-time\annual_capacity.py`; validation:
`python -m unittest discover -s .\ci-benchmark\build-time -p "test_*.py"`.
Inputs/source excerpts: [balanced-inputs.json](balanced-inputs.json).
Existing evidence: [README](README.md), [OPTIONS](OPTIONS.md),
[PGO-LTO-PROJECTION](PGO-LTO-PROJECTION.md), [source probe](SOURCE-PROBE.md).
Only this fork report/model branch is changed. No workflow, ordinary CI,
infrastructure, upstream publication or compiler run is changed or launched.
