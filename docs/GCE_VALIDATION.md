# GCE validation (Phase O)

Run the same checks as **`scripts/ci_local.ps1`** on a Linux VM before tagging releases.

## Prereqs (laptop)

1. `gcloud auth login` (refresh if you see *Reauthentication failed*).
2. Know **VM name**, **zone**, and **project** (Console → Compute Engine → VM instances).
3. Optional env (new terminal after `setx`):

```powershell
setx FRAGILITY_GCE_INSTANCE "chrysalis-test-vm"
setx FRAGILITY_GCE_ZONE "us-central1-a"
setx FRAGILITY_GCE_PROJECT "chrysalis-dev-f5x6qv"
```

**Routine sync** (after one-time bootstrap):

```powershell
powershell -NoProfile -File scripts/gce_bootstrap_git.ps1   # first time only
powershell -NoProfile -File scripts/gce_sync_vm.ps1       # pull + full ci_local on VM
```

**Validated 2026-05-20** on `chrysalis-test-vm` (Debian, Python 3.11): **481 passed**, 7-bundle validate, manifest pins, Phase O smokes.

| Method | When |
|--------|------|
| **Git (preferred)** | `powershell -File scripts/gce_bootstrap_git.ps1` once, then `scripts/gce_sync_vm.ps1` |
| **Tarball fallback** | `scripts/gce_run_tarball_test.sh` when git auth is unavailable |

Git auth: repo deploy keys are **disabled** on GitHub; bootstrap copies a read-only **`gh` token** to `~/.config/fragility-engine/github_token` on the VM (see `scripts/gce_git_auth.sh`).

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

`git pull` on the VM needs a deploy key registered on GitHub — [`archive/GCE_DEPLOY_KEY.md`](archive/GCE_DEPLOY_KEY.md). If clone fails, use tarball deploy from laptop:

```powershell
tar --exclude=.venv --exclude=.git --exclude=build --exclude=dist -czf $env:TEMP\fragility-engine-src.tar.gz .
gcloud compute scp $env:TEMP\fragility-engine-src.tar.gz chrysalis-test-vm:fragility-engine-src.tar.gz --zone=us-central1-a --project=chrysalis-dev-f5x6qv
gcloud compute scp scripts/gce_run_tarball_test.sh chrysalis-test-vm:gce_run_tarball_test.sh --zone=us-central1-a --project=chrysalis-dev-f5x6qv
gcloud compute ssh chrysalis-test-vm --zone=us-central1-a --project=chrysalis-dev-f5x6qv --command="sudo apt-get install -y python3.11-venv build-essential && bash ~/gce_run_tarball_test.sh"
```
