#Requires -Version 5.1
<#
.SYNOPSIS
  Generate (if needed) and register the GCE GitHub deploy key on the repo via gh.
#>
param(
  [string]$Title = "gce-chrysalis-test-vm",
  [switch]$GenerateIfMissing
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$DeployDir = Join-Path $RepoRoot ".deploy"
$KeyPath = Join-Path $DeployDir "gce_github_ed25519"
$PubPath = "$KeyPath.pub"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  throw "gh CLI required. Install GitHub CLI and run gh auth login."
}

if (-not (Test-Path $PubPath)) {
  if (-not $GenerateIfMissing) {
    throw "Missing $PubPath - run: powershell -File scripts/generate_gce_deploy_key.ps1 or pass -GenerateIfMissing"
  }
  & (Join-Path $RepoRoot "scripts/generate_gce_deploy_key.ps1")
}

$pub = (Get-Content $PubPath -Raw).Trim()
if (-not $pub) { throw "Empty public key: $PubPath" }

$remote = (git -C $RepoRoot remote get-url origin 2>$null)
$nameWithOwner = (gh repo view --json nameWithOwner -q .nameWithOwner 2>$null)
if ($nameWithOwner -match "^([^/]+)/([^/]+)$") {
  $owner = $Matches[1]
  $repo = $Matches[2]
} elseif ($remote -match "github\.com[:/](?<owner>[^/]+)/(?<repo>[^/.]+)") {
  $owner = $Matches.owner
  $repo = $Matches.repo
} else {
  throw "Could not resolve GitHub repo (run gh auth login; origin=$remote)"
}

Write-Host "==> list existing deploy keys on ${owner}/${repo}"
$raw = gh api "repos/${owner}/${repo}/keys" 2>$null
$existing = @()
if ($raw) {
  $parsed = $raw | ConvertFrom-Json
  if ($parsed -is [System.Array]) { $existing = $parsed } else { $existing = @($parsed) }
}
foreach ($k in $existing) {
  if ($k.title -eq $Title) {
    Write-Host "OK: deploy key title '$Title' already exists (id=$($k.id))"
    exit 0
  }
}

Write-Host "==> register deploy key: $Title"
$payload = @{
  title     = $Title
  key       = $pub
  read_only = $true
} | ConvertTo-Json
$tmp = Join-Path $env:TEMP ("deploy-key-{0}.json" -f [Guid]::NewGuid().ToString("N"))
try {
  [System.IO.File]::WriteAllText($tmp, $payload, [System.Text.UTF8Encoding]::new($false))
  gh api -X POST "repos/${owner}/${repo}/keys" --input $tmp 2>&1 | Tee-Object -Variable apiOut
  if ($LASTEXITCODE -ne 0) {
    $msg = ($apiOut | Out-String)
    if ($msg -match "Deploy keys are disabled") {
      Write-Host "WARN: Deploy keys are disabled on ${owner}/${repo} — keep using gh HTTPS token sync (gce_bootstrap_git.ps1)."
      exit 2
    }
    throw "gh api deploy key create failed: $msg"
  }
} finally {
  Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
}

Write-Host "OK: registered deploy key '$Title'"
Write-Host "Next: powershell -File scripts/gce_bootstrap_git.ps1"
