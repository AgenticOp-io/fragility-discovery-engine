<#
.SYNOPSIS
  Check whether hub.agenticop.io (or another host) resolves to the GCE workbench IP.
#>
param(
  [string]$PublicHost = "hub.agenticop.io",
  [string]$ExpectedIp = "34.61.255.147"
)

$ErrorActionPreference = "Stop"
Write-Host "Host:     $PublicHost"
Write-Host "Expected: $ExpectedIp"
try {
  $resolved = ([System.Net.Dns]::GetHostAddresses($PublicHost) |
    Where-Object { $_.AddressFamily -eq 'InterNetwork' } |
    Select-Object -First 1).IPAddressToString
} catch {
  $resolved = $null
}
if ($resolved -eq $ExpectedIp) {
  Write-Host "OK: DNS is ready. Run: powershell -File scripts/gce_enable_https.ps1"
  exit 0
}
Write-Host "Not ready: resolved=$(if ($resolved) { $resolved } else { '(no A record)' })"
Write-Host "Add an A record at your DNS provider, then re-run this script."
exit 1
