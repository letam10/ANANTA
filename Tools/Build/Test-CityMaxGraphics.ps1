[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$qaPath = Join-Path $projectRoot 'Saved\QA\CityMaxGraphics'
New-Item -ItemType Directory -Path $qaPath -Force | Out-Null
$configPath = Join-Path $qaPath 'GameUserSettings.ini'
$settings = @'
[/Script/ANANTA.ANANTAGraphicsSettings]
Version=5
Language=vi
bShowFPS=True
bUseVSync=False
bUseDynamicResolution=False
ResolutionSizeX=1920
ResolutionSizeY=1080
LastUserConfirmedResolutionSizeX=1920
LastUserConfirmedResolutionSizeY=1080
FullscreenMode=2
LastConfirmedFullscreenMode=2
FrameRateLimit=90.000000

[ScalabilityGroups]
sg.ResolutionQuality=100.000000
sg.ViewDistanceQuality=3
sg.AntiAliasingQuality=3
sg.ShadowQuality=3
sg.GlobalIlluminationQuality=3
sg.ReflectionQuality=3
sg.PostProcessQuality=3
sg.TextureQuality=3
sg.EffectsQuality=3
sg.FoliageQuality=3
sg.ShadingQuality=3
'@
[IO.File]::WriteAllText($configPath, $settings, [Text.UTF8Encoding]::new($false))
$logPath = Join-Path $projectRoot 'Saved\Logs\CityMaxGraphics.log'
$consolePath = Join-Path $projectRoot 'Saved\Logs\CityMaxGraphicsConsole.log'
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$arguments = @(
    "$projectRoot\ANANTA.uproject", '/Game/ANANTA/Maps/ANANTA_City',
    '-game', '-RenderOffscreen', '-windowed', '-ForceRes', '-ResX=1920', '-ResY=1080',
    '-CityServiceCheck', '-CityObserveGraphics', '-CityQASlot', "-GameUserSettingsINI=$configPath",
    '-NoSplash', '-nosound', '-unattended', "-abslog=$logPath"
)
& $editorPath @arguments *> $consolePath
if ($LASTEXITCODE -ne 0) {
    throw "Max graphics gameplay failed: $LASTEXITCODE. See $logPath"
}
$log = Get-Content -LiteralPath $logPath -Raw
if (-not $log.Contains('CITY_SERVICE_JOURNEY_FINISH mode=Check success=1') -or
    -not $log.Contains('CITY_GRAPHICS_OBSERVATION_WRITTEN')) {
    throw "Required gameplay or observation evidence missing: $logPath"
}
Copy-Item -LiteralPath (Join-Path $projectRoot 'Saved\QA\CityServiceJourney\Report.txt') -Destination $qaPath
Write-Output "CITY_MAX_GRAPHICS_OBSERVED $qaPath"
