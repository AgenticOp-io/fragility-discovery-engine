# Phase P — public product workbench (shipped)

The public host is the **working product UI** (static viewers + frozen bundled JSON), not a marketing clone of [agenticop.io](https://agenticop.io).

## URLs

| Host | URL |
|------|-----|
| **GCE** (`chrysalis-test-vm`, nginx) | FDE: http://34.61.255.147/ · Hub: https://hub.agenticop.io/ |
| **GitHub Pages** | https://agenticop-io.github.io/fragility-discovery-engine/ |

**Product entry:** `/` — workbench with embedded flagship replay + links to all viewers with bundled demos.

## Build & deploy

```bash
python scripts/build_public_site.py
# → artifacts/public_site/
```

```powershell
powershell -NoProfile -File scripts/gce_deploy_public_site.ps1
```

## What ships on the host

- **Replay / Pareto / Attribution / Composite** viewers (`artifacts/*_viewer/`)
- **Bundled demos** (flagship replay, domain samples, composite JSON)
- **Docs** (`/docs/whitepaper.html`) and **This host** (`/host.html`) — secondary to the workbench; `/install.html` redirects to host

## What this is not

- Not a hosted search/rollout API (run Python locally or in CI)
- Not agenticop.io corporate marketing styling
