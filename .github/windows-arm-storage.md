# Windows Arm release build storage

The release-binaries workflow can use otherwise unused NVMe storage on
GitHub-hosted Windows Arm64 runners. It detects the runner OS and architecture,
not a particular runner label. Linux, macOS, x64 Windows and self-hosted runners
are unchanged.

Before checkout, the workflow requires all of the following:

- No partition, volume or filesystem drive has the letter `D`.
- Exactly one online, writable NVMe disk is reported as completely raw, with no
  partitions and at least 50 GiB capacity. It must not be a boot or system disk.
- The initial workspace is an empty directory, not a link.

If these conditions are not met, it logs the reason and leaves storage and
build paths unchanged. It never clears a disk, resizes an existing partition or
reformats an existing volume. Provisioning errors fail the job rather than
silently falling back after a partial change.

An eligible disk is initialized as GPT and formatted as a ReFS Dev Drive using
Windows defaults. The workflow does not disable antivirus, add exclusions or
override Dev Drive filter/trust policy.

The empty workspace is moved to `D:\workspace` and its original path becomes a
junction. Checkout, Cargo build outputs, artifact collection and post-job steps
therefore keep the runner-provided logical workspace path. Cargo home is also
moved behind a junction, preserving its configuration and installed binaries.
`CARGO_HOME` explicitly names the new physical path, `D:\cargo-home`, so cache
archives do not traverse the workspace junction's parents to find Cargo data.
The Rust toolchain remains in its original location. `TEMP` and `TMP` point to
`D:\build-temp` for subsequent steps.

The running Actions agent, `GITHUB_WORKSPACE`, `RUNNER_TEMP` and the hosted tool
cache are not reconfigured. In particular, changing a running agent's work
directory is unnecessary and could break its control files and cleanup.

Raw NVMe availability is an observed runner property, not a GitHub storage
guarantee. See [GitHub-hosted runner specifications][runners] and
[Microsoft's Dev Drive documentation][dev-drive].

[runners]: https://docs.github.com/en/actions/reference/runners/github-hosted-runners
[dev-drive]: https://learn.microsoft.com/en-us/windows/dev-drive/
