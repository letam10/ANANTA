$ErrorActionPreference = 'Stop'
$project = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$validator = Join-Path $project 'Tools\Build\Test-CityHLODLog.ps1'
$output = Join-Path $project 'Saved\QA\CityHLODLogCases'
New-Item -ItemType Directory -Force -Path $output | Out-Null
$first = '[1 / 2] Building HLOD actor City_HLOD/A...'
$second = '[2 / 2] Building HLOD actor City_HLOD/B...'
$complete = @('[63 / 63] Processing cell DifferentCellCount...', $first, $second,
    '#### Built 2 HLOD actors ####') -join "`n"
$cases = @(
    @{ Name = 'DifferentCellCount'; Text = $complete; Pass = $true },
    @{ Name = 'Unfinished'; Text = "$first`n$second"; Pass = $false },
    @{ Name = 'MissingActor'; Text = "$first`n#### Built 2 HLOD actors ####"; Pass = $false },
    @{ Name = 'SkippedSequence'; Text = $complete.Replace('[2 / 2]', '[3 / 2]'); Pass = $false },
    @{ Name = 'DuplicateActor'; Text = $complete.Replace('City_HLOD/B', 'City_HLOD/A'); Pass = $false },
    @{ Name = 'WrongTotal'; Text = $complete.Replace('[2 / 2]', '[2 / 3]'); Pass = $false },
    @{ Name = 'ZeroBuilt'; Text = '#### Built 0 HLOD actors ####'; Pass = $false },
    @{ Name = 'WrongSample'; Text = '[1 / 1] Building HLOD actor City_HLOD/A...' +
        "`n#### Built 1 HLOD actors ####"; Sample = 'City_HLOD/B'; Pass = $false },
    @{ Name = 'CorrectSample'; Text = '[1 / 1] Building HLOD actor City_HLOD/A...' +
        "`n#### Built 1 HLOD actors ####"; Sample = 'City_HLOD/A'; Pass = $true }
)
$results = foreach ($case in $cases) {
    $path = Join-Path $output ($case.Name + '.log')
    [IO.File]::WriteAllText($path, $case.Text)
    $passed = $false
    $detail = ''
    try {
        & $validator -LogPath $path -SingleHLOD $case.Sample | Out-Null
        $passed = $true
    }
    catch {
        $detail = $_.Exception.Message
    }
    if ($passed -ne $case.Pass) {
        throw "Unexpected HLOD validator result for $($case.Name): $detail"
    }
    [PSCustomObject]@{ Case = $case.Name; ExpectedPass = $case.Pass; ActualPass = $passed }
}
$results | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $output 'Results.json') -Encoding utf8
Write-Output "CITY_HLOD_LOG_CASES_OK cases=$($results.Count)"
