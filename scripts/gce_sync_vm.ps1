<#
.SYNOPSIS
  Push latest gce_pull_and_test.sh to a GCE VM and run it (git pull + pip + ruff + pytest with CI perf gate).

.DESCRIPTION
  Requires: gcloud CLI, network access, and IAM on the target project including
  compute.instances.get, compute.instances.list (for scp/ssh), and ssh to the VM.

  If `gcloud compute instances list` fails with permission errors, you can still
  use this script: copy the **instance name** and **zone** from the GCP Console
  (VM instances page — even a single row), then pass `-Instance` / `-Zone` or set
  **`FRAGILITY_GCE_INSTANCE`** / **`FRAGILITY_GCE_ZONE`** (optional **`FRAGILITY_GCE_PROJECT`**).

.PARAMETER Instance
  GCE instance name. Optional if **`FRAGILITY_GCE_INSTANCE`** is set.

.PARAMETER Zone
  Zone, e.g. us-central1-a. Optional if **`FRAGILITY_GCE_ZONE`** is set.

.PARAMETER Project
  Optional. If set, runs: gcloud config set project <Project> before scp/ssh.
  If omitted, **`FRAGILITY_GCE_PROJECT`** is used when set; otherwise the active
  gcloud project is unchanged.
#>
param(
  [string]$Instance = $env:FRAGILITY_GCE_INSTANCE,
  [string]$Zone = $env:FRAGILITY_GCE_ZONE,
  [string]$Project = $env:FRAGILITY_GCE_PROJECT
)

$ErrorActionPreference = "Stop"
if (-not $Instance -or -not $Zone) {
  throw "Missing instance/zone. Pass -Instance and -Zone, or set env FRAGILITY_GCE_INSTANCE and FRAGILITY_GCE_ZONE (see GCP Console → Compute Engine → VM instances)."
}

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$ScriptLocal = Join-Path $RepoRoot "scripts/gce_pull_and_test.sh"
if (-not (Test-Path $ScriptLocal)) {
  throw "Missing $ScriptLocal"
}

if ($Project) {
  Write-Host "==> gcloud config set project $Project"
  gcloud config set project $Project
}

Write-Host "==> gcloud compute scp -> ${Instance}:~/gce_pull_and_test.sh (zone=$Zone)"
gcloud compute scp $ScriptLocal "${Instance}:~/gce_pull_and_test.sh" --zone=$Zone

$remote = "bash ~/gce_pull_and_test.sh"
Write-Host "==> gcloud compute ssh $Instance -- $remote"
gcloud compute ssh $Instance --zone=$Zone --command=$remote
Write-Host "==> done."
