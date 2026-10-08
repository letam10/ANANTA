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
& (Join-Path $PSScriptRoot 'Test-CityHLODLog.ps1') -LogPath $logPath -SingleHLOD $SingleHLOD
Write-Output "CITY_HLOD_BUILD_OK LOG=$logPath"
