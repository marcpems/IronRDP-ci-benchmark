$ErrorActionPreference = 'Stop'
$workflow = Get-Content -Raw (Join-Path $PSScriptRoot '..\..\.github\workflows\release-binaries.yml')
$match = [regex]::Match($workflow, '(?ms)^      - name: Prepare Windows Arm build storage\r?\n.*?^        run: \|\r?\n(?<body>.*?)(?=^      - name:)')
if (-not $match.Success) { throw 'cannot find the guarded storage step' }
$body = ($match.Groups['body'].Value -split '\r?\n' | ForEach-Object { $_ -replace '^ {10}', '' }) -join "`n"
$code = [scriptblock]::Create($body)
if ([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture -ne 'Arm64') {
    throw 'run guard tests under ARM64 PowerShell'
}

# All storage/filesystem reads are mocked. Initialization is a sentinel, never a real disk operation.
function Get-Partition { $script:partitions }
function Get-Volume { $script:volumes }
function Get-PSDrive { param($PSProvider) $script:drives }
function Get-Disk {
    if ($script:queryFailure) { throw 'STORAGE_QUERY_FAILED' }
    $script:disks
}
function Get-Item {
    param($LiteralPath, [switch]$Force)
    if ($LiteralPath -eq $script:cargoPath) { $script:cargoDirectory } else { $script:workspace }
}
function Get-ChildItem { param($LiteralPath, [switch]$Force) $script:children }
function Test-Path { param($LiteralPath) $script:cargoExists }
function Initialize-Disk {
    param($InputObject, $PartitionStyle, [switch]$PassThru)
    if ($InputObject.Number -ne 7 -or $PartitionStyle -ne 'GPT') { throw 'wrong initialization request' }
    throw 'ELIGIBLE'
}
function New-Partition { throw 'must not create a partition in guard tests' }
function Format-Volume { throw 'must not format in guard tests' }

$cases = @(
    @{ Name = 'one raw NVMe'; Change = {}; Eligible = $true }
    @{ Name = 'D partition, even without filesystem'; Change = { $script:partitions = @([pscustomobject]@{DriveLetter = 'D'; DiskNumber = 3}) } }
    @{ Name = 'D volume'; Change = { $script:volumes = @([pscustomobject]@{DriveLetter = 'D'}) } }
    @{ Name = 'D mapped drive'; Change = { $script:drives = @([pscustomobject]@{Name = 'D'}) } }
    @{ Name = 'no raw disk'; Change = { $script:disks = @() } }
    @{ Name = 'ambiguous disks'; Change = { $script:disks += $script:disks[0].PSObject.Copy() } }
    @{ Name = 'initialized disk'; Change = { $script:disks[0].PartitionStyle = 'GPT' } }
    @{ Name = 'non-NVMe disk'; Change = { $script:disks[0].BusType = 'SAS' } }
    @{ Name = 'boot disk'; Change = { $script:disks[0].IsBoot = $true } }
    @{ Name = 'system disk'; Change = { $script:disks[0].IsSystem = $true } }
    @{ Name = 'offline disk'; Change = { $script:disks[0].IsOffline = $true } }
    @{ Name = 'read-only disk'; Change = { $script:disks[0].IsReadOnly = $true } }
    @{ Name = 'disk with partitions'; Change = { $script:disks[0].NumberOfPartitions = 1 } }
    @{ Name = 'partition inventory disagreement'; Change = { $script:partitions = @([pscustomobject]@{DriveLetter = ''; DiskNumber = 7}) } }
    @{ Name = 'insufficient capacity'; Change = { $script:disks[0].Size = 49GB } }
    @{ Name = 'nonempty workspace'; Change = { $script:children = @('existing file') } }
    @{ Name = 'linked workspace'; Change = { $script:workspace.Attributes = [IO.FileAttributes]::ReparsePoint } }
    @{ Name = 'workspace is a file'; Change = { $script:workspace.PSIsContainer = $false } }
    @{ Name = 'ordinary Cargo home'; Change = { $script:cargoExists = $true }; Eligible = $true }
    @{ Name = 'linked Cargo home'; Change = { $script:cargoExists = $true; $script:cargoDirectory.Attributes = [IO.FileAttributes]::ReparsePoint } }
    @{ Name = 'Cargo home is a file'; Change = { $script:cargoExists = $true; $script:cargoDirectory.PSIsContainer = $false } }
    @{ Name = 'storage query errors propagate'; Change = { $script:queryFailure = $true }; ExpectedError = 'STORAGE_QUERY_FAILED' }
)
foreach ($case in $cases) {
    $script:cargoPath = if ($env:CARGO_HOME) { $env:CARGO_HOME } else { Join-Path $HOME '.cargo' }
    $script:cargoExists = $false
    $script:queryFailure = $false
    $script:cargoDirectory = [pscustomobject]@{ PSIsContainer = $true; Attributes = [IO.FileAttributes]::Directory }
    $script:partitions = @([pscustomobject]@{DriveLetter = 'C'; DiskNumber = 0})
    $script:volumes = @()
    $script:drives = @()
    $script:children = @()
    $script:workspace = [pscustomobject]@{
        PSIsContainer = $true; Attributes = [IO.FileAttributes]::Directory; FullName = 'C:\mock-workspace'
    }
    $script:disks = @([pscustomobject]@{
        Number = 7; BusType = 'NVMe'; PartitionStyle = 'RAW'
        IsBoot = $false; IsSystem = $false; IsOffline = $false; IsReadOnly = $false
        NumberOfPartitions = 0; Size = 220GB
    })
    & $case.Change
    $eligible = $false
    $expectedError = $false
    try { & $code } catch {
        if ($_.Exception.Message -eq 'ELIGIBLE') { $eligible = $true }
        elseif ($case.ExpectedError -and $_.Exception.Message -eq $case.ExpectedError) { $expectedError = $true }
        else { throw }
    }
    if ([bool]$case.ExpectedError -ne $expectedError) { throw "expected error did not propagate: $($case.Name)" }
    if ($eligible -ne [bool]$case.Eligible) { throw "unexpected eligibility: $($case.Name)" }
    Write-Host "PASS: $($case.Name)"
}
