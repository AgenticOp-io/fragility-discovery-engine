#!/usr/bin/env bash
# Local parity with .github/workflows/ci.yml "test" job (Linux/macOS/WSL Git Bash).
# Activate your venv first, then from repo root:  bash scripts/ci_local.sh
#
# Optional: set FRAGILITY_CI_LOCAL_BUILD=1 to also run ``python -m build`` (matches CI ``build`` job).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v python >/dev/null 2>&1; then
  echo "python not on PATH — create a venv and activate it (see docs/HOW_TO_USE.md)." >&2
  exit 1
fi

python -m pip install -e ".[dev]"
python -m ruff check .
export FRAGILITY_PERF_GATE=1
export FRAGILITY_PERF_GATE_MS="${FRAGILITY_PERF_GATE_MS:-240000}"
python -m pytest -q
python scripts/run_benchmark_suite.py --validate
python scripts/check_manifest_digest.py
python scripts/check_manifest_inventory.py
if [[ -n "${FRAGILITY_CI_LOCAL_BUILD:-}" ]]; then
  python -m pip install -q build
  python -m build
fi
echo "ci_local: OK (ruff + pytest + benchmark --validate + manifest pins; FRAGILITY_PERF_GATE=1)"
