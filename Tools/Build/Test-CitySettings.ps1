[CmdletBinding()]
param(
    [switch]$Reload,
    [ValidateSet(720, 1080)]
    [int]$Height = 1080,
    [string]$ExecutablePath,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$mode = if ($Reload) { 'Reload' } else { 'Check' }
$variant = if ($ExecutablePath) { 'Packaged' } else { '' }
$qaPath = Join-Path $projectRoot "Saved\QA\CitySettings$variant"
New-Item -ItemType Directory -Path $qaPath -Force | Out-Null
$configPath = Join-Path $qaPath 'GameUserSettings.ini'
$logPath = Join-Path $projectRoot "Saved\Logs\CitySettings$variant$mode.log"
$consolePath = Join-Path $projectRoot "Saved\Logs\CitySettings$variant${mode}Console.log"
$width = if ($Height -eq 720) { 1280 } else { 1920 }
if ($Reload -and -not (Test-Path -LiteralPath $configPath)) {
    throw 'Run Settings Check before Reload'
}
$arguments = @(
    '-RenderOffscreen', '-windowed', '-ForceRes',
    "-ResX=$width", "-ResY=$Height", "-CitySettings$mode", '-CityQASlot',
    "-GameUserSettingsINI=$configPath", '-NoSplash', '-nosound', '-unattended', "-abslog=$logPath"
)
if ($ExecutablePath) {
    $ExecutablePath = (Resolve-Path -LiteralPath $ExecutablePath).Path
    $errorPath = Join-Path $qaPath "${mode}Error.log"
    $process = Start-Process -FilePath $ExecutablePath -ArgumentList $arguments -WindowStyle Hidden `
        -WorkingDirectory (Split-Path $ExecutablePath) -RedirectStandardOutput $consolePath `
        -RedirectStandardError $errorPath -PassThru -Wait
    $code = $process.ExitCode
} else {
    $arguments = @("$projectRoot\ANANTA.uproject", '/Game/ANANTA/Maps/ANANTA_City', '-game') + $arguments
    & $editorPath @arguments *> $consolePath
    $code = $LASTEXITCODE
}
if ($code -ne 0) {
    throw "Settings $mode process failed: $code. See $logPath"
}
$log = Get-Content -LiteralPath $logPath -Raw
if (-not $log.Contains("CITY_SETTINGS_FINISH mode=$mode success=1")) {
    throw "Settings $mode completion marker missing: $logPath"
}
if ($ExecutablePath -and -not $log.Contains('Bringing World /Game/ANANTA/Maps/ANANTA_City')) {
    throw 'Packaged default map was not the city'
}
Write-Output "CITY_SETTINGS_OK variant=$variant mode=$mode resolution=${width}x$Height log=$logPath"
