param(
    [Parameter(Mandatory = $true)][string]$OutputDirectory,
    [ValidatePattern('^[A-Za-z]:$')][string]$BuildDrive = 'C:'
)
$ErrorActionPreference = 'Stop'
$paths = @(
    '\Processor(_Total)\% Processor Time',
    '\Memory\Available MBytes',
    '\Memory\Committed Bytes',
    '\Memory\Pages Input/sec',
    '\PhysicalDisk(*)\Avg. Disk sec/Read',
    '\PhysicalDisk(*)\Avg. Disk sec/Write',
    '\PhysicalDisk(*)\Current Disk Queue Length'
)
$writer = [IO.StreamWriter]::new("$OutputDirectory\telemetry.jsonl", $false, [Text.UTF8Encoding]::new($false))
try {
    while (!(Test-Path -LiteralPath "$OutputDirectory\telemetry-stop")) {
        $counters = Get-Counter -Counter $paths
        if (!$counters -or @($counters.CounterSamples).Count -eq 0) { throw 'No performance counters returned' }
        $row = @{
            UTC = [datetime]::UtcNow.ToString('o')
            CFreeBytes = (Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace
            BuildDrive = $BuildDrive
            BuildFreeBytes = (Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$BuildDrive'").FreeSpace
            Counters = @($counters.CounterSamples | Select-Object Path, CookedValue, Status)
        }
        $writer.WriteLine(($row | ConvertTo-Json -Depth 4 -Compress))
        $writer.Flush()
        if (!(Test-Path -LiteralPath "$OutputDirectory\telemetry-ready")) {
            New-Item -ItemType File -Path "$OutputDirectory\telemetry-ready" | Out-Null
        }
        Start-Sleep -Seconds 5
    }
} finally {
    $writer.Dispose()
}
