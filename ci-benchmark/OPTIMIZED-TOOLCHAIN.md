# Optimized Windows Arm64 Rust for CI

This opt-in compiler package makes the validated Rust **1.94.1** PGO/ThinLTO build
reusable without rebuilding Rust, replacing the official toolchain, or changing
IronRDP product code. It is an **experimental, pinned compiler**, not an official
Rust release or a general production-support commitment.

## GitHub Actions

On `windows-11-arm`, after checking out this fork:

```yaml
- uses: ./.github/actions/setup-optimized-rust
- run: cargo xtask check tests --no-run -v
  shell: pwsh
- run: cargo xtask check tests -v
  shell: pwsh
```

For another repository, use the exact action revision exercised by the full
validation run:

```yaml
- uses: marcpems/IronRDP-ci-benchmark/.github/actions/setup-optimized-rust@c18826dab98f510a418493daa47642d7aac1f181
- run: cargo build --locked
  shell: pwsh
```

The action downloads only from this fork's fixed
`arm64-compiler-ab-v2` release. It does not push, open PRs, or change upstream CI.

The action installs official support components and sets **`RUSTC`**, while
pinning **`RUSTUP_TOOLCHAIN`** to the matching official release. It does not change
the machine's default toolchain. Cargo and rustdoc remain official; official
Clippy and rustfmt are also installed to preserve the repository's required components. This package
does **not** claim to optimize rustdoc, Clippy, rustfmt, or the entire CI job.
The optimized package includes rustc and its bundled linker. Only native Windows
Arm64 and `wasm32-unknown-unknown` target libraries are provided and verified.
Build-script C/C++ compilers and native SDK dependencies still need normal setup.

Use `with: { activate: "false" }` for side-by-side comparisons. Outputs are
`rustc`, `installation`, and `id`; set `RUSTC` only on the steps to optimize.
To restore stock compilation in subsequent steps, set `RUSTC` to
`rustup which --toolchain 1.94.1-aarch64-pc-windows-msvc rustc`.

## Verification and reproducibility

The checked-in [manifest](../.github/actions/setup-optimized-rust/manifest.json)
pins SHA-256 values for **both** the archive and provenance JSON. Installation
validates archive paths, every compiler file, identity, meaningful LLVM training
coverage, byte-identical official target libraries, and native/WASM compilation.
Installation is staged before publication; existing installations are verified
again, never silently overwritten. No authentication token is required for the
public downloads. Updating a compiler requires an explicit manifest change.

For local Windows Arm64 use, install the official 1.94.1 toolchain and WASM target,
then run with Python 3.11 or newer:

```powershell
python .github\scripts\install_optimized_rust.py `
  --manifest .github\actions\setup-optimized-rust\manifest.json `
  --destination D:\tools\optimized-rust-1.94.1
$env:RUSTUP_TOOLCHAIN = '1.94.1-aarch64-pc-windows-msvc'
$env:RUSTC = 'D:\tools\optimized-rust-1.94.1\optimized\bin\rustc.exe'
```

The [original-CI validation workflow](../.github/workflows/native-optimized-validation.yml)
keeps the upstream `ci.yml` unchanged. Its fixed-source replay uses the original
five native compilation commands, common-package control and WASM build, with
the original Cargo profiles and package-specific overrides. It measures offline
CPU/wall time with separate cold outputs per compiler/round, and runs the original
native tests outside those timers. The [protocol](native-ab-protocol.json) fixes
the sampling and analysis before measurements. This is a cold-build comparison,
not a claim about warm dependency-cache hits or every upstream CI job.

The benchmark alone disables optional MSVC telemetry on its disposable runners
using the [documented VSCEIP policy](https://learn.microsoft.com/en-us/visualstudio/ide/visual-studio-experience-improvement-program#registry-settings).
A pilot identified `vctip.exe` outliving a completed native link even with that
policy. The meter therefore retains only the exact SDK telemetry executables
reported by `vswhere` in a shared, owned Job Object across each command block.
Per-command counter deltas include **all** CPU consumed during the build window,
including those helpers; nothing is subtracted. Their idle/post-build lifetime
is not compilation time. Other persistent descendants remain an error. The job
is closed after the block and its untimed correctness checks.
Both variants also set `MSBUILDDISABLENODEREUSE=1` so native build-script workers
exit rather than persist across independently timed compiler blocks.
The reusable installer does not change telemetry policies on consumers' machines.

## Experimental x64 extension

On `windows-2025`, the action at
`d0c9c1a23361750637fa9314e377e6dee2ffe053` automatically selects the native x64
manifest instead of Arm64. It preserves official support tools and remains opt-in:

```yaml
- uses: marcpems/IronRDP-ci-benchmark/.github/actions/setup-optimized-rust@d0c9c1a23361750637fa9314e377e6dee2ffe053
```

Both x64 compiler construction and the full 20-job evaluation passed.
**The original native compilation sequence saves 23.7% wall time
(95% interval 21.7-25.3%) and 24.6% CPU (22.5-26.1%)** against official Rust.
Against the matched effective-PGO control, added ThinLTO saves **7.6% wall /
7.3% CPU**. These are compilation-only results, not full Rust distribution
qualification or a claim about the whole CI job. All 80 untimed original native
correctness commands passed. The x64 release uses freshly trained x64 profiles shared
between the PGO control and ThinLTO treatment, not Arm64 profiles.
See [scope and build evidence](WINDOWS-X64-OPTIMIZATION.md).

## Validated result

[Full original-CI run 36871453828](https://github.com/marcpems/IronRDP-ci-benchmark/actions/runs/36871453828)
completed on five Windows and five Linux Arm64 VMs. On Windows, the original
five-command native compilation sequence fell from **709.64 to 595.99 seconds**:
**16.0% less wall time (95% interval 15.4-16.7%)** and **16.0% less CPU time
(15.4-16.6%)**. All original native correctness commands passed for both compilers.
This is below the earlier 18-19% graphics-only saving, not a claim that the full
GitHub Actions job becomes 18% faster. See the
[combined report](COMBINED-REPORT.md#original-native-ci-validation-16-less-wall-and-cpu-time)
for the breakdown, comparison limits and archived evidence.
