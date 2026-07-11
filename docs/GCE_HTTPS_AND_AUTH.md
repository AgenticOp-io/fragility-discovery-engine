# GCE HTTPS and demo guardrails

**Public workbench default:** browse bundled samples freely; **live `POST /api/run` is closed** unless an operator sets `FRAGILITY_RUN_API_KEY` (or explicitly opts into anonymous runs on a private host).

## Same VM, two products

| Host | Product |
|------|---------|
| **https://hub.agenticop.io/** | AgenticOps **Translation Hub** (existing nginx + TLS → `:19090`) |
| **http://34.61.255.147/** | **Fragility Discovery Engine** workbench (this repo; nginx `default_server`) |

Do **not** point FDE nginx at `server_name hub.agenticop.io` — that name is reserved for the Translation Hub. DNS for `hub.agenticop.io` → `34.61.255.147` is correct for the VM; it does not mean FDE owns that hostname.

FDE status: http://34.61.255.147/status.json · `/api/health` reports `live_runs_enabled` / `run_auth_required`.

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

## Optional: dedicated FDE hostname

Only if you want a name other than the raw IP (and **not** `hub.agenticop.io`):

```powershell
# e.g. fragility.agenticop.io → 34.61.255.147, then:
$env:FRAGILITY_PUBLIC_HOST = "fragility.agenticop.io"
powershell -File scripts/gce_enable_https.ps1 -PublicHost fragility.agenticop.io
```

`scripts/gce_install_public_web.sh` refuses to bind `hub.agenticop.io` to the FDE site.

## PyPI / Zenodo

See [`docs/ZENODO.md`](ZENODO.md) and the PyPI section in [`RELEASING.md`](../RELEASING.md). Tokens required: `ZENODO_TOKEN`, `PYPI_API_TOKEN`.
