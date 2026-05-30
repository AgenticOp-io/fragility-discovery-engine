# Zenodo archive (optional DOI)

Zenodo gives a **citable DOI** for GitHub releases. One-time setup, then automatic on each new release.

## Enable (once)

1. Sign in at [zenodo.org](https://zenodo.org) (GitHub OAuth is fine).
2. **Account → GitHub** → switch on **AgenticOp-io/fragility-discovery-engine**.
3. Choose which releases to archive (recommend: **all releases** or tag pattern `fel-*` + `v*`).

## First archive

Create or sync the **`fel-v0.1`** GitHub Release (FEL preprint snapshot + PDF asset). After Zenodo is enabled:

1. On [Zenodo → GitHub settings](https://zenodo.org/account/settings/github/), click **Sync now** for this repo if the release does not appear within a few minutes.
2. Open the new Zenodo deposit and **Publish** (reserves the DOI).
3. Copy the DOI into `CITATION.cff` (`identifiers:` block) and README badge below.
4. Add to `docs/preprint/FEL_preprint_v0.1.md` reference section if desired.

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXX)
```

## What gets archived

- Release tarball (full repo at tag)
- Attached assets (e.g. `FEL_preprint_v0.1.pdf` on `fel-v0.1`)

## Metadata hints (Zenodo deposit form)

| Field | Suggested value |
|-------|-----------------|
| Title | Fragility Evidence Language (FEL) v0.1 — semantic contract + reference implementation |
| Authors | Peterson, David |
| Description | Semantic contract for reproducible stress-search evidence in discrete-time simulations. |
| License | Apache 2.0 (software) — note preprint is CC BY separately |
| Related identifier | https://github.com/AgenticOp-io/fragility-discovery-engine |

Code and preprint licenses differ by design; mention both in the Zenodo description.
