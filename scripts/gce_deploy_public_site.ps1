<#
.SYNOPSIS
  Build AgenticOps-branded public site and deploy to GCE nginx (port 80).

.DESCRIPTION
  1. python scripts/build_public_site.py
  2. tar artifacts/public_site -> fragility-public-site.tar.gz
  3. scp to VM + run gce_install_public_web.sh + gce_deploy_public_site.sh
  4. Optionally open firewall (tag http-server on instance)

.PARAMETER Instance / Zone / Project
  Same env vars as gce_sync_vm.ps1 (FRAGILITY_GCE_*).
#>
param(
  [string]$Instance = $env:FRAGILITY_GCE_INSTANCE,
  [string]$Zone = $env:FRAGILITY_GCE_ZONE,
  [string]$Project = $env:FRAGILITY_GCE_PROJECT,
  [switch]$SkipFirewall
)

$ErrorActionPreference = "Stop"
if (-not $Instance -or -not $Zone) {
  throw "Set FRAGILITY_GCE_INSTANCE and FRAGILITY_GCE_ZONE (or pass -Instance -Zone)."
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
$OutDir = Join-Path $RepoRoot "artifacts\public_site"
$Archive = Join-Path $env:TEMP "fragility-public-site.tar.gz"

if ($Project) {
  gcloud config set project $Project
}

Write-Host "==> build public site"
Push-Location $RepoRoot
try {
  python (Join-Path $RepoRoot "scripts\build_public_site.py")
} finally {
  Pop-Location
}

if (-not (Test-Path $OutDir)) {
  throw "Missing $OutDir after build"
}

Write-Host "==> tar public_site bundle"
if (Test-Path $Archive) { Remove-Item -LiteralPath $Archive -Force }
Push-Location $OutDir
try {
  tar -czf $Archive .
} finally {
  Pop-Location
}

$InstallSh = Join-Path $RepoRoot "scripts\gce_install_public_web.sh"
$DeploySh = Join-Path $RepoRoot "scripts\gce_deploy_public_site.sh"
foreach ($p in @($InstallSh, $DeploySh)) {
  if (-not (Test-Path $p)) { throw "Missing $p" }
}

function Copy-LfSh {
  param([string]$Local, [string]$Remote)
  $raw = [System.IO.File]::ReadAllText($Local) -replace "`r`n", "`n" -replace "`r", "`n"
  $tmp = Join-Path $env:TEMP ("gce-pub-{0}" -f [Guid]::NewGuid().ToString("N"))
  [System.IO.File]::WriteAllText($tmp, $raw, [System.Text.UTF8Encoding]::new($false))
  try {
    gcloud compute scp $tmp "${Instance}:${Remote}" --zone=$Zone
  } finally {
    Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
  }
}

if (-not $SkipFirewall) {
  Write-Host "==> ensure http-server tag + firewall rule"
  $prevEap = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  gcloud compute instances add-tags $Instance --zone=$Zone --tags=http-server 2>&1 | Out-Null
  gcloud compute firewall-rules describe fragility-allow-http 2>&1 | Out-Null
  if ($LASTEXITCODE -ne 0) {
    gcloud compute firewall-rules create fragility-allow-http `
      --direction=INGRESS --priority=1000 --network=default `
      --action=ALLOW --rules=tcp:80 --target-tags=http-server 2>&1 | Out-Null
  }
  $ErrorActionPreference = $prevEap
}

Write-Host "==> scp archive + install scripts"
gcloud compute scp $Archive "${Instance}:fragility-public-site.tar.gz" --zone=$Zone
Copy-LfSh -Local $InstallSh -Remote "gce_install_public_web.sh"
Copy-LfSh -Local $DeploySh -Remote "gce_deploy_public_site.sh"

Write-Host "==> deploy on VM"
gcloud compute ssh $Instance --zone=$Zone --command='bash ~/gce_install_public_web.sh; bash ~/gce_deploy_public_site.sh ~/fragility-public-site.tar.gz'

$ip = (gcloud compute instances describe $Instance --zone=$Zone --format="get(networkInterfaces[0].accessConfigs[0].natIP)").Trim()
Write-Host "==> done. Public site: http://${ip}/"
Write-Host "    dashboard: http://${ip}/dashboard.html"
