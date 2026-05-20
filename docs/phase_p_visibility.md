# Phase P — visibility & researcher onboarding (shipped)

Lightweight outreach on `main` without hosted SaaS or new physics.

## Shipped

| Item | Location |
|------|----------|
| Public landing page | [`docs/public/index.html`](public/index.html) via GitHub Pages (`.github/workflows/pages.yml`) |
| Research feedback issue template | [`.github/ISSUE_TEMPLATE/research_feedback.yml`](../.github/ISSUE_TEMPLATE/research_feedback.yml) |
| Coupled fork v1 | [`forks/coupled_institution/`](../forks/coupled_institution/) — `coupled_institution_v1` replay + GA demo |

## Enable GitHub Pages (once)

Repo **Settings → Pages → Build and deployment → GitHub Actions**. After the workflow runs, the site URL appears on the Pages settings tab (typically `https://<org>.github.io/<repo>/`).

## Coupled fork quick start

```bash
cd forks/coupled_institution
pip install -e .
pip install -e ../..    # fragility-engine for GA demo
pytest -q
python scripts/run_coupled_ga_demo.py --export-replay /tmp/coupled_demo.json
```

## Non-goals (unchanged)

- Hosted dashboard SaaS, agenticop.io DNS (operator task outside repo)
- Seventh reference domain on `main`
