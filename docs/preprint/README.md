# FEL preprint

**Paper:** [`FEL_preprint_v0.1.md`](FEL_preprint_v0.1.md) · **PDF:** [`FEL_preprint_v0.1.pdf`](FEL_preprint_v0.1.pdf)  
**Publishing guide:** [`PUBLISHING.md`](PUBLISHING.md)  
**Normative spec (implementation):** [`../FRAGILITY_EVIDENCE_LANGUAGE.md`](../FRAGILITY_EVIDENCE_LANGUAGE.md)

## Citation (preprint)

```bibtex
@misc{peterson2026fel,
  author       = {David Peterson},
  title        = {Fragility Evidence Language (FEL): A Semantic Contract for Reproducible Stress-Search and Attribution in Discrete-Time Simulations},
  year         = {2026},
  howpublished = {Preprint, Agentic Ops / Fragility Discovery Engine},
  url          = {https://github.com/AgenticOp-io/fragility-discovery-engine/blob/main/docs/preprint/FEL_preprint_v0.1.md},
  note         = {Founder, Agentic Ops (agenticop.io). Version fel-v0.1. Prose drafting used AI-assisted tools (Cursor/Composer); technical claims verified by the author against the reference implementation.}
}
```

## Building a PDF

Checked-in PDF: **`FEL_preprint_v0.1.pdf`** (regenerate after editing the Markdown).

```powershell
pip install markdown playwright
python -m playwright install chromium
python scripts/build_fel_preprint_pdf.py
```

The script writes `docs/preprint/FEL_preprint_v0.1.html` (intermediate) and `docs/preprint/FEL_preprint_v0.1.pdf`.

**Alternatives:** Pandoc + LaTeX (`pandoc … -o FEL_preprint_v0.1.pdf --pdf-engine=xelatex`) or `npx md-to-pdf docs/preprint/FEL_preprint_v0.1.md` if Node is available.

## Relationship to other docs

| Document | Role |
|----------|------|
| This preprint | Scholarly framing, related work, contribution claims |
| `FRAGILITY_EVIDENCE_LANGUAGE.md` | Normative operator definitions and schema IDs |
| `MATH.md` | Equation-level reference (repo-only, not on public product site) |
| `PAPER_APPENDIX_WORKFLOW.md` | Reproducible artifact pipeline for reviewers |
