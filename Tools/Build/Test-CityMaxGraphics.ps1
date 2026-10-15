[CmdletBinding()]
param(
    [string]$ExecutablePath,
    [switch]$ProfileRender,
    [ValidateSet('None', 'NonNaniteBatchOff', 'VsmOff', 'NaniteAsyncOff',
        'NaniteReservedOff', 'NaniteShadowAsyncOn', 'Dred')]
    [string]$Diagnostic = 'None',
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [ValidateSet('Base', 'GI32', 'Reflections4', 'VsmBias0')]
    [string]$QualityTrial = 'Base'
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'CityGraphicsTrialEvidence.ps1')
if ($QualityTrial -ne 'Base' -and (-not $ExecutablePath -or $ProfileRender -or $Diagnostic -ne 'None')) {
    throw 'Non-Base quality trials require a packaged executable without diagnostic/profile switches.'
}
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$variant = if ($ExecutablePath) { 'Packaged' } else { '' }
if ($ProfileRender) {
    $variant += 'Profile'
}
if ($Diagnostic -ne 'None') {
    $variant += $Diagnostic
}
if ($QualityTrial -ne 'Base') {
    $runId = [datetime]::UtcNow.ToString('yyyyMMddTHHmmssfff') + '-' + [guid]::NewGuid().ToString('N')
    $variant += "$QualityTrial-$runId"
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
if ($Diagnostic -eq 'Dred') {
    $arguments += '-dred'
    $arguments += '-ini:Engine:[SystemSettings]:D3D12.TrackAllAllocations=1'
    'DRED and allocation tracking only; not Max performance acceptance.' |
        Set-Content -LiteralPath (Join-Path $qaPath 'Diagnostic.txt')
} elseif ($Diagnostic -ne 'None') {
    # Chi chan doan duong render gay PageFault; khong tinh la Max mac dinh.
    $override = if ($Diagnostic -eq 'VsmOff') {
        'r.Shadow.Virtual.Enable=0'
    } elseif ($Diagnostic -eq 'NaniteAsyncOff') {
        'r.Nanite.AsyncRasterization=0'
    } elseif ($Diagnostic -eq 'NaniteShadowAsyncOn') {
        'r.Nanite.AsyncRasterization.ShadowDepths=1'
    } elseif ($Diagnostic -eq 'NaniteReservedOff') {
        'r.Nanite.Streaming.ReservedResources=0'
    } else {
        'r.Shadow.Virtual.NonNanite.Batch=0'
    }
    $arguments += "-ForceDPCVars=$override"
    "Diagnostic override: $override; not stock-Max acceptance." |
        Set-Content -LiteralPath (Join-Path $qaPath 'Diagnostic.txt')
}
if ($QualityTrial -ne 'Base') {
    $trialOverrides = @{
        GI32 = 'r.Lumen.ScreenProbeGather.DownsampleFactor=32'
        Reflections4 = 'r.Lumen.Reflections.DownsampleFactor=4'
        VsmBias0 = 'r.Shadow.Virtual.ResolutionLodBiasDirectional=0'
    }
    $arguments += "-ForceDPCVars=$($trialOverrides[$QualityTrial])"
}
$artifactFingerprint = $null
if ($ExecutablePath) {
    $ExecutablePath = (Resolve-Path -LiteralPath $ExecutablePath).Path
    $artifactFingerprint = Get-CityPackageFingerprint $ExecutablePath
    $savedRoot = [IO.Path]::GetFullPath((Join-Path (Split-Path $ExecutablePath) '..\..\Saved'))
} else {
    $arguments = @("$projectRoot\ANANTA.uproject", '/Game/ANANTA/Maps/ANANTA_City', '-game') + $arguments
    $savedRoot = Join-Path $projectRoot 'Saved'
}
$snapshot = @(Get-CityQASlotSnapshot $savedRoot)
$trial = [ordered]@{
    schemaVersion = 1
    qualityTrial = $QualityTrial
    diagnostic = $Diagnostic
    profileRender = [bool]$ProfileRender
    runtimeKind = $(if ($ExecutablePath) { 'Packaged' } else { 'Editor' })
    startedUtc = [datetime]::UtcNow.ToString('o')
    completedUtc = $null
    gameplayPassed = $false
    artifactFingerprint = $artifactFingerprint
    qaSlotsReset = $false
    qaSlotsRestored = $false
}
try {
    Reset-CityQASlots $savedRoot $snapshot
    $trial.qaSlotsReset = $true
    $startedUtc = [datetime]::UtcNow
    $trial.startedUtc = $startedUtc.ToString('o')
    if ($ExecutablePath) {
        $errorPath = Join-Path $qaPath 'Error.log'
        # Bao ve duong dan co khoang trang khi Start-Process noi cac tham so.
        $quotedArguments = $arguments | ForEach-Object { '"' + $_.Replace('"', '\"') + '"' }
        $process = Start-Process -FilePath $ExecutablePath -ArgumentList $quotedArguments -WindowStyle Hidden `
            -WorkingDirectory (Split-Path $ExecutablePath) -RedirectStandardOutput $consolePath `
            -RedirectStandardError $errorPath -PassThru -Wait
        $code = $process.ExitCode
    } else {
        & $editorPath @arguments *> $consolePath
        $code = $LASTEXITCODE
    }
    if ($code -ne 0) {
        throw "Max graphics gameplay failed: $code. See $logPath"
    }
    Assert-CityFreshEvidence $logPath $startedUtc
    $log = Get-Content -LiteralPath $logPath -Raw
    if (-not $log.Contains('CITY_SERVICE_JOURNEY_FINISH mode=Check success=1') -or
        -not $log.Contains('CITY_GRAPHICS_OBSERVATION_WRITTEN')) {
        throw "Required gameplay or observation evidence missing: $logPath"
    }
    $reportPath = Join-Path $savedRoot 'QA\CityServiceJourney\Report.txt'
    Assert-CityFreshEvidence $reportPath $startedUtc
    Copy-Item -LiteralPath $reportPath -Destination $qaPath
    foreach ($name in @('FrameTimes.csv', 'RenderConfig.txt')) {
        $source = Join-Path $savedRoot "QA\CityMaxGraphics\$name"
        Assert-CityFreshEvidence $source $startedUtc
        if ([IO.Path]::GetFullPath($source) -ne [IO.Path]::GetFullPath((Join-Path $qaPath $name))) {
            Copy-Item -LiteralPath $source -Destination $qaPath
        }
    }
    $trial.gameplayPassed = $true
} finally {
    try {
        Restore-CityQASlots $savedRoot $snapshot
        $trial.qaSlotsRestored = $true
    } finally {
        $trial.completedUtc = [datetime]::UtcNow.ToString('o')
        $trial | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $qaPath 'Trial.json') -Encoding UTF8
    }
}
$qaTools = Join-Path $projectRoot 'Tools\QA'
if ($ExecutablePath -and -not $ProfileRender -and $Diagnostic -eq 'None') {
    $validate = 'import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); ' +
        'from CityGraphicsTrialData import load_run; load_run(Path(sys.argv[2]))'
    & python -c $validate $qaTools $qaPath
    if ($LASTEXITCODE -ne 0) {
        throw "Observed native/quality trial validation failed: $qaPath"
    }
}
& python (Join-Path $qaTools 'SummarizeCityFrameTimes.py') $qaPath
if ($LASTEXITCODE -ne 0) {
    throw "Frame summary failed: $qaPath"
}
Write-Output "CITY_MAX_GRAPHICS_OBSERVED $qaPath"
