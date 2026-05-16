<#
.SYNOPSIS
  Push latest gce_configure_git_ssh.sh + gce_pull_and_test.sh to a GCE VM and run pull + test
  (git pull + pip + ruff + pytest with CI perf gate). The SSH helper is idempotent: it writes
  ~/.ssh/config so git to GitHub uses the deploy key without GIT_SSH_COMMAND.

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
$ConfigureLocal = Join-Path $RepoRoot "scripts/gce_configure_git_ssh.sh"
$ScriptLocal = Join-Path $RepoRoot "scripts/gce_pull_and_test.sh"
if (-not (Test-Path $ConfigureLocal)) {
  throw "Missing $ConfigureLocal"
}
if (-not (Test-Path $ScriptLocal)) {
  throw "Missing $ScriptLocal"
}

function Copy-GceShellScriptToVm {
  param(
    [Parameter(Mandatory = $true)][string]$LocalPath,
    [Parameter(Mandatory = $true)][string]$Instance,
    [Parameter(Mandatory = $true)][string]$Zone,
    [Parameter(Mandatory = $true)][string]$RemoteName
  )
  # Worktrees on Windows may be CRLF; bash on Linux requires LF for `#!/` and line continuations.
  $raw = [System.IO.File]::ReadAllText($LocalPath)
  $unix = $raw -replace "`r`n", "`n" -replace "`r", "`n"
  $tmp = Join-Path $env:TEMP ("gce-sync-{0}-{1}" -f $RemoteName, [Guid]::NewGuid().ToString("N"))
  [System.IO.File]::WriteAllText($tmp, $unix, [System.Text.UTF8Encoding]::new($false))
  try {
    # Relative remote path is under the SSH user's home (pscp does not expand "~/" reliably on Windows).
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

Write-Host "==> gcloud compute scp -> ${Instance}:gce_configure_git_ssh.sh (zone=$Zone)"
Copy-GceShellScriptToVm -LocalPath $ConfigureLocal -Instance $Instance -Zone $Zone -RemoteName "gce_configure_git_ssh.sh"

Write-Host "==> gcloud compute scp -> ${Instance}:gce_pull_and_test.sh (zone=$Zone)"
Copy-GceShellScriptToVm -LocalPath $ScriptLocal -Instance $Instance -Zone $Zone -RemoteName "gce_pull_and_test.sh"

$remote = "bash ~/gce_configure_git_ssh.sh && bash ~/gce_pull_and_test.sh"
Write-Host "==> gcloud compute ssh $Instance -- $remote"
gcloud compute ssh $Instance --zone=$Zone --command=$remote
Write-Host "==> done."
