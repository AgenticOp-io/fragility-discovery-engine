<#
.SYNOPSIS
  Verify all AgenticOps demo hostnames resolve to the GCE VM IP.
#>
param(
  [string]$ExpectedIp = "34.61.255.147",
  [string[]]$Hosts = @(
    "hub.agenticop.io",
    "fragility.agenticop.io",
    "chrysalis.agenticop.io"
  )
)

$ErrorActionPreference = "Stop"
$fail = 0
foreach ($hostName in $Hosts) {
  Write-Host ""
  Write-Host "==> $hostName"
  try {
    $resolved = ([System.Net.Dns]::GetHostAddresses($hostName) |
      Where-Object { $_.AddressFamily -eq 'InterNetwork' } |
      Select-Object -First 1).IPAddressToString
  } catch {
    $resolved = $null
  }
  if ($resolved -eq $ExpectedIp) {
    Write-Host "OK: $resolved"
  } else {
    Write-Host "FAIL: resolved=$(if ($resolved) { $resolved } else { '(no A record)' }) expected=$ExpectedIp"
    $fail++
  }
}

Write-Host ""
if ($fail -eq 0) {
  Write-Host "All DNS checks passed."
  exit 0
}
Write-Host "$fail host(s) not ready. See docs/HOSTNAME_MAP.md Step 1 (GoDaddy)."
exit 1
