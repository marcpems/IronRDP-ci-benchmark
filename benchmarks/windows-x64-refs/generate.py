import copy
import json
import pathlib
import random

import yaml

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_COMMIT = "b9d140003323f3ae3cd22f91be556e58ed43322e"
SEED = 20261022
source = yaml.safe_load((ROOT / ".github" / "workflows" / "release-binaries.yml").read_text())
prepare = (HERE / "Prepare-Storage.ps1").read_text()

rows = []
rng = random.Random(SEED)
for block in range(1, 9):
    variants = ["baseline", "refs"]
    rng.shuffle(variants)
    rows.extend({"block": block, "storage": storage, "target": "x86_64-pc-windows-msvc",
                 "os_arch": "windows-x64", "macos_deployment_target": ""} for storage in variants)

steps = [{
    "name": "Shrink NTFS and prepare ReFS storage",
    "if": "matrix.storage == 'refs'",
    "shell": "pwsh",
    "env": {"STORAGE_RUNNER_ENVIRONMENT": "${{ runner.environment }}"},
    "run": prepare,
}]
for original in source["jobs"]["build"]["steps"]:
    if original["name"] == "Prepare Windows Arm build storage":
        continue
    step = copy.deepcopy(original)
    if step.get("uses") == "actions/checkout@v6":
        step["with"] = {"repository": "Devolutions/IronRDP", "ref": SOURCE_COMMIT}
    if step.get("uses") == "Swatinem/rust-cache@v2.9.1":
        step["with"] = {
            "prefix-key": "x64-refs-rep-${{ github.run_id }}-${{ github.run_attempt }}-${{ matrix.block }}-${{ matrix.storage }}"
        }
    if "run" in step:
        step["run"] = step["run"].replace("${{ needs.select-package.outputs.package }}", "ironrdp-agent")
    if step["name"] == "Build release binary":
        assert step["run"].count("cargo build --locked") == 1
        step["run"] = step["run"].replace("cargo build --locked", "cargo build --timings --locked")
    if step["name"] == "Package binary":
        step["env"]["PACKAGE"] = "ironrdp-agent"
        step["env"]["VERSION"] = "storage-benchmark"
    if step.get("uses") == "actions/upload-artifact@v7":
        step["with"]["name"] = "release-${{ matrix.block }}-${{ matrix.storage }}"
    steps.append(step)

steps.extend([
    {"name": "Verify release and storage", "shell": "pwsh",
     "env": {"STORAGE_VARIANT": "${{ matrix.storage }}"},
     "run": r"""
$ErrorActionPreference = 'Stop'
$sidecars = @(Get-ChildItem release-assets -Filter '*.sha256')
if ($sidecars.Count -ne 1) { throw 'expected one release archive checksum' }
$archive = $sidecars[0].FullName.Substring(0, $sidecars[0].FullName.Length - 7)
if ((Get-FileHash $archive).Hash.ToLowerInvariant() -ne (Get-Content $sidecars[0].FullName).Split(' ')[0]) {
    throw 'archive checksum mismatch'
}
tar -tzf $archive
if ($LASTEXITCODE -ne 0) { throw 'archive verification failed' }
& '.\target\x86_64-pc-windows-msvc\release\ironrdp-agent.exe' --help
if ($LASTEXITCODE -ne 0) { throw 'executable smoke check failed' }
if ($env:STORAGE_VARIANT -eq 'refs') {
    $report = Get-Content "$env:RUNNER_TEMP\x64-storage-preparation.json" -Raw | ConvertFrom-Json
    if ($env:CARGO_HOME -ne 'R:\cargo-home' -or $env:TEMP -ne 'R:\build-temp' -or
        $env:TMP -ne 'R:\build-temp' -or (Get-Volume -DriveLetter R).FileSystem -ne 'ReFS' -or
        (Get-Partition -DriveLetter D).Size -ne $report.before.supported_minimum) {
        throw 'incorrect ReFS storage configuration'
    }
    foreach ($entry in $report.relocations) {
        if ((Get-Item -LiteralPath $entry.Source).Target -ne $entry.Destination -or
            -not (Test-Path -LiteralPath $entry.Backup -PathType Container)) {
            throw 'relocation junction or preserved backup missing'
        }
    }
}
"""},
    {"name": "Record host and storage", "if": "always()", "shell": "pwsh",
     "run": r"""
$ErrorActionPreference = 'Stop'
$sourceCommit = $null
$nasmVersion = $null
if (Test-Path "$env:GITHUB_WORKSPACE\.git") {
    $sourceCommit = git rev-parse HEAD
    if ($LASTEXITCODE -ne 0) { throw 'source revision query failed' }
}
if (Get-Command nasm -ErrorAction SilentlyContinue) {
    $nasmVersion = nasm -v
    if ($LASTEXITCODE -ne 0) { throw 'NASM version query failed' }
}
@{
    source_commit = $sourceCommit
    nasm_version = $nasmVersion
    image = $env:ImageVersion
    cpu = @(Get-CimInstance Win32_Processor | Select-Object Name, NumberOfLogicalProcessors)
    disks = @(Get-Disk | Select-Object Number, BusType, PartitionStyle, Size, IsBoot, IsSystem)
    partitions = @(Get-Partition | Select-Object DiskNumber, PartitionNumber, DriveLetter, Offset, Size, Type)
    volumes = @(Get-Volume | Select-Object DriveLetter, FileSystem, Size, SizeRemaining, AllocationUnitSize)
    paging = @(Get-CimInstance Win32_PageFileUsage | Select-Object Name, AllocatedBaseSize, CurrentUsage, PeakUsage)
    paging_settings = @(Get-CimInstance Win32_PageFileSetting | Select-Object Name, InitialSize, MaximumSize)
    memory = Get-CimInstance Win32_OperatingSystem |
        Select-Object TotalVisibleMemorySize, FreePhysicalMemory, TotalVirtualMemorySize, FreeVirtualMemory
    cargo_home = if ($env:CARGO_HOME) { $env:CARGO_HOME } else { Join-Path $HOME '.cargo' }
    workspace_target = (Get-Item $env:GITHUB_WORKSPACE).Target
    runner_temp_target = (Get-Item $env:RUNNER_TEMP).Target
    temp = $env:TEMP
    tmp = $env:TMP
    defender = Get-MpComputerStatus | Select-Object RealTimeProtectionEnabled, AntivirusEnabled
    power_plan = powercfg /getactivescheme
} | ConvertTo-Json -Depth 8 | Set-Content "$env:RUNNER_TEMP\x64-host.json"
if ($LASTEXITCODE -ne 0) { throw 'power plan query failed' }
"""},
    {"name": "Upload measurements", "if": "always()", "uses": "actions/upload-artifact@v7",
     "with": {"name": "measurements-${{ matrix.block }}-${{ matrix.storage }}",
              "path": "${{ runner.temp }}/x64-host.json\n${{ runner.temp }}/x64-storage-preparation.json\n"
                      "${{ github.workspace }}/target/cargo-timings/cargo-timing.html",
              "if-no-files-found": "error", "retention-days": 30}},
])

