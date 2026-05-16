# GitHub deploy key for GCE (SSH clone)

Use a **deploy key** so a VM can `git clone` / `git pull` a **private** repo without your personal GitHub password or PAT in URLs.

## 1. Generate a key pair (local)

**Windows (repo root):**

```powershell
pwsh -File scripts/generate_gce_deploy_key.ps1
```

**Any OS:**

```bash
mkdir -p .deploy
ssh-keygen -t ed25519 -f .deploy/gce_github_ed25519 -q -N "" -C "gce-fragility-discovery-engine-deploy"
```

Files (both under `.deploy/`, **gitignored**):

- **Private:** `.deploy/gce_github_ed25519` — copy only to the VM (`chmod 600`).
- **Public:** `.deploy/gce_github_ed25519.pub` — paste into GitHub (next step).

## 2. Add the public key on GitHub

1. Repo → **Settings** → **Deploy keys** → **Add deploy key**.
2. Title: e.g. `gce-acs-hss`.
3. Key: paste the **single line** from `gce_github_ed25519.pub`.
4. Leave **Allow write access** unchecked unless you need pushes from the VM.

## 3. Install the private key on the VM

From your laptop (adjust zone / instance name):

```bash
gcloud compute scp .deploy/gce_github_ed25519 acs-hss-server:~/.ssh/gce_github_ed25519 --zone=us-central1-a
gcloud compute ssh acs-hss-server --zone=us-central1-a --command='chmod 600 ~/.ssh/gce_github_ed25519'
```

Trust GitHub host key once (optional if you use [`scripts/gce_configure_git_ssh.sh`](../scripts/gce_configure_git_ssh.sh), which also runs **`ssh-keyscan`** when **`github.com`** is missing from **`known_hosts`**):

```bash
gcloud compute ssh acs-hss-server --zone=us-central1-a --command='ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null'
```

### 3b. Persist GitHub SSH (no `GIT_SSH_COMMAND` on every pull)

[`scripts/gce_configure_git_ssh.sh`](../scripts/gce_configure_git_ssh.sh) prepends a small **`Host github.com`** block to **`~/.ssh/config`** (marked with **`# fragility-discovery-engine: gce-github-deploy`**) so **`git`** uses **`~/.ssh/gce_github_ed25519`** with **`IdentitiesOnly yes`**. It is **idempotent** and safe to re-run.

From your laptop (repo root):

```bash
gcloud compute scp scripts/gce_configure_git_ssh.sh INSTANCE:~/ --zone=ZONE
gcloud compute ssh INSTANCE --zone=ZONE --command='bash ~/gce_configure_git_ssh.sh'
```

[`scripts/gce_sync_vm.ps1`](../scripts/gce_sync_vm.ps1) uploads this script to **`~/`** automatically before running **`gce_pull_and_test.sh`**. [`scripts/gce_pull_and_test.sh`](../scripts/gce_pull_and_test.sh) and [`scripts/gce_pull_pytest.sh`](../scripts/gce_pull_pytest.sh) also **source** the helper from **`~/`** or from the clone when present, and fall back to **`GIT_SSH_COMMAND`** only until **`~/.ssh/config`** contains that marker.

**Override key path:** set **`FRAGILITY_GCE_DEPLOY_KEY`** before running the configure script.

## 4. Clone / deploy with SSH remote

**Private repos:** `raw.githubusercontent.com` returns **404** without auth — copy `gce_git_deploy.sh` to the VM, then run the wrapper.

From your laptop (repo root; adjust instance and zone):

```bash
gcloud compute scp scripts/gce_git_deploy.sh scripts/gce_remote_git_deploy.sh acs-hss-server:/tmp/ --zone=us-central1-a
gcloud compute ssh acs-hss-server --zone=us-central1-a --command='bash /tmp/gce_remote_git_deploy.sh'
```

**Public repos** can use curl instead:

```bash
export FRAGILITY_REPO_URL='git@github.com:theorem6/fragility-discovery-engine.git'
export GIT_SSH_COMMAND='ssh -i ~/.ssh/gce_github_ed25519 -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new'
curl -fsSL https://raw.githubusercontent.com/theorem6/fragility-discovery-engine/main/scripts/gce_git_deploy.sh | bash
```

Or use a repo under another org:

```bash
export FRAGILITY_REPO_URL='git@github.com:YOUR_ORG/fragility-discovery-engine.git'
```

Subsequent updates: rerun `gce_git_deploy.sh` with the same env vars (it will `git pull`).

## Sync latest `main` on an existing VM (Linux pull + test)

