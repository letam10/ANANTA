[CmdletBinding()]
param(
    [string]$SingleHLOD = '',
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$qaPath = Join-Path $projectRoot 'Saved\QA'
$applyPath = Join-Path $qaPath 'CityExpansionApplied.json'
$readbackPath = Join-Path $qaPath 'CityMobilityMapReadback.json'

function Get-HLODFileHash([string]$Path) {
    $stream = [IO.File]::OpenRead($Path)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        [BitConverter]::ToString($algorithm.ComputeHash($stream)).Replace('-', '').ToLowerInvariant()
    } finally {
        $algorithm.Dispose()
        $stream.Dispose()
    }
}

function Get-SourceIdentity {
    $applied = Get-Content -LiteralPath $applyPath -Raw | ConvertFrom-Json
    $readback = Get-Content -LiteralPath $readbackPath -Raw | ConvertFrom-Json
    if ($applied.map -cne '/Game/ANANTA/Maps/ANANTA_City' -or $applied.stage -cne 'expanded' -or
        [Math]::Abs($applied.layout.widthMetres - 6788.2250993908565) -ge 0.000001 -or
        $applied.writtenGroups -ne 85386 -or $applied.writtenInstances -ne 1660761 -or
        $applied.layout.groups -ne 85386 -or $applied.layout.instances -ne 1660761) {
        throw 'Applied map identity does not match the current 6.8 km city'
    }
    if ($readback.status -cne 'PASS' -or $readback.groups -ne $applied.writtenGroups -or
        $readback.instances -ne $applied.writtenInstances -or
        (Get-Item -LiteralPath $readbackPath).LastWriteTimeUtc -lt
        (Get-Item -LiteralPath $applyPath).LastWriteTimeUtc) {
        throw 'Current persisted map readback is missing, stale or mismatched'
    }
    [ordered]@{
        map = $applied.map
        stage = $applied.stage
        widthMetres = $applied.layout.widthMetres
        sourceGroups = $applied.writtenGroups
        sourceInstances = $applied.writtenInstances
        applySha256 = Get-HLODFileHash $applyPath
        readbackSha256 = Get-HLODFileHash $readbackPath
    }
}

$identity = Get-SourceIdentity
$runId = [Guid]::NewGuid().ToString('N')
$logName = if ($SingleHLOD) { 'CityHLODSample' } else { 'CityHLOD' }
$logPath = Join-Path $projectRoot "Saved\Logs\$logName-$runId.log"
$consolePath = Join-Path $projectRoot "Saved\Logs\$logName-${runId}Console.log"
$receiptName = if ($SingleHLOD) { 'CityHLODBuildSampleReceipt.json' } else { 'CityHLODBuildReceipt.json' }
$receiptPath = Join-Path $qaPath $receiptName
$receipt = [ordered]@{
    schemaVersion = 1
    status = 'BUILDING'
    scope = $(if ($SingleHLOD) { 'sample' } else { 'full' })
    singleHLOD = $(if ($SingleHLOD) { $SingleHLOD } else { $null })
    runId = $runId
    sourceIdentity = $identity
    startedUtc = [DateTime]::UtcNow.ToString('o')
    logPath = $logPath
    forceRebuild = $true
}
# Vo hieu bien nhan cu truoc khi bat dau; lan build that bai khong duoc tai dung PASS.
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
$arguments = @(
    "$projectRoot\ANANTA.uproject",
    '/Game/ANANTA/Maps/ANANTA_City',
    '-run=WorldPartitionBuilderCommandlet',
    '-Builder=WorldPartitionHLODsBuilder',
    '-SetupHLODs',
    '-BuildHLODs',
    '-RebuildHLODs',
    '-AllowCommandletRendering',
    '-RenderOffscreen',
    '-unattended',
    '-nop4',
    '-nosound',
    "-abslog=$logPath"
)
if ($SingleHLOD) {
    $arguments += "-BuildSingleHLOD=$SingleHLOD"
}
& $editorPath @arguments *> $consolePath
if ($LASTEXITCODE -ne 0) {
    throw "City HLOD build failed: $LASTEXITCODE. See $logPath"
}
$validated = & (Join-Path $PSScriptRoot 'Test-CityHLODLog.ps1') `
    -LogPath $logPath -SingleHLOD $SingleHLOD -PassThru
$after = Get-SourceIdentity
if (($identity | ConvertTo-Json -Compress) -cne ($after | ConvertTo-Json -Compress)) {
    throw 'Map identity evidence changed while HLOD was building'
}
$logItem = Get-Item -LiteralPath $logPath
if ($logItem.LastWriteTimeUtc -lt [DateTime]::Parse($receipt.startedUtc).ToUniversalTime()) {
    throw 'Build log predates this run'
}
$receipt.status = 'PASS'
$receipt.completedUtc = [DateTime]::UtcNow.ToString('o')
$receipt.logSha256 = $validated.logSha256
$receipt.builtActorCount = $validated.builtActorCount
$receipt.builtActors = @($validated.builtActors)
$temporaryReceipt = "$receiptPath.$runId.tmp"
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $temporaryReceipt -Encoding UTF8
Move-Item -LiteralPath $temporaryReceipt -Destination $receiptPath -Force
Write-Output "CITY_HLOD_BUILD_OK LOG=$logPath"
Write-Output "CITY_HLOD_RECEIPT=$receiptPath SCOPE=$($receipt.scope)"
