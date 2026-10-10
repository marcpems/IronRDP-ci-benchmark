# Microsoft-linker experiment: profiling-runtime investigation

This is an interim feasibility result, **not an IronRDP performance result**.

## Hosted build outcome

[Run 37965170591](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/37965170591)
successfully constructed and packaged the unoptimized Arm64 and x64 baseline
compilers. The Arm64 instrumented compiler also built and passed the native
linker/compiler audits, but four upstream training workloads failed with
`0xc0000005` (`STATUS_ACCESS_VIOLATION`): cargo-0.87.1,
token-stream-stress, tuple-stress, and diesel-2.2.10.

Some failures occurred during Cargo's compiler target-information query, not
while compiling workload source. The collector wrapper propagates the child
compiler's exit status. These failures do not justify dropping the affected
workloads or using the incomplete profiles.

The x64 frontend-profile job subsequently **succeeded**: all nine upstream
training workloads completed, the merged profile hash verified, and the
native-tool audit passed. Coverage included 10,104 active `rustc_middle`
functions and 1,633 active `rustc_mir_transform` functions.

| x64 frontend-profile stage | Wall time (minutes) |
|---|---:|
| Bootstrap/compiler construction | 74.02 |
| Collector binaries | 2.64 |
| Training | 23.07 |
| Profile merge | 1.45 |

These are compiler-construction/training times, not IronRDP compilation
times. GitHub skipped LLVM-profile and final-compiler jobs because the
original workflow gates both architectures on the complete initial matrix.
The x64 frontend profile is valid, but LLVM PGO and the final Rust-ThinLTO
compiler have not yet been qualified.

## Independent local reproduction

The successful Arm64 baseline archive was downloaded, SHA-256 checked against
its metadata, and extracted without modification. It identifies itself as:

* Rust `1.101.0-nightly`, commit `5b615ab3eb2cd5a26afc6025b5863180ffdc20d7`.
* LLVM `23.1.3`; its own bundled llvm-profdata was used.

Local probes used Microsoft link.exe from MSVC `14.44.35207`, SDK
`10.0.26100.0`, and two small Rust programs: a main executable with an rlib,
and an executable with a Rust dylib. Both the library and executable were
built with `-Cprofile-generate`, `-O`, and 16 codegen units. Each executable
ran 40 times with four concurrent processes, writing unique
`default_%m_%p.profraw` files.

| Diagnostic configuration | rlib-linked executions | dylib-linked executions | Raw-profile merge |
|---|---:|---:|---|
| Original runtime | 40/40 succeeded | 40/40 succeeded | Failed for both: symbol name is empty |
| `/OPT:NOICF` | 40/40 succeeded | 40/40 succeeded | Same failure |
| `/OPT:NOREF /OPT:NOICF` | 0/40 succeeded | 40/40 succeeded | Failed for both |
| One codegen unit | 40/40 succeeded | 40/40 succeeded | Same empty-name failure |
| Candidate names-boundary fix, diagnostic runtime object | 40/40 succeeded | 40/40 succeeded | Succeeded for both |

These are correctness probes on a different local MSVC version, not standard
runner speed measurements. None of these compiler packages or profiles will
be used in the IronRDP comparison.

## Confirmed name-section padding problem

The Microsoft-linked executable's `.lprfn` section starts with four zero
bytes before the first encoded function-name block. The runtime defines a
one-byte `NamesStart` sentinel and returns `&NamesStart + 1`, leaving three
padding bytes at the start of the serialized name stream.

As a diagnostic only, shifting those three bytes out of the names region in
one copied raw profile changed llvm-profdata from failure to success.
**No training profiles were repaired or accepted this way.**

A source-level candidate changes `__llvm_profile_begin_names` to skip leading
zero padding, bounded by `NamesEnd`. The exact runtime source was obtained
from LLVM revision `aab11ee0ea5ea9a1d462ad0bc1fae9d9bb643019` in an isolated
checkout. Its modified platform object was rebuilt locally with cl.exe `/MD`
and substituted into a **separate diagnostic copy** of profiler_builtins.
Both ordinary rlib and dylib probes then produced mergeable profiles.

The isolated candidate changes only this function:

```c
const char *__llvm_profile_begin_names(void) {
  const char *Begin = &NamesStart + 1;
  /* MSVC's ARM64 linker can pad the one-byte start sentinel to four bytes. */
  while (Begin < &NamesEnd && *Begin == '\0')
    ++Begin;
  return Begin;
}
```

This experiment does not qualify the candidate fix for production. In
particular, the `/OPT:NOREF` probe still failed after the names fix, with a
zero-counter diagnostic. At this stage the original instrumented-rustc access
violation had not yet been reproduced under a debugger. The later captured
compiler investigation below identifies a separate online-merge offset bug.

