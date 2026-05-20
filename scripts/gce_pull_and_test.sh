#!/usr/bin/env bash
# Run on GCE after scp: bash ~/gce_pull_and_test.sh
# Full CI parity (ruff + pytest + benchmark validate + manifest pins + Phase O smokes).
set -euo pipefail
DEPLOY_DIR="${FRAGILITY_DEPLOY_DIR:-${HOME}/fragility-discovery-engine}"
KEY="${HOME}/.ssh/gce_github_ed25519"
MARK="# fragility-discovery-engine: gce-github-deploy"

for _cfg in "${HOME}/gce_configure_git_ssh.sh" "${DEPLOY_DIR}/scripts/gce_configure_git_ssh.sh"; do
  if [[ -f "${_cfg}" ]]; then
    # shellcheck source=/dev/null
    source "${_cfg}"
    fragility_gce_ensure_github_ssh_config
    break
  fi
done

cd "${DEPLOY_DIR}"
if [[ -f "${KEY}" ]] && ! grep -qF "${MARK}" "${HOME}/.ssh/config" 2>/dev/null; then
  export GIT_SSH_COMMAND="ssh -i ${KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
fi
git fetch origin main
git checkout main
git pull --ff-only origin main
# shellcheck source=/dev/null
source .venv/bin/activate
pip install -q -U pip setuptools wheel
pip install -q -e ".[dev]"
python -m ruff check .
export FRAGILITY_PERF_GATE="${FRAGILITY_PERF_GATE:-1}"
export FRAGILITY_PERF_GATE_MS="${FRAGILITY_PERF_GATE_MS:-240000}"
python -m pytest -q
python scripts/run_benchmark_suite.py --validate
python scripts/check_manifest_digest.py
python scripts/check_manifest_inventory.py
python scripts/check_flagship_bundled.py
python scripts/check_manifest_summary.py
python scripts/validate_viewer_presets.py
python scripts/check_bundled_artifacts.py
python scripts/check_bundled_pareto_hypervolume.py
# Phase O stretch smokes (fast)
python scripts/fragility_robustness_stretch.py --preset small --dry-run
python scripts/export_static_dashboard.py --out artifacts/dashboard/index.html
python scripts/institutional_composite_demo.py --hexa --horizon 6 | python -c "import json,sys; d=json.load(sys.stdin); assert d['schema']=='fragility-institutional-composite-v5'"
echo "OK: GCE pull + full ci_local parity + Phase O smokes (FRAGILITY_PERF_GATE=${FRAGILITY_PERF_GATE})"
