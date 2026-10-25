# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

#Requires -Version 7.2
param([string]$workRoot = '', [string]$logFile = '')

. "$PSScriptRoot\ironrdp_build_common.ps1"
$lock = $null
try {
    $context = Initialize-IronRdpContext $workRoot $logFile 'teardown'
    $lock = Lock-IronRdpWork $context
    Remove-IronRdpTarget $context
    log 'Removed only build outputs; source, toolchain and dependency caches are retained.'
} catch {
    Write-Host " ERROR - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    if ($lock) { $lock.Dispose() }
}
