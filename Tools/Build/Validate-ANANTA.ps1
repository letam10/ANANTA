[CmdletBinding()]
param(
    [string]$ProjectRoot,
    [switch]$RequireCompiledBridge
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}

$uprojectPath = Join-Path $ProjectRoot 'ANANTA.uproject'
$bridgePath = Join-Path $ProjectRoot 'Plugins\UE_MCP_Bridge\UE_MCP_Bridge.uplugin'
$ymlPath = Join-Path $ProjectRoot 'ue-mcp.yml'

if (-not (Test-Path -LiteralPath $uprojectPath)) { throw "Missing project: $uprojectPath" }
$project = Get-Content -LiteralPath $uprojectPath -Raw | ConvertFrom-Json

$requiredPlugins = @('UE_MCP_Bridge', 'PythonScriptPlugin', 'EnhancedInput', 'GameplayAbilities', 'Niagara', 'PCG')
$enabledPlugins = @($project.Plugins | Where-Object { $_.Enabled } | ForEach-Object { $_.Name })
$missingPlugins = @($requiredPlugins | Where-Object { $_ -notin $enabledPlugins })

$requiredFiles = @(
    'Source\ANANTA.Target.cs',
    'Source\ANANTAEditor.Target.cs',
    'Source\ANANTA\ANANTA.Build.cs',
    'Source\ANANTA\Private\ANANTA.cpp',
    'Source\ANANTA\Public\ANANTACharacter.h',
    'Tools\Editor\GenerateFoundation.py'
)
$missingFiles = @($requiredFiles | Where-Object { -not (Test-Path -LiteralPath (Join-Path $ProjectRoot $_)) })

$checks = [ordered]@{
    Project = $uprojectPath
    BridgeDescriptor = (Test-Path -LiteralPath $bridgePath)
    WorkflowConfig = (Test-Path -LiteralPath $ymlPath)
    MissingPlugins = ($missingPlugins -join ', ')
    MissingFiles = ($missingFiles -join ', ')
}

if ($RequireCompiledBridge) {
    $checks.CompiledBridge = @(
        Get-ChildItem -LiteralPath (Join-Path $ProjectRoot 'Plugins\UE_MCP_Bridge\Binaries\Win64') -Filter 'UnrealEditor-UE_MCP_Bridge.dll' -File -ErrorAction SilentlyContinue
    ).Count -gt 0
}

$checks.GetEnumerator() | ForEach-Object { '{0}: {1}' -f $_.Key, $_.Value }

if (-not $checks.BridgeDescriptor -or -not $checks.WorkflowConfig -or $missingPlugins.Count -gt 0 -or $missingFiles.Count -gt 0) {
    throw 'ANANTA foundation validation failed.'
}
if ($RequireCompiledBridge -and -not $checks.CompiledBridge) {
    throw 'UnrealEditor-UE_MCP_Bridge.dll is not compiled yet. Close Unreal Editor before building.'
}

Write-Output 'ANANTA foundation validation passed.'
