[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$qaPath = Join-Path $projectRoot 'Saved\QA\CityCivicCheck'
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
if (-not (Test-Path -LiteralPath $editorPath)) {
    throw "Missing Unreal executable: $editorPath"
}
New-Item -ItemType Directory -Path $qaPath -Force | Out-Null
$configPath = Join-Path $qaPath 'GameUserSettings.ini'
Copy-Item -LiteralPath (Join-Path $projectRoot 'Config\DefaultGameUserSettings.ini') -Destination $configPath
$logPath = Join-Path $qaPath 'CityCivicCheck.log'
$reportPath = Join-Path $qaPath 'Report.json'
foreach ($stalePath in @($logPath, $reportPath)) {
    if (Test-Path -LiteralPath $stalePath) {
        Remove-Item -LiteralPath $stalePath
    }
}
$arguments = @(
    "$projectRoot\ANANTA.uproject", '/Game/ANANTA/Maps/ANANTA_City', '-game',
    '-NullRHI', '-CityCivicCheck', '-CityQASlot', "-GameUserSettingsINI=$configPath",
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
$preservedSlots = @()
$processStarted = $false
try {
    # Chi cach ly hai slot QA; khong doc, xoa hay ghi save thuong.
    foreach ($name in @('ANANTA_City_QA.sav', 'ANANTA_City_QA_Backup.sav')) {
        $slotPath = Join-Path $projectRoot "Saved\SaveGames\$name"
        $backupPath = Join-Path $qaPath "$name.preserved"
        if (Test-Path -LiteralPath $backupPath) {
            throw "A previous interrupted run left a preserved QA save: $backupPath"
        }
        $existed = Test-Path -LiteralPath $slotPath
        if ($existed) {
            Copy-Item -LiteralPath $slotPath -Destination $backupPath
        }
        $preservedSlots += [PSCustomObject]@{ Slot = $slotPath; Backup = $backupPath; Existed = $existed }
        if ($existed) {
            Remove-Item -LiteralPath $slotPath
        }
    }
    if (-not $process.Start()) {
        throw 'Cannot start the civic physics/input fixture process'
    }
    $processStarted = $true
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    if (-not $process.WaitForExit(330000)) {
        $process.Kill()
        $process.WaitForExit(5000) | Out-Null
        throw "Civic fixture exceeded process watchdog (330 seconds). See $logPath"
    }
    $exitCode = $process.ExitCode
    [IO.File]::WriteAllText((Join-Path $qaPath 'Console.log'), $stdoutTask.GetAwaiter().GetResult())
    [IO.File]::WriteAllText((Join-Path $qaPath 'Error.log'), $stderrTask.GetAwaiter().GetResult())
    if ($exitCode -ne 0) {
        throw "Civic fixture exited with code ${exitCode}. See $logPath"
    }
} finally {
    if ($processStarted -and -not $process.HasExited) {
        $process.Kill()
        $process.WaitForExit()
    }
    $process.Dispose()
    foreach ($slot in $preservedSlots) {
        if ($slot.Existed) {
            Copy-Item -LiteralPath $slot.Backup -Destination $slot.Slot -Force
            Remove-Item -LiteralPath $slot.Backup
        } elseif (Test-Path -LiteralPath $slot.Slot) {
            Remove-Item -LiteralPath $slot.Slot
        }
    }
}
if (-not (Test-Path -LiteralPath $reportPath) -or -not (Test-Path -LiteralPath $logPath)) {
    throw "Missing fresh civic report or log in $qaPath"
}
if ((Get-Item -LiteralPath $reportPath).LastWriteTimeUtc -lt $startedUtc `
    -or (Get-Item -LiteralPath $logPath).LastWriteTimeUtc -lt $startedUtc) {
    throw "Stale civic evidence: $reportPath"
}
$report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
$log = Get-Content -LiteralPath $logPath -Raw
if ($report.passed -ne $true -or $report.scope -ne 'authored-map physics/input fixture' `
    -or $report.map -ne 'ANANTA_City' -or $report.elapsedSeconds -gt 240.5 `
    -or $report.legs.Count -ne 8 -or $report.services.Count -ne 4 `
    -or $report.setupRelocations -ne 4 -or $report.measuredLegRelocations -ne 0 `
    -or $report.collisionBypass -ne $false -or $report.speedModified -ne $false `
    -or $report.isolatedQASlot -ne $true -or $report.keysReleased -ne $true `
    -or $report.capsuleRadiusCm -ne 38 -or $report.capsuleHalfHeightCm -ne 92 `
    -or $report.walkSpeedCmS -ne 350 -or $report.sprintSpeedCmS -ne 650 `
    -or -not $log.Contains('CITY_CIVIC_CHECK_FINISH success=1')) {
    throw "Civic fixture failed or completion evidence is incomplete: $reportPath"
}
$completedUtc = ([DateTimeOffset]$report.completedUtc).UtcDateTime
if ($completedUtc -lt $startedUtc -or $completedUtc -gt [DateTime]::UtcNow.AddSeconds(1)) {
    throw 'Civic report completion timestamp is outside this run'
}
foreach ($id in @('Police_Read', 'Fire_Read', 'Bar_Read', 'Arcade_Read')) {
    $services = @($report.services | Where-Object { $_.id -eq $id })
    if ($services.Count -ne 1 -or $services[0].interactedByE -ne $true `
        -or [string]::IsNullOrWhiteSpace($services[0].prompt)) {
        throw "Missing, duplicate or incomplete E interaction: $id"
    }
    foreach ($direction in @('inward', 'outward')) {
        $legs = @($report.legs | Where-Object { $_.service -eq $id -and $_.direction -eq $direction })
        if ($legs.Count -ne 1) {
            throw "Missing or duplicate civic doorway leg: $id $direction"
        }
        $leg = $legs[0]
        if ($leg.status -ne 'PASS' -or $leg.travelCm -lt 2900 -or $leg.elapsedSeconds -gt 30 `
            -or $leg.groundChecks -lt 10 -or $leg.collisionChecks -lt 10 -or $leg.inputChecks -lt 10 `
            -or $leg.sprintInputChecks -lt 10 `
            -or $leg.crossedDoor -ne $true `
            -or ($direction -eq 'inward' -and $leg.endX - $leg.startX -lt 2900) `
            -or ($direction -eq 'outward' -and $leg.startX - $leg.endX -lt 2900)) {
            throw "Incomplete civic doorway leg: $id $direction $($leg.reason)"
        }
    }
}
Write-Output "CITY_CIVIC_CHECK_OK services=4 legs=8 scope=authored_map_physics_input_fixture report=$reportPath"
