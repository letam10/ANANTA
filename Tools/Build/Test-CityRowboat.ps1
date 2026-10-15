[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$qaPath = Join-Path $projectRoot 'Saved\QA\CityRowboatCheck'
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
if (-not (Test-Path -LiteralPath $editorPath)) {
    throw "Missing Unreal executable: $editorPath"
}
New-Item -ItemType Directory -Path $qaPath -Force | Out-Null
$configPath = Join-Path $qaPath 'GameUserSettings.ini'
Copy-Item -LiteralPath (Join-Path $projectRoot 'Config\DefaultGameUserSettings.ini') -Destination $configPath
$logPath = Join-Path $qaPath 'CityRowboatCheck.log'
$reportPath = Join-Path $qaPath 'Report.json'
foreach ($stalePath in @($logPath, $reportPath)) {
    if (Test-Path -LiteralPath $stalePath) {
        Remove-Item -LiteralPath $stalePath
    }
}
$arguments = @(
    "$projectRoot\ANANTA.uproject", '/Game/ANANTA/Maps/ANANTA_City', '-game',
    '-NullRHI', '-CityRowboatCheck', '-CityQASlot', "-GameUserSettingsINI=$configPath",
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
        throw 'Cannot start authored rowboat input QA'
    }
    # Doc hai luong song song de khong chan process khi Unreal ghi log.
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    if (-not $process.WaitForExit(180000)) {
        $process.Kill()
        $process.WaitForExit(5000) | Out-Null
        throw "Rowboat input QA exceeded 180-second process watchdog. See $logPath"
    }
    $exitCode = $process.ExitCode
    [IO.File]::WriteAllText((Join-Path $qaPath 'Console.log'), $stdoutTask.GetAwaiter().GetResult())
    [IO.File]::WriteAllText((Join-Path $qaPath 'Error.log'), $stderrTask.GetAwaiter().GetResult())
    if ($exitCode -ne 0) {
        throw "Rowboat input QA exited with code ${exitCode}. See $logPath"
    }
} finally {
    $process.Dispose()
}
if (-not (Test-Path -LiteralPath $reportPath) -or -not (Test-Path -LiteralPath $logPath)) {
    throw "Missing fresh rowboat report or log in $qaPath"
}
if ((Get-Item -LiteralPath $reportPath).LastWriteTimeUtc -lt $startedUtc) {
    throw "Stale rowboat report: $reportPath"
}
$report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
$log = Get-Content -LiteralPath $logPath -Raw
if ($report.passed -ne $true -or $report.scope -ne 'authored-map player rowboat input' `
    -or $report.map -ne 'ANANTA_City' -or $report.isolatedQASlot -ne $true `
    -or $report.streamingReady -ne $true -or $report.elapsedSeconds -gt 91 `
    -or -not $log.Contains('CITY_ROWBOAT_CHECK_FINISH success=1')) {
    throw "Rowboat input QA failed or completion evidence is incomplete: $reportPath"
}
# PowerShell 7 da doc ISO JSON thanh DateTime UTC; Parse lai se lam mat timezone.
$completedUtc = ([DateTimeOffset]$report.completedUtc).UtcDateTime
if ($completedUtc -lt $startedUtc -or $completedUtc -gt [DateTime]::UtcNow.AddSeconds(1)) {
    throw 'Rowboat report completion timestamp is outside this run'
}
foreach ($gate in @('board', 'rowInput', 'brakeInput', 'brake', 'alight', 'dryFloor', 'openSeaExitRejected')) {
    if ($report.$gate -ne $true) {
        throw "Rowboat gate failed: $gate"
    }
}
if ($report.measuredTravelCm -le 20 -or $report.rowDisplacementCm -le 20 `
    -or $report.rowSeconds -lt 1 -or $report.peakSpeedKmh -le 0 -or $report.stoppedSpeedKmh -gt 0.05 `
    -or $report.brakeStartSpeedKmh -le 0.05 -or $report.stoppedSpeedKmh -ge $report.brakeStartSpeedKmh `
    -or $report.capsule.radiusCm -ne 38 -or $report.capsule.halfHeightCm -ne 92 `
    -or $report.capsule.unchanged -ne $true -or $report.capsule.clearAfterAlight -ne $true `
    -or $report.openSeaSetupRelocatedBoat -ne $true -or $report.openSeaRelocationIncludedInTravel -ne $false `
    -or $report.artificialSupportFloors -ne $false -or $report.boatSpeedModified -ne $false `
    -or $report.collisionBypassDuringMeasurement -ne $false) {
    throw "Incomplete input, movement, capsule or separate sea setup evidence: $reportPath"
}
$expectedPhases = @('WaitReady', 'Settle', 'Board', 'Row', 'Brake', 'Alight', 'OpenSea')
if ($report.phases.Count -ne $expectedPhases.Count) {
    throw 'Unexpected number of rowboat phase outcomes'
}
foreach ($phase in $expectedPhases) {
    $rows = @($report.phases | Where-Object { $_.phase -eq $phase })
    if ($rows.Count -ne 1 -or $rows[0].status -ne 'PASS') {
        throw "Missing, duplicate or failed rowboat phase: $phase"
    }
}
Write-Output "CITY_ROWBOAT_CHECK_OK travelCm=$($report.measuredTravelCm) report=$reportPath"
