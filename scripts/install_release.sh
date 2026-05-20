#!/usr/bin/env bash
# Install fragility-engine from a git tag or GitHub Release wheel (no PyPI required).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TAG="${1:-v0.5.0}"
VER="${TAG#v}"
REPO="${FRAGILITY_REPO:-https://github.com/AgenticOp-io/fragility-discovery-engine}"
MODE="${FRAGILITY_INSTALL_MODE:-auto}"

if [[ "${MODE}" == auto ]]; then
  if [[ -f "${ROOT}/pyproject.toml" ]] && grep -q "^version = \"${VER}\"" "${ROOT}/pyproject.toml" 2>/dev/null; then
    MODE=editable
  else
    MODE=wheel
  fi
fi

case "${MODE}" in
  editable)
    echo "==> pip install -e ${ROOT}[dev] (checkout at ${TAG})"
    pip install -e "${ROOT}[dev]"
    ;;
  git)
    echo "==> pip install from git ${TAG}"
    pip install "fragility-engine @ git+${REPO}.git@${TAG}"
    ;;
  wheel)
    WHEEL_URL="${REPO}/releases/download/${TAG}/fragility_engine-${VER}-py3-none-any.whl"
    echo "==> pip install ${WHEEL_URL}"
    pip install "${WHEEL_URL}"
    ;;
  *)
    echo "FRAGILITY_INSTALL_MODE must be auto, editable, git, or wheel (got ${MODE})" >&2
    exit 2
    ;;
esac

python -c "import fragility_engine; print('import_ok', fragility_engine.__file__)"
