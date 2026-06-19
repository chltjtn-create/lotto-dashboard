param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "Running tests..."
& $Python -m unittest discover -s tests

Write-Host "Rebuilding dashboard without network sync..."
& $Python -m lotto_analyzer update-site --db data/lotto.db --site-dir docs --count 10 --seed 42 --no-sync

if (-not (Test-Path -LiteralPath "docs/index.html")) {
    throw "Missing docs/index.html"
}
if (-not (Test-Path -LiteralPath "docs/data/latest.json")) {
    throw "Missing docs/data/latest.json"
}

Write-Host "Preflight OK."
