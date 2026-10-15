[CmdletBinding()]
param(
    [switch]$ReportOnly,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$arguments = @(
    "$projectRoot\ANANTA.uproject",
    '/Game/ANANTA/Maps/ANANTA_City',
    '-run=WorldPartitionConvertCommandlet',
    '-AllowCommandletRendering',
    '-unattended',
    '-nop4',
    '-NullRHI',
    '-nosound',
    "-abslog=$projectRoot\Saved\Logs\CityPartition.log"
)
if ($ReportOnly) {
    $arguments += '-ReportOnly'
}
& $editorPath @arguments
if ($LASTEXITCODE -ne 0) {
    throw "City partition conversion failed: $LASTEXITCODE"
}
Write-Output "CITY_PARTITION_COMMAND_OK ReportOnly=$ReportOnly"
