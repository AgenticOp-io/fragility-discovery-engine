# GCE validation (Phase O)

Run the same checks as **`scripts/ci_local.ps1`** on a Linux VM before tagging releases.

## Prereqs (laptop)

1. `gcloud auth login` (refresh if you see *Reauthentication failed*).
2. Know **VM name**, **zone**, and **project** (Console → Compute Engine → VM instances).
3. Optional env (new terminal after `setx`):

```powershell
setx FRAGILITY_GCE_INSTANCE "fragility-discovery-minimal"
setx FRAGILITY_GCE_ZONE "us-central1-a"
setx FRAGILITY_GCE_PROJECT "chrysalis-dev-f5x6qv"
```

## Sync + test (one command)

From repo root on Windows:

```powershell
pwsh -File scripts\gce_sync_vm.ps1
```

This uploads `gce_configure_git_ssh.sh` + `gce_pull_and_test.sh`, then on the VM runs:

- `git pull` on `main`
- `pip install -e ".[dev]"`
- `ruff` + full `pytest`
- `run_benchmark_suite.py --validate` (7 bundles)
- manifest / flagship / bundled artifact pins
- Phase O: robustness stretch dry-run, static dashboard, `--hexa` composite

## No VM yet?

See [`archive/GCE_BOOTSTRAP.md`](archive/GCE_BOOTSTRAP.md) — create `fragility-discovery-minimal` in a project where you have **Owner** + billing.

## Private repo

Provision **`~/.ssh/gce_github_ed25519`** on the VM — [`archive/GCE_DEPLOY_KEY.md`](archive/GCE_DEPLOY_KEY.md).
