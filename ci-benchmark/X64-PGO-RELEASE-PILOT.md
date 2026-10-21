# x64 upstream-PGO versus local-PGO: qualified full-release pilot

## Result

The first matched fresh full-release pair completed on 20 October 2026:
[run 39456859889](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39456859889),
harness `8b452f3deca20abb6123ff473d9e9a61cc633fc2`.
Both releases passed the unmodified upstream extracted-distribution tests.

| Endpoint | Upstream recipe rebuilt locally | Local recipe | Local increase |
|---|---:|---:|---:|
| Full compiler production | 2h 14m 19.20s | 2h 17m 28.00s | **3m 08.80s / 2.34%** |
| Extracted-distribution qualification | 6m 45.75s | 6m 24.07s | -21.68s |
| Whole successful CI job | 2h 49m 44s | 2h 54m 00s | **4m 16s / 2.51%** |

This is a **qualified single-pair observation**, not a stable estimate or a
confidence interval. Upstream ran first, local second, on the same machine.
Reverse-order fresh-profile repetitions remain necessary before generalizing
the CI-cost difference.

Production includes helper construction, fresh rustc/LLVM PGO training,
compilation and packaging. It excludes initial source/tool setup, extracted
tests, artifact uploads and cleanup. It contains dependency downloads and is
**not an offline raw-compile measurement**. Whole-job time is GitHub's successful
job start-to-completion interval, excluding queue time, the separate readiness
job and all failed preparation attempts.

## Controls and qualification

The [protocol](x64-pgo-release-protocol.json) fixes Rust 1.94.1
(`e408947bfd200af42db322daf0fadfe7e26d3bd1`), LLVM
`00d23d10dc48c6bb9d57ba96d4a748d85d77d0c7`, rustc-perf
`c0301bc44d175b9b2c5442b25049475c39d7700c`, clang-cl 20.1.3,
16 logical processors and short isolated C: NVMe paths on `MARCPE-TEST01-X64`.
Both cells used fresh compiler objects, profiles and Cargo homes; neither
added LLVM or Rust cross-crate ThinLTO. Rust retained `thin-local`.

The upstream cell uses the upstream `opt-dist windows-ci` PGO sequence and
Microsoft link/lib. The local cell adds the static-LLVM training relink and
uses LLVM lld-link/llvm-lib. This is a recipe comparison, **not an isolated
PGO-profile-quality intervention**. Both use the same bootstrap-only runtime
discovery patch. Source integrity, native-tool identities, normalized settings,
profile use and required distribution output gates passed.

The preserved evidence contains identical sets of 18 distribution files,
including complete Rust bundles, MSI, docs, Cargo, rustc, standard libraries,
LLVM tools, Clippy, rustfmt and rust-analyzer. Profile hashes, coverage counts,
matching source/tool/configuration identities, successful timer sections and
GitHub job accounting were checked again after download.

## Where the production difference occurred

These are non-overlapping elapsed-time categories, not exclusive compiler CPU
measurements. Do not add the nested LLVM substeps below to their parent.

| Production phase | Upstream seconds | Local seconds | Local minus upstream |
|---|---:|---:|---:|
| Rustc PGO stage | 3,094.98 | 3,056.91 | -38.07 |
| LLVM PGO stage | 1,485.54 | 1,688.19 | +202.65 |
| Final full-distribution build | 3,275.24 | 3,294.32 | +19.08 |
| Helper and remaining production overhead | 203.44 | 208.58 | +5.14 |
| **Total** | **8,059.20** | **8,248.00** | **+188.80** |

Within the LLVM stage, instrumented build time increased from 1,184.24 to
1,229.37 seconds (+45.13s), while profile gathering increased from 297.10 to
454.22 seconds (+157.12s). Thus the net observed cost is concentrated in the
stage that changes training behavior. One pair cannot separate treatment
effects from run-to-run variation.

## Profile gap observed in this rebuild

| LLVM component | Upstream functions / active | Local functions / active |
|---|---:|---:|
| `X86TargetLowering` | 0 / 0 | 255 / 167 |
| `InstCombine` | 6 / 0 | 873 / 597 |

The upstream-recipe rebuild produced a nonempty 21,058,848-byte LLVM profile,
but no active counters in these two checked backend areas. The local profile
was 48,245,720 bytes and had substantial activity in both. Size alone does not
establish quality; the executed counters are the relevant evidence.

