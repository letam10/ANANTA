[CmdletBinding()]
param(
    [switch]$HeadedHero,
    [switch]$BlueHour,
    [ValidateRange(1, 86400)]
    [int]$TimeoutSeconds = 330,
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$projectFile = Join-Path $projectRoot 'ANANTA.uproject'
$editorPath = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$mode = if ($HeadedHero) { 'headed-hero' } else { 'nullrhi' }
$expectedViews = if ($HeadedHero) { 5 } else { 122 }
$timestamp = [DateTime]::UtcNow.ToString(
    'yyyyMMdd-HHmmssfff',
    [Globalization.CultureInfo]::InvariantCulture
)
$artifactRoot = Join-Path $projectRoot 'Saved\QA\CoastalInteractive'
$runFolder = Join-Path $artifactRoot $timestamp
$suffix = 0
while (Test-Path -LiteralPath $runFolder) {
    $suffix++
    $runFolder = Join-Path $artifactRoot "$timestamp-$suffix"
}
New-Item -ItemType Directory -Path $runFolder -Force | Out-Null
$runtimeLogPath = Join-Path $runFolder 'runtime.log'
$consoleLogPath = Join-Path $runFolder 'console.log'
$errorLogPath = Join-Path $runFolder 'error.log'
New-Item -ItemType File -Path $runtimeLogPath -Force | Out-Null
New-Item -ItemType File -Path $consoleLogPath -Force | Out-Null
New-Item -ItemType File -Path $errorLogPath -Force | Out-Null

if (-not (Test-Path -LiteralPath $projectFile -PathType Leaf)) {
    throw "Missing ANANTA project file: $projectFile. Artifacts: $runFolder"
}
if (-not (Test-Path -LiteralPath $editorPath -PathType Leaf)) {
    throw "Missing UnrealEditor-Cmd executable: $editorPath. Artifacts: $runFolder"
}

$arguments = @(
    $projectFile,
    '/Game/ANANTA/Maps/ANANTA_CoastalCity',
    '-game',
    '-CoastalQA'
)
if (-not $HeadedHero) {
    $arguments += '-NullRHI'
}
$arguments += @(
    '-unattended',
    '-NoSound',
    '-NoSplash',
    '-FullStdOutLogOutput',
    "-abslog=$runtimeLogPath"
)
if ($HeadedHero) {
    $arguments += @(
        '-CoastalHeroOnly',
        '-windowed',
        '-ForceRes',
        '-ResX=1280',
        '-ResY=720'
    )
}
if ($BlueHour) {
    $arguments += '-CoastalBlueHour'
}

function ConvertTo-ProcessArgument {
    param([string]$Value)
    if ($Value -notmatch '[\s"]') {
        return $Value
    }
    return '"' + $Value.Replace('"', '\"') + '"'
}

$process = [System.Diagnostics.Process]::new()
$startInfo = [System.Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $editorPath
$startInfo.WorkingDirectory = $projectRoot
$startInfo.UseShellExecute = $false
$startInfo.CreateNoWindow = $true
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true
$arguments | ForEach-Object {
    [void]$startInfo.ArgumentList.Add([string]$_)
}
$process.StartInfo = $startInfo
$exitCode = $null
$runError = $null
$runStartedUtc = [DateTime]::UtcNow
try {
    if (-not $process.Start()) {
        throw "UnrealEditor-Cmd failed to start. Artifacts: $runFolder"
    }
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $waitMilliseconds = $TimeoutSeconds * 1000
    if (-not $process.WaitForExit($waitMilliseconds)) {
        try {
            $process.Kill($true)
        }
        catch {
            try {
                $process.Kill()
            }
            catch {
            }
        }
        $process.WaitForExit(5000) | Out-Null
        throw "Coastal interactive run timed out after $TimeoutSeconds seconds. Artifacts: $runFolder"
    }
    $process.WaitForExit()
    $exitCode = $process.ExitCode
    [IO.File]::WriteAllText($consoleLogPath, $stdoutTask.GetAwaiter().GetResult(), [Text.UTF8Encoding]::new($false))
    [IO.File]::WriteAllText($errorLogPath, $stderrTask.GetAwaiter().GetResult(), [Text.UTF8Encoding]::new($false))
}
catch {
    $runError = $_.Exception.Message
}
finally {
    $process.Dispose()
}
if ($null -ne $runError) {
    throw $runError
}
if ($exitCode -ne 0) {
    throw "Coastal interactive run failed with exit code $exitCode. Artifacts: $runFolder"
}

$runtimeLog = Get-Content -LiteralPath $runtimeLogPath -Raw -ErrorAction SilentlyContinue
$consoleLog = Get-Content -LiteralPath $consoleLogPath -Raw -ErrorAction SilentlyContinue
$errorLog = Get-Content -LiteralPath $errorLogPath -Raw -ErrorAction SilentlyContinue
$combinedLog = "$runtimeLog`n$consoleLog`n$errorLog"
$markerPattern = 'COASTAL_QA_COMPLETE\s+failures=0\s+views=' + $expectedViews + '\b'
if ($combinedLog -notmatch $markerPattern) {
    throw "Missing CoastalQA completion marker for views=$expectedViews. Artifacts: $runFolder"
}

$runtimeFolder = $null
$folderPattern = 'COASTAL_QA_COMPLETE\s+failures=0\s+views=' + $expectedViews + '\s+folder=(?<folder>\S+)'
$folderMatch = [Regex]::Match($combinedLog, $folderPattern)
if ($folderMatch.Success) {
    $candidate = $folderMatch.Groups['folder'].Value.Trim()
    if (Test-Path -LiteralPath $candidate -PathType Container) {
        $runtimeFolder = (Resolve-Path -LiteralPath $candidate).Path
    }
}
if ($null -eq $runtimeFolder) {
    $latestRuntimePath = Join-Path $projectRoot 'Saved\Upgrade\latest-runtime.txt'
    if (Test-Path -LiteralPath $latestRuntimePath -PathType Leaf) {
        $latestRuntimeItem = Get-Item -LiteralPath $latestRuntimePath
        if ($latestRuntimeItem.LastWriteTimeUtc -ge $runStartedUtc) {
            $candidate = (Get-Content -LiteralPath $latestRuntimePath -Raw).Trim()
            if (Test-Path -LiteralPath $candidate -PathType Container) {
                $runtimeFolder = (Resolve-Path -LiteralPath $candidate).Path
            }
        }
    }
}
if ($null -eq $runtimeFolder) {
    throw "CoastalQA runtime folder was not found from marker or fresh latest-runtime.txt. Artifacts: $runFolder"
}

Write-Output "COASTAL_INTERACTIVE_CHECK_OK mode=$mode log=$runtimeLogPath runtime_folder=$runtimeFolder"
