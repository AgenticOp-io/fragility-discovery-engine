# What's left to do

Charter Phases H–P are shipped on `main`. The next build sequence is **Q → R → S** (research artifact → BYOW toolkit → falsification harness). No seventh reference domain is open.

## Next phases (build in order)

| Phase | Memo | Intent |
|-------|------|--------|
| **Q** — Research artifact polish | [`phase_q_research_artifact.md`](phase_q_research_artifact.md) | Honest positioning, citation path, version hygiene |
| **R** — BYOW toolkit surface | [`phase_r_byow_toolkit.md`](phase_r_byow_toolkit.md) | CLI + adapter SDK + second generic example |
| **S** — Falsification harness | [`phase_s_falsification_harness.md`](phase_s_falsification_harness.md) | Predicate damage + snapshot reset (after R) |

Normative gates live in [`BOUNDARIES.md`](../BOUNDARIES.md) (Phase Q/R/S). Roadmap narrative: [`ROADMAP_NEXT.md`](../ROADMAP_NEXT.md).

**Recommended start:** Phase Q (docs/version) in parallel with Phase R.1 (CLI entry points). Do not start Phase S until R’s public adapter path works.

## Ops leftovers (optional)

- [ ] **Custom hostname + HTTPS** — `fragility.agenticop.io` → `34.61.255.147`, then `powershell -File scripts/gce_enable_https.ps1`. See `docs/GCE_HTTPS_AND_AUTH.md`.
- [ ] **Deploy keys** — org policy may block; token sync works. See `docs/GCE_DEPLOY_KEY.md`.

## Out of scope (by design)

- Hosted SaaS, live market feeds, or regulatory certifications
- LLM-driven policy inside the simulation engine
- A seventh reference domain (open a new charter phase first)
- Coupled mega-institution physics on `main` (fork only)

## Maintenance

| Task | Command |
|------|---------|
| Run tests (Windows) | `powershell -File scripts/ci_local.ps1` |
| Run tests (Linux / GCE) | `bash scripts/gce_pull_and_test.sh` |
| Deploy public demo | `powershell -File scripts/gce_deploy_public_site.ps1` |
| Publish GitHub Pages mirror | `powershell -File scripts/deploy_github_pages.ps1` |
| GitHub Actions | Manual only — not triggered on push (until Phase R CI hygiene) |
