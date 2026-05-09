# Regenerate browser-friendly bundles under artifacts/test_exports/ (not run by pytest).
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$out = Join-Path $Root "artifacts/test_exports"
New-Item -ItemType Directory -Force -Path $out | Out-Null

python scripts/export_replay.py --out "$out/replay_aggregate.json"
python scripts/export_replay.py --initial-panic 0.22 --out "$out/replay_aggregate_high_panic.json"
python scripts/export_replay.py --continue-after-collapse --horizon 40 --out "$out/replay_aggregate_continue.json"
python scripts/export_replay.py --mode network --out "$out/replay_network_er.json" --nodes 28 --horizon 22 --seed 12345
python scripts/export_replay.py --mode network --graph-kind watts_strogatz --nodes 20 --ws-k 4 --ws-p 0.14 --horizon 18 --out "$out/replay_network_ws.json"
python scripts/export_replay.py --mode network --continue-after-collapse --nodes 18 --horizon 16 --out "$out/replay_network_continue.json"
python scripts/export_replay.py --mode resource_cascade --out "$out/replay_resource_cascade.json" --horizon 18 --seed 55001 --genome-seed 55002 --initial-overload 0.068

python scripts/run_ga_demo.py --generations 5 --population-size 16 --seed 999 --export-replay "$out/ga_best.json" --export-minimized-replay "$out/ga_minimized.json"
python scripts/run_mc_demo.py --samples 48 --horizon 20 --seed 303 --export-replay "$out/mc_best.json"
python scripts/run_mc_demo.py --samples 24 --horizon 14 --seed 404 --continue-after-collapse --export-replay "$out/mc_continue.json"
python scripts/export_minimized_replay.py --out "$out/minimized_standalone.json" --horizon 30 --max-tries 300 --genome-search-seed 11

python scripts/export_pareto_front.py --out "$out/pareto_front.json" --seed 606
python scripts/export_pareto_front.py --mode resource_cascade --out "$out/pareto_front_resource_cascade.json" --horizon 10 --generations 2 --population-size 10 --seed 55202 --initial-overload 0.06 --max-steps 24
python scripts/export_counterfactual.py --out "$out/counterfactual_report.json" --export-replay-dir "$out/counterfactual_replays" --horizon 16 --remove "0,1,2" --seed 424242 --genome-seed 7
python scripts/export_counterfactual.py --mode resource_cascade --out "$out/counterfactual_resource_cascade_remove.json" --horizon 12 --remove "0" --seed 55101 --genome-seed 55102 --initial-overload 0.07
python scripts/run_coevolution.py --export-replay "$out/coevolution_final.json"
python scripts/run_coevolution.py --mode network --nodes 14 --rounds 1 --attacker-horizon 10 --attacker-generations 2 --attacker-population 8 --defender-generations 2 --defender-population 7 --seed 424242 --export-replay "$out/coevolution_network.json"
python scripts/find_cheap_collapse.py --export-replay "$out/cheap_collapse_best.json"
python scripts/run_network_demo.py --nodes 32 --generations 5 --population-size 14 --ga-seed 131 --export-replay "$out/network_ga_best.json"

Write-Host "Wrote exports under $out"
