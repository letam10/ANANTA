[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$LogPath,
    [string]$SingleHLOD = '',
    [switch]$PassThru
)

$ErrorActionPreference = 'Stop'
$log = Get-Content -LiteralPath $LogPath -Raw
$built = [regex]::Matches($log, '#### Built (\d+) HLOD actors? ####')
if ($built.Count -ne 1 -or [int]$built[0].Groups[1].Value -lt 1) {
    throw "No unique completed HLOD build found in $LogPath"
}
$count = [int]$built[0].Groups[1].Value
$pattern = '\[(\d+) / (\d+)\] Building HLOD actor ([^\r\n]+?)\.\.\.'
$actors = [regex]::Matches($log, $pattern)
if ($actors.Count -ne $count) {
    throw "Completed count differs from actor progress in $LogPath"
}
$labels = @{}
for ($index = 0; $index -lt $actors.Count; $index++) {
    $actor = $actors[$index]
    if ([int]$actor.Groups[1].Value -ne $index + 1 -or [int]$actor.Groups[2].Value -ne $count) {
        throw "Incomplete HLOD actor sequence in $LogPath"
    }
    $label = $actor.Groups[3].Value
    if ($labels.ContainsKey($label)) {
        throw "Duplicate HLOD actor in $LogPath"
    }
    $labels[$label] = $true
}
# So o SetupHLODs khong bang so actor o nhieu muc LOD.
if ($SingleHLOD -and ($count -ne 1 -or -not $labels.ContainsKey($SingleHLOD))) {
    throw "Requested HLOD sample was not built: $SingleHLOD"
}
if (-not $SingleHLOD -and $log -match '(?i)-BuildSingleHLOD=') {
    throw "Sample build log cannot validate a full build: $LogPath"
}
if ($PassThru) {
    $stream = [IO.File]::OpenRead((Resolve-Path -LiteralPath $LogPath).Path)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        $hash = [BitConverter]::ToString($algorithm.ComputeHash($stream)).Replace('-', '').ToLowerInvariant()
    } finally {
        $algorithm.Dispose()
        $stream.Dispose()
    }
    [pscustomobject]@{
        builtActorCount = $count
        builtActors = @($labels.Keys | Sort-Object -CaseSensitive)
        logSha256 = $hash
    }
} else {
    Write-Output "CITY_HLOD_LOG_OK actors=$count LOG=$LogPath"
}
