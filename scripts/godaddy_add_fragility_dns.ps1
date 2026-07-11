<#
.SYNOPSIS
  Add GoDaddy DNS A record for the workbench hostname (default hub.agenticop.io).

.DESCRIPTION
  hub.agenticop.io is already expected to point at the GCE VM IP.
  Prefer scripts/godaddy_setup_agenticop_dns.ps1 for hub + fragility + chrysalis together.

  Requires GoDaddy API credentials:
    $env:GODADDY_API_KEY
    $env:GODADDY_API_SECRET

  Manual fallback: GoDaddy → DNS → agenticop.io → A record
    Host: hub   Type: A   Value: 34.61.255.147   TTL: 600

  After DNS propagates:
    powershell -File scripts/check_fragility_dns.ps1
    powershell -File scripts/gce_enable_https.ps1
#>
param(
  [string]$Domain = "agenticop.io",
  [string]$Subdomain = "hub",
  [string]$TargetIp = "34.61.255.147",
  [int]$Ttl = 600
)

$ErrorActionPreference = "Stop"
$key = $env:GODADDY_API_KEY
$secret = $env:GODADDY_API_SECRET
if (-not $key -or -not $secret) {
  Write-Host "Set GODADDY_API_KEY and GODADDY_API_SECRET (GoDaddy developer portal)."
  Write-Host "Manual: A record $Subdomain.$Domain -> $TargetIp (TTL $Ttl)"
  exit 1
}

$headers = @{
  Authorization = "sso-key ${key}:${secret}"
  "Content-Type" = "application/json"
}
$name = $Subdomain
$uri = "https://api.godaddy.com/v1/domains/$Domain/records/A/$name"

# Fetch existing records for this name
try {
  $existing = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
} catch {
  $existing = @()
}

$body = @(
  @{
    data = $TargetIp
    ttl  = $Ttl
  }
) | ConvertTo-Json -Compress
if (-not $body.StartsWith("[")) { $body = "[$body]" }

Invoke-RestMethod -Method Put -Uri $uri -Headers $headers -Body $body | Out-Null
Write-Host "OK: A $Subdomain.$Domain -> $TargetIp"
Write-Host "Next:"
Write-Host "  powershell -File scripts/check_fragility_dns.ps1"
Write-Host "  powershell -File scripts/gce_enable_https.ps1"
