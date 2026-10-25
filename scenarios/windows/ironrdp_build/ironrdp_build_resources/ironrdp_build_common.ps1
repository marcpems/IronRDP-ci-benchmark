# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:resourceRoot = $PSScriptRoot
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)

function log {
    param([string]$Message)
    Write-Host $Message
    Add-Content -LiteralPath $script:logFile -Value $Message -Encoding utf8
}

function Assert-IronRdpPath {
    param([string]$Path)
    $itemPath = [IO.Path]::GetFullPath($Path)
    while ($itemPath) {
        if (Test-Path -LiteralPath $itemPath) {
            $item = Get-Item -LiteralPath $itemPath -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Refusing a reparse point in scenario path: $itemPath"
            }
        }
        $itemPath = [IO.Path]::GetDirectoryName($itemPath)
    }
}

function Initialize-IronRdpContext {
    param([string]$WorkRoot, [string]$LogFile, [string]$Phase, [switch]$Create)
    $scriptDrive = Split-Path -Qualifier $script:resourceRoot
    if (-not $WorkRoot) { $WorkRoot = Join-Path $script:resourceRoot 'work' }
    if (-not $LogFile) { $LogFile = "$scriptDrive\hobl_data\ironrdp_build_$Phase.log" }
    $WorkRoot = [IO.Path]::GetFullPath($WorkRoot)
    if ($WorkRoot.TrimEnd('\') -eq [IO.Path]::GetPathRoot($WorkRoot).TrimEnd('\')) {
        throw 'The working directory must not be a drive root.'
    }
    Assert-IronRdpPath $WorkRoot
    Assert-IronRdpPath $LogFile
    $script:logFile = [IO.Path]::GetFullPath($LogFile)
    $null = New-Item -ItemType Directory -Path (Split-Path $script:logFile) -Force
    $marker = Join-Path $WorkRoot '.ironrdp-build-owner'
    if (-not (Test-Path -LiteralPath $marker)) {
        if (-not $Create) { throw 'Scenario resources are missing. Run prep first.' }
        if ((Test-Path -LiteralPath $WorkRoot) -and
            @(Get-ChildItem -LiteralPath $WorkRoot -Force).Count -ne 0) {
            throw "Refusing to adopt a nonempty working directory: $WorkRoot"
        }
        $null = New-Item -ItemType Directory -Path $WorkRoot -Force
        Set-Content -LiteralPath $marker -Value 'ironrdp_build:1' -Encoding ascii
    }
    Assert-IronRdpPath $marker
    if ((Get-Content -LiteralPath $marker -Raw).Trim() -ne 'ironrdp_build:1') {
        throw "Invalid scenario ownership marker: $marker"
    }
    $configPath = Join-Path $script:resourceRoot 'ironrdp_build.json'
    $config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
    $architecture = [Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString().ToLowerInvariant()
    $hostTriple = switch ($architecture) {
        'x64' { 'x86_64-pc-windows-msvc' }
        'arm64' { 'aarch64-pc-windows-msvc' }
        default { throw "Unsupported Windows architecture: $architecture" }
    }
    return @{
        Root = $WorkRoot
        Source = Join-Path $WorkRoot "source-$($config.revision)"
        Target = Join-Path $WorkRoot 'target'
        Data = Split-Path $script:logFile
        Config = $config
        ConfigHash = (Get-FileHash -LiteralPath $configPath -Algorithm SHA256).Hash
        Architecture = $architecture
        HostTriple = $hostTriple
        Toolchain = "$($config.rust_version)-$hostTriple"
        Receipt = Join-Path $WorkRoot 'prep.json'
        Active = Join-Path $WorkRoot 'active.json'
    }
}

function Lock-IronRdpWork {
    param($Context)
    $path = Join-Path $Context.Root 'work.lock'
    Assert-IronRdpPath $path
    try {
        return [IO.File]::Open($path, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    } catch [IO.IOException] {
        throw "The scenario working directory is busy: $($Context.Root)"
    }
}

function Register-IronRdpOwner {
    param($Context)
    Assert-IronRdpPath $Context.Active
    $owner = Get-Process -Id $PID
    @{ pid = $PID; start_ticks = $owner.StartTime.ToUniversalTime().Ticks; executable = $owner.Path } |
        ConvertTo-Json | Set-Content -LiteralPath "$($Context.Active).tmp" -Encoding utf8
    Move-Item -LiteralPath "$($Context.Active).tmp" -Destination $Context.Active -Force
}

function Remove-IronRdpTarget {
    param($Context)
    Assert-IronRdpPath $Context.Target
    if (Test-Path -LiteralPath $Context.Target) {
        $links = @(Get-ChildItem -LiteralPath $Context.Target -Recurse -Force -Attributes ReparsePoint)
        if ($links.Count) { throw 'Refusing to clean build output containing a reparse point.' }
        Remove-Item -LiteralPath $Context.Target -Recurse -Force
    }
}

function Get-IronRdpEnvironment {
    param($Context)
    return @{
        CARGO_HOME = Join-Path $Context.Root 'cargo-home'
        RUSTUP_HOME = Join-Path $Context.Root 'rustup-home'
        RUSTUP_TOOLCHAIN = $Context.Toolchain
        CARGO_TARGET_DIR = $Context.Target
        CARGO_INCREMENTAL = '0'
        CARGO_PROFILE_DEV_DEBUG = '0'
        CARGO_NET_OFFLINE = 'true'
        GIT_CONFIG_GLOBAL = Join-Path $Context.Root 'gitconfig'
        GIT_CONFIG_NOSYSTEM = '1'
        MSBUILDDISABLENODEREUSE = '1'
    }
}

function Get-IronRdpNativeTools {
    param($Context, [switch]$Install)
    $tools = @{}
    foreach ($package in $Context.Config.native_tools.($Context.Architecture)) {
        $directory = Join-Path $Context.Root "tools\$($package.name)-$($package.version)-$($Context.Architecture)"
        $executable = Join-Path $directory $package.executable
        Assert-IronRdpPath $directory
        Assert-IronRdpPath $executable
        if ($Install -and -not (Test-Path -LiteralPath $executable)) {
            $null = New-Item -ItemType Directory -Path (Split-Path $directory) -Force
            $archive = "$directory.zip"
            Assert-IronRdpPath $archive
            Assert-IronRdpPath "$archive.download"
            if (-not (Test-Path -LiteralPath $archive)) {
                Invoke-WebRequest -Uri $package.url -OutFile "$archive.download"
                if ((Get-FileHash "$archive.download" -Algorithm SHA256).Hash -ne $package.sha256) {
                    throw "$($package.name) archive checksum mismatch."
                }
                Move-Item -LiteralPath "$archive.download" -Destination $archive
            }
            if ((Get-FileHash $archive -Algorithm SHA256).Hash -ne $package.sha256) {
                throw "Cached $($package.name) archive checksum mismatch."
            }
            Expand-Archive -LiteralPath $archive -DestinationPath $directory -Force
        }
        if (-not (Test-Path -LiteralPath $executable)) {
            throw "Native $($package.name) is missing. Re-run prep."
        }
        $tools[$package.name] = $executable
    }
    return $tools
}

function Invoke-IronRdpProcess {
    param(
        [string]$Executable, [string[]]$Arguments, [string]$Directory,
        [hashtable]$Environment, [string]$OutputPrefix, [int]$TimeoutSeconds = 2400
    )
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = $Executable
    $start.WorkingDirectory = $Directory
    $start.UseShellExecute = $false
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    foreach ($argument in $Arguments) { $start.ArgumentList.Add($argument) }
    foreach ($key in @($start.Environment.Keys)) {
        if ($key -match '^(CARGO_|RUST|SCCACHE_|CC($|_)|CXX($|_)|CFLAGS($|_)|CXXFLAGS($|_)|AR($|_)|ARFLAGS($|_)|CL$|_CL_$|CMAKE($|_)|GH_TOKEN$|GITHUB_TOKEN$)') {
            $null = $start.Environment.Remove($key)
        }
    }
    foreach ($key in $Environment.Keys) { $start.Environment[$key] = $Environment[$key] }
    $stdout = [IO.File]::Create("$OutputPrefix.stdout.log")
    $stderr = [IO.File]::Create("$OutputPrefix.stderr.log")
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $start
    $started = $false
    try {
        $watch = [Diagnostics.Stopwatch]::StartNew()
        $started = $process.Start()
        if (-not $started) { throw "Could not start $Executable" }
        $outTask = $process.StandardOutput.BaseStream.CopyToAsync($stdout)
        $errTask = $process.StandardError.BaseStream.CopyToAsync($stderr)
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
            throw "Command timed out after ${TimeoutSeconds}s: $Executable"
        }
        $watch.Stop()
        $null = $outTask.GetAwaiter().GetResult()
        $null = $errTask.GetAwaiter().GetResult()
        if ($process.ExitCode -ne 0) {
            throw "Command exited $($process.ExitCode): $Executable. See $OutputPrefix.stderr.log"
        }
        return $watch.Elapsed.TotalSeconds
    } finally {
        if ($started -and -not $process.HasExited) {
            $process.Kill($true)
            $process.WaitForExit()
        }
        $stdout.Dispose()
        $stderr.Dispose()
        $process.Dispose()
    }
}

function getVSVersion {
    param([string]$Architecture)
    $candidates = @(
        "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe",
        "${env:ProgramFiles}\Microsoft Visual Studio\Installer\vswhere.exe"
    )
    $onPath = Get-Command vswhere.exe -ErrorAction SilentlyContinue
    if ($onPath) { $candidates = @($onPath.Source) + $candidates }
    $vswhere = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $vswhere) { return $null }
    $component = if ($Architecture -eq 'arm64') {
        'Microsoft.VisualStudio.Component.VC.Tools.ARM64'
    } else {
        'Microsoft.VisualStudio.Component.VC.Tools.x86.x64'
    }
    $instances = & $vswhere -latest -products '*' -requires $component -format json -utf8 | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0) { throw 'vswhere failed to discover Visual Studio.' }
    if (-not $instances) { return $null }
    return [pscustomobject]@{
        installationPath = $instances[0].installationPath
        installationVersion = $instances[0].installationVersion
        vswhere = $vswhere
    }
}

