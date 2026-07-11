<#
.SYNOPSIS
  Operator checklist: DNS for HTTPS, deploy key, PyPI secret, live workbench status.

.EXAMPLE
  powershell -File scripts/gce_operator_preflight.ps1
#>
param(
  [string]$PublicHost = "hub.agenticop.io",
  [string]$VmIp = "34.61.255.147",
  [string]$StatusUrl = "http://hub.agenticop.io/status.json"
)

$ErrorActionPreference = "Continue"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$ok = $true

function Step($label, [scriptblock]$fn) {
  Write-Host ""
  Write-Host "==> $label"
  try {
    & $fn
  } catch {
    Write-Host "FAIL: $($_.Exception.Message)"
    $script:ok = $false
  }
}

Step "DNS (HTTPS prerequisite)" {
  & (Join-Path $RepoRoot "scripts/check_fragility_dns.ps1") -PublicHost $PublicHost -ExpectedIp $VmIp
  if ($LASTEXITCODE -ne 0) {
    Write-Host "Hint: add A record $PublicHost -> $VmIp then run scripts/gce_enable_https.ps1"
    throw "DNS not ready"
  }
}

Step "Deploy key (.deploy + GitHub)" {
  $pub = Join-Path $RepoRoot ".deploy/gce_github_ed25519.pub"
  if (-not (Test-Path $pub)) {
    Write-Host "WARN: no local deploy key - optional if using gh token sync"
    Write-Host "      run: powershell -File scripts/register_gce_deploy_key.ps1 -GenerateIfMissing"
    return
  }
  if (Get-Command gh -ErrorAction SilentlyContinue) {
    $nwo = gh repo view --json nameWithOwner -q .nameWithOwner 2>$null
    if ($nwo) {
      $keys = @(gh api "repos/$nwo/keys" 2>$null | ConvertFrom-Json)
      $titles = ($keys | ForEach-Object { $_.title }) -join ", "
      if ($titles -match "gce-chrysalis") {
        Write-Host "OK: GCE deploy key registered ($titles)"
      } else {
        Write-Host "WARN: deploy keys on repo: $(if ($titles) { $titles } else { '(none)' })"
        Write-Host "      org may disable deploy keys - token sync is OK"
      }
    }
  }
}

Step "PyPI secret (optional publish)" {
  if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "SKIP: gh not installed"
    return
  }
  $names = @(gh secret list --json name -q ".[].name" 2>$null)
  if ($names -contains "PYPI_API_TOKEN") {
    Write-Host "OK: PYPI_API_TOKEN secret is set"
  } else {
    Write-Host "WARN: PYPI_API_TOKEN not in repo secrets"
    Write-Host "      local fallback: python scripts/check_pypi_ready.py && twine upload dist/*"
  }
}

Step "Live workbench status" {
  $r = Invoke-WebRequest -Uri $StatusUrl -UseBasicParsing -TimeoutSec 15
  $j = $r.Content | ConvertFrom-Json
  Write-Host ($j | ConvertTo-Json -Compress)
  if ($j.benchmark_validate -ne "ok") { throw "benchmark_validate not ok" }
  if ($j.research_fork_validate -ne "ok") { throw "research_fork_validate not ok" }
  Write-Host "OK: workbench healthy (git_head=$($j.git_head))"
}

Write-Host ""
if ($ok) {
  Write-Host "Preflight: all checks passed."
  exit 0
}
Write-Host "Preflight: one or more checks failed (see above)."
exit 1
