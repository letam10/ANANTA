$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$runner = Join-Path $projectRoot 'Tools\Build\Test-CityRowboat.ps1'
$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($runner, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count -gt 0) {
    throw 'Rowboat runner parse failed'
}
$assignment = @($ast.FindAll({
    param($node)
    $node -is [System.Management.Automation.Language.AssignmentStatementAst] -and
        $node.Left.Extent.Text -eq '$completedUtc'
}, $true))
$gate = @($ast.FindAll({
    param($node)
    $node -is [System.Management.Automation.Language.IfStatementAst] -and
        $node.Extent.Text.Contains('Rowboat report completion timestamp is outside this run')
}, $true))
if ($assignment.Count -ne 1 -or $gate.Count -ne 1) {
    throw 'Missing actual rowboat timestamp assignment or freshness gate'
}
$readTimestamp = [scriptblock]::Create($assignment[0].Extent.Text)
$freshness = [scriptblock]::Create($gate[0].Extent.Text)
$instant = [DateTime]::UtcNow.AddSeconds(-10)
$utcText = $instant.ToString('o', [Globalization.CultureInfo]::InvariantCulture)
$offsetText = ([DateTimeOffset]$instant).ToOffset([TimeSpan]::FromHours(7)).ToString('o')
$jsonReport = ('{"completedUtc":"' + $utcText + '"}') | ConvertFrom-Json
$cases = @(
    @{
        value = $utcText
        expected = $true
    },
    @{
        value = $instant
        expected = $true
    },
    @{
        value = $jsonReport.completedUtc
        expected = $true
    },
    @{
        value = $offsetText
        expected = $true
    },
    @{
        value = $instant.AddMinutes(-10)
        expected = $false
    },
    @{
        value = $instant.AddMinutes(10)
        expected = $false
    },
    @{
        value = 'invalid timestamp'
        expected = $false
    }
)
$startedUtc = $instant.AddSeconds(-1)
foreach ($case in $cases) {
    $report = [pscustomobject]@{ completedUtc = $case.value }
    $passed = $true
    try {
        . $readTimestamp
        . $freshness
        if ([Math]::Abs(($completedUtc - $instant).TotalMilliseconds) -gt 0.01) {
            throw 'Timestamp lost timezone or precision'
        }
    } catch {
        $passed = $false
    }
    if ($passed -ne $case.expected) {
        throw "Unexpected timestamp acceptance: $($case.value)"
    }
}
Write-Output 'CITY_ROWBOAT_TIMESTAMP_TEST_OK cases=7'
