[CmdletBinding()]
param(
    [ValidateSet('Collision', 'Transit')]
    [string]$Mode = 'Collision',
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$qaPath = Join-Path $projectRoot "Saved\QA\City${Mode}Check"
New-Item -ItemType Directory -Path $qaPath -Force | Out-Null
$configPath = Join-Path $qaPath 'GameUserSettings.ini'
Copy-Item -LiteralPath (Join-Path $projectRoot 'Config\DefaultGameUserSettings.ini') -Destination $configPath
$logPath = Join-Path $projectRoot "Saved\Logs\City${Mode}Check.log"
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$arguments = @(
    "$projectRoot\ANANTA.uproject", '/Game/ANANTA/Maps/ANANTA_City', '-game',
    '-RenderOffscreen', '-windowed', '-ForceRes', '-ResX=1920', '-ResY=1080',
    "-City${Mode}Check", '-CityQASlot', "-GameUserSettingsINI=$configPath",
    '-NoSplash', '-nosound', '-unattended', "-abslog=$logPath"
)
& $editorPath @arguments *> (Join-Path $qaPath 'Console.log')
if ($LASTEXITCODE -ne 0) {
    throw "City $Mode failed: $LASTEXITCODE. See $logPath"
}
$marker = "CITY_$($Mode.ToUpper())_CHECK_FINISH success=1"
if (-not (Get-Content -LiteralPath $logPath -Raw).Contains($marker)) {
    throw "Missing completion evidence $marker in $logPath"
}
Write-Output "CITY_MOBILITY_CHECK_OK mode=$Mode log=$logPath"