function Get-IronRdpVsEnvironment {
    param($Context, $VisualStudio)
    $devcmd = Join-Path $VisualStudio.installationPath 'Common7\Tools\VsDevCmd.bat'
    if (-not (Test-Path -LiteralPath $devcmd)) { throw "Visual Studio developer script is missing: $devcmd" }
    if ($devcmd -match '["%!\r\n]') { throw 'Unsupported command-shell characters in Visual Studio path.' }
    $discoveryPath = Split-Path $VisualStudio.vswhere
    if ($discoveryPath -match '["%!\r\n]') { throw 'Unsupported command-shell characters in vswhere path.' }
    log "Visual Studio: $($VisualStudio.installationPath) ($($VisualStudio.installationVersion))"
    $architecture = $Context.Architecture
    $lines = & $env:ComSpec /d /c "set `"PATH=$discoveryPath;%PATH%`" && call `"$devcmd`" -no_logo -arch=$architecture -host_arch=$architecture >nul && set"
    if ($LASTEXITCODE -ne 0) { throw 'Visual Studio native environment setup failed.' }
    $environment = @{}
    foreach ($line in $lines) {
        if ($line -match '^([^=]+)=(.*)$') { $environment[$Matches[1]] = $Matches[2] }
    }
    if ($environment.VSCMD_ARG_HOST_ARCH -ne $architecture -or $environment.VSCMD_ARG_TGT_ARCH -ne $architecture) {
        throw 'Visual Studio did not select the requested native host and target architecture.'
    }
    $cl = $environment.Path.Split(';') | ForEach-Object {
        if ($_) { Join-Path $_ 'cl.exe' }
    } | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $cl) { throw 'The native Visual C++ compiler is missing after environment setup.' }
    if (-not $cl.StartsWith($VisualStudio.installationPath + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'The compiler resolved from PATH belongs to a different Visual Studio installation.'
    }
    log "Native compiler: $cl"
    # Only import the developer environment changes, not inherited compiler overrides.
    $result = @{}
    foreach ($key in @('Path', 'INCLUDE', 'LIB', 'LIBPATH', 'VSINSTALLDIR', 'VCINSTALLDIR', 'WindowsSdkDir', 'WindowsSDKVersion')) {
        if ($environment.ContainsKey($key)) { $result[$key] = $environment[$key] }
    }
    $nativeTools = Get-IronRdpNativeTools $Context
    $cmake = $nativeTools.cmake
    $ninja = $nativeTools.ninja
    log "CMake: $cmake; Ninja: $ninja"
    # The pinned cmake crate otherwise requests host=x64 even on native ARM64.
    $result.CMAKE_GENERATOR = 'Ninja'
    $result.CMAKE = $cmake
    $result.CC = $cl
    $result.CXX = $cl
    $result.Path = (Split-Path $ninja) + ';' + (Split-Path $cmake) + ';' + $result.Path
    return $result
}

function Assert-IronRdpSource {
    param($Context, [string]$Git, [hashtable]$Environment)
    $prefix = Join-Path $Context.Data 'ironrdp_build_source_check'
    $null = Invoke-IronRdpProcess $Git @('-C', $Context.Source, 'rev-parse', 'HEAD') $Context.Root $Environment $prefix
    if ([IO.File]::ReadAllText("$prefix.stdout.log").Trim() -ne $Context.Config.revision) {
        throw 'IronRDP source revision does not match the pinned workload.'
    }
    $null = Invoke-IronRdpProcess $Git @('-C', $Context.Source, 'status', '--porcelain', '--untracked-files=all') $Context.Root $Environment $prefix
    if (-not [string]::IsNullOrWhiteSpace([IO.File]::ReadAllText("$prefix.stdout.log"))) {
        throw 'IronRDP source or lockfile was modified. Refusing to measure a different workload.'
    }
}
