$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$buildRoot = Join-Path $projectRoot 'Tools\Build'
$scripts = @(
    (Join-Path $buildRoot 'Test-CitySettings.ps1'),
    (Join-Path $buildRoot 'Test-CitySettingsRound.ps1'),
    $PSCommandPath,
    (Join-Path $PSScriptRoot 'CitySettingsBaselineCases.ps1')
)
foreach ($path in $scripts) {
    $tokens = $null
    $parseErrors = $null
    [void][Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$parseErrors)
    if ($parseErrors.Count) {
        throw "PowerShell parse failed: $path / $parseErrors"
    }
}

function Assert-Test([bool]$Condition, [string]$Message) {
    if (-not $Condition) {
        throw $Message
    }
}

$fixture = Join-Path ([IO.Path]::GetTempPath()) ('City Settings Test ' + [guid]::NewGuid().ToString('N'))
$fixtureBuild = Join-Path $fixture 'Tools\Build'
$binaryDirectory = Join-Path $fixture 'Package\ANANTA\Binaries\Win64'
$savedRoot = Join-Path $fixture 'Package\ANANTA\Saved'
$saveDirectory = Join-Path $savedRoot 'SaveGames'
$runtimeEvidence = Join-Path $savedRoot 'QA\CitySettings'
foreach ($directory in @($fixtureBuild, $binaryDirectory, $saveDirectory, $runtimeEvidence)) {
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
}
foreach ($name in @('Test-CitySettings.ps1', 'Test-CitySettingsRound.ps1', 'CityGraphicsTrialEvidence.ps1')) {
    Copy-Item -LiteralPath (Join-Path $buildRoot $name) -Destination (Join-Path $fixtureBuild $name)
}
$executable = Join-Path $binaryDirectory 'ANANTA.exe'
Set-Content -LiteralPath $executable -Value 'INERT TEST FIXTURE; NEVER EXECUTE'
Set-Content -LiteralPath (Join-Path $fixture 'Package\test.pak') -Value 'inert container'
$mainSave = Join-Path $saveDirectory 'ANANTA_City_QA.sav'
$backupSave = Join-Path $saveDirectory 'ANANTA_City_QA_Backup.sav'
$normalSave = Join-Path $saveDirectory 'ANANTA_City.sav'
Set-Content -LiteralPath $normalSave -Value 'untouched player save'
$normalHash = (Get-FileHash -LiteralPath $normalSave).Hash
$settingsTestState = @{ Case = ''; Calls = @() }

