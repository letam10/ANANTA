[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$qaConfig = Join-Path $projectRoot 'Saved\QA\CityAutomation\GameUserSettings.ini'
New-Item -ItemType Directory -Path (Split-Path $qaConfig) -Force | Out-Null
$arguments = @(
    "$projectRoot\ANANTA.uproject",
    '-unattended',
    '-nop4',
    '-NullRHI',
    '-nosound',
    '-nosplash',
    "-GameUserSettingsINI=$qaConfig",
    '-ExecCmds=Automation RunTests ANANTA.City',
    '-TestExit=Automation Test Queue Empty',
    "-ReportExportPath=$projectRoot\Saved\QA\CityAutomation",
    "-abslog=$projectRoot\Saved\Logs\CityAutomation.log"
)
& $editorPath @arguments
if ($LASTEXITCODE -ne 0) {
    throw "City runtime automation failed: $LASTEXITCODE"
}
$report = Get-Content -LiteralPath "$projectRoot\Saved\QA\CityAutomation\index.json" -Raw | ConvertFrom-Json
if ($report.failed -ne 0 -or $report.notRun -ne 0 -or $report.inProcess -ne 0 -or $report.succeeded -lt 1) {
    throw "Automation report did not pass: $($report.succeeded) passed, $($report.failed) failed"
}
Write-Output 'CITY_AUTOMATION_PROCESS_OK'
