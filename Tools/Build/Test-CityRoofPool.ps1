[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$qaPath = Join-Path $projectRoot 'Saved\QA\CityRoofPoolCheck'
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
if (-not (Test-Path -LiteralPath $editorPath)) {
    throw "Missing Unreal executable: $editorPath"
}
New-Item -ItemType Directory -Path $qaPath -Force | Out-Null
$configPath = Join-Path $qaPath 'GameUserSettings.ini'
Copy-Item -LiteralPath (Join-Path $projectRoot 'Config\DefaultGameUserSettings.ini') -Destination $configPath
$logPath = Join-Path $qaPath 'CityRoofPoolCheck.log'
$reportPath = Join-Path $qaPath 'Report.json'
foreach ($stalePath in @($logPath, $reportPath)) {
    if (Test-Path -LiteralPath $stalePath) {
        Remove-Item -LiteralPath $stalePath
    }
}
$arguments = @(
    "$projectRoot\ANANTA.uproject", '/Game/ANANTA/Maps/ANANTA_City', '-game',
    '-NullRHI', '-CityRoofPoolCheck', '-CityQASlot', "-GameUserSettingsINI=$configPath",
    '-NoSaveConfig', '-NoSplash', '-nosound', '-unattended', "-abslog=$logPath"
)
$quotedArguments = ($arguments | ForEach-Object { '"' + $_ + '"' }) -join ' '
$startedUtc = [DateTime]::UtcNow
$process = New-Object System.Diagnostics.Process
$process.StartInfo.FileName = $editorPath
$process.StartInfo.Arguments = $quotedArguments
$process.StartInfo.UseShellExecute = $false
$process.StartInfo.CreateNoWindow = $true
$process.StartInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$process.StartInfo.RedirectStandardOutput = $true
$process.StartInfo.RedirectStandardError = $true
try {
    if (-not $process.Start()) {
        throw 'Cannot start authored rooftop stair input QA'
    }
    # Doc hai luong song song de khong chan process khi Unreal ghi log.
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    if (-not $process.WaitForExit(240000)) {
        $process.Kill()
        $process.WaitForExit(5000) | Out-Null
        throw "RoofPool input QA exceeded 240-second process watchdog. See $logPath"
    }
    $exitCode = $process.ExitCode
    [IO.File]::WriteAllText((Join-Path $qaPath 'Console.log'), $stdoutTask.GetAwaiter().GetResult())
    [IO.File]::WriteAllText((Join-Path $qaPath 'Error.log'), $stderrTask.GetAwaiter().GetResult())
    if ($exitCode -ne 0) {
        throw "RoofPool input QA exited with code ${exitCode}. See $logPath"
    }
} finally {
    $process.Dispose()
}
if (-not (Test-Path -LiteralPath $reportPath) -or -not (Test-Path -LiteralPath $logPath)) {
    throw "Missing fresh rooftop stair report or log in $qaPath"
}
if ((Get-Item -LiteralPath $reportPath).LastWriteTimeUtc -lt $startedUtc) {
    throw "Stale rooftop stair report: $reportPath"
}
$report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
$log = Get-Content -LiteralPath $logPath -Raw
if ($report.passed -ne $true -or $report.scope -ne 'authored-map rooftop pool stair walking input' `
    -or $report.map -ne 'ANANTA_City' -or $report.isolatedQASlot -ne $true `
    -or $report.streamingReady -ne $true -or $report.elapsedSeconds -gt 151 `
    -or -not $log.Contains('CITY_ROOFPOOL_CHECK_FINISH success=1')) {
    throw "Rooftop stair QA failed or completion evidence is incomplete: $reportPath"
}
$completedUtc = [DateTime]::Parse($report.completedUtc).ToUniversalTime()
if ($completedUtc -lt $startedUtc -or $completedUtc -gt [DateTime]::UtcNow.AddSeconds(1)) {
    throw 'Rooftop report completion timestamp is outside this run'
}
foreach ($gate in @('roofReached', 'courtyardReturned')) {
    if ($report.$gate -ne $true) {
        throw "Rooftop stair gate failed: $gate"
    }
}
foreach ($direction in @('ascent', 'descent')) {
    $leg = $report.$direction
    if ($leg.travelCm -lt 4100 -or $leg.forwardTravelCm -lt 4100 `
        -or $leg.samples -lt 41 -or $leg.inputSamples -lt 41 -or $leg.sampledTreads -ne 41 `
        -or $leg.treadIndices.Count -ne 41) {
        throw "Incomplete $direction input or 41-tread movement evidence: $reportPath"
    }
    for ($index = 0; $index -lt 41; $index++) {
        if ($leg.treadIndices[$index] -ne $index) {
            throw "Missing or duplicate $direction tread index $index"
        }
    }
}
if ([Math]::Abs($report.roofHeightCm - 840) -gt 3 `
    -or [Math]::Abs($report.lastFloorHeightCm - 20) -gt 3 `
    -or $report.floorSamples -lt 84 -or $report.clearanceSamples -ne $report.floorSamples `
    -or $report.landingInputSamples -lt 2 -or $report.returnInputSamples -lt 2 -or $report.roofSamples -lt 2 `
    -or $report.capsule.radiusCm -ne 38 -or $report.capsule.halfHeightCm -ne 92 `
    -or $report.capsule.unchanged -ne $true -or $report.capsule.clear -ne $true `
    -or $report.artificialSupportFloors -ne $false -or $report.teleportDuringMeasurement -ne $false `
    -or $report.movementSettingsModified -ne $false -or $report.swimmingTested -ne $false) {
    throw "Incomplete rooftop floor, clearance or unchanged movement evidence: $reportPath"
}
if ($report.ascent.heightChangeCm -lt 810 -or $report.descent.heightChangeCm -gt -810) {
    throw 'Ascent/descent did not cover the full 820 cm rise'
}
$expectedPhases = @('WaitReady', 'Settle', 'Ascent', 'Landing', 'Roof', 'ReturnLanding', 'Descent', 'Ground')
if ($report.phases.Count -ne $expectedPhases.Count) {
    throw 'Unexpected number of rooftop stair phase outcomes'
}
foreach ($phase in $expectedPhases) {
    $rows = @($report.phases | Where-Object { $_.phase -eq $phase })
    if ($rows.Count -ne 1 -or $rows[0].status -ne 'PASS') {
        throw "Missing, duplicate or failed rooftop stair phase: $phase"
    }
}
Write-Output "CITY_ROOFPOOL_CHECK_OK ascentCm=$($report.ascent.forwardTravelCm) report=$reportPath"
