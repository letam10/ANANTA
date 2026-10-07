[CmdletBinding()]
param(
    [ValidateSet('Capture', 'InputSmoke', 'MissionCheck', 'MissionReload', 'NavigationCheck',
        'ServiceCheck', 'ServiceReload')]
    [string]$Mode = 'Capture',
    [switch]$BlueHour,
    [switch]$ExpansionViews,
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
& $editorPath @arguments *> $consolePath
$code = $LASTEXITCODE
Write-Output "CITY_GPU_EXIT=$code MODE=$Mode LOG=$logPath"
if ($code -ne 0) {
    throw "City GPU check failed: $code. See $logPath"
}
if ($Mode -eq 'Capture') {
    $env:ANANTA_CITY_CAPTURE_DIR = Join-Path $projectRoot "Saved\QA\CityGPU$lightingSuffix"
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
