# Cac ham nay chi thao tac hai slot QA va bang chung cua lan choi dang chay.
function Assert-CityQASlotPath([string]$SavedRoot, [string]$Path) {
    $root = [IO.Path]::GetFullPath((Join-Path $SavedRoot 'SaveGames'))
    $full = [IO.Path]::GetFullPath($Path)
    $names = @('ANANTA_City_QA.sav', 'ANANTA_City_QA_Backup.sav')
    if ((Split-Path $full) -ne $root -or (Split-Path $full -Leaf) -notin $names) {
        throw "Refusing non-QA save path: $full"
    }
    $cursor = $full
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            $item = Get-Item -LiteralPath $cursor -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Refusing redirected QA save path: $cursor"
            }
        }
        $cursor = Split-Path $cursor
    }
    return $full
}

function Get-CityQASlotSnapshot([string]$SavedRoot) {
    foreach ($name in @('ANANTA_City_QA.sav', 'ANANTA_City_QA_Backup.sav')) {
        $path = Assert-CityQASlotPath $SavedRoot (Join-Path $SavedRoot "SaveGames\$name")
        $entry = @{ Path = $path; Existed = (Test-Path -LiteralPath $path); Bytes = $null }
        if ($entry.Existed) {
            $item = Get-Item -LiteralPath $path -Force
            $entry.Bytes = [IO.File]::ReadAllBytes($path)
            $entry.WriteUtc = $item.LastWriteTimeUtc
            $entry.CreationUtc = $item.CreationTimeUtc
            $entry.Attributes = $item.Attributes
        }
        $entry
    }
}

function Reset-CityQASlots([string]$SavedRoot, [array]$Snapshot) {
    foreach ($entry in $Snapshot) {
        $path = Assert-CityQASlotPath $SavedRoot $entry.Path
        if (Test-Path -LiteralPath $path) {
            Remove-Item -LiteralPath $path -Force
        }
    }
}

function Restore-CityQASlots([string]$SavedRoot, [array]$Snapshot) {
    $failures = @()
    foreach ($entry in $Snapshot) {
        try {
            $path = Assert-CityQASlotPath $SavedRoot $entry.Path
            if ($entry.Existed) {
                New-Item -ItemType Directory -Path (Split-Path $path) -Force | Out-Null
                if (Test-Path -LiteralPath $path) {
                    [IO.File]::SetAttributes($path, [IO.FileAttributes]::Normal)
                }
                [IO.File]::WriteAllBytes($path, $entry.Bytes)
                [IO.File]::SetCreationTimeUtc($path, $entry.CreationUtc)
                [IO.File]::SetLastWriteTimeUtc($path, $entry.WriteUtc)
                [IO.File]::SetAttributes($path, $entry.Attributes)
                $restored = [Convert]::ToBase64String([IO.File]::ReadAllBytes($path))
                if ($restored -ne [Convert]::ToBase64String($entry.Bytes)) {
                    throw "QA save restore bytes mismatch: $path"
                }
            } elseif (Test-Path -LiteralPath $path) {
                Remove-Item -LiteralPath $path -Force
            }
        } catch {
            $failures += $_.Exception.Message
        }
    }
    if ($failures.Count) {
        throw ($failures -join '; ')
    }
}

function Get-CityPackageFingerprint([string]$ExecutablePath) {
    $binaryDirectory = Split-Path $ExecutablePath
    if ((Split-Path $binaryDirectory -Leaf) -ne 'Win64' -or
        (Split-Path (Split-Path $binaryDirectory) -Leaf) -ne 'Binaries') {
        throw 'Use the packaged ANANTA\Binaries\Win64 executable, not the bootstrap executable.'
    }
    $packageRoot = [IO.Path]::GetFullPath((Join-Path $binaryDirectory '..\..\..'))
    $prefix = $packageRoot.TrimEnd('\') + '\'
    $containers = @(Get-ChildItem -LiteralPath $packageRoot -Recurse -File |
        Where-Object { $_.Extension -in @('.pak', '.utoc', '.ucas') } | Sort-Object FullName)
    if (-not $containers.Count) {
        throw "No packaged containers found under $packageRoot"
    }
    $entries = @($containers | ForEach-Object {
        @{
            path = $_.FullName.Substring($prefix.Length).Replace('\', '/')
            sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
        }
    })
    return @{
        executable = @{
            path = $ExecutablePath.Substring($prefix.Length).Replace('\', '/')
            sha256 = (Get-FileHash -LiteralPath $ExecutablePath -Algorithm SHA256).Hash
        }
        containers = $entries
    }
}

function Assert-CityFreshEvidence([string]$Path, [datetime]$StartedUtc) {
    $item = Get-Item -LiteralPath $Path
    if ($item.LastWriteTimeUtc -lt $StartedUtc -or $item.LastWriteTimeUtc -gt [datetime]::UtcNow) {
        throw "Stale or future evidence: $Path"
    }
}
