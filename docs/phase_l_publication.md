# Phase L — Narration & publication layer

**Normative guardrails** remain in [`BOUNDARIES.md`](../BOUNDARIES.md) (Phase L). This page is a **CLI index** for frozen artifacts.

## Deterministic narration (no LLM)

- **Library:** `fragility_engine.explain.narration` — `load_frozen_json_artifact`, `narrate_frozen_artifact`
- **CLI:** `scripts/narrate_frozen_json.py` — `--cite-digest`, `--json-out` → `narration-summary-v1`
- **Fingerprints:** `scripts/frozen_json_digest.py`

## Optional LLM wrapper (external prose only)

- **Versioned templates:** `artifacts/llm_prompts/narration_v1/` (`version.txt`, `system.txt`, `user_template.txt`)
- **CLI:** `scripts/export_llm_narration_prompt.py` → **`llm-prompt-bundle-v1`** JSON
- **Optional invoke:** `--invoke-openai` (stdlib HTTP; API key from env, default `OPENAI_API_KEY`). Model output is labeled **do not feed into simulation**.

## Figure hooks (matplotlib; `[dev]` / `[viz]`)

| Script | Input | Style schema |
|--------|--------|----------------|
| `plot_replay_timeline.py` | replay JSON | `fragility-plot-style-v1` |
| `plot_epsilon_sweep.py` | `counterfactual-epsilon-sweep-v1` | `fragility-plot-epsilon-sweep-style-v1` |
| `plot_pareto_front.py` | `pareto-front-v1` | `fragility-plot-pareto-style-v1` |
| `plot_fragility_surface_csv.py` | `fragility_surface.py` CSV | `fragility-plot-surface-style-v1` |

Pinned defaults live under `artifacts/plot_styles/`.
