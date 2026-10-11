[CmdletBinding()]
param(
    [switch]$Reload,
    [ValidateSet(720, 1080)]
    [int]$Height = 1080,
    [string]$ExecutablePath,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [ValidateSet('None', 'NaniteShadowAsyncOn', 'NaniteShadowAsyncOff')]
    [string]$Diagnostic = 'None',
    [ValidatePattern('^$|^[A-Za-z0-9-]+$')]
    [string]$RunId = ''
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'CityGraphicsTrialEvidence.ps1')
if ($Diagnostic -ne 'None' -and $Height -ne 1080) {
    throw 'Settings diagnostic requires native 1920x1080.'
}
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$mode = if ($Reload) { 'Reload' } else { 'Check' }
$variant = if ($ExecutablePath) { 'Packaged' } else { '' }
if ($Diagnostic -ne 'None') {
    $variant += $Diagnostic
}
if ($RunId) {
    $variant += "-$RunId"
}
$qaPath = Join-Path $projectRoot "Saved\QA\CitySettings$variant"
New-Item -ItemType Directory -Path $qaPath -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $projectRoot 'Saved\Logs') -Force | Out-Null
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
$startupOverrides = @()
if ($Diagnostic -eq 'NaniteShadowAsyncOn') {
    $startupOverrides = @('r.Nanite.AsyncRasterization.ShadowDepths=1')
} elseif ($Diagnostic -eq 'NaniteShadowAsyncOff') {
    $startupOverrides = @('r.Nanite.AsyncRasterization=1', 'r.Nanite.AsyncRasterization.ShadowDepths=0')
}
if ($startupOverrides.Count) {
    $arguments += '-ForceDPCVars=' + ($startupOverrides -join ',')
}
$savedRoot = Join-Path $projectRoot 'Saved'
if ($ExecutablePath) {
    $ExecutablePath = (Resolve-Path -LiteralPath $ExecutablePath).Path
    $savedRoot = [IO.Path]::GetFullPath((Join-Path (Split-Path $ExecutablePath) '..\..\Saved'))
}
$startedUtc = [datetime]::UtcNow
$sourcePath = Join-Path $savedRoot 'QA\CitySettings'
$reportPath = Join-Path $sourcePath "$mode.txt"
$captures = if ($Reload) {
    @('ReloadMenu', 'ReloadLanguage')
} else {
    @('ApplyReview', 'MenuEnglish', 'MenuVietnamese', 'MenuLanguage', 'FPSHidden', 'FPSVisible')
}
try {
    if ($ExecutablePath) {
        $errorPath = Join-Path $qaPath "${mode}Error.log"
        # Start-Process noi tham so: giu duong dan co khoang trang thanh mot gia tri.
        $quotedArguments = $arguments | ForEach-Object { '"' + $_.Replace('"', '\"') + '"' }
        $process = Start-Process -FilePath $ExecutablePath -ArgumentList $quotedArguments -WindowStyle Hidden `
            -WorkingDirectory (Split-Path $ExecutablePath) -RedirectStandardOutput $consolePath `
            -RedirectStandardError $errorPath -PassThru -Wait
        $code = $process.ExitCode
    } else {
        $arguments = @("$projectRoot\ANANTA.uproject", '/Game/ANANTA/Maps/ANANTA_City', '-game') + $arguments
        & $editorPath @arguments *> $consolePath
        $code = $LASTEXITCODE
    }
} finally {
    # Luu ca bang chung moi cua lan that bai truoc khi lan sau ghi de thu muc runtime.
    $stagePath = Join-Path $qaPath $mode
    New-Item -ItemType Directory -Path $stagePath -Force | Out-Null
    $names = @("$mode.txt") + @($captures | ForEach-Object { "$_.png" })
    foreach ($name in $names) {
        $source = Join-Path $sourcePath $name
        if ((Test-Path -LiteralPath $source) -and
            (Get-Item -LiteralPath $source).LastWriteTimeUtc -ge $startedUtc) {
            Copy-Item -LiteralPath $source -Destination (Join-Path $stagePath $name)
        }
    }
    if ($startupOverrides.Count) {
        # Chi log moi duoc dung lam bang chung CVar startup, ke ca khi process loi.
        $startup = [ordered]@{
            diagnostic = $Diagnostic
            executable = $ExecutablePath
            arguments = $arguments
            log = $logPath
            freshLog = $false
            overrides = @()
        }
        $startupLog = @()
        if ((Test-Path -LiteralPath $logPath) -and
            (Get-Item -LiteralPath $logPath).LastWriteTimeUtc -ge $startedUtc -and
            (Get-Item -LiteralPath $logPath).LastWriteTimeUtc -le [datetime]::UtcNow) {
            $startup.freshLog = $true
            $startupLog = @(Get-Content -LiteralPath $logPath)
        }
        foreach ($override in $startupOverrides) {
            $parts = $override -split '='
            $pattern = 'LogConfig: Set CVar \[\[' + [regex]::Escape($parts[0]) + ':([^\]]+)\]\]'
            $lines = @($startupLog | Where-Object { $_ -match $pattern } | ForEach-Object { "$_" })
            $effective = $null
            if ($lines.Count -and $lines[-1] -match $pattern) {
                $effective = $Matches[1]
            }
            $startup.overrides += @{
                name = $parts[0]
                requested = $parts[1]
                observed = $effective
                matched = ($effective -eq $parts[1])
                logLines = $lines
            }
        }
        $startup | ConvertTo-Json -Depth 6 |
            Set-Content -LiteralPath (Join-Path $stagePath 'Startup.json') -Encoding UTF8
    }
}
if ($code -ne 0) {
    throw "Settings $mode process failed: $code. See $logPath"
}
Assert-CityFreshEvidence $logPath $startedUtc
Assert-CityFreshEvidence $reportPath $startedUtc
if ($Diagnostic -eq 'NaniteShadowAsyncOff' -and
    @($startup.overrides | Where-Object { -not $_.matched }).Count) {
    throw "Explicit Nanite async startup values were not confirmed: $logPath"
}
$log = Get-Content -LiteralPath $logPath -Raw
if (-not $log.Contains("CITY_SETTINGS_FINISH mode=$mode success=1")) {
    throw "Settings $mode completion marker missing: $logPath"
}
if ($ExecutablePath -and -not $log.Contains('Bringing World /Game/ANANTA/Maps/ANANTA_City')) {
    throw 'Packaged default map was not the city'
}
$reloadValue = [int][bool]$Reload
if (-not (Get-Content -LiteralPath $reportPath -Raw).Contains("success=1 reload=$reloadValue")) {
    throw "Settings $mode report did not pass: $reportPath"
}
foreach ($name in $captures) {
    $capturePath = Join-Path $sourcePath "$name.png"
    Assert-CityFreshEvidence $capturePath $startedUtc
    if ((Get-Item -LiteralPath $capturePath).Length -eq 0) {
        throw "Empty settings capture: $capturePath"
    }
}
if (-not $Reload) {
    Assert-CityFreshEvidence $configPath $startedUtc
}
Write-Output "CITY_SETTINGS_OK variant=$variant mode=$mode resolution=${width}x$Height log=$logPath"
