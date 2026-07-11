# GCE HTTPS and demo guardrails

**Public workbench default:** browse bundled samples freely; **live `POST /api/run` is closed** unless an operator sets `FRAGILITY_RUN_API_KEY` (or explicitly opts into anonymous runs on a private host).

**Full vhost + DNS plan:** [`HOSTNAME_MAP.md`](HOSTNAME_MAP.md)

## Same VM, two products

| Host | Product |
|------|---------|
| **https://hub.agenticop.io/** | **Chrysalis / Translation Hub** (nginx `:443` → `127.0.0.1:19090`) |
| **http://34.61.255.147:19090/** | Chrysalis direct (HTTP, bypasses nginx TLS) |
| **https://fragility.agenticop.io/** | **FDE workbench** (target URL after DNS + TLS) |
| **http://34.61.255.147/** | FDE IP fallback (`default_server` on `:80`) |

Do **not** point FDE nginx at `server_name hub.agenticop.io` or `chrysalis.agenticop.io` — those names are reserved for Chrysalis. DNS A records for all names can point at the same IP; nginx routes by hostname.

FDE status: https://fragility.agenticop.io/status.json (or http://34.61.255.147/status.json) · `/api/health` reports `live_runs_enabled` / `run_auth_required`.

## Guardrails (default)

| Control | Default | Env |
|---------|---------|-----|
| Anonymous live runs | **off** | `FRAGILITY_ALLOW_ANONYMOUS_RUNS=1` to open (private hosts only) |
| Run API key | required when anonymous off | `FRAGILITY_RUN_API_KEY` |
| Per-IP hourly cap | **3** | `FRAGILITY_MAX_RUNS_PER_IP_HOUR` |
| Concurrent runs | 1 | hard-coded |
| Bind address | `127.0.0.1` (nginx proxy) | `FRAGILITY_RUNNER_HOST` |

`gce_install_run_server.sh` writes a **random** API key into `/etc/fragility/runner.env` when missing.

Clients send `X-Fragility-Run-Key: <key>` or `Authorization: Bearer <key>`.

**Do not** set `FRAGILITY_ALLOW_ANONYMOUS_RUNS=1` on the public IP demo.

```bash
sudo nano /etc/fragility/runner.env
sudo systemctl restart fragility-runner
```

## FDE hostname + HTTPS

After GoDaddy A record `fragility` → `34.61.255.147`:

```powershell
powershell -File scripts/check_all_dns.ps1
powershell -File scripts/gce_enable_https.ps1 -PublicHost fragility.agenticop.io
```

On the VM:

```bash
FRAGILITY_PUBLIC_HOST=fragility.agenticop.io bash scripts/gce_install_public_web.sh
```

`scripts/gce_install_public_web.sh` refuses Chrysalis hostnames. Raw IP access stays on `fragility-default-ip`.

## PyPI / Zenodo

**Zenodo:** already synced from GitHub Releases (concept [10.5281/zenodo.20455688](https://doi.org/10.5281/zenodo.20455688)).

**PyPI:** Trusted Publishing (no API token). Log in at [pypi.org](https://pypi.org/account/login/), then [Add pending publisher](https://pypi.org/manage/account/publishing/):

| Field | Value |
|-------|--------|
| Project name | `fragility-engine` |
| Owner | `AgenticOp-io` |
| Repository | `fragility-discovery-engine` |
| Workflow | `pypi.yml` |
| Environment | *(blank)* |

Then: Actions → **Publish to PyPI** → confirm `publish`.

API-token fallback: create at [account/token](https://pypi.org/manage/account/token/) and `gh secret set PYPI_API_TOKEN`.
