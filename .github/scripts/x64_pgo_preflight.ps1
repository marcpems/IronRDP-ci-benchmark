param([Parameter(Mandatory = $true)][string]$Output)
$ErrorActionPreference = 'Stop'
if ($env:RUNNER_NAME -ne 'MARCPE-TEST01-X64' -or $env:RUNNER_ENVIRONMENT -ne 'self-hosted') {
    throw 'Expected the dedicated self-hosted x64 runner'
}
$processes = @(Get-CimInstance Win32_Process)
$ancestors = @()
$cursor = $PID
while ($cursor -and $cursor -notin $ancestors) {
    $ancestors += $cursor
    $parent = $processes | Where-Object ProcessId -eq $cursor
    if (!$parent) { break }
    $cursor = $parent.ParentProcessId
}
$blockers = @($processes | Where-Object {
    $_.ProcessId -notin $ancestors -and $_.Name -in @(
        'Runner.Worker.exe', 'cmake.exe', 'ninja.exe', 'clang-cl.exe', 'cl.exe',
        'link.exe', 'lld-link.exe', 'rustc.exe', 'rustdoc.exe', 'cargo.exe', 'opt-dist.exe'
    )
} | Select-Object Name, ProcessId, ParentProcessId)
$volumes = @(Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' |
    Select-Object DeviceID, FileSystem, Size, FreeSpace)
$mapping = @(
    foreach ($volume in $volumes) {
        $partition = Get-Partition -DriveLetter $volume.DeviceID.Substring(0, 1)
        $disk = Get-Disk -Number $partition.DiskNumber
        @{
            Drive = $volume.DeviceID
            DiskNumber = $disk.Number
            Model = $disk.FriendlyName
            BusType = $disk.BusType.ToString()
            Size = $disk.Size
        }
    }
)
$os = Get-CimInstance Win32_OperatingSystem
$power = & powercfg /getactivescheme
if ($LASTEXITCODE) { throw 'Cannot inspect active power scheme' }
$samples = @(
    foreach ($index in 1..4) {
        @{
            UTC = [datetime]::UtcNow.ToString('o')
            CPU = @(Get-CimInstance Win32_PerfFormattedData_PerfOS_Processor |
                Where-Object Name -eq '_Total' | Select-Object PercentProcessorTime)
            Disks = @(Get-CimInstance Win32_PerfFormattedData_PerfDisk_PhysicalDisk |
                Select-Object Name, CurrentDiskQueueLength, DiskBytesPersec, PercentDiskTime)
        }
        if ($index -lt 4) { Start-Sleep -Seconds 5 }
    }
)
$result = @{
    Schema = 1
    Runner = $env:RUNNER_NAME
    RunId = $env:GITHUB_RUN_ID
    UTC = [datetime]::UtcNow.ToString('o')
    CPU = @(Get-CimInstance Win32_Processor |
        Select-Object Name, NumberOfCores, NumberOfLogicalProcessors)
    PhysicalMemoryBytes = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
    FreeMemoryKiB = $os.FreePhysicalMemory
    OS = @{Caption = $os.Caption; Version = $os.Version}
    Volumes = $volumes
    DiskMapping = $mapping
    PhysicalDisks = @(Get-PhysicalDisk | Select-Object FriendlyName, MediaType, BusType, Size, HealthStatus)
    PowerScheme = $power -join ' '
    ConflictingProcesses = $blockers
    IdleSamples = $samples
    Scope = 'Read-only readiness inventory; no builds, cleanup, or system-setting changes.'
}
if (Test-Path -LiteralPath $Output) { throw 'Refusing to overwrite existing preflight evidence' }
$result | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -LiteralPath $Output
Get-Content -LiteralPath $Output
if ($blockers.Count) { throw 'Concurrent compiler work detected; no build may start' }
