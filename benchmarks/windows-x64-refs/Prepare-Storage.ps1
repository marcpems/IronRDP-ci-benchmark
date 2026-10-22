$ErrorActionPreference = 'Stop'
if ($env:GITHUB_ACTIONS -ne 'true' -or
    $env:STORAGE_RUNNER_ENVIRONMENT -ne 'github-hosted' -or
    $env:RUNNER_OS -ne 'Windows' -or $env:RUNNER_ARCH -ne 'X64' -or
    [Runtime.InteropServices.RuntimeInformation]::OSArchitecture -ne 'X64') {
    throw 'storage experiment requires a GitHub-hosted Windows x64 runner'
}

$partitions = @(Get-Partition)
$volumes = @(Get-Volume)
$drives = @(Get-PSDrive -PSProvider FileSystem)
if (($partitions | Where-Object DriveLetter -eq 'R') -or
    ($volumes | Where-Object DriveLetter -eq 'R') -or
    ($drives | Where-Object Name -eq 'R')) {
    throw 'R is already assigned'
}
$partition = @($partitions | Where-Object DriveLetter -eq 'D')
if ($partition.Count -ne 1) { throw 'expected exactly one D partition' }
$partition = $partition[0]
$disk = Get-Disk -Number $partition.DiskNumber
$volume = Get-Volume -DriveLetter D
$eligibility = [ordered]@{
    disk_not_boot = -not $disk.IsBoot
    disk_not_system = -not $disk.IsSystem
    disk_online = -not $disk.IsOffline
    disk_writable = -not $disk.IsReadOnly
    partition_not_boot = -not $partition.IsBoot
    partition_not_system = -not $partition.IsSystem
    supported_style = $disk.PartitionStyle -in @('MBR', 'GPT')
    single_partition = @($partitions | Where-Object DiskNumber -eq $disk.Number).Count -eq 1
    ntfs = $volume.FileSystem -eq 'NTFS'
    healthy = $volume.HealthStatus -eq 'Healthy'
    fixed = $volume.DriveType -eq 'Fixed'
}
$eligibility | ConvertTo-Json | Write-Host
$disk | Select-Object Number, PartitionStyle, IsBoot, IsSystem, IsOffline, IsReadOnly |
    ConvertTo-Json | Write-Host
$volume | Select-Object DriveLetter, FileSystem, HealthStatus, DriveType |
    ConvertTo-Json | Write-Host
Write-Host "PartitionStyle type: $($disk.PartitionStyle.GetType().FullName)"
if ($disk.IsBoot -or $disk.IsSystem -or $disk.IsOffline -or $disk.IsReadOnly -or
    $partition.IsBoot -or $partition.IsSystem -or
    $disk.PartitionStyle -notin @('MBR', 'GPT') -or
    @($partitions | Where-Object DiskNumber -eq $disk.Number).Count -ne 1 -or
    $volume.FileSystem -ne 'NTFS' -or $volume.HealthStatus -ne 'Healthy' -or
    $volume.DriveType -ne 'Fixed') {
    throw 'D is not an eligible standalone non-system NTFS data partition'
}

