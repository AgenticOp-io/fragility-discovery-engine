# CLI smoke slices — batch 4 (ten slices)

Regression and parity extensions after batch 3. See [`CLI_SLICES.md`](CLI_SLICES.md) for the full inventory.

| # | Slice | What it guards |
|---|--------|----------------|
| 1 | `test_sample_penta_composite_schema_and_narration` | Bundled v4 composite + narration |
| 2 | Manifest tests for **v4**, `bundle_attack_cost_bands`, `bundle_collapsed_expect` | Benchmark manifest review artifact |
| 3 | `test_attack_cost_band_rejects_out_of_range` | Attack-cost regression floor |
| 4 | `test_collapsed_expect_rejects_mismatch` | Collapse-bit regression floor |
| 5 | Liquidity `delever_rate_shift` + `--export-replay-dir` | Counterfactual replay pair export |
| 6 | Pareto liquidity + `--replay-pareto-index 0` | Indexed replay from Pareto archive |
| 7 | `export_replay` continue-after-collapse (service_backlog + resource_cascade) | Recovery fields on domain replays |
| 8 | `paper_appendix_v1` LLM pack on bundled penta | Publication prompt on v4 composite |
| 9 | Summarize bundled service_backlog joint merge | Interaction summary on SB merge |
| 10 | Certificate `--digest-json` on penta + network GA `eval-workers` + twin bar plot + `frozen_json_digest` on penta | Certificate digest, parallelism, composite viz |
