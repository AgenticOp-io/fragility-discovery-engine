#!/usr/bin/env bash
set -euo pipefail
rm -rf "${HOME}/fragility-discovery-engine"
mkdir -p "${HOME}/fragility-discovery-engine"
tar -xzf "${HOME}/fragility-engine-src.tar.gz" -C "${HOME}/fragility-discovery-engine"
cd "${HOME}/fragility-discovery-engine"
python3 -m venv .venv
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -U pip setuptools wheel
pip install -q -e ".[dev]"
python -m ruff check .
export FRAGILITY_PERF_GATE=1
export FRAGILITY_PERF_GATE_MS=240000
python -m pytest -q
python scripts/run_benchmark_suite.py --validate
python scripts/check_manifest_digest.py
python scripts/check_manifest_inventory.py
python scripts/check_flagship_bundled.py
python scripts/check_manifest_summary.py
python scripts/validate_viewer_presets.py
python scripts/check_bundled_artifacts.py
python scripts/check_bundled_pareto_hypervolume.py
python scripts/fragility_robustness_stretch.py --preset small --dry-run
python scripts/export_static_dashboard.py --out artifacts/dashboard/index.html
python scripts/institutional_composite_demo.py --hexa --horizon 6 | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['schema']=='fragility-institutional-composite-v5'"
echo "OK: GCE tarball ci_local + Phase O"
