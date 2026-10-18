param([Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
$errors = [Collections.Generic.List[object]]::new()
function Read-Optional {
    param([string]$Name, [scriptblock]$Query)
    try { & $Query } catch {
        $errors.Add(@{Query=$Name; ErrorType=$_.Exception.GetType().FullName; ErrorId=$_.FullyQualifiedErrorId})
        Write-Warning "Diagnostic query unavailable: $Name ($($_.Exception.GetType().Name))"
        return $null
    }
}
function Read-PowerSetting {
    param([string]$Setting)
    $text = & powercfg /query SCHEME_CURRENT SUB_PROCESSOR $Setting
    if ($LASTEXITCODE) { throw "Cannot query processor power setting $Setting" }
    $values = @([regex]::Matches(($text -join "`n"), '0x([0-9a-fA-F]+)'))
    if ($values.Count -lt 2) { throw "Unexpected power setting output for $Setting" }
    return @{AC=[Convert]::ToUInt32($values[-2].Groups[1].Value,16); DC=[Convert]::ToUInt32($values[-1].Groups[1].Value,16)}
}
function Read-Events {
    param([string]$Log, [string]$Provider, [int[]]$Ids)
    try {
        @(Get-WinEvent -FilterHashtable @{
            LogName=$Log; ProviderName=$Provider; Id=$Ids
            StartTime=[datetime]'2026-10-15T00:00:00Z'; EndTime=[datetime]'2026-10-18T00:00:00Z'
        } -MaxEvents 200 | Select-Object Id, @{Name='UTC';Expression={$_.TimeCreated.ToUniversalTime().ToString('o')}})
    } catch {
        if ($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*') { return @() }
        throw
    }
}
$system = Get-CimInstance Win32_ComputerSystem
$os = Get-CimInstance Win32_OperatingSystem
$snapshot = @{
    UTC=[datetime]::UtcNow.ToString('o')
    CPU=@(Get-CimInstance Win32_Processor | Select-Object Name,Manufacturer,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed,CurrentClockSpeed)
    PhysicalMemoryBytes=$system.TotalPhysicalMemory
    AvailablePhysicalMemoryKiB=$os.FreePhysicalMemory
    OS=@{Caption=$os.Caption; Version=$os.Version; LastBootUTC=$os.LastBootUpTime.ToUniversalTime().ToString('o')}
    MemoryModules=@(Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity,Speed,ConfiguredClockSpeed)
    Volumes=@(Get-CimInstance Win32_LogicalDisk | Where-Object DeviceID -in @('C:','E:') |
        Select-Object DeviceID,FileSystem,Size,FreeSpace)
}
$snapshot.PowerMinimum = Read-Optional 'processor-minimum' { Read-PowerSetting PROCTHROTTLEMIN }
$snapshot.StorageDevices = Read-Optional 'storage-device-mapping' {
    foreach ($letter in @('C','E')) {
        $partition = Get-Partition -DriveLetter $letter
        $disk = Get-Disk -Number $partition.DiskNumber
        $volume = Get-Volume -DriveLetter $letter
        @{Drive=$letter; DiskNumber=$disk.Number; Model=$disk.FriendlyName
          BusType=$disk.BusType.ToString(); Size=$disk.Size; LogicalSectorSize=$disk.LogicalSectorSize
          PhysicalSectorSize=$disk.PhysicalSectorSize; AllocationUnitSize=$volume.AllocationUnitSize}
    }
}
$snapshot.PhysicalDisks = Read-Optional 'physical-disk-media' {
    Get-PhysicalDisk | Select-Object FriendlyName,MediaType,BusType,Size,HealthStatus
}
$snapshot.PowerMaximum = Read-Optional 'processor-maximum' { Read-PowerSetting PROCTHROTTLEMAX }
$snapshot.ActivePowerScheme = Read-Optional 'active-power-scheme' {
    $text = & powercfg /getactivescheme
    if ($LASTEXITCODE) { throw 'Cannot query active power scheme' }
    [regex]::Match(($text -join ''), '[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}').Value
}
$snapshot.Defender = Read-Optional 'defender-status' {
    Get-MpComputerStatus | Select-Object AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled,
        BehaviorMonitorEnabled,IoavProtectionEnabled,AMEngineVersion,FullScanStartTime,FullScanEndTime,QuickScanStartTime,QuickScanEndTime
}
$snapshot.ReportedDefenderPathExclusions = Read-Optional 'defender-exclusion-matches' {
    $preferences = Get-MpPreference
    foreach ($path in @('E:\','E:\m16997224t16r1','E:\m69758791t4r1','E:\m80060732t16r1')) {
        $matches = @($preferences.ExclusionPath | Where-Object {
            $excluded = [Environment]::ExpandEnvironmentVariables($_).TrimEnd('\')
            $excluded -and ($path -like $excluded -or $path.StartsWith($excluded + '\', [StringComparison]::OrdinalIgnoreCase))
        })
        @{Path=$path; ReportedMatchingExclusion=($matches.Count -gt 0)}
    }
}
$snapshot.ThrottlingEvents = Read-Optional 'firmware-throttling-events' {
    Read-Events System Microsoft-Windows-Kernel-Processor-Power @(37)
}
$snapshot.MemoryExhaustionEvents = Read-Optional 'memory-exhaustion-events' {
    Read-Events System Microsoft-Windows-Resource-Exhaustion-Detector @(2004)
}
$snapshot.DiskRetryEvents = Read-Optional 'disk-retry-events' { Read-Events System disk @(7,51,153) }
$snapshot.DefenderScanEvents = Read-Optional 'defender-scan-events' {
    Read-Events 'Microsoft-Windows-Windows Defender/Operational' 'Microsoft-Windows-Windows Defender' @(1000,1001,1002)
}
$snapshot.Errors = @($errors.ToArray())
$snapshot | ConvertTo-Json -Depth 7 | Set-Content -Encoding UTF8 -LiteralPath "$OutputDirectory\system.json"
$paths = @(
    '\Processor(_Total)\% Processor Time',
    '\System\Processor Queue Length',
    '\Memory\Available MBytes',
    '\Memory\Committed Bytes',
    '\Memory\Commit Limit',
    '\Memory\Pages Input/sec',
    '\Memory\Pages Output/sec',
    '\PhysicalDisk(*)\Avg. Disk sec/Read',
    '\PhysicalDisk(*)\Avg. Disk sec/Write',
    '\PhysicalDisk(*)\Current Disk Queue Length',
    '\PhysicalDisk(*)\Disk Read Bytes/sec',
    '\PhysicalDisk(*)\Disk Write Bytes/sec',
    '\Processor Information(_Total)\% Processor Performance',
    '\Processor Information(_Total)\Processor Frequency'
)
$output = [IO.StreamWriter]::new("$OutputDirectory\telemetry.jsonl", $false, [Text.UTF8Encoding]::new($false))
try {
    New-Item -ItemType File -Path "$OutputDirectory\telemetry-ready" | Out-Null
    while (!(Test-Path -LiteralPath "$OutputDirectory\telemetry-stop")) {
        $counterErrors = @()
        $values = Get-Counter -Counter $paths -ErrorAction SilentlyContinue -ErrorVariable counterErrors
        if (!$values -or @($values.CounterSamples).Count -eq 0) {
            throw 'No performance counters available; telemetry cannot be accepted'
        }
        if ($counterErrors.Count) { Write-Warning 'Some performance counters unavailable; errors recorded in telemetry' }
        $processes = @(Get-CimInstance Win32_PerfFormattedData_PerfProc_Process |
            Where-Object { $_.Name -notin @('_Total','Idle') } |
            Sort-Object PercentProcessorTime -Descending | Select-Object -First 12 |
            Select-Object Name,IDProcess,PercentProcessorTime,WorkingSetPrivate,IODataBytesPersec)
        $sample = @{
            UTC=[datetime]::UtcNow.ToString('o')
            Counters=@($values.CounterSamples | Select-Object Path,CookedValue,Status)
            Processes=$processes
            CounterErrors=@($counterErrors | ForEach-Object FullyQualifiedErrorId)
        }
        $output.WriteLine(($sample | ConvertTo-Json -Depth 5 -Compress))
        $output.Flush()
        Start-Sleep -Seconds 2
    }
} finally {
    $output.Dispose()
}
