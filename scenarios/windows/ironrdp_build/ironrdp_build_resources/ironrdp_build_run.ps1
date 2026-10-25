# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

#Requires -Version 7.2
param(
    [string]$workRoot = '', [string]$logFile = '',
    [string]$startTime = (Get-Date).ToString('o'),
    [int]$jobs = 0, [int]$timeoutSeconds = 2400
)

. "$PSScriptRoot\ironrdp_build_common.ps1"
$lock = $null
$context = $null
try {
    if ($jobs -lt 0 -or $jobs -gt 4096) { throw 'jobs must be between 0 (all available processors) and 4096.' }
    if ($timeoutSeconds -lt 1 -or $timeoutSeconds -gt 2400) { throw 'timeoutSeconds must be between 1 and 2400.' }
    $origin = [DateTimeOffset]::Parse($startTime, [Globalization.CultureInfo]::InvariantCulture)
    $context = Initialize-IronRdpContext $workRoot $logFile 'run'
    $lock = Lock-IronRdpWork $context
    $results = Join-Path $context.Data 'ironrdp_build_results.csv'
    if (Test-Path -LiteralPath $results) { Remove-Item -LiteralPath $results }
    Register-IronRdpOwner $context
    if (-not (Test-Path -LiteralPath $context.Receipt)) { throw 'Prep receipt is missing. Re-run prep.' }
    $receipt = Get-Content -LiteralPath $context.Receipt -Raw | ConvertFrom-Json -AsHashtable
    if ($receipt.config_sha256 -ne $context.ConfigHash -or $receipt.host_triple -ne $context.HostTriple) {
        throw 'Prepared resources do not match this workload or architecture. Re-run prep.'
    }
    foreach ($tool in $receipt.tools.Keys) {
        Assert-IronRdpPath $receipt.tools[$tool]
        if ((Get-FileHash $receipt.tools[$tool] -Algorithm SHA256).Hash -ne $receipt.tool_sha256[$tool]) {
            throw "The prepared $tool executable changed. Re-run prep."
        }
    }
    $environment = Get-IronRdpEnvironment $context
    $vs = getVSVersion $context.Architecture
    if (-not $vs) { throw 'Native Visual C++ tools are missing. Re-run prep.' }
    $vsEnvironment = Get-IronRdpVsEnvironment $context $vs
    foreach ($key in $vsEnvironment.Keys) { $environment[$key] = $vsEnvironment[$key] }
    $environment.RUSTC = $receipt.tools.rustc
    $environment.RUSTDOC = $receipt.tools.rustdoc
    $environment.Path = (Split-Path $receipt.tools.rustc) + ';' + $environment.Path
    Assert-IronRdpSource $context $receipt.git $environment
    if ((Get-FileHash (Join-Path $context.Source 'Cargo.lock') -Algorithm SHA256).Hash -ne $receipt.lock_sha256) {
        throw 'The workload lockfile changed after prep.'
    }
    if ($jobs -eq 0) { $jobs = [Environment]::ProcessorCount }
    Remove-IronRdpTarget $context
    $iteration = [DateTimeOffset]::UtcNow.ToString('yyyyMMddTHHmmssfffZ') + '-' + [Guid]::NewGuid().ToString('N').Substring(0, 8)
    $prefix = Join-Path $context.Data "ironrdp_build_$iteration"
    $arguments = @('build', '--workspace', '--frozen', '--target', $context.HostTriple,
        '--jobs', "$jobs", '--message-format=json', '--timings')
    log "Fresh offline workspace build: cargo $($arguments -join ' ')"
    log "Rust $($context.Toolchain), source $($context.Config.revision), jobs $jobs; dev debuginfo=0, incremental=0."
    $seconds = Invoke-IronRdpProcess $receipt.tools.cargo $arguments $context.Source $environment $prefix $timeoutSeconds
    $compiled = 0
    $finished = $false
    foreach ($line in [IO.File]::ReadLines("$prefix.stdout.log")) {
        $message = $line | ConvertFrom-Json
        if ($message.reason -eq 'compiler-artifact' -and -not $message.fresh) { $compiled++ }
        if ($message.reason -eq 'build-finished') { $finished = $message.success }
    }
    if (-not $finished -or $compiled -eq 0) { throw 'Cargo did not report a successful build with new compiled artifacts.' }
    Assert-IronRdpSource $context $receipt.git $environment
    $timingReport = Join-Path $context.Target 'cargo-timings\cargo-timing.html'
    if (-not (Test-Path -LiteralPath $timingReport)) { throw 'Cargo timing report is missing.' }
    Copy-Item -LiteralPath $timingReport -Destination "$prefix.timings.html"
    $invariant = [Globalization.CultureInfo]::InvariantCulture
    $buildTime = $seconds.ToString('F6', $invariant)
    $elapsed = ([DateTimeOffset]::UtcNow - $origin).TotalSeconds.ToString('F6', $invariant)
    @{
        iteration = $iteration; build_time = $seconds; scenario_runtime = $seconds
        architecture = $context.Architecture; jobs = $jobs; command = $arguments
        revision = $context.Config.revision; toolchain = $context.Toolchain
        lock_sha256 = $receipt.lock_sha256; tool_sha256 = $receipt.tool_sha256
        compiled_artifacts = $compiled; target_was_removed = $true
        visual_studio_version = $vs.installationVersion
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath "$prefix.json" -Encoding utf8
    $trace = Join-Path $context.Data 'ironrdp_build_results.trace'
    if (-not (Test-Path -LiteralPath $trace)) {
        Set-Content -LiteralPath $trace -Value 'Timestamp,ironrdp_build_time' -Encoding utf8
    }
    Add-Content -LiteralPath $trace -Value "$elapsed,$buildTime" -Encoding utf8
    @("scenario_runtime,$buildTime", "build_time,$buildTime", "architecture,$($context.Architecture)", "jobs,$jobs") |
        Set-Content -LiteralPath $results -Encoding utf8
    log '========================================'
    log 'IronRDP Build Metrics Summary'
    log "Build Time: $buildTime seconds"
    log "scenario_runtime: $buildTime seconds"
    log "Architecture: $($context.Architecture); jobs: $jobs; compiled artifacts: $compiled"
    log '========================================'
} catch {
    Write-Host " ERROR - $($_.Exception.Message)" -ForegroundColor Red
    if ($script:logFile -and (Test-Path -LiteralPath (Split-Path $script:logFile))) {
        Add-Content -LiteralPath $script:logFile -Value " ERROR - $($_.Exception.Message)" -Encoding utf8
        Add-Content -LiteralPath $script:logFile -Value $_.ScriptStackTrace -Encoding utf8
    }
    exit 1
} finally {
    if ($lock) {
        if (Test-Path -LiteralPath $context.Active) { Remove-Item -LiteralPath $context.Active }
        $lock.Dispose()
    }
}
