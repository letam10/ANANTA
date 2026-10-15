[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [string]$ArchiveDirectory
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if ([string]::IsNullOrWhiteSpace($ArchiveDirectory)) {
    $ArchiveDirectory = Join-Path $projectRoot 'Saved\Packages\ANANTA-Coastal-Windows'
}
$automation = Join-Path $EngineRoot 'Engine\Build\BatchFiles\RunUAT.bat'
$project = Join-Path $projectRoot 'ANANTA.uproject'
if (-not (Test-Path -LiteralPath $automation)) {
    throw "Missing AutomationTool: $automation"
}
$arguments = @(
    'BuildCookRun',
    "-project=$project",
    '-noP4',
    '-platform=Win64',
    '-clientconfig=Shipping',
    '-build',
    '-cook',
    '-map=/Game/ANANTA/Maps/ANANTA_CoastalCity',
    '-stage',
    '-pak',
    '-iostore',
    '-compressed',
    '-archive',
    "-archivedirectory=$ArchiveDirectory",
    '-unattended',
    '-utf8output',
    '-prereqs',
    '-nodebuginfo'
)
& $automation @arguments
if ($LASTEXITCODE -ne 0) {
    throw "Packaging failed with exit code $LASTEXITCODE."
}
$executable = Join-Path $ArchiveDirectory 'Windows\ANANTA.exe'
if (-not (Test-Path -LiteralPath $executable)) {
    throw "Archive has no launcher: $executable"
}
Write-Output "ANANTA_PACKAGE_OK $executable"
Write-Output 'Package created only. The game executable was not launched.'
