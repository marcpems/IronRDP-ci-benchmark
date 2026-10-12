# Release job throughput investigation

The approximately 20% CPU ceiling is imposed by this experiment harness, not
an intrinsic Windows or Rust limit. `msvc_experiment.execute` originally passes
four CPUs to a Windows Job Object, and the matched release configuration sets
`build.jobs = 4`. All descendants inherit that affinity. Four logical CPUs are
20% of the 20-logical-CPU Arm64 custom runner and 25% of the 16-logical-CPU x64
custom runner. Lower readings can reflect serial work, dependency stalls, I/O,
or downloads. The standard hosted comparison intentionally uses four CPUs.

**No new experiments were dispatched to either custom timing runner.** The
undispatched capacity-workflow changes were removed. The matched workflow and
four-CPU defaults remain unchanged. New experiments ran only on the local
MARCPE-C2-1 Windows Arm64 PC (Snapdragon X2 Elite, 12 logical CPUs).

## Where the completed baseline releases spend time

Source: qualified, excluded hosted pilot
[38172717639](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38172717639).
These historical baselines use Rust `ab0afc7ee6827da442070b034830b5d69a9b537c`;
they are not measurements of the currently running custom machines.
The following numbers sum **exclusive** bootstrap step durations so nested
compiler work is not counted again inside documentation or distribution steps.

| Production scope | x64 minutes | x64 share | Arm64 minutes | Arm64 share |
|---|---:|---:|---:|---:|
| Rust tool builds | 45.2 | 29.4% | 27.4 | 23.9% |
| Compiler, standard library, codegen backends | 41.0 | 26.7% | 24.0 | 21.0% |
| LLVM and LLD builds | 40.0 | 26.0% | 25.2 | 22.0% |
| Distribution assembly and compression | 23.6 | 15.3% | 27.8 | 24.3% |
| Documentation generation | 2.7 | 1.7% | 6.7 | 5.9% |
| Other bootstrap work | 1.3 | 0.9% | 3.4 | 3.0% |

The denominator is the recorded bootstrap distribution invocation: 9,229.1s
x64 and 6,869.5s Arm64, with 0.5s/3.5s unattributed. Compiler scopes include
linking, subprocess waits and incidental I/O; these are **not raw compile CPU**
figures. Assembly includes copying, MSI construction and compression, not just
XZ. The bootstrap CPU samples describe system utilization and are not used as
process-tree CPU measurements.

| Job component | x64 minutes | Arm64 minutes |
|---|---:|---:|
| Production command, including bootstrap startup | 155.1 | 115.8 |
| Extracted-distribution test command | 22.1 | 26.5 |
| Remaining job time | 7.3 | 14.2 |
| Complete GitHub job | 184.4 | 156.5 |

Remaining job time is the residual, not a directly instrumented stage: setup,
downloads, runtime preparation, extraction, manifest/profile checks, uploads
and orchestration. Production's measured process-tree CPU averages were 2.91
and 2.86 effective cores, or approximately 73%/71% of the allowed four.
These averages cannot prove the cause of every idle interval.

The failed first custom x64 pilot also spent about 9.6 minutes reaching native
source/tool preparation and 26.2 minutes in that setup step. It failed during
runtime preparation before Rust production. This establishes substantial
setup overhead on that attempt, not slow compiler execution.

## Completed local experiments

### CPU affinity and build parallelism

`release_llvm_probe.py` built the pinned LLVM
`aab11ee0ea5ea9a1d462ad0bc1fae9d9bb643019` dependency graph for `llvm-as` and
`llvm-dis`, including LLVMCore and Support. Every sample generated **845 fresh
object files** in a new CMake/object directory. The order was 4, 12, 12, 4
CPUs/jobs; there were two samples per setting. Source and OS caches were not
flushed. Configuration and correctness checks were outside the build clock.
The built tools successfully round-tripped an LLVM IR fixture.

| Setting | Samples (s) | Median (s) | Peak job memory, maximum |
|---|---|---:|---:|
| 4 CPUs, 4 build jobs | 207.58, 207.50 | 207.54 | 1.06 GB |
| 12 CPUs, 12 build jobs | 86.86, 75.36 | 81.11 | 1.94 GB |

