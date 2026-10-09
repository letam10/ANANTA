[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$qaPath = Join-Path $projectRoot 'Saved\QA\CityRoadRoutesCheck'
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
if (-not (Test-Path -LiteralPath $editorPath)) {
    throw "Missing Unreal executable: $editorPath"
}
New-Item -ItemType Directory -Path $qaPath -Force | Out-Null
$configPath = Join-Path $qaPath 'GameUserSettings.ini'
Copy-Item -LiteralPath (Join-Path $projectRoot 'Config\DefaultGameUserSettings.ini') -Destination $configPath
$logPath = Join-Path $qaPath 'CityRoadRoutesCheck.log'
$reportPath = Join-Path $qaPath 'Report.json'
foreach ($stalePath in @($logPath, $reportPath)) {
    if (Test-Path -LiteralPath $stalePath) {
        Remove-Item -LiteralPath $stalePath
    }
}
$arguments = @(
    "$projectRoot\ANANTA.uproject", '/Game/ANANTA/Maps/ANANTA_City', '-game',
    '-NullRHI', '-CityRoadRoutesCheck', '-CityQASlot', "-GameUserSettingsINI=$configPath",
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
        throw 'Cannot start the road route physics fixture process'
    }
    # Doc ca hai luong song song, tranh deadlock khi Unreal ghi nhieu log.
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    if (-not $process.WaitForExit(390000)) {
        $process.Kill()
        $process.WaitForExit(5000) | Out-Null
        throw "Road route physics fixture exceeded process watchdog (390 seconds). See $logPath"
    }
    $exitCode = $process.ExitCode
    [IO.File]::WriteAllText((Join-Path $qaPath 'Console.log'), $stdoutTask.GetAwaiter().GetResult())
    [IO.File]::WriteAllText((Join-Path $qaPath 'Error.log'), $stderrTask.GetAwaiter().GetResult())
    if ($exitCode -ne 0) {
        throw "Road route physics fixture exited with code ${exitCode}. See $logPath"
    }
} finally {
    $process.Dispose()
}
if (-not (Test-Path -LiteralPath $reportPath) -or -not (Test-Path -LiteralPath $logPath)) {
    throw "Missing fresh road route report or log in $qaPath"
}
if ((Get-Item -LiteralPath $reportPath).LastWriteTimeUtc -lt $startedUtc) {
    throw "Stale road route report: $reportPath"
}
$report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
$log = Get-Content -LiteralPath $logPath -Raw
if ($report.passed -ne $true -or $report.schemaVersion -ne 1 `
    -or $report.scope -ne 'authored-map physics fixture' -or $report.map -ne 'ANANTA_City' `
    -or $null -eq $report.elapsedSeconds -or $report.elapsedSeconds -le 0 `
    -or $report.elapsedSeconds -gt 240 -or $report.results.Count -ne 8 `
    -or $report.fixtureVehiclesPerKind -ne 2 -or $report.observerRelocated -ne $true `
    -or $report.streamingRadiusCm -ne 62000 -or $report.isolatedQASlot -ne $true `
    -or -not $log.Contains('CITY_ROAD_ROUTES_CHECK_FINISH success=1')) {
    throw "Road route fixture failed or completion evidence is incomplete: $reportPath"
}
foreach ($field in @('artificialSupportFloors', 'vehicleSpeedModified', 'routesModified',
    'geometryModified', 'collisionBypass')) {
    if ($report.$field -ne $false) {
        throw "Missing or invalid fixture scope evidence: $field"
    }
}
$completedUtc = [DateTime]::Parse($report.completedUtc).ToUniversalTime()
if ($completedUtc -lt $startedUtc -or $completedUtc -gt [DateTime]::UtcNow.AddSeconds(1)) {
    throw 'Road route report completion timestamp is outside this run'
}
$kinds = @('Coach', 'CityBus', 'Taxi', 'BoxTruck', 'CargoTruck', 'TankerTruck', 'PoliceCar', 'Ambulance')
foreach ($kind in $kinds) {
    $rows = @($report.results | Where-Object { $_.kind -eq $kind })
    if ($rows.Count -ne 1) {
        throw "Missing or duplicate road route result: $kind"
    }
    $row = $rows[0]
    if ($row.status -ne 'PASS' -or $row.boarded -lt 4 -or $row.alighted -lt 4 `
        -or $row.boardedMask -ne 15 -or $row.alightedMask -ne 15 -or $row.probes.Count -ne 2 `
        -or $row.travelCm -lt 180000 -or $null -eq $row.elapsedSeconds `
        -or $row.elapsedSeconds -le 0 -or $row.elapsedSeconds -gt 240) {
        throw "Incomplete authored road stop coverage for ${kind}: $($row.reason)"
    }
    foreach ($initialPoint in @(0, 2)) {
        $probes = @($row.probes | Where-Object { $_.initialPoint -eq $initialPoint })
        if ($probes.Count -ne 1) {
            throw "Missing or duplicate vehicle probe for ${kind}, point $initialPoint"
        }
        $probe = $probes[0]
        if ($probe.status -ne 'PASS' -or $probe.boarded -lt 2 -or $probe.alighted -lt 2 `
            -or $probe.pointMask -ne 255 -or $probe.returned -ne $true -or $probe.travelCm -lt 90000 `
            -or $null -eq $probe.startDistanceCm -or $probe.startDistanceCm -ge 200 `
            -or $null -eq $probe.maxRoadDeviationCm -or $probe.maxRoadDeviationCm -gt 100 `
            -or $null -eq $probe.maxFloorGapCm -or $probe.maxFloorGapCm -gt 10 `
            -or $null -eq $probe.elapsedSeconds -or $probe.elapsedSeconds -le 0 `
            -or $probe.elapsedSeconds -gt 240 -or $probe.sideTravelCm.Count -ne 4) {
            throw "Incomplete authored road loop for ${kind}, point ${initialPoint}: $($probe.reason)"
        }
        foreach ($distance in $probe.sideTravelCm) {
            if ($null -eq $distance -or $distance -le 10000) {
                throw "Missing cardinal side travel for ${kind}, point $initialPoint"
            }
        }
    }
    $boardedMask = [int]$row.probes[0].boardedMask -bor [int]$row.probes[1].boardedMask
    $alightedMask = [int]$row.probes[0].alightedMask -bor [int]$row.probes[1].alightedMask
    $boarded = $row.probes[0].boarded + $row.probes[1].boarded
    $alighted = $row.probes[0].alighted + $row.probes[1].alighted
    if ($boardedMask -ne 15 -or $alightedMask -ne 15 -or $boarded -ne $row.boarded `
        -or $alighted -ne $row.alighted) {
        throw "Aggregate passenger coverage disagrees with vehicle probes for $kind"
    }
}
Write-Output "CITY_ROAD_ROUTES_CHECK_OK routes=8 vehicles=16 scope=authored_map_physics_fixture report=$reportPath"
