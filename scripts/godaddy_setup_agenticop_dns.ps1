<#
.SYNOPSIS
  Add GoDaddy A records for all AgenticOps demo hostnames on chrysalis-test-vm.

.DESCRIPTION
  Creates or updates A records (same IP for every name):
    hub.agenticop.io       — Chrysalis Translation Hub
    fragility.agenticop.io — Fragility Discovery Engine
    chrysalis.agenticop.io — optional alias for hub

  Requires:
    $env:GODADDY_API_KEY
    $env:GODADDY_API_SECRET

  Manual fallback: GoDaddy → DNS → agenticop.io → A records (see docs/HOSTNAME_MAP.md)

  After DNS propagates:
    powershell -File scripts/check_all_dns.ps1
    powershell -File scripts/gce_enable_https.ps1 -PublicHost fragility.agenticop.io
#>
param(
  [string]$Domain = "agenticop.io",
  [string[]]$Subdomains = @("hub", "fragility", "chrysalis"),
  [string]$TargetIp = "34.61.255.147",
  [int]$Ttl = 600
)

$ErrorActionPreference = "Stop"
$key = $env:GODADDY_API_KEY
$secret = $env:GODADDY_API_SECRET
if (-not $key -or -not $secret) {
  Write-Host "Set GODADDY_API_KEY and GODADDY_API_SECRET (GoDaddy developer portal)."
  Write-Host ""
  Write-Host "Manual A records on $Domain (TTL $Ttl):"
  foreach ($sub in $Subdomains) {
    Write-Host "  $sub -> $TargetIp"
  }
  Write-Host ""
  Write-Host "See docs/HOSTNAME_MAP.md for the full vhost plan."
  exit 1
}

$headers = @{
  Authorization = "sso-key ${key}:${secret}"
  "Content-Type" = "application/json"
}

foreach ($name in $Subdomains) {
  $uri = "https://api.godaddy.com/v1/domains/$Domain/records/A/$name"
  $body = @(@{ data = $TargetIp; ttl = $Ttl }) | ConvertTo-Json -Compress
  Invoke-RestMethod -Method Put -Uri $uri -Headers $headers -Body $body | Out-Null
  Write-Host "OK: A $name.$Domain -> $TargetIp"
}

Write-Host ""
Write-Host "Next:"
Write-Host "  powershell -File scripts/check_all_dns.ps1"
Write-Host "  # FDE HTTPS:"
Write-Host "  powershell -File scripts/gce_enable_https.ps1 -PublicHost fragility.agenticop.io"
Write-Host "  # Chrysalis: give docs/HOSTNAME_MAP.md Step 5 to your Chrysalis AI"