# Chan hoan toan Start-Process; chi fixture tam duoc phep di qua stub nay.
function Start-Process {
    param(
        [string]$FilePath,
        [string[]]$ArgumentList,
        [string]$WindowStyle,
        [string]$WorkingDirectory,
        [string]$RedirectStandardOutput,
        [string]$RedirectStandardError,
        [switch]$PassThru,
        [switch]$Wait
    )
    Assert-Test ($FilePath -eq $executable) 'Stub received a non-fixture executable'
    $argsClean = @($ArgumentList | ForEach-Object {
        Assert-Test ($_.StartsWith('"') -and $_.EndsWith('"')) 'Arguments must preserve spaces'
        $_.Substring(1, $_.Length - 2)
    })
    $mode = if ($argsClean -contains '-CitySettingsReload') { 'Reload' } else { 'Check' }
    $config = ($argsClean | Where-Object { $_ -like '-GameUserSettingsINI=*' }).Substring(21)
    $log = ($argsClean | Where-Object { $_ -like '-abslog=*' }).Substring(8)
    Assert-Test ($config.StartsWith($fixture)) 'Config escaped temp fixture'
    Assert-Test ($argsClean -contains '-ResX=1920' -and $argsClean -contains '-ResY=1080') 'Not native 1080'
    Assert-Test ($argsClean -contains '-CityQASlot') 'Missing isolated save switch'
    if ($mode -eq 'Check') {
        Assert-Test (-not (Test-Path -LiteralPath $mainSave)) 'Check did not reset the QA slot'
        Assert-Test (-not (Test-Path -LiteralPath $backupSave)) 'Check did not reset backup'
        Set-Content -LiteralPath $config -Value 'persisted settings fixture'
    } else {
        Assert-Test ((Get-Content -LiteralPath $mainSave -Raw).Trim() -eq 'Check') 'Reload reset Check save'
        Assert-Test (Test-Path -LiteralPath $config) 'Reload lost Check config'
        Assert-Test ((Get-Content -LiteralPath $backupSave -Raw).Trim() -eq 'temporary backup') 'Backup reset'
        Assert-Test ((Get-FileHash -LiteralPath $config).Hash -eq $settingsTestState.CheckHash) 'INI bytes changed'
    }
    if ($mode -eq 'Check') {
        $settingsTestState.CheckHash = (Get-FileHash -LiteralPath $config).Hash
    }
    $settingsTestState.Calls += @{ Mode = $mode; Config = $config; Log = $log; Arguments = $argsClean }
    Set-Content -LiteralPath $mainSave -Value $mode
    Set-Content -LiteralPath $backupSave -Value 'temporary backup'
    if ($settingsTestState.Case -eq 'LaunchThrow' -or
        ($mode -eq 'Reload' -and $settingsTestState.Case -eq 'ReloadThrow')) {
        throw 'Injected process launch failure'
    }
    $marker = "CITY_SETTINGS_FINISH mode=$mode success=1"
    Set-Content -LiteralPath $log -Value "Bringing World /Game/ANANTA/Maps/ANANTA_City`n$marker"
    $force = @($argsClean | Where-Object { $_ -like '-ForceDPCVars=*' })
    if ($force.Count -and -not ($mode -eq 'Reload' -and $settingsTestState.Case -eq 'ReloadMissingStartup')) {
        foreach ($override in $force[0].Substring('-ForceDPCVars='.Length).Split(',')) {
            $observed = $override.Replace('=', ':')
            Add-Content -LiteralPath $log -Value "LogConfig: Set CVar [[$observed]]"
        }
    }
    if ($mode -eq 'Reload' -and $settingsTestState.Case -eq 'ReloadWrongStartup') {
        Add-Content -LiteralPath $log -Value 'LogConfig: Set CVar [[r.Nanite.AsyncRasterization.ShadowDepths:1]]'
    }
    if ($mode -eq 'Check' -and $settingsTestState.Case -eq 'ArtifactChanged') {
        Add-Content -LiteralPath (Join-Path $fixture 'Package\test.pak') -Value 'changed container'
    }
    if ($mode -eq 'Reload' -and $settingsTestState.Case -eq 'ReloadConfigUpdate') {
        Add-Content -LiteralPath $config -Value 'settings changed by Reload'
    }
    Set-Content -LiteralPath $RedirectStandardOutput -Value 'stub console'
    Set-Content -LiteralPath $RedirectStandardError -Value ''
    $reloadValue = [int]($mode -eq 'Reload')
    $report = Join-Path $runtimeEvidence "$mode.txt"
    Set-Content -LiteralPath $report -Value "success=1 reload=$reloadValue"
    $captures = if ($mode -eq 'Reload') {
        @('ReloadMenu', 'ReloadLanguage')
    } else {
        @('ApplyReview', 'MenuEnglish', 'MenuVietnamese', 'MenuLanguage', 'FPSHidden', 'FPSVisible')
    }
    foreach ($name in $captures) {
        Set-Content -LiteralPath (Join-Path $runtimeEvidence "$name.png") -Value 'fixture image bytes'
    }
    if ($settingsTestState.Case -eq 'StaleLog' -or
        ($mode -eq 'Reload' -and $settingsTestState.Case -eq 'ReloadStaleLog')) {
        [IO.File]::SetLastWriteTimeUtc($log, [datetime]'2001-01-01')
    }
    if ($settingsTestState.Case -eq 'StaleReport' -or
        ($mode -eq 'Reload' -and $settingsTestState.Case -eq 'ReloadStaleReport')) {
        [IO.File]::SetLastWriteTimeUtc($report, [datetime]'2001-01-01')
    }
    if ($settingsTestState.Case -eq 'StaleCapture') {
        [IO.File]::SetLastWriteTimeUtc((Join-Path $runtimeEvidence 'FPSVisible.png'), [datetime]'2001-01-01')
    }
    if ($settingsTestState.Case -eq 'StaleConfig') {
        [IO.File]::SetLastWriteTimeUtc($config, [datetime]'2001-01-01')
    }
    $exitCode = if ($settingsTestState.Case -eq "${mode}Exit") { 17 } else { 0 }
    return [pscustomobject]@{ ExitCode = $exitCode }
}

