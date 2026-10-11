$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
. (Join-Path $projectRoot 'Tools\Build\CityPlacementDiagnostics.ps1')
$enabled = 'LogD3D12RHI: [DRED] DRED enabled'
$tracking = 'D3D12.TrackAllAllocations=1'
$cases = @(
    @{ log = $enabled; config = @($tracking); pass = $true },
    @{ log = $enabled; config = @('D3D12.TrackAllAllocations=true'); pass = $true },
    @{ log = $enabled; config = @('D3D12.TrackAllAllocations=false'); pass = $false },
    @{ log = $enabled; config = @('D3D12.TrackAllAllocations=true_extra'); pass = $false },
    @{ log = $enabled.Replace('enabled', 'disabled'); config = @($tracking); pass = $false },
    @{ log = $enabled; config = @('D3D12.TrackAllAllocations=0'); pass = $false },
    @{ log = $enabled; config = @(); pass = $false },
    @{ log = 'diagnostic requested DRED enabled'; config = @($tracking); pass = $false },
    @{ log = $enabled; config = @($tracking, $tracking); pass = $false },
    @{ log = $enabled; config = @('D3D12.TrackAllAllocations=not_registered'); pass = $false },
    @{
        log = "$enabled`nLogConfig: CVar [[D3D12.TrackAllAllocations:1]] deferred - dummy variable"
        config = @()
        pass = $false
    }
)
foreach ($case in $cases) {
    $passed = $true
    try {
        Assert-CityPlacementDred -Log $case.log -RenderConfig $case.config
    } catch {
        $passed = $false
    }
    if ($passed -ne $case.pass) {
        throw 'DRED placement startup regression failed'
    }
}
$taskNativeConfig = Join-Path $projectRoot 'Saved\QA\CityPlacement_small_Dred\RenderConfig.txt'
$taskNativeLog = Join-Path $projectRoot 'Saved\Logs\CityPlacement_small_Dred.log'
if (Test-Path -LiteralPath $taskNativeConfig) {
    Assert-CityPlacementDred -Log (Get-Content -LiteralPath $taskNativeLog -Raw) `
        -RenderConfig (Get-Content -LiteralPath $taskNativeConfig)
}
Write-Output 'CITY_PLACEMENT_DRED_TESTS_OK cases=11'
