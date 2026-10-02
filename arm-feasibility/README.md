# Windows Arm64 full-distribution feasibility

This fork-only experiment measures a fresh Rust 1.94.1 distribution on standard
`windows-11-arm` runners. It does not modify or publish upstream releases.

Two independent variants build the exact same source with full tools, documentation,
profiling runtime, native MSVC SDK/DIA defaults, and both native and Arm64EC standard
libraries. The baseline uses the upstream Arm64 distribution recipe. The treatment
adds fresh rustc and LLVM PGO, Rust ThinLTO, LLVM ThinLTO, and native LLD for rustc.
It also runs opt-dist's extracted-distribution tests. Neither trims LLVM tools.

The original matrix launched both variants. The workflow now selects treatment
only. The baseline completed in run 36991902911 in **141.82 minutes**.
The corrected treatment in run 36994829038 exhausted its **350-minute safety
budget** during Stage 2's instrumented LLVM build, before LLVM training and final
distribution/tests. Both runs are terminal and must not be duplicated merely to
update documentation. See [measured outcomes](FEASIBILITY.md).
An early treatment helper build exposed that `opt-dist` itself must be built with
explicit native `--host`/`--target`; otherwise the full distribution target list
also tries to build the helper for Arm64EC using stage0 without Arm64EC std.
This helper-only correction does not remove Arm64EC from final distribution.
ThinLTO must explicitly retain `llvm.link-shared=false` on MSVC, since bootstrap
otherwise defaults ThinLTO to unsupported shared LLVM. The treatment uses the
bundled native LLVM librarian for bitcode archives, as well as native LLD.

`patches/` contains only the two candidate upstream fixes: static LLVM relinking
before training, and read-only clang runtime discovery during bootstrap dry-run.
Runner setup, resource monitoring, lockfile migration, and experiment settings
are separate in `run.py` and the workflow.

The harness deliberately omits upstream S3/sccache credentials, publication,
installed-tool deletion, and rustup self-uninstallation. Builds receive an explicit
environment allowlist because opt-dist prints its entire environment. Source,
tool downloads, SDK selection, configuration, raw build logs, resource samples,
stage elapsed times, profiles, and final component hashes are recorded.

Each job has a 360-minute hosted/workflow limit. The owned build process tree is
stopped at 350 minutes from the first step, reserving ten minutes for diagnostics;
that safety boundary is not a measurement of failure at exactly 360 minutes.
Setup is included in the job budget but separated from build stage timings.
Preflight diagnostics upload before compilation; resource samples stream to
Actions logs every minute. No cache/profile reuse or job splitting hides costs.

Run `python -m unittest discover -s arm-feasibility -p test_run.py` to check the
configuration and environment safety invariants. Successful compilation is
necessary but insufficient for upstream release qualification: see the final
feasibility report for measured outcomes and remaining gates.
