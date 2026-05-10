# Generate an SSH key pair for GitHub "Deploy keys" (repo-scoped read access).
# Private key stays in .deploy/ (gitignored). Add ONLY the .pub line to GitHub.
#
#   pwsh -File scripts/generate_gce_deploy_key.ps1
#
# See docs/GCE_DEPLOY_KEY.md for GitHub + GCE wiring.

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
if (-not (Test-Path (Join-Path $root "pyproject.toml"))) {
    throw "Run from repo root (pyproject.toml missing above scripts/)."
}
$deployDir = Join-Path $root ".deploy"
$keyPath = Join-Path $deployDir "gce_github_ed25519"

New-Item -ItemType Directory -Force -Path $deployDir | Out-Null
if (Test-Path $keyPath) {
    Write-Host "Key already exists: $keyPath"
    Write-Host "Remove it first if you want a new key."
    exit 1
}

& ssh-keygen -t ed25519 -f $keyPath -q -N '""' -C "gce-fragility-discovery-engine-deploy"
Write-Host "Private: $keyPath"
Write-Host "Public:  $keyPath.pub"
Write-Host ""
Write-Host "Add this line to GitHub -> Repo Settings -> Deploy keys (read-only):"
Get-Content "$keyPath.pub"
