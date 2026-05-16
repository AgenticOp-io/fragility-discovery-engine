# Bootstrap a minimal GCE VM (create → install git/Python → clone → venv)

This repo **cannot** use a separate “AI” Google account: `gcloud` on your laptop uses **your** credentials. If your current project denies **`compute.instances.create`**, create a **new** GCP project with **billing**, make yourself **Owner**, then run the script below.

## 0. Prereqs

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`).
- A GCP **project** where you are **Owner** (or **Compute Admin** + **Service Usage Admin**) and **billing** is linked.
- **Charges:** `e2-micro` may be free-tier eligible in some regions; you still accept GCP pricing.

## 1. Create project (optional)

```bash
gcloud projects create YOUR_NEW_PROJECT_ID --name="fragility-discovery"
gcloud billing projects link YOUR_NEW_PROJECT_ID --billing-account=YOUR_BILLING_ACCOUNT_ID
gcloud config set project YOUR_NEW_PROJECT_ID
```

## 2. Create VM + first-boot install (one command)

**Private repo:** GitHub may return **404** for anonymous **`curl`** / **`git clone https://…`**, or **`could not read Username`** on a headless VM. Install a **read-only deploy key** on the VM at **`~/.ssh/gce_github_ed25519`** (see [`GCE_DEPLOY_KEY.md`](GCE_DEPLOY_KEY.md)). Scripts such as **`gce_clone_pull_and_test.sh`** default to **`git@github.com:theorem6/fragility-discovery-engine.git`** when that key exists.

From this repo root on **Windows**:

```powershell
pwsh -File scripts\gce_create_minimal.ps1 -Project YOUR_NEW_PROJECT_ID
```

Defaults: **zone** `us-central1-a`, **name** `fragility-discovery-minimal`, **machine type** `e2-micro`, **Ubuntu 24.04 LTS** (Python **3.12** in default repos).

**What the startup script does** (runs automatically on first boot as **root**, log: **`/var/log/fragility-bootstrap.log`** on the VM):

1. **`apt-get`** — `git`, `curl`, `ca-certificates`, `build-essential`, **`python3-venv`**, **`python3-pip`** (uses default **`python3`**, e.g. 3.11 on Debian 12 or 3.12 on Ubuntu 24.04).
2. **`git clone`** — shallow **`main`** into **`/home/ubuntu/fragility-discovery-engine`**: HTTPS (non-interactive) by default, or **SSH** when metadata **`fragility_repo_url`** is **`git@…`** and **`/home/ubuntu/.ssh/gce_github_ed25519`** exists (private repos — provision key via image or post-boot `scp`). For SSH, the startup script writes **`~/.ssh/config`** for **`github.com`** (same marker as [`gce_configure_git_ssh.sh`](../scripts/gce_configure_git_ssh.sh)) so **`git`** does not rely on **`GIT_SSH_COMMAND`**.
3. **`python3 -m venv .venv`** + **`pip install -e ".[dev]"`** as user **`ubuntu`**.

Wait **~3–8 minutes** after `instances create` returns, then SSH and check the log:

```bash
gcloud compute ssh fragility-discovery-minimal --zone=us-central1-a --project=YOUR_NEW_PROJECT_ID --command='tail -50 /var/log/fragility-bootstrap.log'
```

### Options

| Goal | How |
|------|-----|
| **Private fork** | `pwsh -File scripts\gce_create_minimal.ps1 -Project ... -RepoUrl "git@github.com:YOU/fragility-discovery-engine.git"` (you still need deploy-key / SSH access on the VM — often easier to use **`-NoStartup`** and follow [`GCE_DEPLOY_KEY.md`](GCE_DEPLOY_KEY.md).) |
| **Bare VM only** | `pwsh -File scripts\gce_create_minimal.ps1 -Project ... -NoStartup` |

**Linux / macOS** (same behaviour):

```bash
bash scripts/gce_create_minimal.sh YOUR_NEW_PROJECT_ID
# Bare VM: SKIP_STARTUP=1 bash scripts/gce_create_minimal.sh YOUR_NEW_PROJECT_ID
# Custom URL: REPO_URL='https://github.com/...' bash scripts/gce_create_minimal.sh YOUR_NEW_PROJECT_ID
```

## 3. Ongoing deploy (pull + CI-like tests from your laptop)

After the VM is up and the startup log shows **done**:

```powershell
setx FRAGILITY_GCE_INSTANCE "fragility-discovery-minimal"
setx FRAGILITY_GCE_ZONE "us-central1-a"
setx FRAGILITY_GCE_PROJECT "YOUR_NEW_PROJECT_ID"
```

New terminal, repo root:

```powershell
pwsh -File scripts\gce_sync_vm.ps1
```

That uploads **`gce_configure_git_ssh.sh`** and **`gce_pull_and_test.sh`**, then runs **git pull**, **pip**, **ruff**, **pytest** (with the same perf gate env as CI).

## 4. Tighten security (recommended)

- Prefer **IAP TCP forwarding** and narrow firewall rules instead of **`0.0.0.0/0`** SSH from the whole internet.
- See [SSH best practices](https://cloud.google.com/compute/docs/connect/standard-ssh).

## Related

- [`GCE_DEPLOY_KEY.md`](GCE_DEPLOY_KEY.md) — deploy keys, `gce_git_deploy`, single-VM env vars.
- [`scripts/gce_create_minimal.ps1`](../scripts/gce_create_minimal.ps1) / [`scripts/gce_create_minimal.sh`](../scripts/gce_create_minimal.sh)
- [`scripts/gce_minimal_vm_startup.sh`](../scripts/gce_minimal_vm_startup.sh) — first-boot script.
