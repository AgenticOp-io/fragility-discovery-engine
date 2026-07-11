# GCE HTTPS and demo guardrails

**Public workbench default:** browse bundled samples freely; **live `POST /api/run` is closed** unless an operator sets `FRAGILITY_RUN_API_KEY` (or explicitly opts into anonymous runs on a private host).

| URL | Role |
|-----|------|
| **https://hub.agenticop.io/** (preferred) | Public hostname (A → `34.61.255.147`) |
| http://34.61.255.147/ | Same VM by IP |
| `/status.json` · `/api/health` | Validation + run-policy flags |

## Guardrails (default)

| Control | Default | Env |
|---------|---------|-----|
| Anonymous live runs | **off** | `FRAGILITY_ALLOW_ANONYMOUS_RUNS=1` to open (private hosts only) |
| Run API key | required when anonymous off | `FRAGILITY_RUN_API_KEY` |
| Per-IP hourly cap | **3** | `FRAGILITY_MAX_RUNS_PER_IP_HOUR` |
| Concurrent runs | 1 | hard-coded |
| Bind address | `127.0.0.1` (nginx proxy) | `FRAGILITY_RUNNER_HOST` |
| Public hostname | `hub.agenticop.io` | `FRAGILITY_PUBLIC_HOST` |

`gce_install_run_server.sh` writes a **random** API key into `/etc/fragility/runner.env` when missing, and hardens older open installs the same way.

Clients send `X-Fragility-Run-Key: <key>` or `Authorization: Bearer <key>`. The run page shows a key field when `/api/health` reports `run_auth_required: true`. Operators can open `https://hub.agenticop.io/run.html?run_key=YOUR_KEY` once (session storage).

**Do not** set `FRAGILITY_ALLOW_ANONYMOUS_RUNS=1` on the public hub.

Edit on the VM:

```bash
sudo nano /etc/fragility/runner.env
sudo systemctl restart fragility-runner
```

Example file: [`scripts/gce_runner.env.example`](../scripts/gce_runner.env.example).

---

## HTTPS (Let's Encrypt)

DNS is already in place:

| Record | Type | Value |
|--------|------|-------|
| `hub.agenticop.io` | A | `34.61.255.147` |

Enable TLS:

```powershell
powershell -File scripts/check_fragility_dns.ps1   # should exit 0 for hub.agenticop.io
powershell -File scripts/gce_enable_https.ps1      # defaults to hub.agenticop.io
```

Or on the VM:

```bash
sudo FRAGILITY_PUBLIC_HOST=hub.agenticop.io bash scripts/gce_install_https.sh
```

---

## PyPI publish

GitHub Actions workflow **Publish to PyPI** (`.github/workflows/pypi.yml`) runs manually:

1. Add repository secret `PYPI_API_TOKEN` (PyPI → Account → API tokens).
2. Actions → **Publish to PyPI** → Run workflow → type `publish` in the confirm field.

Local:

```bash
python scripts/check_pypi_ready.py --tag v0.6.0
python -m twine upload dist/*   # TWINE_USERNAME=__token__ TWINE_PASSWORD=<pypi token>
```

---

## Zenodo version (software release)

Concept DOI: [10.5281/zenodo.20455688](https://doi.org/10.5281/zenodo.20455688).

```powershell
$env:ZENODO_TOKEN = "<personal access token with deposit:write>"
python scripts/publish_zenodo_version.py --tag v0.6.0 --attach-dist --publish
```

See [`docs/ZENODO.md`](ZENODO.md).
