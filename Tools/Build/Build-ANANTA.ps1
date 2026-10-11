[CmdletBinding()]
param(
    [string]$ProjectRoot,
    [ValidateSet('ANANTAEditor', 'ANANTA')]
    [string]$Target = 'ANANTAEditor',
    [ValidateSet('Development', 'DebugGame', 'Shipping')]
    [string]$Configuration = 'Development',
    [int]$MaxParallelActions = 2,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}

$uprojectPath = Join-Path $ProjectRoot 'ANANTA.uproject'
$ubtPath = Join-Path $EngineRoot 'Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll'

if (-not (Test-Path -LiteralPath $uprojectPath)) { throw "Missing project: $uprojectPath" }
if (-not (Test-Path -LiteralPath $ubtPath)) { throw "Missing UnrealBuildTool: $ubtPath" }

$editorProcesses = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -in @('UnrealEditor.exe', 'UnrealEditor-Cmd.exe')
})
if ($editorProcesses.Count -gt 0) {
    $pids = ($editorProcesses | ForEach-Object { $_.ProcessId }) -join ', '
    throw "Unreal Editor is running (PID $pids). Close it before compiling ANANTA."
}

$arguments = @(
    $ubtPath,
    $Target,
    'Win64',
    $Configuration,
    "-Project=$uprojectPath",
    '-WaitMutex',
    '-FromMsBuild',
    "-MaxParallelActions=$MaxParallelActions"
)

Write-Output "Building $Target $Configuration..."
& dotnet @arguments
if ($LASTEXITCODE -ne 0) {
    throw "UnrealBuildTool failed with exit code $LASTEXITCODE."
}
Write-Output 'ANANTA build completed.'
