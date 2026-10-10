# Dot-source tu TestCitySettingsDiagnostics.ps1; moi du lieu/lenh launch deu nam trong fixture tam.
$baselineCases = @(
    'Pass', 'ReloadConfigUpdate', 'ReloadExit', 'ReloadThrow', 'ReloadStaleReport',
    'ReloadStaleLog', 'ReloadMissingStartup', 'ReloadWrongStartup', 'ArtifactChanged'
)
$genericConfig = Join-Path $savedRoot 'Config\Windows\GameUserSettings.ini'
New-Item -ItemType Directory -Path (Split-Path $genericConfig) -Force | Out-Null
Set-Content -LiteralPath $genericConfig -Value 'generic settings must remain untouched'
$genericHash = (Get-FileHash -LiteralPath $genericConfig).Hash
$seenReports = @(Get-ChildItem -LiteralPath $qaRoot -Recurse -Filter 'Round.json' |
    ForEach-Object { $_.FullName })
foreach ($case in $baselineCases) {
    $originals = @()
    foreach ($path in @($mainSave, $backupSave)) {
        Set-Content -LiteralPath $path -Value ('original slot ' + (Split-Path $path -Leaf))
        [IO.File]::SetCreationTimeUtc($path, [datetime]'2019-02-03T04:05:06Z')
        [IO.File]::SetLastWriteTimeUtc($path, [datetime]'2020-03-04T05:06:07Z')
        [IO.File]::SetAttributes($path, [IO.FileAttributes]::ReadOnly)
        $originals += @{
            Path = $path
            Hash = (Get-FileHash -LiteralPath $path).Hash
            Created = (Get-Item -LiteralPath $path).CreationTimeUtc
            Written = (Get-Item -LiteralPath $path).LastWriteTimeUtc
            Attributes = (Get-Item -LiteralPath $path).Attributes
        }
    }
    $settingsTestState.Case = $case
    $settingsTestState.Calls = @()
    $failed = $false
    try {
        & $roundRunner -ExecutablePath $executable -Diagnostic NaniteShadowAsyncOn `
            -ReloadDiagnostic NaniteShadowAsyncOff | Out-Null
    } catch {
        $failed = $true
    }
    $pass = $case -in @('Pass', 'ReloadConfigUpdate')
    Assert-Test ($failed -eq (-not $pass)) "Wrong baseline result: $case"
    $reports = @(Get-ChildItem -LiteralPath $qaRoot -Recurse -Filter 'Round.json' |
        Where-Object { $_.FullName -notin $seenReports })
    Assert-Test ($reports.Count -eq 1) 'Baseline must retain one fresh Round report'
    $seenReports += $reports[0].FullName
    $round = Get-Content -LiteralPath $reports[0].FullName -Raw | ConvertFrom-Json
    Assert-Test ($round.diagnostic -eq 'NaniteShadowAsyncOn') 'Check diagnostic lost'
    Assert-Test ($round.reloadDiagnostic -eq 'NaniteShadowAsyncOff') 'Reload diagnostic lost'
    Assert-Test ($round.checkPassed -and $round.reloadPassed -eq $pass) 'Wrong baseline stage results'
    Assert-Test (($round.status -eq 'PASS') -eq $pass) 'Wrong baseline persisted status'
    Assert-Test ($round.qaSlotsReset -and $round.qaSlotsRestored) 'Baseline lost slot protection'
    Assert-Test ($round.config.copied -and $round.config.continuity) 'Check INI was not copied exactly'
    Assert-Test ($round.config.checkSha256 -eq $settingsTestState.CheckHash) 'Wrong Check INI hash'
    Assert-Test ($round.config.checkSha256 -eq $round.config.reloadBeforeSha256) 'Pre-Reload INI differs'
    Assert-Test ($round.config.checkSha256 -eq $round.config.checkAfterSha256) 'Check INI was overwritten'
    $changed = $round.config.reloadBeforeSha256 -ne $round.config.reloadAfterSha256
    Assert-Test ($changed -eq ($case -eq 'ReloadConfigUpdate')) 'Wrong after-Reload config evidence'
    Assert-Test ($round.artifactUnchanged -eq ($case -ne 'ArtifactChanged')) 'Fingerprint drift undetected'
    Assert-Test ($round.reloadArtifactFingerprint.containers.Count -eq 1) 'Reload fingerprint missing'
    foreach ($original in $originals) {
        $item = Get-Item -LiteralPath $original.Path
        Assert-Test ((Get-FileHash -LiteralPath $original.Path).Hash -eq $original.Hash) 'Lost slot bytes'
        Assert-Test ($item.CreationTimeUtc -eq $original.Created) 'Lost creation metadata'
        Assert-Test ($item.LastWriteTimeUtc -eq $original.Written) 'Lost write metadata'
        Assert-Test ($item.Attributes -eq $original.Attributes) 'Lost slot attributes'
        [IO.File]::SetAttributes($original.Path, [IO.FileAttributes]::Normal)
    }
    Assert-Test ((Get-FileHash -LiteralPath $normalSave).Hash -eq $normalHash) 'Player save changed'
    Assert-Test ((Get-FileHash -LiteralPath $genericConfig).Hash -eq $genericHash) 'Generic INI changed'
    $calls = $settingsTestState.Calls
    $expectedCalls = if ($case -eq 'ArtifactChanged') { 1 } else { 2 }
    Assert-Test ($calls.Count -eq $expectedCalls) 'Wrong baseline launch count'
    $checkEvidence = Split-Path $calls[0].Config
    Assert-Test ($checkEvidence -eq $round.checkEvidence) 'Wrong Check evidence location'
    Assert-Test ($checkEvidence.EndsWith('-' + $round.runId)) 'Check RunId differs'
    Assert-Test (Test-Path -LiteralPath (Join-Path $checkEvidence 'Check\Check.txt')) 'Missing Check report'
    if ($calls.Count -eq 1) {
        continue
    }
    Assert-Test ($calls[0].Mode -eq 'Check' -and $calls[1].Mode -eq 'Reload') 'Wrong stage order'
    Assert-Test ($calls[0].Config -ne $calls[1].Config) 'Baseline overwrites Check INI'
    $reloadEvidence = Split-Path $calls[1].Config
    Assert-Test ($reloadEvidence -eq $round.reloadEvidence) 'Wrong Reload evidence location'
    Assert-Test ($reloadEvidence.EndsWith('-' + $round.runId)) 'Pair RunId differs'
    Assert-Test ($calls[1].Config.Contains('PackagedNaniteShadowAsyncOff-')) 'Off config suffix missing'
    Assert-Test ($calls[1].Log.Contains('PackagedNaniteShadowAsyncOff-')) 'Off log suffix missing'
    $on = '-ForceDPCVars=r.Nanite.AsyncRasterization.ShadowDepths=1'
    $off = '-ForceDPCVars=r.Nanite.AsyncRasterization=1,r.Nanite.AsyncRasterization.ShadowDepths=0'
    Assert-Test ($calls[0].Arguments -contains $on) 'Check override changed'
    Assert-Test ($calls[1].Arguments -contains $off) 'Explicit Off override missing'
    $startupFile = Join-Path $reloadEvidence 'Reload\Startup.json'
    $startup = Get-Content -LiteralPath $startupFile -Raw | ConvertFrom-Json
    Assert-Test ($startup.executable -eq $executable) 'Startup executable provenance missing'
    Assert-Test ($startup.arguments -contains $off) 'Startup override provenance missing'
    $matched = @($startup.overrides | Where-Object { $_.matched }).Count -eq 2
    $expectedMatched = $case -notin @('ReloadThrow', 'ReloadStaleLog', 'ReloadMissingStartup', 'ReloadWrongStartup')
    Assert-Test ($matched -eq $expectedMatched) 'Wrong effective startup evidence'
    $reloadReport = Join-Path $reloadEvidence 'Reload\Reload.txt'
    $expectedReport = $case -notin @('ReloadThrow', 'ReloadStaleReport')
    Assert-Test ((Test-Path -LiteralPath $reloadReport) -eq $expectedReport) 'Stale report reused'
}

# Invalid pair va native guard phai dung truoc launch, giu nguyen hai slot va generic INI.
$settingsTestState.Calls = @()
$guardHashes = @($mainSave, $backupSave | ForEach-Object { (Get-FileHash -LiteralPath $_).Hash })
$rejected = $false
try {
    & $roundRunner -ExecutablePath $executable -ReloadDiagnostic NaniteShadowAsyncOff | Out-Null
} catch {
    $rejected = $true
}
Assert-Test ($rejected -and $settingsTestState.Calls.Count -eq 0) 'Invalid pairing launched a process'
$reports = @(Get-ChildItem -LiteralPath $qaRoot -Recurse -Filter 'Round.json' |
    Where-Object { $_.FullName -notin $seenReports })
Assert-Test ($reports.Count -eq 1) 'Invalid pairing lost rejection report'
$invalid = Get-Content -LiteralPath $reports[0].FullName -Raw | ConvertFrom-Json
Assert-Test ($invalid.status -eq 'FAIL' -and -not $invalid.qaSlotsReset) 'Invalid pairing touched QA slots'
$rejected = $false
try {
    & $runner -ExecutablePath $executable -Diagnostic NaniteShadowAsyncOff -Height 720 | Out-Null
} catch {
    $rejected = $true
}
Assert-Test ($rejected -and $settingsTestState.Calls.Count -eq 0) 'Off native guard did not reject'
$afterHashes = @($mainSave, $backupSave | ForEach-Object { (Get-FileHash -LiteralPath $_).Hash })
Assert-Test (($guardHashes -join ',') -eq ($afterHashes -join ',')) 'Guards changed QA slots'
Assert-Test ((Get-FileHash -LiteralPath $genericConfig).Hash -eq $genericHash) 'Guards changed generic INI'
