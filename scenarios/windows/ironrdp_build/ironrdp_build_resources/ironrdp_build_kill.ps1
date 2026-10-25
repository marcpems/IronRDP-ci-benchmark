# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

#Requires -Version 7.2
param([string]$workRoot = '', [string]$logFile = '')

. "$PSScriptRoot\ironrdp_build_common.ps1"
try {
    $context = Initialize-IronRdpContext $workRoot $logFile 'kill'
    if (Test-Path -LiteralPath $context.Active) {
        Assert-IronRdpPath $context.Active
        $active = Get-Content -LiteralPath $context.Active -Raw | ConvertFrom-Json
        $process = Get-Process -Id $active.pid -ErrorAction SilentlyContinue
        if ($process -and $process.Id -ne $PID -and
            $process.StartTime.ToUniversalTime().Ticks -eq $active.start_ticks -and
            $process.Path -eq $active.executable) {
            log "Stopping the recorded scenario process tree (PID $($process.Id))."
            $process.Kill($true)
            $process.WaitForExit()
        } else {
            log 'No matching active scenario process; no processes were stopped.'
        }
    } else {
        log 'No active scenario process record; no processes were stopped.'
    }
} catch {
    Write-Host " ERROR - Scenario process cleanup: $($_.Exception.Message)" -ForegroundColor Red
}
exit 0
