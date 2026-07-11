<#
.SYNOPSIS
  Open port 443 on GCE and run gce_install_https.sh when DNS points at the VM.

.PARAMETER PublicHost
  Hostname for Let's Encrypt. Do **not** use hub.agenticop.io (Translation Hub).
  Example: fragility.agenticop.io

.PARAMETER VmIp
  Expected A-record target (default 34.61.255.147). Script skips HTTPS if DNS does not match.

.PARAMETER Force
  Run certbot even when DNS check fails (for testing on IP-only hosts — will fail at Let's Encrypt).
#>
param(
  [string]$Instance = $env:FRAGILITY_GCE_INSTANCE,
  [string]$Zone = $env:FRAGILITY_GCE_ZONE,
  [string]$Project = $env:FRAGILITY_GCE_PROJECT,
  [string]$PublicHost = "fragility.agenticop.io",
  [string]$VmIp = "34.61.255.147",
  [string]$CertbotEmail = "admin@agenticop.io",
  [switch]$Force
)

$ErrorActionPreference = "Stop"
if (-not $Instance -or -not $Zone) {
  throw "Set FRAGILITY_GCE_INSTANCE and FRAGILITY_GCE_ZONE."
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
$HttpsSh = Join-Path $RepoRoot "scripts\gce_install_https.sh"
if (-not (Test-Path $HttpsSh)) { throw "Missing $HttpsSh" }

if ($Project) { gcloud config set project $Project }

Write-Host "==> DNS check: $PublicHost should resolve to $VmIp"
$resolved = $null
try {
  $resolved = ([System.Net.Dns]::GetHostAddresses($PublicHost) | Where-Object { $_.AddressFamily -eq 'InterNetwork' } | Select-Object -First 1).IPAddressToString
} catch {
  $resolved = $null
}
if ($resolved -eq $VmIp) {
  Write-Host "OK: DNS resolves to $resolved"
} elseif ($Force) {
  Write-Warning "DNS is '$resolved' (expected $VmIp); continuing because -Force was set."
} else {
  Write-Host @"

DNS is not ready for HTTPS yet.
  Host:     $PublicHost
  Resolved: $(if ($resolved) { $resolved } else { '(no A record)' })
  Expected: $VmIp

Add an A record at your DNS provider, then re-run:
  powershell -File scripts/gce_enable_https.ps1

Or pass -Force to attempt certbot anyway (Let's Encrypt will fail without correct DNS).
"@
  exit 2
}

Write-Host "==> firewall: allow tcp:443 (https-server tag)"
$prev = $ErrorActionPreference
$ErrorActionPreference = "Continue"
gcloud compute instances add-tags $Instance --zone=$Zone --tags=https-server 2>&1 | Out-Null
gcloud compute firewall-rules describe fragility-allow-https 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
  gcloud compute firewall-rules create fragility-allow-https `
    --direction=INGRESS --priority=1000 --network=default `
    --action=ALLOW --rules=tcp:443 --target-tags=https-server 2>&1 | Out-Null
}
$ErrorActionPreference = $prev

function Copy-LfSh {
  param([string]$Local, [string]$Remote)
  $raw = [System.IO.File]::ReadAllText($Local) -replace "`r`n", "`n" -replace "`r", "`n"
  $tmp = Join-Path $env:TEMP ("gce-https-{0}" -f [Guid]::NewGuid().ToString("N"))
  [System.IO.File]::WriteAllText($tmp, $raw, [System.Text.UTF8Encoding]::new($false))
  try {
    gcloud compute scp $tmp "${Instance}:${Remote}" --zone=$Zone
  } finally {
    Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
  }
}

Write-Host "==> upload and run gce_install_https.sh on VM"
Copy-LfSh -Local $HttpsSh -Remote "gce_install_https.sh"
$remote = @"
set -e
REPO=~/fragility-discovery-engine
mkdir -p "`$REPO/scripts"
cp -f ~/gce_install_https.sh "`$REPO/scripts/gce_install_https.sh"
chmod +x "`$REPO/scripts/gce_install_https.sh"
sudo FRAGILITY_PUBLIC_HOST='$PublicHost' FRAGILITY_CERTBOT_EMAIL='$CertbotEmail' bash "`$REPO/scripts/gce_install_https.sh"
"@
gcloud compute ssh $Instance --zone=$Zone --command=$remote

Write-Host ""
Write-Host "OK: https://${PublicHost}/ (also http://${VmIp}/ until you switch bookmarks)"
