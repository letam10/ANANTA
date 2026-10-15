function Assert-CityPlacementDred {
    param(
        [Parameter(Mandatory)][string]$Log,
        [string[]]$RenderConfig = @()
    )

    $dredEnabled = $Log -match '(?m)^.*LogD3D12RHI: \[DRED\] DRED enabled\s*$'
    $tracking = @($RenderConfig | Where-Object { $_.StartsWith('D3D12.TrackAllAllocations=') })
    $trackingEnabled = $tracking.Count -eq 1 -and $tracking[0] -cin @(
        'D3D12.TrackAllAllocations=1',
        'D3D12.TrackAllAllocations=true'
    )
    if (-not $dredEnabled -or -not $trackingEnabled) {
        throw 'DRED placement diagnostic startup evidence is missing'
    }
}
