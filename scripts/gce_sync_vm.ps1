<#
.SYNOPSIS
  Push latest gce_pull_and_test.sh to a GCE VM and run it (git pull + pip + ruff + pytest with CI perf gate).

.DESCRIPTION
  Requires: gcloud CLI, network access, and IAM on the target project including
  compute.instances.get, compute.instances.list (for scp/ssh), and ssh to the VM.

  If `gcloud compute instances list` fails with permission errors, switch project
  or ask a project owner for a Compute role — see docs/GCE_DEPLOY_KEY.md section 0b.

.PARAMETER Instance
  GCE instance name (required).

.PARAMETER Zone
  Zone, e.g. us-central1-a (required).

.PARAMETER Project
  Optional. If set, runs: gcloud config set project <Project> before scp/ssh.
#>
param(
  [Parameter(Mandatory = $true)][string]$Instance,
  [Parameter(Mandatory = $true)][string]$Zone,
  [string]$Project = ""
)

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
