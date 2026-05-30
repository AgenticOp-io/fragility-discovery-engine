# FEL preprint

**Paper:** [`FEL_preprint_v0.1.md`](FEL_preprint_v0.1.md)  
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

## Building a PDF (optional)

The source is Markdown. Common paths:

1. **Pandoc** (fastest if installed):
   ```bash
   pandoc docs/preprint/FEL_preprint_v0.1.md -o FEL_preprint_v0.1.pdf \
     --pdf-engine=xelatex -V geometry:margin=1in -V fontsize=11pt
   ```
2. **arXiv:** upload `.tex` converted from Pandoc (`pandoc -t latex`) or write LaTeX from the Markdown sections.
3. **GitHub:** render Markdown in the browser for informal sharing; link the raw file in arXiv `comments` field.

## Relationship to other docs

| Document | Role |
|----------|------|
| This preprint | Scholarly framing, related work, contribution claims |
| `FRAGILITY_EVIDENCE_LANGUAGE.md` | Normative operator definitions and schema IDs |
| `MATH.md` | Equation-level reference (repo-only, not on public product site) |
| `PAPER_APPENDIX_WORKFLOW.md` | Reproducible artifact pipeline for reviewers |
