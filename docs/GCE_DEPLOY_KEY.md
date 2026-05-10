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

Trust GitHub host key once:

```bash
gcloud compute ssh acs-hss-server --zone=us-central1-a --command='ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null'
```

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

## Rotate / revoke

- Remove the deploy key in GitHub **Settings → Deploy keys**.
- Generate a new pair (step 1), add new public key, replace file on VM, redeploy.