[Rust issue #150123](https://github.com/rust-lang/rust/issues/150123)
reports a similar Arm64 malformed-profile symptom for coverage. That is
supporting context, not proof that the two failures have the same cause.

## Follow-up investigation

The next investigation preserved an instrumented compiler, captured its
failing invocation/stack, and checked both fixes against that compiler.
Final PGO compilers and IronRDP benchmarks remain gated on successful training
and strict profile-integrity checks.
The original Rust review branch and pinned experimental Rust source have not
been changed by these local diagnostics.

### Instrumented-compiler capture attempt

[Diagnostic run 37975403778](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/37975403778)
reproduced training failure, but the new diagnostic archiver then exhausted
memory while recursively enumerating the stage2 sysroot. It had not applied
the source-junction exclusions used by the existing successful baseline
packager. The uploaded ZIP is empty and is **not** a usable compiler artifact.

The diagnostic branch now reuses the existing sysroot-copy exclusions,
preserves the compiler before training, and renames the archive from a partial
file only after successful completion. A regression test constructs an actual
Windows directory junction back into the source tree and confirms that the
archive contains the compiler and helper binaries without traversing that
junction. Only the single Arm64 diagnostic job is being repeated; the valid
x64 profile and both baseline artifacts remain unchanged.

### Captured compiler: online-merge crash reproduced

[Run 37993684565](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/37993684565)
successfully preserved the instrumented compiler before reproducing the
training failure. Its diagnostic ZIP was downloaded and verified against
SHA-256 `524dd89ccaed9317ac09509536082eabc37fc28db90ba14ae4275fdee4f103ee`.

Locally, the captured compiler completed 16 concurrent `-vV` invocations with
unique raw-profile paths; its captured collector wrapper also completed 12.
When forced to reuse an online-merge file (`LLVM_PROFILE_FILE=default_%m.profraw`),
the first invocation succeeded and the next five all exited with
`0xc0000005`. Microsoft CDB located the exception in
`lprofMergeValueProfData`, called by `__llvm_profile_merge_from_buffer`,
`openFileForMerging`, and `__llvm_profile_write_file` during process exit.
Windows process-ID reuse makes an equivalent collision possible with the
training pattern `%m_%p`; actual PID reuse in the hosted failure was not logged.

The profile writer emits `PaddingBytesAfterBitmapBytes`, but the online-merge
reader omitted it when locating the names and subsequent value-profile data.
This causes the value merger to interpret bytes at the wrong offset. A second
candidate source fix adds that header field to `SrcNameStart`.

With **both** source fixes rebuilt into a separate diagnostic runtime, the
small rlib and dylib programs each completed 40 concurrent executions sharing
their online-merge files, and llvm-profdata merged both successfully. The rlib
profile reports exactly 40 main calls and 4,000 loop iterations, matching
40 executions of a 100-iteration loop. An attempted counter-sentinel alignment
change did not fix the crash and was reverted.

The isolated diagnostic branch applies the exact two-file runtime patch
before compiler construction, records the modified source hashes, preserves
the compiler, and requires eight repeated online-merge version queries plus
an offline merge before running all original training workloads. This is a
feasibility check, not permission to mix patched and unpatched toolchains
in the final benchmark. The original review branch is unchanged.

### Real Arm64 compiler and frontend training now pass

[Run 38001265175](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38001265175)
completed successfully on the standard native Arm64 runner. The real
instrumented compiler was rebuilt from source with both fixes, passed all
eight repeated online-merge version queries and the offline smoke merge, and
completed all nine original frontend training workloads. Native tool audits
still require clang-cl, Microsoft link.exe and lib.exe.

The downloaded frontend profile was checked against its recorded SHA-256:
`98c6505634d4a8584bbeb0d9dfa1d9cbfe58f44aa4fb5ebd2e9c92486fcc7b80`.
Coverage includes 26,438 active `rustc_middle` functions out of 84,942 and
3,631 active `rustc_mir_transform` functions out of 9,285.

| Component | Wall seconds |
|---|---:|
| Compiler/bootstrap build command | 3,000.05 |
| Collector helper construction | 157.85 |
| Frontend workload training | 1,636.57 |
| Training-profile merge | 170.23 |
| Separate runtime smoke merge | 1.27 |

These are compiler-construction and training timings, **not offline IronRDP
measurements** and not the complete job duration.

The exact modified runtime sources are recorded in the artifact metadata:

| File | SHA-256 |
|---|---|
| `InstrProfilingMerge.c` | `b4eb470286b8006e5eac7c7301efa6fea4f7890d3a25280a058324b4a860250c` |
| `InstrProfilingPlatformWindows.c` | `4b964e3ed045710e1de050e78c8ce8f4c68cb2b0c2ba094c226171eb1fcd5726` |

The next diagnostic phase reuses this Arm64 profile and the earlier successful
x64 profile in independent LLVM/backend jobs, preserving their separate
parent metadata hashes and runtime provenance. The x64 profile predates the
runtime patch; it is not silently treated as a same-source matched sample.
Clang 22 supplies a separate profiling runtime for LLVM instrumentation. A
small instrumented C program, linked explicitly with Microsoft link.exe,
must pass eight repeated online merges and an offline merge with the matching
Clang llvm-profdata before the full backend build starts. This guards against
assuming that repairing Rust's in-tree runtime also repaired Clang's runtime.

LLVM/backend training, final optimized compiler construction and the matched
IronRDP comparison remain outstanding. The runtime fixes have only been
qualified for these tested configurations, not all profiling modes.

### Backend feasibility: x64 succeeds; Clang's Arm64 runtime also needs repair

[Run 38009549235](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38009549235)
completed the x64 LLVM/backend build and all seven backend training workloads.
The downloaded LLVM profile's SHA-256 is
`e5a40cad19e9a43fc34c7a1ddfbb5e3ea12f340231814649ae99f74d8bfd0b8d`.
Coverage includes 178 active `X86TargetLowering` functions out of 273 and
645 active `InstCombine` functions out of 979.

| x64 backend component | Wall seconds |
|---|---:|
| Compiler/bootstrap build command | 5,712.31 |
| Collector helper construction | 175.02 |
| Backend workload training | 1,060.75 |
| Training-profile merge | 194.40 |

The independent Arm64 job stopped before compiler construction: the new small
Clang-runtime probe crashed with `0xc0000005` on its second shared-profile
write. Thus the successful Rust frontend runtime repair does not by itself
make the separate Clang 22 runtime safe.

Locally, the same Clang 22.1.8 Arm64 package reproduced the second-write crash.
The two layout corrections were applied to its exact runtime source,
LLVM `ca7933e47d3a3451d81e72ac174dcb5aa28b59d1`. The entire profiling library
was rebuilt through compiler-rt's CMake `profile` target using the unchanged
clang-cl executable and explicitly pinned Microsoft link.exe/lib.exe.
No library-member surgery or repaired profile bytes were used.

The rebuilt runtime passed all eight shared-profile executions and offline
merging. The merged result contains exactly eight main invocations, 800 loop
iterations, 800 calls to `bump`, and 800 recorded indirect calls to `bump`.
The harness now checks these exact counts, records original/rebuilt library
hashes, source revision and modified source hashes, and audits its CMake tools.
Only the Arm64 backend job is being repeated; the successful x64 evidence is
retained. Hosted backend training with this rebuilt runtime is still pending.

### Rebuilt Clang runtime passes hosted probes; bootstrap still crashes

[Run 38018027911](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/38018027911)
rebuilt the Arm64 Clang runtime with the audited Microsoft tools, then passed
all eight shared-profile executions, offline merging and exact counter/target
checks. Runtime CMake configuration took 61.71 seconds; its build took 1.94.

The subsequent compiler bootstrap failed after approximately 49 minutes:
stage-1 rustc exited with `0xc0000005` while compiling `yoke` for stage 2.
Backend workload training never started. This is a new failure location, not
evidence that all profiling-runtime defects are resolved; no root cause is
claimed without capturing the failing compiler.

The next Arm64 attempt preserves the available stage-1 sysroot on bootstrap
failure, without requiring collector binaries that have not yet been built.
It remains explicitly diagnostic and cannot be accepted as a final compiler.
Independent x64 jobs now construct a fresh baseline and both final optimized
variants from the same in-tree runtime source patch. Both optimized variants
consume the same verified frontend/backend profiles from run 38009549235.

### Captured stage 1 reveals a runtime search-path bug

Run 38021536352 successfully produced all three final x64 compiler packages.
Their archive hashes were verified after download, and their recorded in-tree
runtime sources match. An independent x64 IronRDP pilot is now running.

Arm64 failed again, this time while compiling `cfg-if`. Its captured stage-1
archive is SHA-256
`6aa054505dd93bfceced99d1ca6432cde398007591dc09b7ecef1af36801d3e2`.
A Windows minidump resolves the crash to `lprofMergeValueProfData` during
process-exit online merging. Locally, three unique-profile version queries
succeeded; the first shared-profile query succeeded and the next two crashed.

Crucially, disassembly of the captured compiler's merge routine reads
`NumBitmapBytes` at header offset `0x38` but never adds the padding field at
`0x40`: **the compiler contains the unpatched runtime**, despite the successful
standalone check of the rebuilt library.

The bootstrap log records a malformed native library search path:
`C:aIronRDP-ci-benchmarkIronRDP-ci-benchmarkharnesstoolsclanglibclang22libwindows`.
Bootstrap emits an unquoted Windows path in `LLVM_LINKER_FLAGS`; the receiving
build script parses it with POSIX shlex, consuming its backslashes. This
allows runtime resolution to fall back to another library instead of the
explicitly rebuilt one. The precise fallback library was not logged.

The diagnostic bootstrap patch normalizes separators and quotes the complete
`-L` argument. The runtime-selection audit now uses full Microsoft linker
verbosity and requires the merge and Windows-platform objects to be loaded
from the expected library, not merely mentioned in a search path. This audit
was checked against an actual local link log. The prior x64 standalone runtime
hash likewise does not prove which library its instrumented compiler loaded;
its successful profiles and final compiler comparisons remain useful, but
that provenance limitation must not be concealed.
