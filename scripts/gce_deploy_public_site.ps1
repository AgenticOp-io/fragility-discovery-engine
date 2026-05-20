<#
.SYNOPSIS
  Publish product workbench on GCE (build + validate + nginx) — all on the VM.

.DESCRIPTION
  End users only need a browser at http://<vm-ip>/.
  This script SSHs to the VM and runs gce_publish_workbench.sh inside the git clone
  (after optional git pull). No local Python build required.

  Prerequisite: gce_bootstrap_git.ps1 once; FRAGILITY_GCE_* env vars set.
#>
param(
  [string]$Instance = $env:FRAGILITY_GCE_INSTANCE,
  [string]$Zone = $env:FRAGILITY_GCE_ZONE,
  [string]$Project = $env:FRAGILITY_GCE_PROJECT,
  [switch]$SkipFirewall,
  [switch]$SkipGitPull
)

$ErrorActionPreference = "Stop"
if (-not $Instance -or -not $Zone) {
  throw "Set FRAGILITY_GCE_INSTANCE and FRAGILITY_GCE_ZONE (or pass -Instance -Zone)."
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
$PublishSh = Join-Path $RepoRoot "scripts\gce_publish_workbench.sh"
$InstallSh = Join-Path $RepoRoot "scripts\gce_install_public_web.sh"
foreach ($p in @($PublishSh, $InstallSh)) {
  if (-not (Test-Path $p)) { throw "Missing $p" }
}

if ($Project) {
  gcloud config set project $Project
}

function Copy-LfSh {
  param([string]$Local, [string]$Remote)
  $raw = [System.IO.File]::ReadAllText($Local) -replace "`r`n", "`n" -replace "`r", "`n"
  $tmp = Join-Path $env:TEMP ("gce-pub-{0}" -f [Guid]::NewGuid().ToString("N"))
  [System.IO.File]::WriteAllText($tmp, $raw, [System.Text.UTF8Encoding]::new($false))
  try {
    gcloud compute scp $tmp "${Instance}:${Remote}" --zone=$Zone
  }
  finally {
    Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
  }
}

if (-not $SkipFirewall) {
  Write-Host "==> ensure http-server tag + firewall rule"
  $prevEap = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  gcloud compute instances add-tags $Instance --zone=$Zone --tags=http-server 2>&1 | Out-Null
  gcloud compute firewall-rules describe fragility-allow-http 2>&1 | Out-Null
  if ($LASTEXITCODE -ne 0) {
    gcloud compute firewall-rules create fragility-allow-http `
      --direction=INGRESS --priority=1000 --network=default `
      --action=ALLOW --rules=tcp:80 --target-tags=http-server 2>&1 | Out-Null
  }
  $ErrorActionPreference = $prevEap
}

Write-Host "==> upload publish scripts"
Copy-LfSh -Local $PublishSh -Remote "gce_publish_workbench.sh"
Copy-LfSh -Local $InstallSh -Remote "gce_install_public_web.sh"

$remote = @'
set -e
REPO=~/fragility-discovery-engine
mkdir -p "$REPO/scripts"
cd "$REPO"
if [ -f scripts/gce_git_auth.sh ]; then . scripts/gce_git_auth.sh; elif [ -f ~/gce_git_auth.sh ]; then . ~/gce_git_auth.sh; fi
# Discard any drift from earlier scp-uploaded scripts so git pull is clean.
git checkout -- scripts/ 2>/dev/null || true
if declare -F fragility_gce_git >/dev/null 2>&1; then
  fragility_gce_git fetch origin main
  fragility_gce_git checkout main
  fragility_gce_git pull --ff-only origin main
else
  git fetch origin main
  git checkout main
  git pull --ff-only origin main
fi
# After pull, overlay the freshly uploaded copies (lets us iterate without a push).
for f in gce_publish_workbench.sh gce_install_public_web.sh; do
  if [ -f ~/"$f" ]; then mv -f ~/"$f" "$REPO/scripts/$f"; chmod +x "$REPO/scripts/$f"; fi
done
bash scripts/gce_publish_workbench.sh
'@.Trim()
if ($SkipGitPull) {
  $remote = @'
set -e
REPO=~/fragility-discovery-engine
mkdir -p "$REPO/scripts"
for f in gce_publish_workbench.sh gce_install_public_web.sh; do
  if [ -f ~/"$f" ]; then mv -f ~/"$f" "$REPO/scripts/$f"; chmod +x "$REPO/scripts/$f"; fi
done
cd "$REPO"
bash scripts/gce_publish_workbench.sh
'@.Trim()
}

Write-Host "==> publish on VM (build + validate + nginx)"
$remoteLf = ($remote -replace "`r`n", "`n") -replace "`r", "`n"
gcloud compute ssh $Instance --zone=$Zone --command=$remoteLf
if ($LASTEXITCODE -ne 0) { throw "gce_publish_workbench failed (exit $LASTEXITCODE)" }

$ip = (gcloud compute instances describe $Instance --zone=$Zone --format="get(networkInterfaces[0].accessConfigs[0].natIP)").Trim()
Write-Host "==> done. Browser-only workbench: http://${ip}/"
Write-Host "    status: http://${ip}/status.json"
