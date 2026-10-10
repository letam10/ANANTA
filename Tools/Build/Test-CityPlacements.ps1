[CmdletBinding()]
param(
    [ValidateSet('metro', 'small', 'facilities')]
    [string]$Scope = 'metro',
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
& python (Join-Path $projectRoot 'Tools\QA\PrepareCityPlacementViews.py') --scope $Scope
if ($LASTEXITCODE -ne 0) {
    throw 'Placement camera preparation failed'
}
$qaDirectory = Join-Path $projectRoot "Saved\QA\CityPlacement_$Scope"
$manifest = Join-Path $qaDirectory 'Manifest.json'
$qaConfig = Join-Path $qaDirectory 'GameUserSettings.ini'
Copy-Item -LiteralPath (Join-Path $projectRoot 'Config\DefaultGameUserSettings.ini') -Destination $qaConfig
$settings = Get-Content -LiteralPath $qaConfig -Raw
$settings = $settings.Replace('[/Script/Engine.GameUserSettings]', '[/Script/ANANTA.ANANTAGraphicsSettings]')
$settings = $settings -replace 'sg\.ResolutionQuality=[0-9.]+', 'sg.ResolutionQuality=100'
$settings = $settings -replace '(sg\.[A-Za-z]+Quality)=\d+', '${1}=3'
Set-Content -LiteralPath $qaConfig -Value $settings -Encoding ASCII
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$logPath = Join-Path $projectRoot "Saved\Logs\CityPlacement_$Scope.log"
$arguments = @(
    "$projectRoot\ANANTA.uproject",
    '/Game/ANANTA/Maps/ANANTA_City',
    '-game',
    '-RenderOffscreen',
    '-windowed',
    '-ForceRes',
    '-ResX=1920',
    '-ResY=1080',
    '-CityCapture',
    '-CityQASlot',
    "-CityPlacementViews=$manifest",
    "-GameUserSettingsINI=$qaConfig",
    '-NoSplash',
    '-nosound',
    '-unattended',
    "-abslog=$logPath"
)
& $editorPath @arguments *> (Join-Path $projectRoot "Saved\Logs\CityPlacement_${Scope}Console.log")
if ($LASTEXITCODE -ne 0) {
    throw "Placement GPU capture failed: $LASTEXITCODE"
}
if (-not (Get-Content -LiteralPath $logPath -Raw).Contains('CITY_CAPTURE_FINISH success=1')) {
    throw 'Placement capture completion marker missing'
}
$env:ANANTA_PLACEMENT_MANIFEST = $manifest
& python -c @'
import json
import os
from pathlib import Path
from PIL import Image
path = Path(os.environ['ANANTA_PLACEMENT_MANIFEST'])
data = json.loads(path.read_text(encoding='utf-8'))
for view in data['views']:
    image = path.parent / view['image']
    assert image.is_file(), image
    assert Image.open(image).size == (1920, 1080), image
print('CITY_PLACEMENT_CAPTURE_OK', len(data['views']))
'@
if ($LASTEXITCODE -ne 0) {
    throw 'Placement images missing or wrong resolution'
}
