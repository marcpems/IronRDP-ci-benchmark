# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

#Requires -Version 7.2
param()

$resources = Join-Path (Split-Path $PSScriptRoot) 'ironrdp_build_resources'
. "$resources\ironrdp_build_common.ps1"
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ("hobl-ironrdp-tests-" + [Guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $testRoot
$passed = 0
function Assert-Test {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw " ERROR - Test failed: $Message" }
}
function Assert-Throws {
    param([scriptblock]$Action, [string]$Pattern)
    $caught = $false
    try { & $Action } catch {
        $caught = $true
        Assert-Test ($_.Exception.Message -match $Pattern) "Unexpected error: $($_.Exception.Message)"
    }
    Assert-Test $caught "Expected failure matching $Pattern"
}
try {
    $foreign = Join-Path $testRoot 'foreign'
    $null = New-Item -ItemType Directory -Path $foreign
    Set-Content (Join-Path $foreign 'keep.txt') 'user data'
    Assert-Throws { Initialize-IronRdpContext $foreign "$testRoot\data\test.log" 'test' -Create } 'nonempty'
    Assert-Test (Test-Path "$foreign\keep.txt") 'foreign directory must be preserved'
    $passed++

    $context = Initialize-IronRdpContext "$testRoot\owned" "$testRoot\data\test.log" 'test' -Create
    $lock = Lock-IronRdpWork $context
    try { Assert-Throws { Lock-IronRdpWork $context } 'busy' } finally { $lock.Dispose() }
    $passed++

    $null = New-Item -ItemType Directory -Path $context.Target, $context.Source
    Set-Content "$($context.Target)\build.obj" 'build output'
    Set-Content "$($context.Source)\Cargo.lock" 'preserve source'
    Set-Content $context.Receipt 'preserve prep'
    Remove-IronRdpTarget $context
    Assert-Test (-not (Test-Path $context.Target)) 'build output was not removed'
    Assert-Test (Test-Path "$($context.Source)\Cargo.lock") 'source was removed'
    Assert-Test (Test-Path $context.Receipt) 'prep receipt was removed'
    Remove-IronRdpTarget $context
    $passed++

    $null = New-Item -ItemType Junction -Path $context.Target -Target $foreign
    try {
        Assert-Throws { Remove-IronRdpTarget $context } 'reparse point'
        Assert-Test (Test-Path "$foreign\keep.txt") 'junction target must be preserved'
    } finally { Remove-Item -LiteralPath $context.Target }
    $passed++

    $package = $context.Config.native_tools.($context.Architecture)[0]
    $badArchive = Join-Path $context.Root "tools\$($package.name)-$($package.version)-$($context.Architecture).zip"
    $null = New-Item -ItemType Directory -Path (Split-Path $badArchive) -Force
    Set-Content -LiteralPath $badArchive -Value 'corrupt cached download'
    Assert-Throws { Get-IronRdpNativeTools $context -Install } 'checksum mismatch'
    $passed++

    $git = (Get-Command git -ErrorAction Stop).Source
    $null = Invoke-IronRdpProcess $git @('init', '--quiet', $context.Source) $testRoot @{} "$testRoot\git"
    $null = Invoke-IronRdpProcess $git @('-C', $context.Source, 'add', 'Cargo.lock') $testRoot @{} "$testRoot\git"
    $null = Invoke-IronRdpProcess $git @('-C', $context.Source, '-c', 'user.name=Fixture',
        '-c', 'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false', 'commit', '--quiet', '-m',
        "Fixture`n`nCo-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>") $testRoot @{} "$testRoot\git"
    $null = Invoke-IronRdpProcess $git @('-C', $context.Source, 'rev-parse', 'HEAD') $testRoot @{} "$testRoot\git"
    $context.Config.revision = [IO.File]::ReadAllText("$testRoot\git.stdout.log").Trim()
    Assert-IronRdpSource $context $git @{}
    Add-Content "$($context.Source)\Cargo.lock" 'changed'
    Assert-Throws { Assert-IronRdpSource $context $git @{} } 'modified'
    $passed++

    $pwsh = (Get-Process -Id $PID).Path
    $oldRustflags = $env:RUSTFLAGS
    $env:RUSTFLAGS = 'must-not-leak'
    try {
        $seconds = Invoke-IronRdpProcess $pwsh @('-NoProfile', '-NonInteractive', '-Command',
            'if (Test-Path Env:RUSTFLAGS) { exit 23 }; [Console]::Write("output"); [Console]::Error.Write("diagnostic")') `
            $testRoot @{} "$testRoot\process"
    } finally { $env:RUSTFLAGS = $oldRustflags }
    Assert-Test ($seconds -is [double] -and $seconds -gt 0) 'timer must return only elapsed seconds'
    Assert-Test ((Get-Content "$testRoot\process.stdout.log" -Raw) -eq 'output') 'stdout was not retained'
    Assert-Test ((Get-Content "$testRoot\process.stderr.log" -Raw) -eq 'diagnostic') 'stderr was not retained'
    Assert-Throws {
        Invoke-IronRdpProcess $pwsh @('-NoProfile', '-NonInteractive', '-Command', 'exit 19') $testRoot @{} "$testRoot\failure"
    } 'exited 19'
    $passed++

    & {
        function New-IronRdpStopwatch {
            $clock = [pscustomobject]@{ Elapsed = [TimeSpan]::FromSeconds(30) }
            $clock | Add-Member -MemberType ScriptMethod -Name Stop -Value {}
            return $clock
        }
        Assert-Throws {
            Invoke-IronRdpProcess $pwsh @('-NoProfile', '-NonInteractive', '-Command',
                '[Console]::Write("completed")') $testRoot @{} "$testRoot\resumed" 10
        } 'wall-clock deadline'
        Assert-Test ([IO.File]::ReadAllText("$testRoot\resumed.stdout.log") -eq 'completed') 'completed process over the elapsed deadline was not rejected'
    }
    $passed++

    $childFile = Join-Path $testRoot 'child.txt'
    $scriptText = '$child = Start-Process -FilePath "' + $pwsh + '" -ArgumentList "-NoProfile -NonInteractive -Command Start-Sleep 120" -PassThru; ' +
        'Set-Content -LiteralPath "' + $childFile + '" -Value $child.Id; Start-Sleep 120'
    Assert-Throws {
        Invoke-IronRdpProcess $pwsh @('-NoProfile', '-NonInteractive', '-Command', $scriptText) $testRoot @{} "$testRoot\timeout" 5
    } 'timed out'
    Assert-Test (Test-Path $childFile) 'timeout fixture did not start its child'
    $childPid = [int](Get-Content $childFile)
    $child = Get-Process -Id $childPid -ErrorAction SilentlyContinue
    if ($child) { $null = $child.WaitForExit(5000) }
    Assert-Test (-not (Get-Process -Id $childPid -ErrorAction SilentlyContinue)) 'timed-out descendant survived'
    $passed++

    $owner = Get-Process -Id $PID
    @{ pid = $PID; start_ticks = 1; executable = $owner.Path } |
        ConvertTo-Json | Set-Content $context.Active
    $null = Invoke-IronRdpProcess $pwsh @('-NoProfile', '-NonInteractive', '-File',
        "$resources\ironrdp_build_kill.ps1", '-workRoot', $context.Root, '-logFile', "$testRoot\data\kill.log") `
        $testRoot @{} "$testRoot\kill"
    Assert-Test ($null -ne (Get-Process -Id $PID)) 'stale PID record stopped an unrelated process'
    Assert-Test ((Get-Content "$testRoot\data\kill.log" -Raw) -match 'no processes were stopped') 'stale PID was not reported'
    $passed++
    Write-Host "$passed PowerShell scenario regression cases passed."
} finally {
    Remove-Item -LiteralPath $testRoot -Recurse -Force
}
