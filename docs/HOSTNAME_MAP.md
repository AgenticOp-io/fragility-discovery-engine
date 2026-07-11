# Hostname and vhost map — `chrysalis-test-vm` (`34.61.255.147`)

One GCE VM hosts **two products**. DNS uses **multiple A records to the same IP**; **nginx** routes by `server_name`.

| Product | Public URL (target) | Backend | nginx site file | Owner repo |
|---------|---------------------|---------|-----------------|------------|
| **Chrysalis / Translation Hub** | https://chrysalis.agenticop.io/ | `127.0.0.1:19090` | `chrysalis-hub` (product vhost) | Chrysalis / hub repo |
| **Hub path (same app)** | https://hub.agenticop.io/hub/ | same `:19090` | `chrysalis-hub` | Chrysalis / hub repo |
| **Project directory** | https://hub.agenticop.io/ | static `/var/www/chrysalis/projects` | `chrysalis-hub` | AgenticOps directory |
| **Chrysalis direct (legacy)** | http://34.61.255.147:19090/ | app on `:19090` | bypass nginx | Chrysalis / hub repo |
| **Fragility Discovery Engine** | https://fragility.agenticop.io/ | static + `/api/` → `:8765` | `fragility-public` | this repo (**live HTTPS**) |
| **FDE IP fallback** | http://34.61.255.147/ | same FDE site | `fragility-default-ip` | this repo |
| **Corporate site** | https://agenticop.io | external hosting | N/A | agenticops-web |

**Do not** bind `hub.agenticop.io` or `chrysalis.agenticop.io` to FDE configs. FDE scripts refuse those names.

---

## Step 1 — GoDaddy DNS (`agenticop.io`)

GoDaddy → **DNS** → **agenticop.io** → add or verify these **A** records (all same IP):

| Type | Name (Host) | Value | TTL | Purpose |
|------|-------------|-------|-----|---------|
| A | `hub` | `34.61.255.147` | 600 | Chrysalis hub (likely **already set**) |
| A | `fragility` | `34.61.255.147` | 600 | FDE workbench + TLS |
| A | `chrysalis` | `34.61.255.147` | 600 | Optional alias → same hub app |

No extra IP addresses needed — only additional **names** pointing at the same VM.

### API (optional)

```powershell
$env:GODADDY_API_KEY = "..."
$env:GODADDY_API_SECRET = "..."
powershell -File scripts/godaddy_setup_agenticop_dns.ps1
```

### Verify from your PC

```powershell
powershell -File scripts/check_all_dns.ps1
```

All three hosts should resolve to `34.61.255.147`.

---

## Step 2 — GCE firewall (once)

Ensure ingress allows web traffic to the VM:

| Rule | Ports | Tag |
|------|-------|-----|
| HTTP | `tcp:80` | `http-server` |
| HTTPS | `tcp:443` | `https-server` |
| Chrysalis direct (optional) | `tcp:19090` | only if you keep public `:19090` |

FDE HTTPS helper opens `:443` automatically:

```powershell
powershell -File scripts/gce_enable_https.ps1 -PublicHost fragility.agenticop.io
```

---

## Step 3 — nginx vhost layout on the VM

After setup, `/etc/nginx/sites-enabled/` should look like:

```
chrysalis-hub          → hub.agenticop.io, chrysalis.agenticop.io (:443 → :19090)
fragility-public       → fragility.agenticop.io (:443 + :80 redirect)
fragility-default-ip   → default_server :80 for raw IP (FDE)
```

Test after any change:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

---

## Step 4 — FDE side (this repo)

Run **after** DNS for `fragility.agenticop.io` propagates.

### 4a. Publish workbench + split vhosts

```powershell
# From your PC — deploy static site + nginx default-ip vhost
powershell -File scripts/gce_deploy_public_site.ps1
```

On the VM (or via deploy script):

```bash
cd ~/fragility-discovery-engine
git pull
FRAGILITY_PUBLIC_HOST=fragility.agenticop.io bash scripts/gce_install_public_web.sh
bash scripts/gce_publish_workbench.sh
```

### 4b. Enable HTTPS for FDE