workflow = {
    "name": "Windows x64 NTFS versus resized ReFS",
    "on": {"push": {"branches": ["perf/windows-x64-refs-replication"]}, "workflow_dispatch": {}},
    "permissions": {"contents": "read"},
    "env": source["env"],
    "jobs": {"build": {
        "name": "${{ matrix.block }} / ${{ matrix.storage }}",
        "runs-on": "windows-2022", "timeout-minutes": 45,
        "strategy": {"fail-fast": False, "max-parallel": 8, "matrix": {"include": rows}},
        "steps": steps,
    }},
}


def represent_string(dumper, value):
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|" if "\n" in value else None)


yaml.SafeDumper.add_representer(str, represent_string)
(ROOT / ".github" / "workflows" / "windows-x64-refs-replication.yml").write_text(
    yaml.safe_dump(workflow, sort_keys=False, width=120), encoding="utf-8"
)
(HERE / "plan.json").write_text(json.dumps({
    "source_commit": SOURCE_COMMIT, "runner": "windows-2022", "package": "ironrdp-agent",
    "blocks": 8, "variants": ["baseline", "refs"], "max_parallel": 8, "seed": SEED,
    "primary": "Mean completed-build-job seconds, including storage setup and cache persistence; excluding queue time.",
    "secondary": ["Median job seconds", "Cargo seconds", "Step durations",
                  "Results by CPU model, storage bus and runner image"],
    "analysis": "10000 nominal-block bootstrap resamples; blocks do not pair physical hosts.",
    "sampling": "Fixed 16 jobs; no performance-dependent top-ups or hardware-dependent exclusion.",
    "scope": "Combined ReFS/workspace/Cargo/temp relocation versus stock NTFS, not filesystem-only attribution.",
    "cache": "Cold keys isolated by run ID, attempt, block and variant; verify API persistence.",
    "unchanged": ["NASM installation", "Source revision", "Release flags except common --timings",
                  "Pagefile settings", "Security settings"],
    "limitations": ["Ordinary ReFS, not Dev Drive", "Heterogeneous CPU and disk hardware",
                    "Cold agent builds only; viewer covered by separate correctness checks",
                    "Literal NTFS minimum restricts pagefile growth on hosts paging to D"],
    "matrix": rows,
}, indent=2) + "\n", encoding="utf-8")
print("Generated 16 fixed, cold-cache release jobs")
