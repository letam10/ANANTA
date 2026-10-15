[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$qaPath = Join-Path $projectRoot 'Saved\QA\CityHarborCheck'
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
if (-not (Test-Path -LiteralPath $editorPath)) {
    throw "Missing Unreal executable: $editorPath"
}
New-Item -ItemType Directory -Path $qaPath -Force | Out-Null
$configPath = Join-Path $qaPath 'GameUserSettings.ini'
Copy-Item -LiteralPath (Join-Path $projectRoot 'Config\DefaultGameUserSettings.ini') -Destination $configPath
$logPath = Join-Path $qaPath 'CityHarborCheck.log'
$reportPath = Join-Path $qaPath 'Report.json'
foreach ($stalePath in @($logPath, $reportPath)) {
    if (Test-Path -LiteralPath $stalePath) {
        Remove-Item -LiteralPath $stalePath
    }
}
$arguments = @(
    "$projectRoot\ANANTA.uproject", '/Game/ANANTA/Maps/ANANTA_City', '-game',
    '-NullRHI', '-CityHarborCheck', '-CityQASlot', "-GameUserSettingsINI=$configPath",
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
        throw 'Cannot start the harbour physics fixture process'
    }
    # Doc ca hai luong song song, tranh deadlock khi Unreal ghi nhieu log.
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    if (-not $process.WaitForExit(330000)) {
        $process.Kill()
        $process.WaitForExit(5000) | Out-Null
        throw "Harbour physics fixture exceeded process watchdog (330 seconds). See $logPath"
    }
    $exitCode = $process.ExitCode
    [IO.File]::WriteAllText((Join-Path $qaPath 'Console.log'), $stdoutTask.GetAwaiter().GetResult())
    [IO.File]::WriteAllText((Join-Path $qaPath 'Error.log'), $stderrTask.GetAwaiter().GetResult())
    if ($exitCode -ne 0) {
        throw "Harbour physics fixture exited with code ${exitCode}. See $logPath"
    }
} finally {
    $process.Dispose()
}
if (-not (Test-Path -LiteralPath $reportPath) -or -not (Test-Path -LiteralPath $logPath)) {
    throw "Missing fresh harbour report or log in $qaPath"
}
if ((Get-Item -LiteralPath $reportPath).LastWriteTimeUtc -lt $startedUtc) {
    throw "Stale harbour report: $reportPath"
}
$report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
$log = Get-Content -LiteralPath $logPath -Raw
if ($report.passed -ne $true -or $report.scope -ne 'authored-map physics fixture' `
    -or $report.elapsedSeconds -gt 181 -or $report.results.Count -ne 3 `
    -or -not $log.Contains('CITY_HARBOR_CHECK_FINISH success=1')) {
    throw "Harbour fixture failed or completion evidence is incomplete: $reportPath"
}
$completedUtc = [DateTime]::Parse($report.completedUtc).ToUniversalTime()
if ($completedUtc -lt $startedUtc -or $completedUtc -gt [DateTime]::UtcNow.AddSeconds(1)) {
    throw "Harbour report completion timestamp is outside this run"
}
foreach ($kind in @('CargoShip', 'Motorboat', 'Sailboat')) {
    $rows = @($report.results | Where-Object { $_.kind -eq $kind })
    if ($rows.Count -ne 1) {
        throw "Missing or duplicate harbour result: $kind"
    }
    $row = $rows[0]
    if ($row.status -ne 'PASS' -or $row.boarded -lt 1 -or $row.alighted -lt 1 `
        -or $row.maxDistanceCm -le 9000 -or $row.dockDistanceCm -ge 200 `
        -or $row.minWaterlineCm -lt -125 -or $row.outbound -ne $true -or $row.returned -ne $true) {
        throw "Incomplete authored harbour round trip for ${kind}: $($row.reason)"
    }
}
Write-Output "CITY_HARBOR_CHECK_OK vessels=3 scope=authored_map_physics_fixture report=$reportPath"
