# Zenodo archive

Zenodo gives a **citable DOI** for GitHub releases. Integration is enabled for **AgenticOp-io/fragility-discovery-engine**.

## Published archive

| Tag | DOI | Record |
|-----|-----|--------|
| `fel-v0.1.1` | [10.5281/zenodo.20455689](https://doi.org/10.5281/zenodo.20455689) | https://zenodo.org/records/20455689 |

Badge (also in README):

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20455689.svg)](https://doi.org/10.5281/zenodo.20455689)
```

## Enable (once — done)

1. Sign in at [zenodo.org](https://zenodo.org) (GitHub OAuth).
2. **Account → GitHub** → enable **AgenticOp-io/fragility-discovery-engine** (org OAuth grant required).
3. **Sync now** after each new release if the deposit does not appear automatically.

## New releases

1. Create a GitHub release tag (e.g. `v0.6.0`, `fel-v0.2`).
2. Zenodo ingests the release tarball (+ attached assets) within minutes.
3. Open the draft deposit → **Publish** to mint the DOI.
4. Add the new DOI to `CITATION.cff` if it supersedes the FEL snapshot.

## What gets archived

- Release tarball (full repo at tag)
- Attached release assets (e.g. `FEL_preprint_v0.1.pdf` on `fel-v0.1.1`)

Code is **Apache 2.0**; preprint PDF is **CC BY 4.0** — mention both in deposit descriptions when editing metadata.
