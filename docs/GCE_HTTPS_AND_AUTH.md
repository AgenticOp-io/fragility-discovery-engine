# GCE HTTPS and run API authentication

**Demo deployments** can use the VM IP only (for example http://34.61.255.147/). The sections below are optional operator notes, not required for the public workbench demo.

## HTTPS (Let's Encrypt) — optional

The workbench VM external IP is **34.61.255.147**. A friendly hostname needs a DNS **A record** before certificates can be issued.

| Record | Type | Value |
|--------|------|-------|
| `fragility.agenticop.io` | A | `34.61.255.147` |

`agenticop.io` itself may point elsewhere (for example GitHub Pages); only the **subdomain** should target the GCE VM.

After DNS propagates:

```powershell
# Check A record (exit 0 when ready)
powershell -File scripts/check_fragility_dns.ps1

# From the repo on your laptop (firewall 443 is opened on every deploy; this runs certbot)
powershell -File scripts/gce_enable_https.ps1
```

**DNS not configured yet:** `fragility.agenticop.io` needs an **A → 34.61.255.147** record at your DNS provider (see `scripts/check_fragility_dns.ps1`).

Operator checklist (DNS, deploy key, PyPI secret, live status):

```powershell
powershell -File scripts/gce_operator_preflight.ps1
```

Or on the VM:

```bash
sudo FRAGILITY_PUBLIC_HOST=fragility.agenticop.io bash scripts/gce_install_https.sh
```

The HTTPS nginx config keeps `/api/` proxying to the scenario runner and `/runs/` for artifacts.

---

## Run API key (optional)

By default, `POST /api/run` is open to the public workbench (still rate-limited). To require a shared secret on the VM:

```bash
sudo mkdir -p /etc/fragility
sudo cp scripts/gce_runner.env.example /etc/fragility/runner.env
sudo nano /etc/fragility/runner.env   # set FRAGILITY_RUN_API_KEY=...
sudo systemctl restart fragility-runner
```

Clients send `X-Fragility-Run-Key: <key>` or `Authorization: Bearer <key>`.

The run page (`/run.html`) shows a key field when `/api/health` reports `run_auth_required: true`. Users can set the key once via `https://…/run.html?run_key=YOUR_KEY` (stored in session storage for that browser tab).

---

## PyPI publish

GitHub Actions workflow **Publish to PyPI** (`.github/workflows/pypi.yml`) runs manually:

1. Add repository secret `PYPI_API_TOKEN` (PyPI → Account → API tokens).
2. Actions → **Publish to PyPI** → Run workflow → type `publish` in the confirm field.

Local smoke before publishing:

```bash
python scripts/check_pypi_ready.py
# optional: verify tag matches pyproject version
python scripts/check_pypi_ready.py --tag v0.5.0
```

CI job **`pypi-smoke`** on every push/PR builds the wheel/sdist and runs `twine check` (no upload).

**Note:** GitHub Actions may refuse to run workflows if org **billing** is blocked; use local publish as fallback:

```bash
python scripts/check_pypi_ready.py --tag v0.5.0
python -m twine upload dist/*   # needs TWINE_PASSWORD / PYPI_API_TOKEN in env
```

See [RELEASING.md](../RELEASING.md) for tagging and GitHub Release wheels.
