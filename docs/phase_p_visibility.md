# Phase P — visibility & researcher onboarding (shipped)

Lightweight outreach on `main` without hosted SaaS or new physics.

## Shipped

| Item | Location |
|------|----------|
| Public landing page | [`docs/public/index.html`](public/index.html) via GitHub Pages (`.github/workflows/pages.yml`) |
| Research feedback issue template | [`.github/ISSUE_TEMPLATE/research_feedback.yml`](../.github/ISSUE_TEMPLATE/research_feedback.yml) |
| Coupled fork v1 | [`forks/coupled_institution/`](../forks/coupled_institution/) — `coupled_institution_v1` replay + GA demo |

## Public site (AgenticOps brand)

| Host | URL |
|------|-----|
| **GCE** (nginx on `chrysalis-test-vm`) | http://34.61.255.147/ |
| **GitHub Pages** | https://agenticop-io.github.io/fragility-discovery-engine/ |

**Build + deploy to GCE:**

```powershell
powershell -NoProfile -File scripts/gce_deploy_public_site.ps1
```

**Build only:**

```bash
python scripts/build_public_site.py
# output: artifacts/public_site/
```

Vendored brand assets: `docs/public/assets/agenticops.css`, `logo.svg` (from [agenticop.io](https://agenticop.io)).

## Coupled fork quick start

```bash
cd forks/coupled_institution
pip install -e .
pip install -e ../..    # fragility-engine for GA demo
pytest -q
python scripts/run_coupled_ga_demo.py --export-replay /tmp/coupled_demo.json
```

## PyPI (optional)

1. Create a PyPI account and API token (scope: entire account or project `fragility-engine`).
2. Repo **Settings → Secrets → Actions** → add `PYPI_API_TOKEN`.
3. **Actions → Publish to PyPI → Run workflow** → set confirm input to `publish`.

Install after publish: `pip install fragility-engine==0.5.0`

## Custom domain (agenticop.io)

1. Enable Pages (above); note the `*.github.io` URL from **Settings → Pages**.
2. **Pages → Custom domain** → `fragility-discovery.agenticop.io` (or apex via A/ALIAS per your DNS host).
3. At your DNS provider, add the records GitHub shows (usually `CNAME` to `<org>.github.io`).
4. Optional: link from the main site root to this Pages URL in your CMS.

## Non-goals (unchanged)

- Hosted dashboard SaaS
- Seventh reference domain on `main`
