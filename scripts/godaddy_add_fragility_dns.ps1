<#
.SYNOPSIS
  Add GoDaddy DNS A record: fragility.agenticop.io -> GCE workbench IP.

.DESCRIPTION
  Requires GoDaddy API credentials (Production keys from developer.godaddy.com):
    $env:GODADDY_API_KEY
    $env:GODADDY_API_SECRET

  Manual fallback (no API): GoDaddy → DNS → agenticop.io → Add A record
    Host: fragility   Type: A   Value: 34.61.255.147   TTL: 600

  After DNS propagates:
    powershell -File scripts/check_fragility_dns.ps1
    powershell -File scripts/gce_enable_https.ps1
#>
param(
  [string]$Domain = "agenticop.io",
  [string]$Subdomain = "fragility",
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
$existing = @()
try {
  $existing = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
} catch {
  if ($_.Exception.Response.StatusCode.value__ -ne 404) { throw }
}

$already = $existing | Where-Object { $_.data -eq $TargetIp -and $_.type -eq "A" }
if ($already) {
  Write-Host "OK: A record already points $Subdomain.$Domain -> $TargetIp"
  exit 0
}

$body = @(@{ data = $TargetIp; ttl = $Ttl }) | ConvertTo-Json
if ($existing.Count -gt 0) {
  Invoke-RestMethod -Uri $uri -Headers $headers -Method Put -Body $body | Out-Null
  Write-Host "Updated A record $Subdomain.$Domain -> $TargetIp"
} else {
  $addUri = "https://api.godaddy.com/v1/domains/$Domain/records"
  $addBody = @(@{ type = "A"; name = $name; data = $TargetIp; ttl = $Ttl }) | ConvertTo-Json
  Invoke-RestMethod -Uri $addUri -Headers $headers -Method Patch -Body $addBody | Out-Null
  Write-Host "Added A record $Subdomain.$Domain -> $TargetIp"
}

Write-Host "Wait 1-5 min for propagation, then:"
Write-Host "  powershell -File scripts/check_fragility_dns.ps1"
Write-Host "  powershell -File scripts/gce_enable_https.ps1"
