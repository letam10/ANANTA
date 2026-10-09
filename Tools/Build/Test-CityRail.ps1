[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$qaPath = Join-Path $projectRoot 'Saved\QA\CityRailCheck'
New-Item -ItemType Directory -Path $qaPath -Force | Out-Null
$configPath = Join-Path $qaPath 'GameUserSettings.ini'
Copy-Item -LiteralPath (Join-Path $projectRoot 'Config\DefaultGameUserSettings.ini') -Destination $configPath
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$logPath = Join-Path $qaPath 'CityRailCheck.log'
$reportPath = Join-Path $qaPath 'Report.json'
$startedUtc = [DateTime]::UtcNow
$arguments = @(
    "$projectRoot\ANANTA.uproject",
    '/Game/ANANTA/Maps/ANANTA_City',
    '-game',
    '-NullRHI',
    '-CityRailCheck',
    '-CityQASlot',
    "-GameUserSettingsINI=$configPath",
    '-NoSaveConfig',
    '-NoSplash',
    '-nosound',
    '-unattended',
    "-abslog=$logPath"
)
& $editorPath @arguments *> (Join-Path $qaPath 'Console.log')
if ($LASTEXITCODE -ne 0) {
    throw "Authored rail fixture failed: $LASTEXITCODE"
}
if ((Get-Item -LiteralPath $reportPath).LastWriteTimeUtc -lt $startedUtc) {
    throw 'Stale rail report'
}
$report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
if ($report.passed -ne $true -or $report.results.Count -ne 2) {
    throw 'Rail fixture incomplete'
}
foreach ($row in $report.results) {
    if ($row.passed -ne $true -or $row.boarded -lt 2 -or $row.alighted -lt 1 -or $row.travelCm -lt 3800) {
        throw 'Missing boarding, alighting or return journey'
    }
}
if (-not (Get-Content -LiteralPath $logPath -Raw).Contains('CITY_RAIL_CHECK_FINISH success=1')) {
    throw 'Rail completion marker missing'
}
Write-Output 'CITY_RAIL_CHECK_OK trains=2 scope=authored_map_rail_physics_fixture'
