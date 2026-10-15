[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$qaPath = Join-Path $projectRoot 'Saved\QA\CityFleetCheck'
New-Item -ItemType Directory -Path $qaPath -Force | Out-Null
$configPath = Join-Path $qaPath 'GameUserSettings.ini'
Copy-Item -LiteralPath (Join-Path $projectRoot 'Config\DefaultGameUserSettings.ini') -Destination $configPath
$logPath = Join-Path $qaPath 'CityFleetCheck.log'
$reportPath = Join-Path $qaPath 'Report.txt'
foreach ($stalePath in @($logPath, $reportPath)) {
    if (Test-Path -LiteralPath $stalePath) {
        Remove-Item -LiteralPath $stalePath
    }
}
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$arguments = @(
    "$projectRoot\ANANTA.uproject", '/Game/ANANTA/Maps/ANANTA_City', '-game',
    '-NullRHI', '-CityFleetCheck', '-CityQASlot', "-GameUserSettingsINI=$configPath",
    '-NoSplash', '-nosound', '-unattended', "-abslog=$logPath"
)
& $editorPath @arguments *> (Join-Path $qaPath 'Console.log')
if ($LASTEXITCODE -ne 0) {
    throw "City fleet physical fixtures failed: $LASTEXITCODE. See $logPath"
}
$log = Get-Content -LiteralPath $logPath -Raw
$report = Get-Content -LiteralPath $reportPath -Raw
if (-not $log.Contains('CITY_FLEET_CHECK_FINISH success=1') -or $report -notmatch '(?m)^passed=1\r?$') {
    throw "Missing successful fleet completion evidence in $qaPath"
}
$kinds = @(
    'Coach', 'CityBus', 'Taxi', 'BoxTruck', 'CargoTruck', 'TankerTruck',
    'PoliceCar', 'Ambulance', 'CargoShip', 'Motorboat', 'Sailboat'
)
foreach ($kind in $kinds) {
    if ($report -notmatch "(?m)^kind=$kind passed=1 ") {
        throw "Missing passing physical fixture for $kind"
    }
}
Write-Output "CITY_FLEET_CHECK_OK fixtures=11 scope=controlled_physics report=$reportPath"
