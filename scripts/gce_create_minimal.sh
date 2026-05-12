#!/usr/bin/env bash
# Enable Compute API and create one minimal Ubuntu VM (e2-micro).
# Usage: bash scripts/gce_create_minimal.sh YOUR_PROJECT_ID [zone] [instance_name]
set -euo pipefail
PROJECT="${1:?project id required}"
ZONE="${2:-us-central1-a}"
NAME="${3:-fragility-discovery-minimal}"
gcloud config set project "${PROJECT}"
gcloud services enable compute.googleapis.com --project="${PROJECT}"
gcloud compute instances create "${NAME}" \
  --project="${PROJECT}" \
  --zone="${ZONE}" \
  --machine-type=e2-micro \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB \
  --tags=allow-ssh \
  --labels=purpose=fragility-discovery-engine \
  --quiet
echo "OK: gcloud compute ssh ${NAME} --zone=${ZONE} --project=${PROJECT}"
echo "Then set FRAGILITY_GCE_* and run scripts/gce_sync_vm.ps1 from Windows, or scp+ssh scripts/gce_pull_and_test.sh (see docs/GCE_BOOTSTRAP.md)."
