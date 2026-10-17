$ErrorActionPreference = 'Continue'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$LogDir = Join-Path $PSScriptRoot 'logs'
$ReceiptPath = Join-Path $PSScriptRoot 'FULL_BUILD_RECEIPT.json'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$results = @()
function Run-Step([string]$Id, [string]$Command, [scriptblock]$Action) {
    $logPath = Join-Path $LogDir ($Id + '.log')
    Push-Location $Root
    try { $output = & $Action 2>&1 | Out-String; $code = $LASTEXITCODE }
    catch { $output = ($_ | Out-String); $code = 1 }
    finally { Pop-Location }
    $output | Set-Content -LiteralPath $logPath -Encoding UTF8
    $script:results += [pscustomobject]@{
        id = $Id
        command = $Command
        exitCode = $code
        log = (Resolve-Path $logPath).Path
        marker = (($output -split "`r?`n" | Where-Object { $_ -match 'OK|PASS|COMPLETE|FAIL|VALIDATION|READBACK' } | Select-Object -Last 3) -join ' | ')
    }
    Write-Output ("FULL_BUILD_STEP " + $Id + " exit=" + $code)
}
Run-Step 'inventory' 'git status and remote' { git status --short --branch; git ls-remote origin refs/heads/main }
Run-Step 'ast_sources' 'AST parse without bytecode' {
    $files = Get-ChildItem (Join-Path $Root 'Tools') -Recurse -Filter '*.py' -File | Where-Object { $_.FullName -match 'Tools\\(A3C|A3D|A4|A5|A6|W3)\\' -and $_.FullName -notmatch '__pycache__' }
    python -B (Join-Path $PSScriptRoot 'ast_parse.py') ($files.FullName)
}
Run-Step 'water_spec' 'ThreeWater check build and spec' {
    Push-Location (Join-Path $Root 'Prototypes/ThreeWater')
    npm run check
    $a = $LASTEXITCODE
    npm run build
    $b = $LASTEXITCODE
    Pop-Location
    python (Join-Path $Root 'Tools/QA/ValidateThreeWaterSpec.py')
    if ($a -ne 0 -or $b -ne 0) { exit 1 }
}
Run-Step 'a3c_validation' 'A3C validator' { python (Join-Path $Root 'Tools/A3C/ValidateAuthoredDetail.py') (Join-Path $Root 'Tools/A3C/output/a3c-authored-detail-v1.json') (Join-Path $Root 'Tools/A3C/output/a3c-art-review-v1.json') }
Run-Step 'a3d_validation' 'A3D validator' { python (Join-Path $Root 'Tools/A3D/ValidateVehicleDetail.py') (Join-Path $Root 'Tools/A3D/output/a3d-vehicle-detail-v1.json') (Join-Path $Root 'Tools/A3D/output/a3d-art-review-v1.json') }
Run-Step 'a4_validation' 'A4 validator' { python (Join-Path $Root 'Tools/A4/ValidateStreetCivic.py') (Join-Path $Root 'Tools/A4/output/a4-street-civic-v1.json') (Join-Path $Root 'Tools/A4/output/a4-art-review-v1.json') }
Run-Step 'a5_validation' 'A5 validator' { python (Join-Path $Root 'Tools/A5/ValidateInteriorVenue.py') (Join-Path $Root 'Tools/A5/output/a5-interior-venue-v1.json') (Join-Path $Root 'Tools/A5/output/a5-art-review-v1.json') }
Run-Step 'a6_validation' 'A6 validator' { python (Join-Path $Root 'Tools/A6/ValidateAnimeCitizen.py') (Join-Path $Root 'Tools/A6/output/a6-anime-citizen-v1.json') (Join-Path $Root 'Tools/A6/output/a6-art-review-v1.json') }
Run-Step 'w3_validation' 'W3 readback validator' { python (Join-Path $Root 'Tools/W3/ValidateReadback.py') }
Run-Step 'unreal_foundation' 'Validate-ANANTA.ps1' { & (Join-Path $Root 'Tools/Build/Validate-ANANTA.ps1') }
Run-Step 'unreal_build' 'Build-ANANTA.ps1 -MaxParallelActions 2' { & (Join-Path $Root 'Tools/Build/Build-ANANTA.ps1') -MaxParallelActions 2 }
Run-Step 'diff_check' 'git diff --check' { git diff --check }
Run-Step 'lfs_check' 'git lfs fsck' { git lfs fsck }
$required = @('inventory','ast_sources','water_spec','a3c_validation','a3d_validation','a4_validation','a5_validation','a6_validation','w3_validation','unreal_foundation','unreal_build','diff_check')
$failed = @($results | Where-Object { $required -contains $_.id -and $_.exitCode -ne 0 })
$receipt = [pscustomobject]@{
    schema = 'ananta.full-build.receipt.v1'
    generatedUtc = ((Get-Date).ToUniversalTime()).ToString('o')
    root = $Root
    taskDirectory = (Resolve-Path $PSScriptRoot).Path
    requiredGatesPass = ($failed.Count -eq 0)
    lfsFsckExitCode = (($results | Where-Object id -eq 'lfs_check').exitCode)
    fpsClaim = $false
    nativeUnrealAcceptance = 'UNVERIFIED'
    headedPerformanceAcceptance = 'UNVERIFIED'
    results = @($results)
    classification = [pscustomobject]@{
        DONE = @('source_ast_parse','three_water_source_spec_build','a3c_a3d_a4_a5_a6_fixture_validators','w3_readback_validator','unreal_foundation_validation','unreal_source_build','diff_check')
        PARTIAL = @('full-build integration receipt')
        UNVERIFIED = @('native import/readback','interaction persistence','W3 native material port','headed F1 CPU GPU VRAM frame-time','60 FPS','full-map AAA visual acceptance')
        BLOCKED = @('native Unreal edits outside task ownership','pre-existing Git LFS unexpectedGitObject entries')
    }
}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReceiptPath -Encoding UTF8
Write-Output ("FULL_BUILD_RECEIPT " + $ReceiptPath)
Write-Output ("FULL_BUILD_REQUIRED_PASS " + ($failed.Count -eq 0))
if ($failed.Count -ne 0) { exit 1 }
exit 0
