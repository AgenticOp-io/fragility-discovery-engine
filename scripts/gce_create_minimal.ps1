#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Enable Compute API and create one minimal Ubuntu VM (e2-micro) for fragility-discovery-engine work.

.PARAMETER Project
  GCP project id (required). Use a project where you have Owner / Compute Admin + billing.

.PARAMETER Zone
  Default: us-central1-a

.PARAMETER InstanceName
  Default: fragility-discovery-minimal

.PARAMETER MachineType
  Default: e2-micro
#>
param(
  [Parameter(Mandatory = $true)][string]$Project,
  [string]$Zone = "us-central1-a",
  [string]$InstanceName = "fragility-discovery-minimal",
  [string]$MachineType = "e2-micro"
)

$ErrorActionPreference = "Stop"
Write-Host "==> gcloud config set project $Project"
gcloud config set project $Project

Write-Host "==> enable compute.googleapis.com"
gcloud services enable compute.googleapis.com --project=$Project

Write-Host "==> create $InstanceName ($MachineType, $Zone)"
gcloud compute instances create $InstanceName `
  --project=$Project `
  --zone=$Zone `
  --machine-type=$MachineType `
  --image-family=ubuntu-2204-lts `
  --image-project=ubuntu-os-cloud `
  --boot-disk-size=20GB `
  --tags=allow-ssh `
  --labels=purpose=fragility-discovery-engine `
  --quiet

Write-Host ""
Write-Host "==> OK. Next:"
Write-Host "  gcloud compute ssh $InstanceName --zone=$Zone --project=$Project"
Write-Host "  setx FRAGILITY_GCE_INSTANCE `"$InstanceName`""
Write-Host "  setx FRAGILITY_GCE_ZONE `"$Zone`""
Write-Host "  setx FRAGILITY_GCE_PROJECT `"$Project`""
Write-Host "  (new shell) pwsh -File scripts\gce_sync_vm.ps1"
Write-Host "See docs/GCE_BOOTSTRAP.md for first-time clone on the VM."
