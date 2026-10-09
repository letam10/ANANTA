[CmdletBinding()]
param(
    [string]$ExecutablePath,
    [switch]$ProfileRender,
    [ValidateSet('None', 'NonNaniteBatchOff', 'VsmOff', 'NaniteAsyncOff', 'NaniteReservedOff')]
    [string]$Diagnostic = 'None',
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$variant = if ($ExecutablePath) { 'Packaged' } else { '' }
if ($ProfileRender) {
    $variant += 'Profile'
}
if ($Diagnostic -ne 'None') {
    $variant += $Diagnostic
}
$qaPath = Join-Path $projectRoot "Saved\QA\CityMaxGraphics$variant"
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
$logPath = Join-Path $projectRoot "Saved\Logs\CityMaxGraphics$variant.log"
$consolePath = Join-Path $projectRoot "Saved\Logs\CityMaxGraphics${variant}Console.log"
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$arguments = @(
    '-RenderOffscreen', '-windowed', '-ForceRes', '-ResX=1920', '-ResY=1080',
    '-CityServiceCheck', '-CityObserveGraphics', '-CityQASlot', "-GameUserSettingsINI=$configPath",
    '-NoSplash', '-nosound', '-unattended', "-abslog=$logPath"
)
if ($ProfileRender) {
    $arguments += '-CityProfileRender'
}
if ($Diagnostic -ne 'None') {
    # Chi chan doan duong render gay PageFault; khong tinh la Max mac dinh.
    $override = if ($Diagnostic -eq 'VsmOff') {
        'r.Shadow.Virtual.Enable=0'
    } elseif ($Diagnostic -eq 'NaniteAsyncOff') {
        'r.Nanite.AsyncRasterization=0'
    } elseif ($Diagnostic -eq 'NaniteReservedOff') {
        'r.Nanite.Streaming.ReservedResources=0'
    } else {
        'r.Shadow.Virtual.NonNanite.Batch=0'
    }
    $arguments += "-ForceDPCVars=$override"
    "Diagnostic override: $override; not stock-Max acceptance." |
        Set-Content -LiteralPath (Join-Path $qaPath 'Diagnostic.txt')
}
if ($ExecutablePath) {
    $ExecutablePath = (Resolve-Path -LiteralPath $ExecutablePath).Path
    $errorPath = Join-Path $qaPath 'Error.log'
    $process = Start-Process -FilePath $ExecutablePath -ArgumentList $arguments -WindowStyle Hidden `
        -WorkingDirectory (Split-Path $ExecutablePath) -RedirectStandardOutput $consolePath `
        -RedirectStandardError $errorPath -PassThru -Wait
    $code = $process.ExitCode
    $savedRoot = [IO.Path]::GetFullPath((Join-Path (Split-Path $ExecutablePath) '..\..\Saved'))
} else {
    $arguments = @("$projectRoot\ANANTA.uproject", '/Game/ANANTA/Maps/ANANTA_City', '-game') + $arguments
    & $editorPath @arguments *> $consolePath
    $code = $LASTEXITCODE
    $savedRoot = Join-Path $projectRoot 'Saved'
}
if ($code -ne 0) {
    throw "Max graphics gameplay failed: $code. See $logPath"
}
$log = Get-Content -LiteralPath $logPath -Raw
if (-not $log.Contains('CITY_SERVICE_JOURNEY_FINISH mode=Check success=1') -or
    -not $log.Contains('CITY_GRAPHICS_OBSERVATION_WRITTEN')) {
    throw "Required gameplay or observation evidence missing: $logPath"
}
Copy-Item -LiteralPath (Join-Path $savedRoot 'QA\CityServiceJourney\Report.txt') -Destination $qaPath
if ($ExecutablePath -or $Diagnostic -ne 'None') {
    foreach ($name in @('FrameTimes.csv', 'RenderConfig.txt')) {
        Copy-Item -LiteralPath (Join-Path $savedRoot "QA\CityMaxGraphics\$name") -Destination $qaPath
    }
}
Write-Output "CITY_MAX_GRAPHICS_OBSERVED $qaPath"
