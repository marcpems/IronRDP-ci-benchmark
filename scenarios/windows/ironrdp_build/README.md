# IronRDP build workload (Windows)

Times a **fresh, offline native build of the IronRDP workspace** using official
Rust 1.94.1 and source revision `0c5419eca6bf53563056ed252f537bca67862705`.
The source revision is the one used in the earlier IronRDP compiler experiments,
but this scenario is a single-toolchain build benchmark, not a PGO comparison.

```text
cargo build --workspace --frozen --target <native-msvc-host> --jobs <jobs> --message-format=json --timings
```

Supports native Windows x64 and ARM64. It builds the upstream default workspace
features, including dependencies, in the dev profile with debug information and
incremental compilation disabled. It does not build excluded workspace members,
all optional features, test executables, or WebAssembly, and does not execute
IronRDP clients or connect to an RDP server. No macOS variant is included.

## HOBL execution

On an already provisioned, dedicated HOBL DUT:

```powershell
.\hobl.cmd -p .\params.ini -s ironrdp_build ironrdp_build:loops=1 ironrdp_build:jobs=0
```

`loops` defaults to 1; each loop removes only the previous Cargo target directory.
`jobs=0` uses all processors available to the process. A positive value fixes
Cargo parallelism; keep it identical when comparing machines or toolchains.
Each build has a 40-minute timeout. Increase loops for repeated or rundown
measurements; the workload is otherwise unchanged.
The elapsed-time limit is also checked after process exit. A machine pause or
suspend cannot turn an over-budget build into a successful timing sample.

## Preparation and isolation

Prep downloads a checksum-pinned Rustup bootstrap, native CMake 4.1.1 and Ninja
1.13.1 archives, installs the pinned native Rust toolchain into scenario-private
`rustup-home`, fetches the pinned IronRDP source and its locked dependencies,
and records tool/lockfile hashes. These private installations do not change a
shared Rust/CMake/Ninja installation, Python environment, or persistent PATH.
The standalone Rustup executable is used without running `rustup-init`.

Git and native Visual C++ tools with a Windows SDK are system prerequisites;
x64 also requires NASM, and ARM64 requires LLVM's `clang-cl` for the AWS-LC
cryptography dependency. Prep discovers installed tools and uses `vswhere` to
locate Visual Studio. On dedicated DUTs it installs missing prerequisites using
winget (Visual Studio 2022 Build Tools on x64, Community on ARM64).
It does not disable services or alter power/security settings.
Native dependencies use the Ninja CMake generator and a native Visual Studio
developer environment. Crates retain their own compiler selection (including
AWS-LC's required `clang-cl` on ARM64); no global `CC`/`CXX` override is forced.
This avoids the pinned CMake Rust crate's x64-host default on
ARM64 and avoids depending on CMake support for a particular Visual Studio
generator version.
The CMake/Ninja binaries match the native architecture; an emulated CMake from
the existing PATH cannot misidentify an ARM64 machine as AMD64.

Source, Cargo downloads, and toolchains live in
`ironrdp_build_resources\work`. They survive teardown. Runtime checks reject
changed source/lockfiles, changed tool executables, wrong architecture, missing
prep, and overlapping use of the same working directory. Never manually edit
this checkout to change the benchmark; update `ironrdp_build.json` and bump
`prep_version` when changing the workload or toolchain.

## Safe standalone validation

PowerShell 7.2 or newer is required. These commands exercise the actual scripts
without starting HOBL, SimpleRemote, DAQ, or any system-preparation scenario.
`-SkipSystemInstall` prevents winget/system installation; it still downloads
scenario-private tools/source/dependencies. Missing system prerequisites fail
with an explicit error rather than modifying the machine.

From the repository root:

```powershell
$scripts = Join-Path $PWD 'scenarios\windows\ironrdp_build\ironrdp_build_resources'
$work = Join-Path $env:TEMP 'hobl-ironrdp-validation\work'
$data = Join-Path $env:TEMP 'hobl-ironrdp-validation\data'
pwsh -NoProfile -File "$scripts\ironrdp_build_prep.ps1" -workRoot $work -logFile "$data\prep.log" -SkipSystemInstall
# Run each script in its own PowerShell process; check its exit code.
pwsh -NoProfile -File "$scripts\ironrdp_build_run.ps1" -workRoot $work -logFile "$data\run.log" -jobs 4
pwsh -NoProfile -File "$scripts\ironrdp_build_run.ps1" -workRoot $work -logFile "$data\run.log" -jobs 4
pwsh -NoProfile -File "$scripts\ironrdp_build_teardown.ps1" -workRoot $work -logFile "$data\teardown.log"
```

For cancellation, invoke `ironrdp_build_kill.ps1` in another process with the
same `-workRoot`. It checks the recorded PID, process start time and executable
before terminating that scenario's process tree. It never kills all PowerShell,
Cargo, Rust, or compiler processes by name. Cleanup failures are logged.

Regression checks (host only, no lab services):

```powershell
python -B -m unittest discover -s scenarios\windows\ironrdp_build\tests -p test_ironrdp_build.py -v
pwsh -NoProfile -File scenarios\windows\ironrdp_build\tests\test_ironrdp_scripts.ps1
```

## Timing and results

`build_time` and `scenario_runtime` are identical **wall-clock seconds from
starting Cargo until it exits**. They exclude tool/source/dependency downloads,
Visual Studio environment setup, target cleanup, provenance validation, and
result processing. They include compilation/linking and Cargo's output.
Filesystem/OS caches are not flushed: this is a fresh **Cargo target**, not a
machine-cold or cold-disk benchmark.

The results directory defaults to `<script-drive>\hobl_data`, or the parent of
`-logFile` for isolated validation. It contains:

- `ironrdp_build_results.csv`: latest successful loop, headerless `key,value`
  metrics (`scenario_runtime`, `build_time`, `architecture`, `jobs`).
- `ironrdp_build_results.trace`: one elapsed-time/build-time row per successful
  loop, for HOBL trace processing.
- Unique `ironrdp_build_<iteration>.json`, stdout/stderr logs and Cargo timing
  HTML for every successful loop. Failed command logs are retained.

The previous summary CSV is invalidated when a run starts; failed builds do not
publish success metrics. Results require Cargo exit code zero, its successful
completion event, newly compiled artifacts, an unchanged source tree, and a
Cargo timing report. These are **build correctness** checks, not execution of
IronRDP's runtime test suite.

The optional `ironrdp-build-validation.yml` workflow validates the same scripts
on disposable native x64/ARM64 runners. It runs on pushes to
`perf/ironrdp-build` and can be dispatched manually once registered. Script validation does not substitute
for an actual HOBL controller/DUT measurement or physical lab/DAQ qualification.
