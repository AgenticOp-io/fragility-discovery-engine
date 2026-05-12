#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Enable Compute API and create one minimal Ubuntu VM (e2-micro) with optional first-boot setup.

.DESCRIPTION
  By default, attaches a startup script that installs git, curl, Python 3.12, build tools,
  shallow-clones this repo into /home/ubuntu/fragility-discovery-engine, creates a venv,
  and pip install -e ".[dev]".

.PARAMETER Project
  GCP project id (required).

.PARAMETER Zone
  Default: us-central1-a

.PARAMETER InstanceName
  Default: fragility-discovery-minimal

.PARAMETER MachineType
  Default: e2-micro

.PARAMETER RepoUrl
  Optional. Git clone URL (public https or SSH). Passed as instance metadata `fragility_repo_url`.

.PARAMETER NoStartup
  If set, do not attach the startup script (VM is bare Ubuntu only).
#>
param(
  [Parameter(Mandatory = $true)][string]$Project,
  [string]$Zone = "us-central1-a",
  [string]$InstanceName = "fragility-discovery-minimal",
  [string]$MachineType = "e2-micro",
  [string]$RepoUrl = "",
  [switch]$NoStartup
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Startup = Join-Path $RepoRoot "scripts/gce_minimal_vm_startup.sh"

Write-Host "==> gcloud config set project $Project"
gcloud config set project $Project

Write-Host "==> enable compute.googleapis.com"
gcloud services enable compute.googleapis.com --project=$Project

$gcloudArgs = @(
  "compute", "instances", "create", $InstanceName,
  "--project=$Project",
  "--zone=$Zone",
  "--machine-type=$MachineType",
  "--image-family=ubuntu-2404-lts",
  "--image-project=ubuntu-os-cloud",
  "--boot-disk-size=25GB",
  "--tags=allow-ssh",
  "--labels=purpose=fragility-discovery-engine",
  "--quiet"
)

if (-not $NoStartup) {
  if (-not (Test-Path $Startup)) {
    throw "Missing startup script: $Startup"
  }
  $gcloudArgs += "--metadata-from-file=startup-script=$Startup"
}
if ($RepoUrl) {
  $gcloudArgs += "--metadata=fragility_repo_url=$RepoUrl"
}

Write-Host "==> create $InstanceName ($MachineType, $Zone, ubuntu-24.04)"
& gcloud @gcloudArgs

Write-Host ""
Write-Host "==> OK. First boot runs apt + git clone + venv (see serial console or /var/log/fragility-bootstrap.log on VM)."
Write-Host "    Wait ~3–8 minutes, then:"
Write-Host "  gcloud compute ssh $InstanceName --zone=$Zone --project=$Project"
Write-Host "  setx FRAGILITY_GCE_INSTANCE `"$InstanceName`""
Write-Host "  setx FRAGILITY_GCE_ZONE `"$Zone`""
Write-Host "  setx FRAGILITY_GCE_PROJECT `"$Project`""
Write-Host "  (new shell) pwsh -File scripts\gce_sync_vm.ps1"
Write-Host "See docs/GCE_BOOTSTRAP.md"
