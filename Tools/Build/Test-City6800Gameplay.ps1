[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Set-Location -LiteralPath $projectRoot
$reportPath = Join-Path $projectRoot 'Saved\QA\City6800GameplayRound.json'
$map = Get-Content -LiteralPath 'Saved\QA\CityExpansionApplied.json' -Raw | ConvertFrom-Json
$readback = Get-Content -LiteralPath 'Saved\QA\CityMobilityMapReadback.json' -Raw | ConvertFrom-Json
$collision = Get-Content -LiteralPath 'Saved\QA\CityWholeMapCollision.json' -Raw | ConvertFrom-Json
$boundaries = Get-Content -LiteralPath 'Saved\QA\CityWorldBoundaries.json' -Raw | ConvertFrom-Json
if ([Math]::Abs($map.layout.widthMetres - 6788.2250993908565) -gt 0.01 `
    -or $readback.status -ne 'PASS' -or $readback.groups -ne $map.writtenGroups `
    -or $readback.instances -ne $map.writtenInstances -or $collision.passed -ne $true `
    -or $collision.errors -ne 0 -or $boundaries.passed -ne 1 -or $boundaries.errors -ne 0 `
    -or $boundaries.boundarySamples -ne 14) {
    throw 'Current expanded map prerequisite evidence is incomplete'
}
$stages = @(
    @{ Name = 'Rail'; Script = 'Test-CityRail.ps1'; Arguments = @() },
    @{ Name = 'Rowboat'; Script = 'Test-CityRowboat.ps1'; Arguments = @() },
    @{ Name = 'RoofPool'; Script = 'Test-CityRoofPool.ps1'; Arguments = @() }
)
foreach ($region in @('Core', 'East', 'West', 'South', 'NorthEast')) {
    $stages += @{ Name = "RoadRoutes_$region"; Script = 'Test-CityRoadRoutes.ps1'; Arguments = @('-Region', $region) }
}
$round = [ordered]@{
    startedUtc = [DateTime]::UtcNow.ToString('o')
    status = 'RUNNING'
    activeStage = ''
    completedStages = @()
    widthMetres = $map.layout.widthMetres
    scope = 'Authored map physics fixtures; no rendered gameplay or FPS acceptance'
}

function Save-Round {
    $round | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8
}

try {
    foreach ($stage in $stages) {
        if (Get-Process -Name UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue) {
            throw 'Another Unreal process is running; stages must be sequential'
        }
        $round.activeStage = $stage.Name
        Save-Round
        $startedUtc = [DateTime]::UtcNow
        $logPath = Join-Path $projectRoot "Saved\Logs\City6800_$($stage.Name)_Gameplay.log"
        Write-Output "CITY_6800_GAMEPLAY_STAGE_START $($stage.Name)"
        $stageArguments = $stage.Arguments
        & powershell -NoProfile -File (Join-Path $PSScriptRoot $stage.Script) @stageArguments *> $logPath
        if ($LASTEXITCODE -ne 0) {
            throw "Stage $($stage.Name) failed with exit $LASTEXITCODE. See $logPath"
        }
        $round.completedStages += [ordered]@{
            name = $stage.Name
            passed = $true
            elapsedSeconds = [Math]::Round(([DateTime]::UtcNow - $startedUtc).TotalSeconds, 2)
            log = $logPath
        }
        Save-Round
        Write-Output "CITY_6800_GAMEPLAY_STAGE_PASS $($stage.Name)"
    }
    $round.status = 'PASS'
    $round.activeStage = ''
    $round.completedUtc = [DateTime]::UtcNow.ToString('o')
    Save-Round
    Write-Output 'CITY_6800_GAMEPLAY_ROUND_OK stages=8 scope=physics_fixtures'
} catch {
    $round.status = 'FAILED'
    $round.error = $_.Exception.Message
    $round.completedUtc = [DateTime]::UtcNow.ToString('o')
    Save-Round
    throw
}
