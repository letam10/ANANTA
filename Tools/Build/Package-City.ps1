[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [string]$OutputDirectory
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $projectRoot 'Saved\Builds\City'
}
$uat = Join-Path $EngineRoot 'Engine\Build\BatchFiles\RunUAT.bat'
$arguments = @(
    'BuildCookRun',
    "-project=$projectRoot\ANANTA.uproject",
    '-noP4',
    '-platform=Win64',
    '-clientconfig=Development',
    '-build',
    '-cook',
    '-map=/Game/ANANTA/Maps/ANANTA_City',
    '-stage',
    '-pak',
    '-archive',
    "-archivedirectory=$OutputDirectory",
    '-unattended',
    '-utf8output'
)
& $uat @arguments
if ($LASTEXITCODE -ne 0) {
    throw "City packaging failed: $LASTEXITCODE"
}
Write-Output "CITY_PACKAGE_OK=$OutputDirectory"