This supports the static-link training concern for **this reproduced x64
upstream recipe**. It does not establish the contents or effectiveness of
the profiles used to produce the official downloadable Rust compiler.
Neither does coverage alone quantify downstream IronRDP benefit.

## Resource observations

Continuous telemetry retained 1,368 upstream and 1,393 local samples, with valid
counter status throughout. Median system CPU utilization was 84.2% and 82.8%.
Minimum available memory was 8,323 and 8,095 MiB. C: free space bottomed at
175.23 and 144.63 GiB; the 180-GiB admission gate is a **before-build** requirement,
not a minimum that must remain free throughout compilation.

NVMe median read latency was approximately 0.125 ms in both cells; sampled
95th-percentile read latency was 0.471/0.512 ms. Median disk queue length was
zero, with 95th percentiles zero/one. These samples do not show sustained
NVMe queueing or exhausted available memory. They cannot rule out all transient
interference, and page-input counts are not proof of pagefile thrashing.

The much shorter jobs than the earlier HDD scaling experiments are encouraging,
but source/training revisions and optimization recipes also differ. Do not
attribute that cross-study difference solely to replacing the HDD with NVMe.

## Relationship to the IronRDP result

The independently qualified, earlier shipping-Rust-to-local-PGO comparison
remains **957.41 to 791.12 seconds: 17.4% less offline native IronRDP wall time,
95% paired interval 15.2-19.1%**. See [native results](X64-NATIVE-RESULTS.md).
It used five independent standard Windows VMs and the earlier fixed compiler
artifacts, without added ThinLTO.

The new full-release artifacts have now completed their
[own five-VM IronRDP replay](X64-PGO-FRESH-REPLAY.md): **18.0% less wall time
versus official shipping Rust (95% interval 15.0-20.8%)**, and **20.9% less
versus the rebuilt upstream recipe (18.1-23.4%)**. The earlier 17.4% result
remains separate. The fresh replay and this first release pair use the same
compiler artifacts, but different benchmark/release machines and CPU allocations;
they do not establish a general break-even count.

The follow-up [replay protocol](x64-pgo-replay-protocol.json) pins these two
compiler archive hashes before measurement. Five independent standard four-CPU
Windows VMs compare official shipping Rust, rebuilt upstream and local PGO with
the same official Cargo and native standard libraries. The established native
meter executes one excluded warmup and three measured rounds, counterbalancing
compiler order and running all four original correctness commands outside the
clock. `x64-pgo-replay.yml` implements this comparison.

A separate `x64-pgo-reverse.yml` repeats production local-first, then upstream,
with fresh source, profiles and caches. The earlier upstream result is downloaded
only to validate the local-first cell's recipe and tool identities; it is not
reused as that pair's production timing. The new upstream cell supplies its
own fresh timing, profiles and qualification.

Fresh replay run:
[39506872211](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39506872211).
Reverse-order release run:
[39506380543](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39506380543).
Both were started after the first pair qualified; neither is included in the
table above. Once all five replay jobs complete, download their
`x64-pgo-fresh-replay-*` artifacts into separate folders beneath one evidence
directory and run:

```powershell
python ci-benchmark\analyze_x64_pgo_replay.py <evidence-directory> --output <results.json>
```

The analyzer rejects incomplete matrices, changed provenance/common inputs,
compiler or command substitutions, reused targets, CPU-accounting violations,
missing correctness checks and mixed workflow attempts. It computes three
paired contrasts using whole-VM resampling; measured rounds are not treated as
independent VMs.

## Evidence

- [Structured results and evidence hashes](X64-PGO-RELEASE-PILOT.json).
- [Upstream job 118746290925](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39456859889/job/118746290925).
- [Local job 118831072757](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/39456859889/job/118831072757).
- Run artifacts: `x64-pgo-upstream-evidence`, `x64-pgo-local-evidence`,
  `x64-pgo-upstream-dist`, `x64-pgo-local-dist`; retention is 30 days.
- Evidence includes result/provenance JSON, profile files, component coverage,
  native tool settings, full logs, bootstrap metrics, telemetry and distribution
  SHA-256 manifests. The JSON report preserves the precise values used here.
