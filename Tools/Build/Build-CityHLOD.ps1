[CmdletBinding()]
param(
    [string]$SingleHLOD = '',
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$logName = if ($SingleHLOD) { 'CityHLODSample' } else { 'CityHLOD' }
$logPath = Join-Path $projectRoot "Saved\Logs\$logName.log"
$consolePath = Join-Path $projectRoot "Saved\Logs\${logName}Console.log"
$arguments = @(
    "$projectRoot\ANANTA.uproject",
    '/Game/ANANTA/Maps/ANANTA_City',
    '-run=WorldPartitionBuilderCommandlet',
    '-Builder=WorldPartitionHLODsBuilder',
    '-SetupHLODs',
    '-BuildHLODs',
    '-AllowCommandletRendering',
    '-RenderOffscreen',
    '-unattended',
    '-nop4',
    '-nosound',
    "-abslog=$logPath"
)
if ($SingleHLOD) {
    $arguments += "-BuildSingleHLOD=$SingleHLOD"
}
& $editorPath @arguments *> $consolePath
if ($LASTEXITCODE -ne 0) {
    throw "City HLOD build failed: $LASTEXITCODE. See $logPath"
}
$log = Get-Content -LiteralPath $logPath -Raw
$built = [regex]::Match($log, '#### Built (\d+) HLOD actors? ####')
if (-not $built.Success -or [int]$built.Groups[1].Value -lt 1) {
    throw "No completed HLOD build found in $logPath"
}
if ($SingleHLOD) {
    $targetMarker = "Building HLOD actor $SingleHLOD..."
    if ([int]$built.Groups[1].Value -ne 1 -or -not $log.Contains($targetMarker)) {
        throw "Requested HLOD sample was not built: $SingleHLOD"
    }
}
else {
    $cells = [regex]::Matches($log, '\[\d+ / (\d+)\] Processing cell ')
    if ($cells.Count -eq 0 -or [int]$cells[-1].Groups[1].Value -ne [int]$built.Groups[1].Value) {
        throw "HLOD setup/build totals do not match. See $logPath"
    }
}
Write-Output "CITY_HLOD_BUILD_OK LOG=$logPath"
