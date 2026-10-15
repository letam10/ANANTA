$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot '..\Build\Test-CityPlacements.ps1'
$tokens = $null
$errors = $null
$ast = [Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref]$tokens, [ref]$errors)
if ($errors.Count -ne 0) {
    throw 'Placement runner PowerShell parse failed'
}
$changes = @($ast.FindAll({
    param($node)
    $node -is [Management.Automation.Language.AssignmentStatementAst] -and
    $node.Left.Extent.Text -eq '$settings' -and $node.Right.Extent.Text -like '*-replace*'
}, $true))
if ($changes.Count -ne 2) {
    throw 'Expected exactly two quality replacements'
}
$cases = @('100.000000', '85', '3', '72.5')
foreach ($value in $cases) {
    $settings = "sg.ResolutionQuality=$value`nsg.ShadowQuality=1`nsg.TextureQuality=2"
    foreach ($change in $changes) {
        Invoke-Expression $change.Extent.Text
    }
    if ($settings -notmatch '(?m)^sg.ResolutionQuality=100$' -or
        $settings -notmatch '(?m)^sg.ShadowQuality=3$' -or
        $settings -notmatch '(?m)^sg.TextureQuality=3$') {
        throw "Native scale regression failed for input $value"
    }
}
Write-Output 'CITY_PLACEMENT_NATIVE_SCALE_TEST_OK cases=4 scope=actual_runner_assignments'
