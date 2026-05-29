<#
.SYNOPSIS
  Build the public workbench and push to the gh-pages branch (manual Pages deploy).

  Does not use the GitHub Actions "pages" workflow. Configure the repo once:
    gh api -X PUT repos/OWNER/REPO/pages `
      -f build_type=legacy `
      -f "source[branch]=gh-pages" `
      -f "source[path]=/"

.EXAMPLE
  powershell -File scripts/deploy_github_pages.ps1
#>
param(
  [string]$Remote = "origin",
  [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$SiteDir = Join-Path $RepoRoot "artifacts\public_site"

if (-not $SkipBuild) {
  Write-Host "==> build public site"
  Push-Location $RepoRoot
  try {
    python scripts/build_public_site.py | Write-Host
  } finally {
    Pop-Location
  }
}

if (-not (Test-Path $SiteDir)) {
  throw "Missing site output: $SiteDir"
}

# GitHub Pages serves from branch root; no Jekyll processing for _underscore paths.
$nojekyll = Join-Path $SiteDir ".nojekyll"
if (-not (Test-Path $nojekyll)) {
  New-Item -ItemType File -Path $nojekyll -Force | Out-Null
}

$nwo = $null
if (Get-Command gh -ErrorAction SilentlyContinue) {
  $nwo = gh repo view --json nameWithOwner -q .nameWithOwner 2>$null
}
if (-not $nwo) {
  $nwo = "AgenticOp-io/fragility-discovery-engine"
}
Write-Host "==> push gh-pages for $nwo"

$tmp = Join-Path $env:TEMP ("fde-pages-" + [guid]::NewGuid().ToString("n"))
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
  Copy-Item -Path (Join-Path $SiteDir "*") -Destination $tmp -Recurse -Force
  Push-Location $tmp
  git init -q
  git config user.name "fde-pages-deploy"
  git config user.email "fde-pages-deploy@users.noreply.github.com"
  git add -A
  $head = (git -C $RepoRoot rev-parse --short HEAD 2>$null)
  if (-not $head) { $head = "unknown" }
  $msg = "Deploy public site from main@$head"
  git commit -q -m $msg
  $remoteUrl = git -C $RepoRoot remote get-url $Remote 2>$null
  if (-not $remoteUrl) {
    $remoteUrl = "https://github.com/$nwo.git"
  }
  git remote add origin $remoteUrl
  git push -f origin HEAD:gh-pages
  Write-Host "OK: https://agenticop-io.github.io/fragility-discovery-engine/ (gh-pages @ $head)"
} finally {
  Pop-Location
  Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
