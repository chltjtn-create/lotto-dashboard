param(
    [Parameter(Mandatory = $true)]
    [string]$RepoUrl,

    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path -LiteralPath ".git")) {
    throw "This folder is not a Git repository."
}

git branch -M $Branch

$existing = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0 -and $existing) {
    git remote set-url origin $RepoUrl
} else {
    git remote add origin $RepoUrl
}

git push -u origin $Branch

Write-Host "Pushed to $RepoUrl on branch $Branch."
Write-Host "Next: GitHub Settings > Pages > Deploy from a branch > $Branch /docs."
