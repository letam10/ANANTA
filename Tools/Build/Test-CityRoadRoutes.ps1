[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [ValidateSet('Core', 'East', 'West', 'South', 'NorthEast')]
    [string]$Region = 'Core'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Region = @('Core', 'East', 'West', 'South', 'NorthEast') | Where-Object { $_ -eq $Region }
$qaName = if ($Region -eq 'Core') { 'CityRoadRoutesCheck' } else { "CityRoadRoutesCheck_$Region" }
$qaPath = Join-Path $projectRoot "Saved\QA\$qaName"
$scope = if ($Region -eq 'Core') {
    'authored-map physics fixture'
} else {
    'authored-map regional road physics fixture'
}
$regionLocations = @{
    East = @(200000, 0, 100)
    West = @(-244000, 420, 100)
    South = @(-28000, -215580, 100)
    NorthEast = @(188000, 288420, 100)
}
$regionAnchors = @{
    East = @(216000, 0)
    West = @(-216000, 0)
    South = @(0, -216000)
    NorthEast = @(216000, 288000)
}
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
    "-CityRoadRoutesRegion=$Region",
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
$marker = if ($Region -eq 'Core') {
    'CITY_ROAD_ROUTES_CHECK_FINISH success=1 reason='
} else {
    "CITY_ROAD_ROUTES_CHECK_FINISH success=1 region=$Region reason="
}
if ($report.passed -ne $true -or $report.schemaVersion -ne 1 `
    -or $report.scope -cne $scope -or $report.map -ne 'ANANTA_City' `
    -or $null -eq $report.elapsedSeconds -or $report.elapsedSeconds -le 0 `
    -or $report.elapsedSeconds -gt 240 -or $report.results.Count -ne 8 `
    -or $report.fixtureVehiclesPerKind -ne 2 -or $report.observerRelocated -ne $true `
    -or $report.streamingRadiusCm -ne 62000 -or $report.isolatedQASlot -ne $true `
    -or -not $log.Contains($marker)) {
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
if ($Region -ne 'Core') {
    $kinds[7] = 'FireEngine'
    $expectedSource = $regionLocations[$Region]
    $anchor = $regionAnchors[$Region]
    $expectedObserver = @((12000 + $anchor[0]), $anchor[1], 2000)
    if ($report.region -cne $Region -or $report.sourcePlayerLocation.Count -ne 3 `
        -or $report.observerLocation.Count -ne 3) {
        throw "Regional route provenance missing or incorrect: $reportPath"
    }
    for ($axis = 0; $axis -lt 3; $axis++) {
        if ($null -eq $report.sourcePlayerLocation[$axis] `
            -or $report.sourcePlayerLocation[$axis] -ne $expectedSource[$axis] `
            -or $null -eq $report.observerLocation[$axis] `
            -or $report.observerLocation[$axis] -ne $expectedObserver[$axis]) {
            throw "Regional source or observer coordinates disagree: $reportPath"
        }
    }
    if (($report.initialRoutePoints -join ',') -ne '0,2' `
        -or ($report.stopPointIndices -join ',') -ne '0,2,4,6' `
        -or ($report.sideOrder -join ',') -ne 'east,north,west,south') {
        throw "Unexpected route probe layout: $reportPath"
    }
}
foreach ($kind in $kinds) {
    $rows = @($report.results | Where-Object { $_.kind -eq $kind })
    if ($rows.Count -ne 1) {
        throw "Missing or duplicate road route result: $kind"
    }
    $row = $rows[0]
    if ($Region -ne 'Core') {
        $expectedKind = if ($kind -eq 'FireEngine') { 11 } else { [Array]::IndexOf($kinds, $kind) }
        $expectedRoute = "${kind}_Road_$($anchor[0])_$($anchor[1])"
        if ($null -eq $row.transportKind -or $row.transportKind -ne $expectedKind `
            -or $row.routeId -cne $expectedRoute) {
            throw "Incorrect regional enum or fixed route selection for $kind"
        }
    }
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
$scopeToken = $scope.Replace('-', '_').Replace(' ', '_')
$regionToken = if ($Region -eq 'Core') { '' } else { "region=$Region " }
Write-Output "CITY_ROAD_ROUTES_CHECK_OK routes=8 vehicles=16 ${regionToken}scope=$scopeToken report=$reportPath"
