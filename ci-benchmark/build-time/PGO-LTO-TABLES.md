# Generated PGO/ThinLTO planning arithmetic

**Hypothetical budgets, not measurements, forecasts with probabilities, or confidence intervals.**
Read [scope, evidence and dependencies](PGO-LTO-PROJECTION.md). Values below are rounded to
five minutes unless showing observed baseline accounting or a conditional threshold.

Representative stock run: **33865610474**; observed job **117.05 min**.
Remove stock compiler 21.24 + cached LLVM/LLD 11.94 min.
Keep **83.87 min**, including **60.37 min** full tools/docs/libraries/packaging.

| Scenario | Fresh PGO + final ThinLTO job | Added Arm64 elapsed/runner-min | Final-build allowance to fit360 | Single job fits360? |
|---|---:|---:|---:|---|
| efficient | ~250 | ~130 | 156 min | yes under these assumptions |
| planning | ~405 | ~290 | 44 min | no |
| stress | ~670 | ~550 | -129 min | no |

## Subsets and scheduling

| Scenario / variant | Arm path elapsed min | Arm runner-min | Longest job min | Whole-merge increase min (Sep4 AM) |
|---|---:|---:|---:|---:|
| efficient / frontend_pgo_only | ~155 | ~155 | ~155 | ~0 |
| efficient / thinlto_only | ~140 | ~140 | ~140 | ~0 |
| efficient / fresh_dual_pgo_no_lto | ~235 | ~235 | ~235 | ~45 |
| efficient / fresh_dual_pgo_thinlto | ~250 | ~250 | ~250 | ~60 |
| efficient / exact_profile_consumer_only | ~140 | ~140 | ~140 | unknown: external profile cost |
| efficient / overlap_llvm_build | ~225 | ~310 | ~125 | ~35 |
| efficient / independent_profiles | ~220 | ~295 | ~125 | ~30 |
| efficient / native_four_job_dag | ~235 | ~295 | ~125 | ~45 |
| efficient / warm_exact_instrumented_llvm | ~220 | ~220 | ~220 | ~30 |
| planning / frontend_pgo_only | ~210 | ~210 | ~210 | ~20 |
| planning / thinlto_only | ~195 | ~195 | ~195 | ~5 |
| planning / fresh_dual_pgo_no_lto | ~370 | ~370 | ~370 | ~185 |
| planning / fresh_dual_pgo_thinlto | ~405 | ~405 | ~405 | ~220 |
| planning / exact_profile_consumer_only | ~200 | ~200 | ~200 | unknown: external profile cost |
| planning / overlap_llvm_build | ~370 | ~515 | ~185 | ~180 |
| planning / independent_profiles | ~345 | ~470 | ~185 | ~155 |
| planning / native_four_job_dag | ~385 | ~475 | ~185 | ~195 |
| planning / warm_exact_instrumented_llvm | ~340 | ~340 | ~340 | ~150 |
| stress / frontend_pgo_only | ~285 | ~285 | ~285 | ~95 |
| stress / thinlto_only | ~295 | ~295 | ~295 | ~105 |
| stress / fresh_dual_pgo_no_lto | ~590 | ~590 | ~590 | ~400 |
| stress / fresh_dual_pgo_thinlto | ~670 | ~670 | ~670 | ~480 |
| stress / exact_profile_consumer_only | ~305 | ~305 | ~305 | unknown: external profile cost |
| stress / overlap_llvm_build | ~605 | ~845 | ~310 | ~415 |
| stress / independent_profiles | ~555 | ~760 | ~295 | ~365 |
| stress / native_four_job_dag | ~630 | ~770 | ~295 | ~440 |
| stress / warm_exact_instrumented_llvm | ~540 | ~540 | ~540 | ~350 |

Serial fresh variants count all runner time in one job. Parallel variants count
duplicate producer setup, reserved-runner waiting and consumer handoff/setup.
Profile-consumer-only is **not** an end-to-end fresh production scenario.

## Assumed component budgets

| Budget (minutes, except slowdown fraction) | Efficient | Planning | Stress |
|---|---:|---:|---:|
| seed_llvm | 12 | 30 | 60 |
| frontend_instrument | 25 | 45 | 70 |
| frontend_training | 10 | 20 | 35 |
| frontend_profile_use | 10 | 20 | 35 |
| llvm_instrument | 35 | 60 | 100 |
| static_relink | 5 | 12 | 25 |
| llvm_training | 8 | 15 | 30 |
| final_thinlto | 45 | 90 | 180 |
| standalone_thinlto | 45 | 90 | 180 |
| final_without_lto | 30 | 55 | 100 |
| profile_support | 5 | 10 | 20 |
| extra_qualification | 10 | 20 | 30 |
| plain_frontend_for_backend | 25 | 45 | 70 |
| backend_training_penalty | 0 | 0.25 | 0.5 |
| handoff | 3 | 6 | 10 |
| consumer_setup | 5 | 10 | 15 |
| instrument_cache_restore | 4 | 10 | 20 |

Definitions and rationale are in [pgo-lto-inputs.json](pgo-lto-inputs.json).
The numbers are exposed assumptions, not per-stage measurements transferred across hardware.

## Whole-merge replay across all three samples

| Baseline merge run | Original makespan | Efficient fresh serial increase | Planning increase | Stress increase |
|---|---:|---:|---:|---:|
| 33865610474 | 189.95 | ~60 | ~220 | ~480 |
| 33916006473 | 279.25 | ~0 | ~135 | ~400 |
| 33961251131 | 191.57 | ~65 | ~220 | ~485 |

Other platform/test jobs are held unchanged, as are measured Arm start offsets and
the final workflow suffix. This is dependency replay, not a queue/concurrency forecast.
In particular, adding a long Arm job can make Arm the new critical path even though
making the old117-minute Arm job faster had no effect on the original merge makespan.

## Tool compilation benefit sensitivity

| Baseline run | Eligible observed stage2-tool minutes | 10% conditional saving | 20% conditional saving |
|---|---:|---:|---:|
| 33865610474 | 20.7 | 2.1 | 4.1 |
| 33916006473 | 18.6 | 1.9 | 3.7 |
| 33961251131 | 23.0 | 2.3 | 4.6 |

Base scenarios deduct **zero**. These are rate sensitivities only, not transferred
IronRDP speedups. Prove which bootstrap compiler actually builds these tools before
using any saving; packaging and documentation are not multiplied by this factor.

Reproduce offline: `python project_pgo_lto.py`. Full precision in JSON is arithmetic
traceability, not measurement precision for hypothetical stages.
