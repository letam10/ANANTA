[CmdletBinding()]
param(
    [string]$ExecutablePath,
    [ValidateSet('Capture', 'InputSmoke', 'MissionCheck', 'MissionReload', 'NavigationCheck',
        'ServiceCheck', 'ServiceReload', 'StreamingCheck')]
    [string]$Mode = 'InputSmoke',
    [switch]$BlueHour,
    [switch]$ExpansionViews,
    [switch]$DressingViews,
    [switch]$FinishingViews,
    [switch]$FixtureViews
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if ([string]::IsNullOrWhiteSpace($ExecutablePath)) {
    $ExecutablePath = Join-Path $projectRoot 'Saved\Builds\City\Windows\ANANTA\Binaries\Win64\ANANTA.exe'
}
if (-not (Test-Path -LiteralPath $ExecutablePath -PathType Leaf)) {
    throw "Missing packaged executable: $ExecutablePath"
}
if ($BlueHour -and $Mode -ne 'Capture') {
    throw 'BlueHour is supported only for Capture.'
}
$ExecutablePath = (Resolve-Path -LiteralPath $ExecutablePath).Path
$lightingSuffix = if ($BlueHour) { 'BlueHour' } else { '' }
$logDirectory = Join-Path $projectRoot 'Saved\Logs'
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
$logPath = Join-Path $logDirectory "CityPackaged$Mode$lightingSuffix.log"
$consolePath = Join-Path $logDirectory "CityPackaged$Mode${lightingSuffix}Console.log"
$errorPath = Join-Path $logDirectory "CityPackaged$Mode${lightingSuffix}Error.log"
$arguments = @(
    '-RenderOffscreen',
    '-windowed',
    '-ForceRes',
    '-ResX=1920',
    '-ResY=1080',
    "-City$Mode",
    '-CityQASlot',
    '-NoSplash',
    '-nosound',
    '-unattended',
    "-abslog=$logPath"
)
if ($BlueHour) {
    $arguments += '-CityBlueHour'
}
if ($ExpansionViews) {
    $arguments += '-CityExpansionViews'
}
if ($DressingViews) {
    $arguments += '-CityDressingViews'
}
if ($FinishingViews) {
    $arguments += '-CityFinishingViews'
}
if ($FixtureViews) {
    $arguments += '-CityFixtureViews'
}
$markers = @{
    Capture = 'CITY_CAPTURE_FINISH success=1'
    InputSmoke = 'CITY_INPUT_SMOKE_FINISH success=1'
    MissionCheck = 'CITY_MISSION_CHECK_FINISH mode=Check success=1'
    MissionReload = 'CITY_MISSION_CHECK_FINISH mode=Reload success=1'
    NavigationCheck = 'CITY_NAVIGATION_CHECK_FINISH success=1'
    ServiceCheck = 'CITY_SERVICE_JOURNEY_FINISH mode=Check success=1'
    ServiceReload = 'CITY_SERVICE_JOURNEY_FINISH mode=Reload success=1'
    StreamingCheck = 'CITY_STREAMING_JOURNEY_FINISH success=1'
}
# Khong truyen ten map: can kiem tra chinh cau hinh khoi dong da cook.
Push-Location (Split-Path -Parent $ExecutablePath)
try {
    $process = Start-Process -FilePath $ExecutablePath -ArgumentList $arguments -WindowStyle Hidden `
        -RedirectStandardOutput $consolePath -RedirectStandardError $errorPath -Wait -PassThru
    $code = $process.ExitCode
}
finally {
    Pop-Location
}
if ($code -ne 0) {
    throw "Packaged $Mode failed with exit code $code. See $logPath"
}
$log = Get-Content -LiteralPath $logPath -Raw
if ($log -notmatch 'Bringing World /Game/ANANTA/Maps/ANANTA_City') {
    throw "Packaged game did not load the city as its default map. See $logPath"
}
if (-not $log.Contains($markers[$Mode])) {
    throw "Packaged $Mode completion marker is missing. See $logPath"
}
Write-Output "CITY_PACKAGED_QA_OK MODE=$Mode EXE=$ExecutablePath LOG=$logPath"
