<#
.SYNOPSIS
  One-shot GCE git bootstrap: deploy key on VM, SSH config, shallow clone, full ci_local parity.

.DESCRIPTION
  Use when ~/fragility-discovery-engine exists without .git (tarball deploy) or on a fresh VM.
  After bootstrap, use gce_sync_vm.ps1 for routine git pull + test.

  Requires: .deploy/gce_github_ed25519 (run generate_gce_deploy_key.ps1 if missing).
  Deploy key must be authorized for AgenticOp-io/fragility-discovery-engine (org deploy key or repo key).
#>
param(
  [string]$Instance = $env:FRAGILITY_GCE_INSTANCE,
  [string]$Zone = $env:FRAGILITY_GCE_ZONE,
  [string]$Project = $env:FRAGILITY_GCE_PROJECT
)

$ErrorActionPreference = "Stop"
if (-not $Instance -or -not $Zone) {
  throw "Missing instance/zone. Pass -Instance and -Zone, or set FRAGILITY_GCE_INSTANCE and FRAGILITY_GCE_ZONE."
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
$KeyPrivate = Join-Path $RepoRoot ".deploy/gce_github_ed25519"
$ConfigureLocal = Join-Path $RepoRoot "scripts/gce_configure_git_ssh.sh"
$AuthLocal = Join-Path $RepoRoot "scripts/gce_git_auth.sh"
$CloneLocal = Join-Path $RepoRoot "scripts/gce_clone_pull_and_test.sh"
foreach ($p in @($ConfigureLocal, $AuthLocal, $CloneLocal)) {
  if (-not (Test-Path $p)) { throw "Missing $p" }
}
if (-not (Test-Path $KeyPrivate)) {
  Write-Host "==> no .deploy/gce_github_ed25519 - will use gh HTTPS token only"
}

function Copy-GceShellScriptToVm {
  param(
    [Parameter(Mandatory = $true)][string]$LocalPath,
    [Parameter(Mandatory = $true)][string]$Instance,
    [Parameter(Mandatory = $true)][string]$Zone,
    [Parameter(Mandatory = $true)][string]$RemoteName
  )
  $raw = [System.IO.File]::ReadAllText($LocalPath)
  $unix = $raw -replace "`r`n", "`n" -replace "`r", "`n"
  $tmp = Join-Path $env:TEMP ("gce-bootstrap-{0}-{1}" -f $RemoteName, [Guid]::NewGuid().ToString("N"))
  [System.IO.File]::WriteAllText($tmp, $unix, [System.Text.UTF8Encoding]::new($false))
  try {
    gcloud compute scp $tmp "${Instance}:${RemoteName}" --zone=$Zone
  }
  finally {
    Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
  }
}

if ($Project) {
  Write-Host "==> gcloud config set project $Project"
  gcloud config set project $Project
}

if (Test-Path $KeyPrivate) {
  Write-Host "==> install deploy key on VM (if needed)"
  gcloud compute scp $KeyPrivate "${Instance}:gce_github_ed25519" --zone=$Zone
  gcloud compute ssh $Instance --zone=$Zone --command='mkdir -p ~/.ssh; mv -f ~/gce_github_ed25519 ~/.ssh/gce_github_ed25519; chmod 600 ~/.ssh/gce_github_ed25519'
}

$ghToken = $null
try {
  $ghToken = (gh auth token 2>$null).Trim()
} catch { }
if ($ghToken) {
  Write-Host "==> install GitHub HTTPS token for private clone (deploy keys disabled on repo)"
  $tokTmp = Join-Path $env:TEMP ("gce-github-token-{0}" -f [Guid]::NewGuid().ToString("N"))
  [System.IO.File]::WriteAllText($tokTmp, $ghToken, [System.Text.UTF8Encoding]::new($false))
  try {
    gcloud compute scp $tokTmp "${Instance}:fragility_github_token" --zone=$Zone
    gcloud compute ssh $Instance --zone=$Zone --command='mkdir -p ~/.config/fragility-engine; mv -f ~/fragility_github_token ~/.config/fragility-engine/github_token; chmod 600 ~/.config/fragility-engine/github_token'
  }
  finally {
    Remove-Item -LiteralPath $tokTmp -Force -ErrorAction SilentlyContinue
  }
} else {
  Write-Warning "No gh auth token; private HTTPS clone may fail if deploy key is disabled."
}

Write-Host "==> upload configure + auth + clone scripts"
Copy-GceShellScriptToVm -LocalPath $ConfigureLocal -Instance $Instance -Zone $Zone -RemoteName "gce_configure_git_ssh.sh"
Copy-GceShellScriptToVm -LocalPath $AuthLocal -Instance $Instance -Zone $Zone -RemoteName "gce_git_auth.sh"
Copy-GceShellScriptToVm -LocalPath $CloneLocal -Instance $Instance -Zone $Zone -RemoteName "gce_clone_pull_and_test.sh"

$remote = 'bash ~/gce_configure_git_ssh.sh; bash ~/gce_clone_pull_and_test.sh'
Write-Host "==> gcloud compute ssh $Instance -- $remote"
gcloud compute ssh $Instance --zone=$Zone --command=$remote
Write-Host "==> bootstrap done. Future syncs: powershell -File scripts/gce_sync_vm.ps1"
