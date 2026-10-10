$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$runner = Join-Path $projectRoot 'Tools\Build\Test-CityPlacements.ps1'
$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($runner, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count -gt 0) {
    throw 'Placement runner parse failed'
}
$guard = @($ast.FindAll({
    param($node)
    $node -is [System.Management.Automation.Language.IfStatementAst] -and
        $node.Extent.Text.Contains('Shadow async diagnostic did not reach')
}, $true))
$configRead = @($ast.FindAll({
    param($node)
    $node -is [System.Management.Automation.Language.AssignmentStatementAst] -and
        $node.Left.Extent.Text -eq '$renderConfig'
}, $true))
if ($guard.Count -ne 1 -or $configRead.Count -ne 1 -or
    $configRead[0].Extent.EndOffset -ge $guard[0].Extent.StartOffset) {
    throw 'Diagnostic guard must read the actual config first'
}
$block = [scriptblock]::Create($guard[0].Extent.Text)
$cases = @(
    @{
        diagnostic = 'NaniteShadowAsyncOn'
        config = @('r.Nanite.AsyncRasterization.ShadowDepths=1')
        pass = $true
    },
    @{
        diagnostic = 'NaniteShadowAsyncOn'
        config = @('r.Nanite.AsyncRasterization.ShadowDepths=0')
        pass = $false
    },
    @{
        diagnostic = 'NaniteShadowAsyncOn'
        config = @('r.ScreenPercentage=100')
        pass = $false
    },
    @{
        diagnostic = 'None'
        config = @('r.ScreenPercentage=100')
        pass = $true
    }
)
foreach ($case in $cases) {
    $Diagnostic = $case.diagnostic
    $renderConfig = $case.config
    $passed = $true
    try {
        & $block
    } catch {
        $passed = $false
    }
    if ($passed -ne $case.pass) {
        throw "Wrong diagnostic acceptance: $Diagnostic / $renderConfig"
    }
}
Write-Output 'CITY_PLACEMENT_DIAGNOSTIC_TESTS_OK cases=4'
