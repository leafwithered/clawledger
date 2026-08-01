param(
    [Parameter(Mandatory = $true)]
    [string]$ConfigDir,

    [string]$ZeroClawExe = "zeroclaw",
    [string]$Agent = "clawledger_demo"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$sourceSkill = Join-Path $repoRoot "zeroclaw\skills\clawledger"
$tempRoot = [System.IO.Path]::GetTempPath()
$stagingRoot = Join-Path $tempRoot ("clawledger-skill-" + [guid]::NewGuid())
$stagingDir = Join-Path $stagingRoot "clawledger"

try {
    Copy-Item -LiteralPath $sourceSkill -Destination $stagingDir -Recurse

    $skillFile = Join-Path $stagingDir "SKILL.md"
    $skillText = Get-Content -LiteralPath $skillFile -Raw -Encoding utf8
    $skillText = $skillText.Replace("<CLAWLEDGER>", $repoRoot)
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($skillFile, $skillText, $utf8NoBom)

    & $ZeroClawExe skills audit $stagingDir
    if ($LASTEXITCODE -ne 0) { throw "Materialized Skill audit failed" }

    & $ZeroClawExe skills install $stagingDir --agent $Agent --config-dir $ConfigDir
    if ($LASTEXITCODE -ne 0) { throw "ZeroClaw Skill install failed" }

    Write-Output "Installed ClawLedger Skill for agent '$Agent'."
}
finally {
    $resolvedTempRoot = [System.IO.Path]::GetFullPath($tempRoot)
    $resolvedStaging = [System.IO.Path]::GetFullPath($stagingRoot)
    if (
        (Test-Path -LiteralPath $resolvedStaging) -and
        $resolvedStaging.StartsWith($resolvedTempRoot, [System.StringComparison]::OrdinalIgnoreCase) -and
        ([System.IO.Path]::GetFileName($resolvedStaging) -like "clawledger-skill-*")
    ) {
        Remove-Item -LiteralPath $resolvedStaging -Recurse -Force
    }
}
