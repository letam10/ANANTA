[CmdletBinding()]
param(
    [ValidateSet('Capture', 'InputSmoke', 'MissionCheck', 'MissionReload', 'NavigationCheck',
        'ServiceCheck', 'ServiceReload', 'StreamingCheck')]
    [string]$Mode = 'Capture',
    [switch]$BlueHour,
    [switch]$ExpansionViews,
    [switch]$DressingViews,
    [switch]$FinishingViews,
    [switch]$FixtureViews,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$lightingSuffix = if ($BlueHour) { 'BlueHour' } else { '' }
$logPath = Join-Path $projectRoot "Saved\Logs\CityGPU$Mode$lightingSuffix.log"
$consolePath = Join-Path $projectRoot "Saved\Logs\CityGPU$Mode${lightingSuffix}Console.log"
$arguments = @(
    "$projectRoot\ANANTA.uproject",
    '/Game/ANANTA/Maps/ANANTA_City',
    '-game',
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
& $editorPath @arguments *> $consolePath
$code = $LASTEXITCODE
Write-Output "CITY_GPU_EXIT=$code MODE=$Mode LOG=$logPath"
if ($code -ne 0) {
    throw "City GPU check failed: $code. See $logPath"
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
$log = Get-Content -LiteralPath $logPath -Raw
if (-not $log.Contains($markers[$Mode])) {
    throw "City GPU $Mode completion marker is missing. See $logPath"
}
if ($Mode -eq 'Capture') {
    $captureName = if ($DressingViews) { 'CityDressing' } else { 'CityGPU' }
    if ($FinishingViews) {
        $captureName = 'CityFinishing'
    }
    if ($FixtureViews) {
        $captureName = 'CityFixtures'
    }
    $env:ANANTA_CITY_CAPTURE_DIR = Join-Path $projectRoot "Saved\QA\$captureName$lightingSuffix"
    python -c @'
import os
from pathlib import Path
from PIL import Image
files = sorted(Path(os.environ['ANANTA_CITY_CAPTURE_DIR']).glob('View_*.png'))
assert len(files) == 8, files
for path in files:
    size = Image.open(path).size
    assert size == (1920, 1080), (path, size)
print('CITY_CAPTURE_RESOLUTION_OK 8 images 1920x1080')
'@
    if ($LASTEXITCODE -ne 0) {
        throw 'GPU capture resolution verification failed'
    }
}