The canonical repo is **GitHub**; the VM only needs **`git pull`**. Push from your laptop to **`origin/main`** as usual, then refresh the VM.

### 0. Refresh `gcloud` credentials (when `invalid_grant` / `instances.list` fails)

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

Use **`gcloud config get-value project`** to see the active project.

### 0b. `Required 'compute.instances.list' permission`

Your Google account is signed in, but the **active project** may be wrong or your principal lacks **Compute Engine** permissions (e.g. Viewer / Instance Admin) on that project.

```bash
gcloud projects list
gcloud config set project THE_PROJECT_THAT_OWNS_THE_VM
gcloud compute instances list
```

Ask a project owner to grant a role that includes **`compute.instances.list`** (often **Compute Viewer** or **Compute Instance Admin (v1)**) on the target project.

### 1. Pull + `ruff` + `pytest` (CI-like, including perf gate)

Replace **`INSTANCE`** and **`ZONE`** with your VM (examples elsewhere in this doc use `acs-hss-server` / `us-central1-a`).

From your **laptop** (this repository’s root):

```powershell
pwsh -File scripts/gce_sync_vm.ps1 -Instance INSTANCE -Zone ZONE [-Project YOUR_PROJECT_ID]
```

Or manually:

```bash
gcloud compute scp scripts/gce_configure_git_ssh.sh scripts/gce_pull_and_test.sh INSTANCE:~/ --zone=ZONE
gcloud compute ssh INSTANCE --zone=ZONE --command='bash ~/gce_configure_git_ssh.sh && bash ~/gce_pull_and_test.sh'
```

[`scripts/gce_pull_and_test.sh`](../scripts/gce_pull_and_test.sh) activates **`~/fragility-discovery-engine/.venv`** (override with **`FRAGILITY_DEPLOY_DIR`**), ensures GitHub SSH config when [`gce_configure_git_ssh.sh`](../scripts/gce_configure_git_ssh.sh) is available (see **§3b**), runs **`git pull`**, **`pip install -e ".[dev]"`**, **`python -m ruff check .`**, and **`python -m pytest`** with **`FRAGILITY_PERF_GATE=1`** and **`FRAGILITY_PERF_GATE_MS=240000`** (same defaults as `.github/workflows/ci.yml`).

**Public repo — no `scp`:** if the VM already has a clone at **`~/fragility-discovery-engine`**, you can pipe the script from `raw.githubusercontent.com`:

```bash
gcloud compute ssh INSTANCE --zone=ZONE --command='curl -fsSL https://raw.githubusercontent.com/theorem6/fragility-discovery-engine/main/scripts/gce_pull_and_test.sh | bash'
```

**Private repo:** install **`~/.ssh/gce_github_ed25519`** (§3), then use **`gce_configure_git_ssh.sh`** (§3b) or rely on **`GIT_SSH_COMMAND`** fallback in [`gce_pull_and_test.sh`](../scripts/gce_pull_and_test.sh) until the marker is present in **`~/.ssh/config`**.

### Single VM (no `instances.list`, or name not in git)

If the project has **only one** (or a known) VM, use **GCP Console → Compute Engine → VM instances**: the table shows **Name** and **Zone** even when `gcloud compute instances list` is denied. Copy those two values.

**Windows — avoid retyping:** set user env vars (open a **new** terminal after `setx`):

```powershell
setx FRAGILITY_GCE_INSTANCE "YOUR_VM_NAME"
setx FRAGILITY_GCE_ZONE "YOUR_ZONE"
setx FRAGILITY_GCE_PROJECT "YOUR_PROJECT_ID"
```

Then from the repo root:

```powershell
pwsh -File scripts\gce_sync_vm.ps1
```

Or pass flags once: `pwsh -File scripts\gce_sync_vm.ps1 -Instance YOUR_VM_NAME -Zone YOUR_ZONE -Project YOUR_PROJECT_ID`.

**IAM note:** `gcloud compute scp` / `ssh` still need **`compute.instances.get`** (and related) on that VM. Env vars replace **discovery**, not **authorization**.

### 3. Optional: pytest-only refresh

[`scripts/gce_pull_pytest.sh`](../scripts/gce_pull_pytest.sh) skips **ruff** but uses the same **perf gate** env vars as CI by default. Upload and run it the same way as **`gce_pull_and_test.sh`** (with **`gce_configure_git_ssh.sh`** first if you use manual **`scp`**).

## Rotate / revoke

- Remove the deploy key in GitHub **Settings → Deploy keys**.
- Generate a new pair (step 1), add new public key, replace file on VM, redeploy.
