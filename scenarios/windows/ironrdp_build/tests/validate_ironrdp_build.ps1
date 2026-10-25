# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

#Requires -Version 7.2
param(
    [Parameter(Mandatory)][string]$workRoot,
    [Parameter(Mandatory)][string]$dataDirectory,
    [ValidateRange(1, 10)][int]$builds = 2
)

$resources = Join-Path (Split-Path $PSScriptRoot) 'ironrdp_build_resources'
. "$resources\ironrdp_build_common.ps1"
$pwsh = (Get-Process -Id $PID).Path
$context = Initialize-IronRdpContext $workRoot (Join-Path $dataDirectory 'validation.log') 'validation' -Create
$dataDirectory = $context.Data
function Invoke-Phase {
    param([string]$Phase, [string[]]$Extra = @(), [int]$Expected = 0)
    & $pwsh -NoProfile -NonInteractive -File "$resources\ironrdp_build_$Phase.ps1" `
        -workRoot $context.Root -logFile "$dataDirectory\$Phase.log" @Extra
    if ($LASTEXITCODE -ne $Expected) { throw " ERROR - $Phase returned $LASTEXITCODE; expected $Expected." }
}
function Assert-Validation {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw " ERROR - $Message" }
}

Invoke-Phase 'prep' @('-SkipSystemInstall')
$measurements = @()
$origin = [DateTimeOffset]::UtcNow.ToString('o')
for ($i = 0; $i -lt $builds; $i++) {
    Invoke-Phase 'run' @('-jobs', '4', '-startTime', $origin)
    $values = @{}
    Import-Csv "$dataDirectory\ironrdp_build_results.csv" -Header key, value |
        ForEach-Object { $values[$_.key] = $_.value }
    $seconds = [double]::Parse($values.build_time, [Globalization.CultureInfo]::InvariantCulture)
    Assert-Validation ($seconds -gt 0 -and $values.scenario_runtime -eq $values.build_time) 'Invalid wall-clock metrics.'
    Assert-Validation ($values.architecture -eq $context.Architecture) 'Architecture metric mismatch.'
    $measurements += $seconds
}

$sourceLock = Join-Path $context.Source 'Cargo.lock'
$originalLock = [IO.File]::ReadAllBytes($sourceLock)
try {
    Add-Content -LiteralPath $sourceLock -Value '# validation-only dirty source'
    Invoke-Phase 'run' @('-jobs', '4') 1
    Assert-Validation (-not (Test-Path "$dataDirectory\ironrdp_build_results.csv")) 'Failed run retained stale success metrics.'
} finally {
    [IO.File]::WriteAllBytes($sourceLock, $originalLock)
}

Remove-IronRdpTarget $context
$start = [Diagnostics.ProcessStartInfo]::new()
$start.FileName = $pwsh
$start.UseShellExecute = $false
foreach ($argument in @('-NoProfile', '-NonInteractive', '-File', "$resources\ironrdp_build_run.ps1",
    '-workRoot', $context.Root, '-logFile', "$dataDirectory\cancelled.log", '-jobs', '4')) {
    $start.ArgumentList.Add($argument)
}
$process = [Diagnostics.Process]::Start($start)
try {
    $deadline = [DateTimeOffset]::UtcNow.AddSeconds(90)
    while (-not (Test-Path -LiteralPath $context.Target) -and -not $process.HasExited -and
        [DateTimeOffset]::UtcNow -lt $deadline) {
        Start-Sleep -Milliseconds 200
    }
    Assert-Validation (-not $process.HasExited -and (Test-Path $context.Target)) 'Cancellation fixture did not enter Cargo.'
    $active = Get-Content -LiteralPath $context.Active -Raw | ConvertFrom-Json
    Assert-Validation ($active.pid -eq $process.Id) 'Cancellation fixture does not own the recorded PID.'
    Invoke-Phase 'kill'
    Assert-Validation ($process.WaitForExit(30000)) 'Scenario cancellation failed to stop its process.'
    Assert-Validation ($process.ExitCode -ne 0) 'Cancelled workload returned success.'
    Assert-Validation (-not (Test-Path "$dataDirectory\ironrdp_build_results.csv")) 'Cancelled workload published success metrics.'
} finally {
    if (-not $process.HasExited) {
        $process.Kill($true)
        $process.WaitForExit()
    }
    $process.Dispose()
}

$receipt = Get-Content -LiteralPath $context.Receipt -Raw | ConvertFrom-Json -AsHashtable
$cachedCrate = Get-ChildItem -LiteralPath (Join-Path $context.Root 'cargo-home\registry\cache') -Recurse -File |
    Select-Object -First 1
Assert-Validation ($null -ne $cachedCrate) 'Cargo dependency cache is missing.'
$retained = @($sourceLock, $context.Receipt, $cachedCrate.FullName) + @($receipt.tools.Values)
$hashes = @{}
foreach ($path in $retained) { $hashes[$path] = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash }
Invoke-Phase 'teardown'
Invoke-Phase 'teardown'
Assert-Validation (-not (Test-Path $context.Target)) 'Teardown did not remove Cargo outputs.'
foreach ($path in $retained) {
    Assert-Validation ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -eq $hashes[$path]) "Teardown modified a prep resource: $path"
}
@{
    architecture = $context.Architecture
    revision = $context.Config.revision
    toolchain = $context.Toolchain
    build_seconds = $measurements
    checks = @('fresh offline builds', 'wall-clock CSV', 'dirty-source failure',
        'stale-metrics rejection', 'active Cargo cancellation', 'idempotent teardown', 'prep-resource preservation')
} | ConvertTo-Json -Depth 4 | Set-Content "$dataDirectory\validation.json" -Encoding utf8
Write-Host 'IronRDP standalone build/lifecycle validation passed.'
