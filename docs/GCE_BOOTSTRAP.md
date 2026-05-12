# Bootstrap a minimal GCE VM (lost old instance / new project)

This repo **cannot** use a separate “AI” Google account. `gcloud` on your laptop uses **your** credentials. If your current project denies **`compute.instances.create`** (like `lte-pci-mapper-65450042-bbf71` in past checks), create a **new** GCP project with **billing** attached, make yourself **Owner**, then run the script below.

## 0. Prereqs

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`) on your machine.
- A GCP **project** where you are **Owner** or have **Compute Admin** + **Service Usage Admin** (to enable APIs).
- **Billing** enabled on that project (e2-micro may be free-tier eligible in some regions; you still accept cloud charges).

## 1. Create project (optional)

```bash
gcloud projects create YOUR_NEW_PROJECT_ID --name="fragility-discovery"
gcloud billing projects link YOUR_NEW_PROJECT_ID --billing-account=YOUR_BILLING_ACCOUNT_ID
gcloud config set project YOUR_NEW_PROJECT_ID
```

## 2. Create minimal VM (script)

From this repo root on **Windows**:

```powershell
pwsh -File scripts\gce_create_minimal.ps1 -Project YOUR_NEW_PROJECT_ID
```

Defaults: **zone** `us-central1-a`, **name** `fragility-discovery-minimal`, **machine type** `e2-micro`, **Ubuntu 22.04 LTS**.

## 3. Deploy engine code on the VM

After the VM exists:

```powershell
setx FRAGILITY_GCE_INSTANCE "fragility-discovery-minimal"
setx FRAGILITY_GCE_ZONE "us-central1-a"
setx FRAGILITY_GCE_PROJECT "YOUR_NEW_PROJECT_ID"
```

Open a **new** terminal, repo root:

```powershell
pwsh -File scripts\gce_sync_vm.ps1
```

For a **first-time** clone on the VM (no `~/fragility-discovery-engine` yet), SSH in and run the curl flow from [`GCE_DEPLOY_KEY.md`](GCE_DEPLOY_KEY.md) (public repo) or upload `gce_git_deploy.sh` + deploy key (private repo).

## 4. Tighten security (recommended)

- Remove broad **`0.0.0.0/0`** SSH rules once you use **IAP** or a fixed IP.
- See Google’s [SSH best practices](https://cloud.google.com/compute/docs/connect/standard-ssh) and **OS Login** / **IAP tunnel** docs.

## Related

- [`GCE_DEPLOY_KEY.md`](GCE_DEPLOY_KEY.md) — deploy keys, pull + test, single-VM env vars.
- [`scripts/gce_create_minimal.ps1`](../scripts/gce_create_minimal.ps1) — implementation.