$runner = Join-Path $fixtureBuild 'Test-CitySettings.ps1'
$roundRunner = Join-Path $fixtureBuild 'Test-CitySettingsRound.ps1'
$qaRoot = Join-Path $fixture 'Saved\QA'
$seenReports = @()
$cases = @('Pass', 'CheckExit', 'ReloadExit', 'LaunchThrow', 'StaleLog', 'StaleReport', 'StaleCapture', 'StaleConfig')
foreach ($diagnostic in @('None', 'NaniteShadowAsyncOn')) {
    foreach ($case in $cases) {
        Set-Content -LiteralPath $mainSave -Value 'original QA bytes'
        [IO.File]::SetLastWriteTimeUtc($mainSave, [datetime]'2020-03-04T05:06:07Z')
        [IO.File]::SetAttributes($mainSave, [IO.FileAttributes]::ReadOnly)
        $originalHash = (Get-FileHash -LiteralPath $mainSave).Hash
        $originalTime = (Get-Item -LiteralPath $mainSave).LastWriteTimeUtc
        $settingsTestState.Case = $case
        $settingsTestState.Calls = @()
        $failed = $false
        try {
            & $roundRunner -ExecutablePath $executable -Diagnostic $diagnostic | Out-Null
        } catch {
            $failed = $true
        }
        Assert-Test ($failed -eq ($case -ne 'Pass')) "Wrong result: $diagnostic / $case"
        $reports = @(Get-ChildItem -LiteralPath $qaRoot -Recurse -Filter 'Round.json' |
            Where-Object { $_.FullName -notin $seenReports })
        Assert-Test ($reports.Count -eq 1) 'Round must produce one unique report even on failure'
        $seenReports += $reports[0].FullName
        $round = Get-Content -LiteralPath $reports[0].FullName -Raw | ConvertFrom-Json
        Assert-Test ($round.schemaVersion -eq 1 -and $round.diagnostic -eq $diagnostic) 'Bad round schema'
        Assert-Test ($round.qaSlotsReset -and $round.qaSlotsRestored) 'QA slots were not protected'
        Assert-Test ($round.artifactFingerprint.executable.sha256.Length -eq 64) 'Fingerprint missing'
        Assert-Test ($round.artifactFingerprint.containers.Count -eq 1) 'Container fingerprint missing'
        Assert-Test ([datetime]$round.completedUtc -ge [datetime]$round.startedUtc) 'Bad round timestamps'
        $expectedStatus = if ($case -eq 'Pass') { 'PASS' } else { 'FAIL' }
        Assert-Test ($round.status -eq $expectedStatus) 'Wrong persisted status'
        Assert-Test ($round.checkPassed -eq ($case -in @('Pass', 'ReloadExit'))) 'Wrong Check status'
        Assert-Test ($round.reloadPassed -eq ($case -eq 'Pass')) 'Wrong Reload status'
        Assert-Test ((Get-FileHash -LiteralPath $mainSave).Hash -eq $originalHash) 'Finally lost QA bytes'
        Assert-Test ((Get-Item -LiteralPath $mainSave).LastWriteTimeUtc -eq $originalTime) 'Finally lost timestamp'
        Assert-Test ((Get-Item -LiteralPath $mainSave).IsReadOnly) 'Finally lost attributes'
        Assert-Test (-not (Test-Path -LiteralPath $backupSave)) 'Finally left new backup behind'
        Assert-Test ((Get-FileHash -LiteralPath $normalSave).Hash -eq $normalHash) 'Player save changed'
        [IO.File]::SetAttributes($mainSave, [IO.FileAttributes]::Normal)
        $calls = $settingsTestState.Calls
        $expectedCount = if ($case -in @('Pass', 'ReloadExit')) { 2 } else { 1 }
        Assert-Test ($calls.Count -eq $expectedCount) 'Stage ran after failed Check'
        Assert-Test ($calls[0].Mode -eq 'Check') 'Check must run first'
        if ($calls.Count -eq 2) {
            Assert-Test ($calls[1].Mode -eq 'Reload') 'Reload must run second'
            Assert-Test ($calls[0].Config -eq $calls[1].Config) 'Check and Reload must share config'
        }
        foreach ($call in $calls) {
            $overrides = @($call.Arguments | Where-Object { $_ -like '-ForceDPCVars=*' })
            if ($diagnostic -eq 'None') {
                Assert-Test ($overrides.Count -eq 0) 'Default API unexpectedly changes renderer'
                Assert-Test (-not $call.Config.Contains('NaniteShadowAsyncOn')) 'Default path has diagnostic suffix'
            } else {
                Assert-Test ($overrides.Count -eq 1) 'Diagnostic must override exactly one variable'
                Assert-Test ($overrides[0] -eq '-ForceDPCVars=r.Nanite.AsyncRasterization.ShadowDepths=1') 'Wrong CVar'
                Assert-Test ($call.Config.Contains('PackagedNaniteShadowAsyncOn-')) 'Config isolation missing'
                Assert-Test ($call.Log.Contains('PackagedNaniteShadowAsyncOn-')) 'Log isolation missing'
            }
        }
        if ($case -eq 'Pass') {
            $evidence = Split-Path $reports[0].FullName
            Assert-Test (Test-Path -LiteralPath (Join-Path $evidence 'Check\Check.txt')) 'Check evidence missing'
            Assert-Test (Test-Path -LiteralPath (Join-Path $evidence 'Reload\Reload.txt')) 'Reload evidence missing'
        }
    }
}
$settingsTestState.Calls = @()
$rejected = $false
try {
    & $runner -ExecutablePath $executable -Diagnostic NaniteShadowAsyncOn -Height 720 | Out-Null
} catch {
    $rejected = $true
}
Assert-Test ($rejected -and $settingsTestState.Calls.Count -eq 0) '720p diagnostic must reject before launch'
$bootstrap = Join-Path $fixture 'Package\ANANTA.exe'
Copy-Item -LiteralPath $executable -Destination $bootstrap
$rejected = $false
try {
    & $roundRunner -ExecutablePath $bootstrap | Out-Null
} catch {
    $rejected = $true
}
Assert-Test ($rejected -and $settingsTestState.Calls.Count -eq 0) 'Bootstrap must reject before launch'
Assert-Test ((Get-FileHash -LiteralPath $mainSave).Hash -eq $originalHash) 'Preflight touched QA save'
Remove-Item -LiteralPath $mainSave
$settingsTestState.Case = 'Pass'
& $runner -ExecutablePath $executable | Out-Null
& $runner -ExecutablePath $executable -Reload | Out-Null
$legacyConfig = Join-Path $qaRoot 'CitySettingsPackaged\GameUserSettings.ini'
Assert-Test ($settingsTestState.Calls.Count -eq 2) 'Legacy API lost Check/Reload'
foreach ($call in $settingsTestState.Calls) {
    Assert-Test ($call.Config -eq $legacyConfig) 'Legacy default path changed'
    $overrides = @($call.Arguments | Where-Object { $_ -like '-ForceDPCVars=*' })
    Assert-Test ($overrides.Count -eq 0) 'Legacy default unexpectedly overrides renderer'
}
. (Join-Path $PSScriptRoot 'CitySettingsBaselineCases.ps1')
Write-Output ("CITY_SETTINGS_DIAGNOSTIC_TESTS_OK rounds=16 guards=2 legacyPair=PASS " +
    "baselineRounds=$($baselineCases.Count) baselineGuards=2 fixture=$fixture")
