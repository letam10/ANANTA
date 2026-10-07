[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Script,
    [string]$LogName = 'CityEditor',
    [switch]$Render,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$projectPath = Join-Path $projectRoot 'ANANTA.uproject'
$scriptPath = (Resolve-Path -LiteralPath $Script).Path
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$logPath = Join-Path $projectRoot "Saved\Logs\$LogName.log"
$arguments = @(
    $projectPath,
    '-run=pythonscript',
    "-script=$scriptPath",
    '-unattended',
    '-nop4',
    '-nosound',
    '-UTF8Output',
    "-abslog=$logPath"
)
if (-not $Render) {
    $arguments += '-NullRHI'
}
& $editorPath @arguments
$code = $LASTEXITCODE
Write-Output "CITY_EDITOR_EXIT=$code LOG=$logPath"
if ($code -ne 0) {
    throw "City editor script failed: $code. See $logPath"
}
