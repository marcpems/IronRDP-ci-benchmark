# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

#Requires -Version 7.2
param([string]$workRoot = '', [string]$logFile = '', [switch]$SkipSystemInstall)

. "$PSScriptRoot\ironrdp_build_common.ps1"
$lock = $null
try {
    $context = Initialize-IronRdpContext $workRoot $logFile 'prep' -Create
    $lock = Lock-IronRdpWork $context
    Register-IronRdpOwner $context
    if (Test-Path -LiteralPath $context.Receipt) { Remove-Item -LiteralPath $context.Receipt }
    $environment = Get-IronRdpEnvironment $context
    Set-Content -LiteralPath $environment.GIT_CONFIG_GLOBAL -Value '' -Encoding ascii
    foreach ($dependency in @(@('git', 'Git.Git'), @('nasm', 'NASM.NASM'), @('clang-cl', 'LLVM.LLVM'))) {
        if ($dependency[0] -eq 'nasm' -and $context.Architecture -eq 'arm64') { continue }
        if ($dependency[0] -eq 'clang-cl' -and $context.Architecture -ne 'arm64') { continue }
        $command = Get-Command $dependency[0] -ErrorAction SilentlyContinue
        if (-not $command) {
            if ($SkipSystemInstall) { throw "Missing $($dependency[0]); system installation is disabled." }
            $winget = Get-Command winget -ErrorAction Stop
            $architectureArgument = if ($dependency[0] -eq 'clang-cl') { @('--architecture', 'arm64') } else { @() }
            & $winget.Source install --exact --id $dependency[1] --silent --accept-package-agreements --accept-source-agreements --disable-interactivity @architectureArgument
            if ($LASTEXITCODE -ne 0) { throw "Installing $($dependency[1]) failed ($LASTEXITCODE)." }
            $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
                [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + $env:Path
            $command = Get-Command $dependency[0] -ErrorAction Stop
        }
        log "$($dependency[0]): $($command.Source)"
    }
    $git = (Get-Command git -ErrorAction Stop).Source
    $vs = getVSVersion $context.Architecture
    if (-not $vs) {
        if ($SkipSystemInstall) { throw 'Native Visual C++ tools are missing; system installation is disabled.' }
        $package = if ($context.Architecture -eq 'arm64') { 'Microsoft.VisualStudio.2022.Community' } else { 'Microsoft.VisualStudio.2022.BuildTools' }
        $workload = if ($context.Architecture -eq 'arm64') { 'Microsoft.VisualStudio.Workload.NativeDesktop' } else { 'Microsoft.VisualStudio.Workload.VCTools' }
        & winget install --exact --id $package --silent --accept-package-agreements --accept-source-agreements --disable-interactivity --override "--quiet --wait --norestart --add $workload --includeRecommended"
        if ($LASTEXITCODE -ne 0) { throw "Installing Visual Studio failed ($LASTEXITCODE)." }
        $vs = getVSVersion $context.Architecture
        if (-not $vs) { throw 'Native Visual C++ tools remain unavailable after installation.' }
    }
    $nativeTools = Get-IronRdpNativeTools $context -Install
    $vsEnvironment = Get-IronRdpVsEnvironment $context $vs
    foreach ($key in $vsEnvironment.Keys) { $environment[$key] = $vsEnvironment[$key] }
    $bootstrap = Join-Path $context.Root "bootstrap-$($context.Config.rustup_version)"
    Assert-IronRdpPath $bootstrap
    $null = New-Item -ItemType Directory -Path $bootstrap -Force
    $rustup = Join-Path $bootstrap 'rustup.exe'
    if (-not (Test-Path -LiteralPath $rustup)) {
        $url = "https://static.rust-lang.org/rustup/archive/$($context.Config.rustup_version)/$($context.HostTriple)/rustup-init.exe"
        Invoke-WebRequest -Uri $url -OutFile "$rustup.download"
        if ((Get-FileHash "$rustup.download" -Algorithm SHA256).Hash -ne $context.Config.rustup_sha256.($context.HostTriple)) {
            throw 'Rustup bootstrap checksum mismatch.'
        }
        Move-Item -LiteralPath "$rustup.download" -Destination $rustup
    }
    if ((Get-FileHash $rustup -Algorithm SHA256).Hash -ne $context.Config.rustup_sha256.($context.HostTriple)) {
        throw 'The cached Rustup bootstrap checksum does not match.'
    }
    log "Installing isolated Rust $($context.Toolchain); no shared Rust installation or PATH is changed."
    $prefix = Join-Path $context.Data 'ironrdp_build_toolchain'
    $null = Invoke-IronRdpProcess $rustup @('toolchain', 'install', $context.Toolchain, '--profile', 'minimal', '--no-self-update') $context.Root $environment $prefix
    $tools = @{}
    foreach ($tool in @('cargo', 'rustc', 'rustdoc')) {
        $null = Invoke-IronRdpProcess $rustup @('which', '--toolchain', $context.Toolchain, $tool) $context.Root $environment $prefix
        $tools[$tool] = (Get-Content "$prefix.stdout.log" -Raw).Trim()
        if (-not (Test-Path -LiteralPath $tools[$tool])) { throw "Missing isolated $tool executable." }
        log "${tool}: $($tools[$tool])"
    }
    foreach ($tool in $nativeTools.Keys) {
        $tools[$tool] = $nativeTools[$tool]
        $null = Invoke-IronRdpProcess $tools[$tool] @('--version') $context.Root $environment (Join-Path $context.Data "ironrdp_build_${tool}_identity")
    }
    if ($context.Architecture -eq 'arm64') {
        $tools['clang-cl'] = (Get-Command clang-cl -ErrorAction Stop).Source
        $null = Invoke-IronRdpProcess $tools['clang-cl'] @('--version') $context.Root $environment (Join-Path $context.Data 'ironrdp_build_clang_identity')
    }
    $environment.RUSTC = $tools.rustc
    $environment.RUSTDOC = $tools.rustdoc
    $environment.Path = (Split-Path $tools.rustc) + ';' + $environment.Path
    $prefix = Join-Path $context.Data 'ironrdp_build_rustc_identity'
    $null = Invoke-IronRdpProcess $tools.rustc @('-vV') $context.Root $environment $prefix
    $identity = Get-Content "$prefix.stdout.log" -Raw
    if ($identity -notmatch "(?m)^host: $([regex]::Escape($context.HostTriple))\r?$" -or
        $identity -notmatch "(?m)^release: $([regex]::Escape($context.Config.rust_version))\r?$") {
        throw 'Installed rustc does not match the pinned release and native host.'
    }
    Assert-IronRdpPath $context.Source
    if (-not (Test-Path -LiteralPath $context.Source)) {
        $prefix = Join-Path $context.Data 'ironrdp_build_fetch_source'
        $null = Invoke-IronRdpProcess $git @('init', '--quiet', $context.Source) $context.Root $environment $prefix
        $null = Invoke-IronRdpProcess $git @('-C', $context.Source, 'config', 'core.autocrlf', 'false') $context.Root $environment $prefix
        $null = Invoke-IronRdpProcess $git @('-C', $context.Source, 'config', 'core.longpaths', 'true') $context.Root $environment $prefix
    }
    $prefix = Join-Path $context.Data 'ironrdp_build_fetch_source'
    $null = Invoke-IronRdpProcess $git @('-C', $context.Source, 'fetch', '--depth', '1', $context.Config.source, $context.Config.revision) $context.Root $environment $prefix
    $null = Invoke-IronRdpProcess $git @('-C', $context.Source, 'checkout', '--detach', $context.Config.revision) $context.Root $environment $prefix
    Assert-IronRdpSource $context $git $environment
    $environment.CARGO_NET_OFFLINE = 'false'
    $prefix = Join-Path $context.Data 'ironrdp_build_fetch_dependencies'
    $null = Invoke-IronRdpProcess $tools.cargo @('fetch', '--locked', '--target', $context.HostTriple) $context.Source $environment $prefix
    Assert-IronRdpSource $context $git $environment
    $toolHashes = @{}
    foreach ($tool in $tools.Keys) { $toolHashes[$tool] = (Get-FileHash $tools[$tool] -Algorithm SHA256).Hash }
    @{
        config_sha256 = $context.ConfigHash
        architecture = $context.Architecture
        host_triple = $context.HostTriple
        toolchain = $context.Toolchain
        tools = $tools
        tool_sha256 = $toolHashes
        git = $git
        visual_studio = $vs
        lock_sha256 = (Get-FileHash (Join-Path $context.Source 'Cargo.lock') -Algorithm SHA256).Hash
    } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $context.Receipt -Encoding utf8
    log 'IronRDP build prep completed.'
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
