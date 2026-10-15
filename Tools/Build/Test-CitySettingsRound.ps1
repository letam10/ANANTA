[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ExecutablePath,
    [ValidateSet('None', 'NaniteShadowAsyncOn')]
    [string]$Diagnostic = 'None',
    [ValidateSet('Same', 'NaniteShadowAsyncOff')]
    [string]$ReloadDiagnostic = 'Same'
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'CityGraphicsTrialEvidence.ps1')
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$runId = [datetime]::UtcNow.ToString('yyyyMMddTHHmmssfff') + '-' + [guid]::NewGuid().ToString('N')
$variant = 'Packaged'
if ($Diagnostic -ne 'None') {
    $variant += $Diagnostic
}
$qaPath = Join-Path $projectRoot "Saved\QA\CitySettings$variant-$runId"
$effectiveReload = if ($ReloadDiagnostic -eq 'Same') { $Diagnostic } else { $ReloadDiagnostic }
$reloadQaPath = $qaPath
if ($ReloadDiagnostic -ne 'Same') {
    $reloadQaPath = Join-Path $projectRoot "Saved\QA\CitySettingsPackaged$effectiveReload-$runId"
}
$checkConfig = Join-Path $qaPath 'GameUserSettings.ini'
$reloadConfig = Join-Path $reloadQaPath 'GameUserSettings.ini'
New-Item -ItemType Directory -Path $qaPath -Force | Out-Null
$round = [ordered]@{
    schemaVersion = 1
    diagnostic = $Diagnostic
    reloadDiagnostic = $effectiveReload
    reloadDiagnosticSelection = $ReloadDiagnostic
    runId = $runId
    checkEvidence = $qaPath
    reloadEvidence = $reloadQaPath
    startedUtc = [datetime]::UtcNow.ToString('o')
    completedUtc = $null
    artifactFingerprint = $null
    reloadArtifactFingerprint = $null
    artifactUnchanged = $false
    config = [ordered]@{
        checkPath = $checkConfig
        reloadPath = $reloadConfig
        copied = $false
        checkSha256 = $null
        reloadBeforeSha256 = $null
        reloadAfterSha256 = $null
        checkAfterSha256 = $null
        continuity = $false
    }
    checkPassed = $false
    reloadPassed = $false
    qaSlotsReset = $false
    qaSlotsRestored = $false
    status = 'FAIL'
}
$snapshot = $null
function Get-FingerprintIdentity($Fingerprint) {
    $entries = @($Fingerprint.executable) + @($Fingerprint.containers)
    return ($entries | ForEach-Object { $_.path + ':' + $_.sha256 }) -join "`n"
}
try {
    if ($ReloadDiagnostic -ne 'Same' -and $Diagnostic -ne 'NaniteShadowAsyncOn') {
        throw 'NaniteShadowAsyncOff Reload requires NaniteShadowAsyncOn Check.'
    }
    $ExecutablePath = (Resolve-Path -LiteralPath $ExecutablePath).Path
    $round.artifactFingerprint = Get-CityPackageFingerprint $ExecutablePath
    $savedRoot = [IO.Path]::GetFullPath((Join-Path (Split-Path $ExecutablePath) '..\..\Saved'))
    $snapshot = @(Get-CityQASlotSnapshot $savedRoot)
    Reset-CityQASlots $savedRoot $snapshot
    $round.qaSlotsReset = $true
    $stageArguments = @{
        ExecutablePath = $ExecutablePath
        Diagnostic = $Diagnostic
        Height = 1080
        RunId = $runId
    }
    $runner = Join-Path $PSScriptRoot 'Test-CitySettings.ps1'
    & $runner @stageArguments
    $round.checkPassed = $true
    $round.config.checkSha256 = (Get-FileHash -LiteralPath $checkConfig -Algorithm SHA256).Hash
    if ($ReloadDiagnostic -ne 'Same') {
        # Copy-Item giu nguyen byte INI; khong reset save hay chay lai Check giua hai process.
        New-Item -ItemType Directory -Path $reloadQaPath -Force | Out-Null
        Copy-Item -LiteralPath $checkConfig -Destination $reloadConfig
        $round.config.copied = $true
    }
    $round.config.reloadBeforeSha256 = (Get-FileHash -LiteralPath $reloadConfig -Algorithm SHA256).Hash
    $round.config.continuity = $round.config.checkSha256 -eq $round.config.reloadBeforeSha256
    if (-not $round.config.continuity) {
        throw 'Reload INI differs from the completed Check INI.'
    }
    $round.reloadArtifactFingerprint = Get-CityPackageFingerprint $ExecutablePath
    $round.artifactUnchanged = (Get-FingerprintIdentity $round.artifactFingerprint) -eq
        (Get-FingerprintIdentity $round.reloadArtifactFingerprint)
    if (-not $round.artifactUnchanged) {
        throw 'Packaged executable or containers changed between Check and Reload.'
    }
    $stageArguments.Diagnostic = $effectiveReload
    & $runner @stageArguments -Reload
    $round.reloadPassed = $true
} catch {
    $round['error'] = $_.Exception.Message
    throw
} finally {
    try {
        # Chi khoi phuc khi snapshot da day du; loi reset/stage van phai chay finally.
        if ($null -ne $snapshot) {
            Restore-CityQASlots $savedRoot $snapshot
            $round.qaSlotsRestored = $true
        }
    } catch {
        $round['restoreError'] = $_.Exception.Message
        throw
    } finally {
        foreach ($entry in @(@('checkAfterSha256', $checkConfig), @('reloadAfterSha256', $reloadConfig))) {
            if (Test-Path -LiteralPath $entry[1]) {
                $round.config[$entry[0]] = (Get-FileHash -LiteralPath $entry[1] -Algorithm SHA256).Hash
            }
        }
        if ($round.checkPassed -and $round.reloadPassed -and $round.qaSlotsReset -and
            $round.qaSlotsRestored -and $round.config.continuity -and $round.artifactUnchanged) {
            $round.status = 'PASS'
        }
        $round.completedUtc = [datetime]::UtcNow.ToString('o')
        $round | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $qaPath 'Round.json') -Encoding UTF8
    }
}
Write-Output ("CITY_SETTINGS_ROUND_OK diagnostic=$Diagnostic reloadDiagnostic=$effectiveReload " +
    "evidence=$qaPath scope=menu_reload_only")