$cargoHome = if ($env:CARGO_HOME) { $env:CARGO_HOME } else { Join-Path $HOME '.cargo' }
$relocations = @(
    @{ Source = $env:RUNNER_TEMP; Destination = 'R:\runner-temp' }
    @{ Source = $env:GITHUB_WORKSPACE; Destination = 'R:\workspace' }
    @{ Source = $cargoHome; Destination = 'R:\cargo-home' }
)
foreach ($entry in $relocations) {
    $source = Get-Item -LiteralPath $entry.Source -Force
    if (-not $source.PSIsContainer -or $null -eq $source.Parent -or
        ($source.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "source is not an ordinary directory: $($entry.Source)"
    }
    $entry.Source = $source.FullName.TrimEnd('\')
}
for ($i = 0; $i -lt $relocations.Count; $i++) {
    for ($j = 0; $j -lt $relocations.Count; $j++) {
        if ($i -ne $j -and ($relocations[$i].Source -eq $relocations[$j].Source -or
            $relocations[$i].Source.StartsWith(
                $relocations[$j].Source + '\', [StringComparison]::OrdinalIgnoreCase))) {
            throw 'relocation sources overlap'
        }
    }
}
if (-not $env:GITHUB_WORKSPACE.StartsWith('D:\', [StringComparison]::OrdinalIgnoreCase) -or
    -not $env:RUNNER_TEMP.StartsWith('D:\', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'expected workspace and runner temporary directory on D'
}

$limits = $partition | Get-PartitionSupportedSize
if ($limits.SizeMin -le 0 -or $limits.SizeMin -ge $partition.Size -or
    $partition.Size - $limits.SizeMin -lt 50GB) {
    throw 'insufficient reclaimable space at the supported NTFS minimum'
}
$before = @{
    disk_number = $disk.Number
    partition_number = $partition.PartitionNumber
    original_size = $partition.Size
    supported_minimum = $limits.SizeMin
    paging_files = @(Get-CimInstance Win32_PageFileUsage |
        Select-Object Name, AllocatedBaseSize, CurrentUsage)
    paging_settings = @(Get-CimInstance Win32_PageFileSetting |
        Select-Object Name, InitialSize, MaximumSize)
    automatic_pagefile = (Get-CimInstance Win32_ComputerSystem).AutomaticManagedPagefile
}
$clock = [Diagnostics.Stopwatch]::StartNew()
Resize-Partition -InputObject $partition -Size $limits.SizeMin
$resizeSeconds = $clock.Elapsed.TotalSeconds
$newPartition = New-Partition -DiskNumber $disk.Number -UseMaximumSize -DriveLetter R
$newVolume = $newPartition | Format-Volume -FileSystem ReFS -NewFileSystemLabel Build -Confirm:$false
if ($newVolume.FileSystem -ne 'ReFS' -or $newVolume.DriveLetter -ne 'R') {
    throw 'new partition is not ReFS on R'
}

Set-Location -LiteralPath $env:SystemRoot
[Environment]::CurrentDirectory = $env:SystemRoot
foreach ($entry in $relocations) {
    New-Item -ItemType Directory -Path $entry.Destination | Out-Null
    robocopy $entry.Source $entry.Destination /E /COPY:DAT /DCOPY:DAT /SL /SJ /R:2 /W:1 /NP /NFL /NDL
    if ($LASTEXITCODE -ge 8) { throw "directory copy failed with robocopy exit code $LASTEXITCODE" }
    $LASTEXITCODE = 0
    $entry.Backup = "$($entry.Source).before-refs-$([guid]::NewGuid())"
    Move-Item -LiteralPath $entry.Source -Destination $entry.Backup
    New-Item -ItemType Junction -Path $entry.Source -Target $entry.Destination | Out-Null
}
New-Item -ItemType Directory -Path 'R:\build-temp' | Out-Null
"CARGO_HOME=R:\cargo-home" >> $env:GITHUB_ENV
"TEMP=R:\build-temp" >> $env:GITHUB_ENV
"TMP=R:\build-temp" >> $env:GITHUB_ENV
"X64_REFS_FILE_COMMAND_OK=true" >> $env:GITHUB_ENV
$clock.Stop()

$afterPartition = Get-Partition -DriveLetter D
if ($afterPartition.Size -ne $limits.SizeMin -or
    (Get-Volume -DriveLetter D).FileSystem -ne 'NTFS') {
    throw 'D does not retain NTFS at the requested supported minimum'
}
@{
    before = $before
    after_d_size = $afterPartition.Size
    after_d_free_bytes = (Get-Volume -DriveLetter D).SizeRemaining
    refs_partition = @{
        disk_number = $newPartition.DiskNumber
        partition_number = $newPartition.PartitionNumber
        size = $newPartition.Size
        filesystem = $newVolume.FileSystem
        allocation_unit_size = $newVolume.AllocationUnitSize
    }
    relocations = $relocations
    resize_seconds = $resizeSeconds
    preparation_seconds = $clock.Elapsed.TotalSeconds
} | ConvertTo-Json -Depth 8 | Set-Content "$env:RUNNER_TEMP\x64-storage-preparation.json"
Write-Host 'D remains NTFS; workspace, Cargo home and temporary files now use the new ReFS partition'
