param(
    [Parameter(Mandatory)][ValidateSet('x64', 'arm64')][string]$Architecture,
    [Parameter(Mandatory)][string]$Script,
    [Parameter(ValueFromRemainingArguments)][string[]]$ScriptArgs
)
$ErrorActionPreference = 'Stop'
$vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
$vs = & $vswhere -latest -products '*' -property installationPath
if (-not $vs) { throw 'Visual Studio installation missing' }
$vcvars = Join-Path $vs 'VC\Auxiliary\Build\vcvarsall.bat'
$archArg = if ($Architecture -eq 'x64') { 'amd64' } else { 'arm64' }
$python = (Get-Command python).Source
$quoted = ($ScriptArgs | ForEach-Object { '"' + $_ + '"' }) -join ' '
& $env:ComSpec /d /s /c "call `"$vcvars`" $archArg >nul && `"$python`" `"$Script`" $quoted"
if ($LASTEXITCODE -ne 0) { throw "Experiment failed with exit code $LASTEXITCODE" }
