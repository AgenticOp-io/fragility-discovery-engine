artifacts/test_exports/
  Heavy replay / pareto / counterfactual JSON bundles for manual browser QA.
  Not produced by pytest (pytest uses ephemeral temp dirs).

  Regenerate:
    pwsh -File scripts/regenerate_test_exports.ps1

  Viewer:
    Serve repo root or artifacts/replay_viewer and load files from test_exports via file picker,
    or copy JSON into replay_viewer folder for simpler paths.
