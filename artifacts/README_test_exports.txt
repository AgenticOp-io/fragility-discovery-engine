artifacts/test_exports/
  Heavy replay / pareto / counterfactual JSON bundles for manual browser QA.
  Not produced by pytest (pytest uses ephemeral temp dirs).

  Regenerate:
    pwsh -File scripts/regenerate_test_exports.ps1
    bash scripts/regenerate_test_exports.sh

  Viewer:
    Serve repo root (e.g. python -m http.server 8765), open artifacts/replay_viewer/index.html —
    Presets dropdown loads local_presets.json (bundled samples + ../test_exports/*).
    Replay contract vs other JSON: artifacts/replay_viewer/README.md
  Pareto scatter: artifacts/pareto_viewer/index.html — presets include ../test_exports/pareto_front.json.
  Regenerate also writes coevolution_network.json (Phase G network alternating GA),
  replay_resource_cascade.json, pareto_front_resource_cascade.json, counterfactual_resource_cascade_remove.json (Phase J).
    Or use file / folder pickers; copy JSON beside the viewer if you prefer file://.
