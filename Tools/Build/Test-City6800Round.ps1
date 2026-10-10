[CmdletBinding()]
param(
    [int]$MapApplyProcessId = 0
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Set-Location -LiteralPath $projectRoot
$reportPath = Join-Path $projectRoot 'Saved\QA\City6800AcceptanceRound.json'
$round = [ordered]@{
    startedUtc = [DateTime]::UtcNow.ToString('o')
    status = 'RUNNING'
    completedStages = @()
    activeStage = 'WaitForMapApply'
    scope = 'Editor build, automation, persisted map, collision and authored gameplay; no GPU acceptance'
}

function Save-Round {
    $round | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8
}

function Invoke-Stage {
    param(
        [string]$Name,
        [string]$ScriptName,
        [string[]]$StageArguments = @()
    )
    $round.activeStage = $Name
    Save-Round
    $logPath = Join-Path $projectRoot "Saved\Logs\City6800_${Name}_Round.log"
    $scriptPath = Join-Path $PSScriptRoot $ScriptName
    $startedUtc = [DateTime]::UtcNow
    Write-Output "CITY_6800_STAGE_START $Name"
    & powershell -NoProfile -File $scriptPath @StageArguments *> $logPath
    if ($LASTEXITCODE -ne 0) {
        throw "Stage $Name failed with exit $LASTEXITCODE. See $logPath"
    }
    $round.completedStages += [ordered]@{
        name = $Name
        passed = $true
        elapsedSeconds = [Math]::Round(([DateTime]::UtcNow - $startedUtc).TotalSeconds, 2)
        log = $logPath
    }
    Save-Round
    Write-Output "CITY_6800_STAGE_PASS $Name"
}

try {
    New-Item -ItemType Directory -Path (Split-Path $reportPath) -Force | Out-Null
    Save-Round
    if ($MapApplyProcessId -gt 0) {
        $deadline = [DateTime]::UtcNow.AddHours(2)
        while (Get-Process -Id $MapApplyProcessId -ErrorAction SilentlyContinue) {
            if ([DateTime]::UtcNow -gt $deadline) {
                throw 'Map apply still running after two hours; no subsequent stage started'
            }
            Start-Sleep -Seconds 5
        }
    }
    $applyLog = Join-Path $projectRoot 'Saved\Logs\City6800ApplyRunner.log'
    if (-not (Get-Content -LiteralPath $applyLog -Raw).Contains('CITY_EDITOR_EXIT=0')) {
        throw 'Map application has not exited successfully'
    }
    $map = Get-Content -LiteralPath 'Saved\QA\CityExpansionApplied.json' -Raw | ConvertFrom-Json
    if ([Math]::Abs($map.layout.widthMetres - 6788.2250993908565) -gt 0.01 `
        -or $map.physicalBoundaryCheckRequired -ne $true) {
        throw 'Saved application report is not the new 6.8 km map'
    }
    if (Get-Process -Name UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue) {
        throw 'Another Unreal process is running; acceptance stages remain sequential'
    }
    Invoke-Stage 'Build' 'Build-ANANTA.ps1' @('-Target', 'ANANTAEditor', '-MaxParallelActions', '2')
    Invoke-Stage 'Automation' 'Test-CityRuntime.ps1'
    $automation = Get-Content -LiteralPath 'Saved\QA\CityAutomation\index.json' -Raw | ConvertFrom-Json
    $railRegression = @($automation.tests | Where-Object {
        $_.fullTestPath -eq 'ANANTA.City.Rail.BoardingUnderStationCanopy'
    })
    if ($automation.tests.Count -lt 21 -or $railRegression.Count -ne 1 `
        -or $railRegression[0].state -notin @('Success', 'SuccessWithWarnings')) {
        throw 'The new rail canopy regression is absent or did not pass'
    }
    Invoke-Stage 'Readback' 'Run-CityEditor.ps1' @(
        '-Script', 'Tools/Editor/VerifyCityMobilityMap.py', '-LogName', 'City6800Readback'
    )
    Invoke-Stage 'Collision' 'Run-CityEditor.ps1' @(
        '-Script', 'Tools/Editor/AuditCityCollision.py', '-LogName', 'City6800Collision'
    )
    Invoke-Stage 'Boundaries' 'Run-CityEditor.ps1' @(
        '-Script', 'Tools/Editor/VerifyCityBoundaries.py', '-LogName', 'City6800Boundaries'
    )
    Invoke-Stage 'Rail' 'Test-CityRail.ps1'
    Invoke-Stage 'Rowboat' 'Test-CityRowboat.ps1'
    Invoke-Stage 'RoofPool' 'Test-CityRoofPool.ps1'
    $round.status = 'PASS'
    $round.activeStage = ''
    $round.completedUtc = [DateTime]::UtcNow.ToString('o')
    Save-Round
    Write-Output 'CITY_6800_ACCEPTANCE_ROUND_OK scope=collision_and_authored_gameplay'
} catch {
    $round.status = 'FAILED'
    $round.error = $_.Exception.Message
    $round.completedUtc = [DateTime]::UtcNow.ToString('o')
    Save-Round
    throw
}
