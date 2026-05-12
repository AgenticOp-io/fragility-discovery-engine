#!/usr/bin/env bash
# Enable Compute API and create one minimal Ubuntu VM (e2-micro) with first-boot install + clone.
# Usage:
#   bash scripts/gce_create_minimal.sh YOUR_PROJECT_ID [zone] [instance_name]
# Env:
#   SKIP_STARTUP=1  — do not attach startup script (bare VM only).
#   REPO_URL=...    — optional; passed as metadata fragility_repo_url (default: public GitHub).
set -euo pipefail
PROJECT="${1:?project id required}"
ZONE="${2:-us-central1-a}"
NAME="${3:-fragility-discovery-minimal}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STARTUP="${SCRIPT_DIR}/gce_minimal_vm_startup.sh"

gcloud config set project "${PROJECT}"
gcloud services enable compute.googleapis.com --project="${PROJECT}"

META=()
if [[ "${SKIP_STARTUP:-0}" != "1" ]]; then
  META+=(--metadata-from-file="startup-script=${STARTUP}")
fi
if [[ -n "${REPO_URL:-}" ]]; then
  META+=(--metadata="fragility_repo_url=${REPO_URL}")
fi

gcloud compute instances create "${NAME}" \
  --project="${PROJECT}" \
  --zone="${ZONE}" \
  --machine-type=e2-micro \
  --image-family=ubuntu-2404-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=25GB \
  --tags=allow-ssh \
  --labels=purpose=fragility-discovery-engine \
  "${META[@]}" \
  --quiet

echo "OK: first boot installs git/python and clones repo (see /var/log/fragility-bootstrap.log)."
echo "SSH: gcloud compute ssh ${NAME} --zone=${ZONE} --project=${PROJECT}"
echo "Then set FRAGILITY_GCE_* and run scripts/gce_sync_vm.ps1 (see docs/GCE_BOOTSTRAP.md)."
