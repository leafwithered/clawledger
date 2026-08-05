param(
    [string]$ZeroClawExe = "zeroclaw",
    [switch]$SkipNetwork
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$validationDir = Join-Path ([System.IO.Path]::GetTempPath()) ("clawledger-validation-" + [guid]::NewGuid())

try {
    Push-Location $repoRoot
    $env:PYTHONPATH = Join-Path $repoRoot "src"

    python -m compileall -q src tests scripts plugins
    if ($LASTEXITCODE -ne 0) { throw "Python compilation failed" }

    python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw "Python tests failed" }

    if (-not $SkipNetwork) {
        python scripts/live_action_smoke.py
        if ($LASTEXITCODE -ne 0) { throw "Devnet RPC smoke test failed" }
    }

    & $ZeroClawExe --version
    if ($LASTEXITCODE -ne 0) { throw "ZeroClaw executable failed" }

    & $ZeroClawExe skills audit (Join-Path $repoRoot "zeroclaw\skills\clawledger")
    if ($LASTEXITCODE -ne 0) { throw "ZeroClaw Skill audit failed" }

    New-Item -ItemType Directory -Path $validationDir | Out-Null
    & $ZeroClawExe --config-dir $validationDir config set sop.sops_dir (Join-Path $repoRoot "zeroclaw\sops")
    if ($LASTEXITCODE -ne 0) { throw "ZeroClaw SOP directory configuration failed" }

    & $ZeroClawExe --config-dir $validationDir sop validate clawledger-anchor
    if ($LASTEXITCODE -ne 0) { throw "ZeroClaw SOP validation failed" }

    Write-Output "ALL VALIDATIONS PASSED"
}
finally {
    Pop-Location -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $validationDir) {
        Remove-Item -LiteralPath $validationDir -Recurse -Force
    }
}
