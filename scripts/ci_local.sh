#!/usr/bin/env bash
# Local parity with .github/workflows/ci.yml "test" job (Linux/macOS/WSL Git Bash).
# Activate your venv first, then from repo root:  bash scripts/ci_local.sh
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
echo "ci_local: OK (ruff + pytest with FRAGILITY_PERF_GATE=1)"
