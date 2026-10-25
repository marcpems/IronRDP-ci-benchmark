# Paired breadth: testing the IronRDP Rust PGO improvement

## Hypothesis

**The Rust PGO improvements that reduced IronRDP build time will also reduce
wall-clock compilation time across a broader, frozen Rust project set.**

We tested that hypothesis rather than assuming it. The base is actual official
Rust 1.94.1; the test is the exact qualified local Rust 1.94.1 compiler used in
the earlier repeated IronRDP comparison. Both use common official Cargo,
rustdoc and byte-identical standard libraries. This is a toolchain-replacement
test of the **PGO training repair plus native-linking production changes**.
Official Rust already has upstream optimizations: this is not PGO-on versus
PGO-off, nor an isolated causal estimate of profile quality.

## Wall-clock findings and conclusion

**The improvement transfers to the three selected workloads for fresh
compilation, but not demonstrably to incremental rebuilding as a family.**
All nine fresh check/debug/release project endpoints improved, with positive
pointwise 95% reduction intervals. The equal-project family summaries were:

| Scenario family | Wall-clock reduction | 95% paired interval | Conclusion |
|---|---:|---:|---|
| Fresh check | **4.56%** | 3.40% to 5.78% | Supports improvement |
| Fresh debug build | **9.45%** | 8.52% to 10.49% | Supports improvement |
| Fresh release build | **14.32%** | 12.53% to 15.86% | Supports improvement |
| Incremental no-op | -0.71% | -6.87% to 4.66% | Inconclusive |
| Incremental comment edit | 1.27% | -0.46% to 3.11% | Inconclusive |

Positive reductions mean the test compiler was faster; negative values mean
slower. Each family gives the three projects equal weight using the geometric
mean of their test/base ratios. This is not a sum of build times or a pooled
full-build/incremental headline.

### Every workload and scenario

Times are seconds, averaged over three measured repetitions within each VM and
then equally over five VMs. Percentages and intervals use unrounded inputs;
subsecond values can therefore round to the same displayed time.

| Workload | Scenario | Base seconds | Test seconds | Reduction | 95% paired reduction interval |
|---|---|---:|---:|---:|---|
| fd | Fresh check | 14.449 | 13.641 | 5.59% | 4.54% to 6.34% |
| fd | Fresh debug | 23.902 | 21.152 | 11.51% | 10.46% to 12.42% |
| fd | Fresh release | 65.010 | 51.511 | 20.76% | 19.36% to 21.66% |
| fd | Incremental no-op | 0.183 | 0.183 | -0.16% | -1.87% to 1.30% |
| fd | Comment edit | 1.500 | 1.489 | 0.75% | 0.39% to 1.16% |
| Alacritty workspace | Fresh check | 32.608 | 31.501 | 3.39% | 0.46% to 5.71% |
| Alacritty workspace | Fresh debug | 47.628 | 42.943 | 9.84% | 8.22% to 11.37% |
| Alacritty workspace | Fresh release | 83.172 | 70.976 | 14.66% | 11.30% to 17.50% |
| Alacritty workspace | Incremental no-op | 0.267 | 0.272 | -1.77% | -21.79% to 13.64% |
| Alacritty workspace | Comment edit | 3.480 | 3.474 | 0.17% | -3.82% to 4.92% |
| Nushell `nu-parser` | Fresh check | 61.126 | 58.260 | 4.69% | 3.18% to 6.96% |
| Nushell `nu-parser` | Fresh debug | 80.503 | 74.904 | 6.95% | 4.99% to 9.59% |
| Nushell `nu-parser` | Fresh release | 81.480 | 75.793 | 6.98% | 2.54% to 10.45% |
| Nushell `nu-parser` | Incremental no-op | 0.426 | 0.427 | -0.22% | -2.55% to 1.31% |
| Nushell `nu-parser` | Comment edit | 1.040 | 1.010 | 2.87% | -0.22% to 6.19% |

Release builds show the strongest transfer: approximately **13.50 seconds saved
for fd, 12.20 seconds for Alacritty and 5.69 seconds for nu-parser** per fresh
release build on these machines. The gains are workload-dependent, not a
universal 18% extrapolation from IronRDP.

The incremental result is materially different. No-op cells compiled zero
artifacts and did not demonstrate a reduction. fd's comment edit has a small
positive interval, but the saving is about 11 milliseconds; the cross-project
comment-edit result remains inconclusive. These comment-only edits do not
establish performance for semantic edits.

### Paired design and validity

[Run 40199323643](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/40199323643),
attempt 1, executed preregistered harness
`72243aeeb7f20974792a7753144e7965c5bb257b` on 25 October 2026.
All **15 independent hosted Windows VM jobs passed**: five per project.
Each VM ran both compilers and every scenario with four workers and four-CPU
affinity. Different projects used separate VMs, not one machine reused under
multiple project labels.

The complete dataset contains **450 measured cells and 150 retained warmup
cells**. Only the single preplanned warmup round was excluded from timing
estimates. Every base/test pair was adjacent and counterbalanced by VM and
round. All measured repetitions were retained; there was no failed-machine,
slow-sample or post-result workload selection.

