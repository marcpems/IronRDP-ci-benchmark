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

For another repository, reference
`marcpems/IronRDP-ci-benchmark/.github/actions/setup-optimized-rust` at a reviewed
full commit SHA. The action downloads only from this fork's fixed
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
A pilot identified `vctip.exe` outliving a completed native link. The CPU meter
still rejects persistent descendants; it does not silently drop their CPU.
The reusable installer does not change telemetry policies on consumers' machines.
