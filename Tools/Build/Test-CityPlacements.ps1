[CmdletBinding()]
param(
    [ValidateSet('metro', 'small', 'facilities')]
    [string]$Scope = 'metro',
    [ValidateSet('All', 'Rowboat')]
    [string]$Asset = 'All',
    [ValidateSet('None', 'NaniteShadowAsyncOn', 'Dred')]
    [string]$Diagnostic = 'None',
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if ($Asset -ne 'All' -and $Scope -ne 'metro') {
    throw 'Selected asset capture requires metro scope'
}
& python (Join-Path $projectRoot 'Tools\QA\PrepareCityPlacementViews.py') `
    --scope $Scope --asset $Asset --diagnostic $Diagnostic
if ($LASTEXITCODE -ne 0) {
    throw 'Placement camera preparation failed'
}
$suffix = if ($Asset -eq 'All') { '' } else { "_$Asset" }
$suffix += if ($Diagnostic -eq 'None') { '' } else { "_$Diagnostic" }
$qaDirectory = Join-Path $projectRoot "Saved\QA\CityPlacement_$Scope$suffix"
$manifest = Join-Path $qaDirectory 'Manifest.json'
$qaConfig = Join-Path $qaDirectory 'GameUserSettings.ini'
Copy-Item -LiteralPath (Join-Path $projectRoot 'Config\DefaultGameUserSettings.ini') -Destination $qaConfig
$settings = Get-Content -LiteralPath $qaConfig -Raw
$settings = $settings.Replace('[/Script/Engine.GameUserSettings]', '[/Script/ANANTA.ANANTAGraphicsSettings]')
$settings = $settings -replace '(sg\.[A-Za-z]+Quality)=\d+', '${1}=3'
$settings = $settings -replace 'sg\.ResolutionQuality=[0-9.]+', 'sg.ResolutionQuality=100'
Set-Content -LiteralPath $qaConfig -Value $settings -Encoding ASCII
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$logPath = Join-Path $projectRoot "Saved\Logs\CityPlacement_$Scope$suffix.log"
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
if ($Diagnostic -eq 'NaniteShadowAsyncOn') {
    $arguments += '-ForceDPCVars=r.Nanite.AsyncRasterization.ShadowDepths=1'
    'Shadow async diagnostic only; production graphics acceptance remains pending.' |
        Set-Content -LiteralPath (Join-Path $qaDirectory 'Diagnostic.txt')
} elseif ($Diagnostic -eq 'Dred') {
    $arguments += '-dred'
    $arguments += '-ini:Engine:[SystemSettings]:D3D12.TrackAllAllocations=1'
    'DRED and allocation tracking only; not Max performance or GPU stability acceptance.' |
        Set-Content -LiteralPath (Join-Path $qaDirectory 'Diagnostic.txt')
}
& $editorPath @arguments *> (Join-Path $projectRoot "Saved\Logs\CityPlacement_${Scope}${suffix}Console.log")
if ($LASTEXITCODE -ne 0) {
    throw "Placement GPU capture failed: $LASTEXITCODE"
}
if (-not (Get-Content -LiteralPath $logPath -Raw).Contains('CITY_CAPTURE_FINISH success=1')) {
    throw 'Placement capture completion marker missing'
}
. (Join-Path $PSScriptRoot 'CityPlacementDiagnostics.ps1')
# Anh 1080p van co the render scale thap; gate doc gia tri thuc sau scalability.
$renderConfig = Get-Content -LiteralPath (Join-Path $qaDirectory 'RenderConfig.txt')
if ($Diagnostic -eq 'Dred') {
    Assert-CityPlacementDred -Log (Get-Content -LiteralPath $logPath -Raw) -RenderConfig $renderConfig
}
if ($Diagnostic -eq 'NaniteShadowAsyncOn' -and
    -not $renderConfig.Contains('r.Nanite.AsyncRasterization.ShadowDepths=1')) {
    throw 'Shadow async diagnostic did not reach the observed render configuration'
}
foreach ($name in @('sg.ResolutionQuality', 'r.ScreenPercentage')) {
    $entry = @($renderConfig | Where-Object { $_.StartsWith("$name=") })
    if ($entry.Count -ne 1) {
        throw "Placement render config is missing $name"
    }
    $actual = [double]::Parse($entry[0].Substring($name.Length + 1), [Globalization.CultureInfo]::InvariantCulture)
    if ([Math]::Abs($actual - 100) -gt 0.001) {
        throw "Placement capture is not native 100%: $name=$actual"
    }
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
& python (Join-Path $projectRoot 'Tools\QA\BuildCityPlacementContacts.py') `
    --scope $Scope --asset $Asset --diagnostic $Diagnostic
if ($LASTEXITCODE -ne 0) {
    throw 'Placement contact generation failed'
}
