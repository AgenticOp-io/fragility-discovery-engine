# GCE deploy key (SSH git on VM)

Read-only deploy key so the VM can `git pull` without a personal PAT. Token-based HTTPS sync still works today; use this when you prefer SSH.

## Quick setup

```powershell
# 1) Generate key pair under .deploy/ (gitignored)
powershell -File scripts/generate_gce_deploy_key.ps1

# 2) Register public key on GitHub (requires gh auth + repo admin)
powershell -File scripts/register_gce_deploy_key.ps1

# 3) Install private key on VM and clone/pull
powershell -File scripts/gce_bootstrap_git.ps1
```

Or generate + register in one step:

```powershell
powershell -File scripts/register_gce_deploy_key.ps1 -GenerateIfMissing
```

## Operator preflight

```powershell
powershell -File scripts/gce_operator_preflight.ps1
```

Checks DNS (HTTPS), deploy key, optional `PYPI_API_TOKEN`, and http://hub.agenticop.io/status.json.

## Org policy

If registration returns **Deploy keys are disabled for this repository**, enable deploy keys in org/repo settings or continue with **HTTPS token sync** (`gce_bootstrap_git.ps1` uses `gh auth token` today).

## Rotate / revoke

1. GitHub → **Settings → Deploy keys** → remove `gce-chrysalis-test-vm`.
2. Delete `.deploy/gce_github_ed25519*` locally and re-run the quick setup.

Extended notes (sync scripts, IAM): [`archive/GCE_DEPLOY_KEY.md`](archive/GCE_DEPLOY_KEY.md).
