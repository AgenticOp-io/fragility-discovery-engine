#!/usr/bin/env bash
# Install (or reinstall) the fragility runner systemd unit on a GCE VM.
# Idempotent: safe to re-run after deploys to pick up code changes.
set -euo pipefail

SERVICE_USER="${SUDO_USER:-${USER}}"
if [[ -z "${FRAGILITY_DEPLOY_DIR:-}" ]]; then
  SERVICE_HOME="$(eval echo "~${SERVICE_USER}")"
  FRAGILITY_DEPLOY_DIR="${SERVICE_HOME}/fragility-discovery-engine"
fi
REPO="${FRAGILITY_DEPLOY_DIR}"
PUBLIC_ROOT="${FRAGILITY_PUBLIC_ROOT:-/var/www/fragility/public}"
PY="${REPO}/.venv/bin/python"
UNIT_PATH="/etc/systemd/system/fragility-runner.service"

if [[ ! -x "${PY}" ]]; then
  echo "error: missing ${PY} — run gce_publish_workbench.sh first to create the venv" >&2
  exit 1
fi

sudo mkdir -p "${PUBLIC_ROOT}/runs" /etc/fragility
if [[ ! -f /etc/fragility/runner.env ]]; then
  sudo cp "${REPO}/scripts/gce_runner.env.example" /etc/fragility/runner.env
  sudo chmod 600 /etc/fragility/runner.env
fi
sudo chown -R "${SERVICE_USER}:${SERVICE_USER}" /var/www/fragility

sudo tee "${UNIT_PATH}" >/dev/null <<EOF
[Unit]
Description=Fragility Discovery Engine — scenario runner (GCE only)
After=network.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${REPO}
Environment=FRAGILITY_PUBLIC_ROOT=${PUBLIC_ROOT}
Environment=FRAGILITY_PYTHON=${PY}
Environment=FRAGILITY_RUNNER_HOST=127.0.0.1
Environment=FRAGILITY_RUNNER_PORT=8765
EnvironmentFile=-/etc/fragility/runner.env
ExecStart=${PY} ${REPO}/scripts/gce_run_server.py
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable fragility-runner.service
sudo systemctl restart fragility-runner.service
sleep 1
sudo systemctl --no-pager --full status fragility-runner.service || true
echo "OK: fragility-runner installed (PUBLIC_ROOT=${PUBLIC_ROOT}, user=${SERVICE_USER})"