**60.9% less wall time; 2.56x speedup.** Average effective cores increased from
2.50/2.51 to 5.69/6.09; twelve available CPUs did not mean twelve continuously
busy CPUs. The experiment retained Clang 22.1.8, Microsoft linker/librarian,
Release optimization, static libraries, no LTO and one concurrent link job.
It does not cover the full LLVM build, instrumented builds, ThinLTO, Rust
compiler builds, or release qualification. Its memory usage is not a safe
memory budget for those larger workloads.

### Existing fast compression profile

The unmodified Rust installer from source
`7db17d9b5bbe6b16be2dc86b4bfae81d6e1ae238` was built locally through the native
`x.ps1 build --stage 1 rust-installer` entry point, outside timing. It repackaged
the retained compiler payload from the failed Arm64 PGO pilot. That compiler
is used **only as packaging data**, not as a qualified compiler.

All four packaging samples used four CPUs. Order was balanced, fast, fast,
balanced. Source data, file timestamp, installer binary and XZ format were
identical. Every decompressed tar stream matched the original SHA-256:
`756c02099c73d4e292869ef295187d42cbeb99dbf2e051dc4682d5dec592dea2`.

| Compression profile | Samples (s) | Median (s) | Archive bytes |
|---|---|---:|---:|
| balanced | 56.75, 55.51 | 56.13 | 88,331,380 |
| fast | 13.97, 13.45 | 13.71 | 107,370,076 |

**75.6% less packaging time, 21.6% more archive bytes.** This saved 42.42s
per compiler archive in the local probe. The extra 19.04 MB consumes about
1.9s at 10 MB/s or 19.0s at 1 MB/s for a single transfer, before overhead.
Repeated distribution/download costs must also be considered.

`dist.compression-profile = "fast"` is an existing bootstrap option; it uses
XZ preset 1 instead of balanced's preset 6. Both use six compression threads
internally. Therefore, simply raising `build.jobs` does not make this compressor
use all twenty CPUs. No installer code changes are needed.

## Prioritized smallest-change options

| Priority | Change | Evidence and constraints |
|---|---|---|
| 1 | Raise build jobs **and** the inherited CPU allowance together | Largest demonstrated local compile gain. Start with a RAM-aware limit and observe peak commit/pagefile pressure. Raising jobs alone cannot bypass the four-CPU Job Object. Do not change controlled timing jobs in flight. |
| 2 | Set `dist.compression-profile = "fast"` | One existing config setting, identical unpacked payload in the experiment. Larger artifacts; test docs/dev packages and total upload cost before adopting broadly. |
| 3 | Reuse verified source/download caches outside the cold-production clock | Targets the measured setup delays. Keep object/profile/Cargo-target caches isolated when measuring cold builds; report cold and warm setup separately. Not tested here. |
| 4 | Try `llvm.link-jobs = 2` where memory permits | Current value 1 serializes independent LLVM links, not all compilation. Likely useful near link-heavy tails; not measured, and ThinLTO links may consume much more RAM. Keep Microsoft linking tools for the retained-MSVC option. |
| 5 | Investigate PGO training's fixed concurrency | `opt-dist/src/training.rs` explicitly passes `--jobs 4` and `--frontend-threads 1`. Environment or bootstrap jobs changes alone do not override those explicit arguments. No training/compiler source edits made. |

Do not remove docs, MSI, Arm64EC or qualification tests to claim a faster
equivalent release. Changing compiler codegen units, LTO, or linker selection
can alter the produced compiler and downstream performance, so those are not
the first production-throughput knobs.

No whole-release saving is claimed from either component probe. Packaging's
15-24% scope includes work unaffected by the compression knob. Compile-heavy
steps have different parallelism and memory behavior from the selected LLVM
graph. A full release A/B on otherwise comparable **permitted** machines is
needed to establish total savings; neither custom timing runner may be used
for these experiments under the current instruction.

Evidence: `llvm-comparison.json`, `compression-comparison.json`, and the two
`*-baseline-phases.json` summaries in this directory. Raw local logs remain
under `D:\copilot\rt-llvm-1` and `D:\copilot\rt-pack-1`.