Every cell used a fresh target directory. Incremental seeds, dependency
fetching, original correctness and successful-target cleanup were outside its
measured compile interval. Empty targets do not imply an OS page-cache flush.
Frozen revisions, lockfiles, features and original application release profiles
were preserved. Source identities and temporary comment restoration were
verified in every cell.

The analysis uses 10,000 paired whole-VM bootstrap draws, seed 1012026.
Both variants and all scenarios stay together when resampling a project's VM;
different projects' VMs are sampled independently. Intervals are **pointwise**
and conditional on these fixed compiler artifacts and selected workloads.
They are not simultaneous guarantees, a random-project population sample or
estimates of PGO retraining variability.

The original qualified release artifacts come from run `39456859889`, staged
by IronRDP replay `39506872211`. Rust source is
`e408947bfd200af42db322daf0fadfe7e26d3bd1`. Executable, driver, Cargo, standard
library and production-receipt hashes are pinned and revalidated. Common
rustdoc has a new explicit pin from the verified official 1.94.1 archive;
the historical replay indexes did not themselves record rustdoc hashes.

## Correctness results

**All 350 original correctness commands passed for both base and test.**
They ran outside compilation timing for every project/scenario/compiler/VM
in warmup. Each measured row links to its matching successful correctness
receipt by hash; it does not falsely claim to have rerun tests itself.

Counts below are per invocation and were identical for base and test:

| Workload | Original command scope | Base passed | Test passed | Upstream ignored per invocation |
|---|---|---:|---:|---:|
| fd | All-feature debug tests | 213 | 213 | 0 |
| fd | All-feature release tests | 213 | 213 | 0 |
| Alacritty | Workspace debug tests/doctests | 259 | 259 | 0 |
| Alacritty | Terminal, no default features | 128 | 128 | 0 |
| Alacritty | Workspace release tests/doctests | 258 | 258 | 0 |
| Nushell `nu-parser` | Package debug tests/doctests | 258 | 258 | 2 |
| Nushell `nu-parser` | Package release tests/doctests | 258 | 258 | 2 |

Nushell's existing `multi_test_parse_number` and `test_parse_any` remain
upstream-ignored. No new ignores, filters, workload patches or lock changes
were introduced. Passing these suites is not full Nushell/plugin/interactive
coverage or Alacritty GUI/display/input validation.

## Summary and remaining concerns

**The hypothesis is supported for fresh compilation of this broader set:**
4.56% lower check time, 9.45% lower debug-build time and 14.32% lower
release-build time under equal-project weighting. Both compilers passed the
declared original correctness coverage. The result extends demonstrated
toolchain-replacement benefit beyond IronRDP, while showing that its magnitude
depends on workload and build mode.

**Do not extend that conclusion beyond the evidence.** Incremental family
improvements remain inconclusive. The roots are held out, but dependencies
overlap training fixtures; strict dependency-disjointness is not established.
The contrast includes native-linking production changes alongside PGO repair.
Application runtime throughput, code-size regressions, other architectures,
the newer Rust 1.101 candidate and arbitrary Rust projects are not qualified
by this test. No maintainer-approved shipping threshold is inferred.

Recommendation: **advance the 1.94.1 recipe's broader compile-time result as
positive evidence, not as unconditional shipping approval.** The wider ADO
research item remains Started for the separate runtime/size, shipping-plan and
current-candidate qualification work.

## Evidence and reproduction

- [Frozen paired protocol](paired-protocol.json).
- [All estimates, per-VM means, correctness counts and evidence hashes](paired-results-40199323643.json).
- [Permanent raw benchmark evidence](paired-raw-40199323643.zip): 4,410 files,
  including every measured and warmup result, stdout/stderr, meter checks,
  frozen inputs and tool identities.
- [Analysis implementation](../analyze_breadth_pairs.py) and
  [focused regression tests](../test_analyze_breadth_pairs.py).

Archive SHA-256:
`eafd954f002cf77a677f6e6d47ef678cae2ff57257a806868032ecd9a009c67a`.
The permanent archive omits only incidental Cargo-cache and installed-tool
JSON files accidentally included by the initial broad upload glob; **no
benchmark cell, log, timing or correctness evidence was omitted**. Analysis
of the scoped archive reproduced all estimates and correctness results exactly.
Future upload paths have been narrowed accordingly, without rerunning or
changing the completed measurements.

From the repository root, extract into a new directory and reproduce:

```powershell
Expand-Archive ci-benchmark\breadth\paired-raw-40199323643.zip <evidence-directory>
python ci-benchmark\analyze_breadth_pairs.py <evidence-directory> `
  --output <reproduced-results.json>
```

The analyzer rejects incomplete or reordered matrices, mixed attempts/tools,
changed inputs, failed commands, invalid artifact behavior, missing/filtered
tests and incorrect warmup-correctness links. A local monitoring network
timeout was reconnected; no benchmark was restarted or excluded.