```powershell
powershell -File scripts/gce_enable_https.ps1 -PublicHost fragility.agenticop.io
```

### 4c. Verify FDE

```bash
curl -sI https://fragility.agenticop.io/status.json | head
curl -sI http://34.61.255.147/status.json | head   # IP fallback still works
curl -s https://fragility.agenticop.io/api/health
```

---

## Step 5 — Copy-paste for Chrysalis AI

Give your Chrysalis agent this block (adjust paths if your hub repo differs):

---

**Task: nginx vhost for Chrysalis Translation Hub on `chrysalis-test-vm`**

**Context**

- VM external IP: `34.61.255.147`
- Hub app already runs on port **19090** (`http://34.61.255.147:19090/` works today)
- DNS (GoDaddy): `hub.agenticop.io` and optionally `chrysalis.agenticop.io` → A → `34.61.255.147`
- **Do not** modify FDE nginx files: `fragility-default-ip`, `fragility-public`
- Reference vhost: `fragility-discovery-engine/docs/nginx/chrysalis-hub.vhost.example`

**Requirements**

1. **Bind hub app to localhost** (recommended): listen on `127.0.0.1:19090` instead of `0.0.0.0:19090` once nginx proxy works. Keep `:19090` public only if we still need the direct URL during migration.

2. **Create** `/etc/nginx/sites-available/chrysalis-hub` using the example vhost:
   - `server_name hub.agenticop.io chrysalis.agenticop.io;`
   - `proxy_pass http://127.0.0.1:19090;`
   - WebSocket headers for long-running translate jobs
   - `client_max_body_size 512m;` for file uploads

3. **TLS** with certbot (webroot or nginx plugin):

   ```bash
   sudo mkdir -p /var/www/chrysalis/acme
   sudo certbot certonly --webroot -w /var/www/chrysalis/acme \
     -d hub.agenticop.io -d chrysalis.agenticop.io \
     --non-interactive --agree-tos -m admin@agenticop.io
   ```

4. **Enable** site:

   ```bash
   sudo ln -sf /etc/nginx/sites-available/chrysalis-hub /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```

5. **Verify**

   ```bash
   curl -sI https://hub.agenticop.io/ | head
   curl -sI https://chrysalis.agenticop.io/ | head   # if DNS added
   curl -s http://127.0.0.1:19090/ | head           # app health on loopback
   ```

6. **Do not** change:
   - FDE `fragility-*` configs
   - Port `8765` runner (FDE internal API)
   - `default_server` on `:80` (owned by FDE for raw IP)

7. **Optional cleanup**: after HTTPS works, remove public firewall rule for `tcp:19090` and rely on `https://hub.agenticop.io/` only.

---

## Step 6 — Update bookmarks and package metadata

After HTTPS is live, prefer:

| Old | New |
|-----|-----|
| http://34.61.255.147/ | https://fragility.agenticop.io/ |
| http://34.61.255.147:19090/ | https://hub.agenticop.io/ |

Files in this repo that reference demo URLs: `README.md`, `pyproject.toml` (`Demo`), `docs/PYPI_README.md`, `docs/DEMO_GUIDE.md`.

---

## Troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| `hub.agenticop.io` shows FDE workbench | Hub nginx vhost missing; request hit FDE `default_server` on :443 incorrectly |
| FDE on wrong host | `FRAGILITY_PUBLIC_HOST=hub.agenticop.io` was set — forbidden |
| certbot fails | DNS not propagated; port 80 blocked; wrong webroot |
| 502 on hub | App not listening on `127.0.0.1:19090` |
| IP still works for FDE | Expected — `fragility-default-ip` keeps `http://34.61.255.147/` |

---

## Related docs

- [`GCE_HTTPS_AND_AUTH.md`](GCE_HTTPS_AND_AUTH.md) — demo guardrails + runner API
- [`phase_p_visibility.md`](phase_p_visibility.md) — public site scope
- [`nginx/chrysalis-hub.vhost.example`](nginx/chrysalis-hub.vhost.example)
- [`nginx/fragility-public.vhost.example`](nginx/fragility-public.vhost.example)
