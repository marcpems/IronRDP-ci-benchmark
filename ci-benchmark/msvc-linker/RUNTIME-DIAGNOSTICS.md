# Microsoft-linker experiment: profiling-runtime blocker

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
workloads or using the incomplete profiles. The x64 profile job is still
running at this update.

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
zero-counter diagnostic. The original instrumented-rustc access violation
has not yet been reproduced under a debugger or demonstrated fixed.
The names bug is confirmed; its relationship to that crash remains unproven.

[Rust issue #150123](https://github.com/rust-lang/rust/issues/150123)
reports a similar Arm64 malformed-profile symptom for coverage. That is
supporting context, not proof that the two failures have the same cause.

## Next required evidence

Preserve an instrumented compiler and capture its failing invocation/stack;
verify the names-boundary fix and any separate record-layout fix against that
compiler. Only after all training workloads and strict profile-integrity
checks succeed should final PGO compilers and IronRDP benchmarks run.
The original Rust review branch and pinned experimental Rust source have not
been changed by these local diagnostics.
