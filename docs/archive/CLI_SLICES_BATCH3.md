# CLI smoke slices — batch 3 (ten slices)

Added in commit after v4 composite work. Each slice is one subprocess test in `tests/test_scripts_cli_smoke.py` unless noted.

| # | Slice | What it guards |
|---|--------|----------------|
| 1 | `export_counterfactual` **`delever_rate_shift`** (liquidity) | CLI wiring for physics-clone counterfactual (not only ε-sweep / joint merge) |
| 2 | `test_export_counterfactual_liquidity_ladder_delever_rate_shift_cli` | Smoke for slice 1 |
| 3 | `test_export_service_backlog_joint_attribution_process_rate_branch_cli` | Second-branch `process_rate_shift` on joint merge |
| 4 | `test_counterfactual_epsilon_sweep_service_backlog_process_rate_cli` | ε-sweep axis `process_rate` |
| 5 | `test_week1_smoke_continue_after_collapse_cli` | Aggregate smoke + recovery fields |
| 6 | `test_export_replay_liquidity_ladder_continue_after_collapse_cli` | Liquidity replay export flag |
| 7 | `test_narrate_frozen_json_penta_composite_cli` | Narration on bundled v4 composite |
| 8 | `test_plot_institutional_composite_bars_penta_bundled_cli` | Bar plot on bundled penta sample |
| 9 | `test_export_llm_narration_prompt_paper_appendix_quad_cli` | `paper_appendix_v1` pack on quad composite |
| 10 | Bundled `sample_attribution_merge_service_backlog.json` + `test_summarize_attribution_merge_liquidity_ladder_cli` | Service-backlog joint preset; interaction summary on liquidity merge |

Regenerate bundled attribution/composite files:

```bash
python scripts/regenerate_bundled_viewer_samples.py --skip-flagship --skip-pareto
```

See also [`CLI_SLICES.md`](CLI_SLICES.md) for the full inventory.
