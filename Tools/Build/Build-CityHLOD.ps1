[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$logPath = Join-Path $projectRoot 'Saved\Logs\CityHLOD.log'
$consolePath = Join-Path $projectRoot 'Saved\Logs\CityHLODConsole.log'
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
& $editorPath @arguments *> $consolePath
if ($LASTEXITCODE -ne 0) {
    throw "City HLOD build failed: $LASTEXITCODE. See $logPath"
}
Write-Output "CITY_HLOD_BUILD_OK LOG=$logPath"
