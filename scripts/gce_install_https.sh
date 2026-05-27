#!/usr/bin/env bash
# Optional: enable HTTPS with Let's Encrypt on the GCE workbench VM.
#
# Prerequisites:
#   1. DNS A record pointing your hostname at this VM's external IP
#      (for example fragility.agenticop.io → 34.61.255.147)
#   2. Port 443 open in the GCP firewall (http-server tag usually covers 80 only;
#      add a rule for tcp:443 or use https-server tag)
#
# Usage (on the VM, after nginx is installed via gce_install_public_web.sh):
#   sudo FRAGILITY_PUBLIC_HOST=fragility.agenticop.io bash scripts/gce_install_https.sh
#
set -euo pipefail

HOST="${FRAGILITY_PUBLIC_HOST:-}"
EMAIL="${FRAGILITY_CERTBOT_EMAIL:-admin@agenticop.io}"
SITE_ROOT="${FRAGILITY_PUBLIC_ROOT:-/var/www/fragility/public}"
NGINX_SITE="/etc/nginx/sites-available/fragility-public"

if [[ -z "${HOST}" ]]; then
  echo "Set FRAGILITY_PUBLIC_HOST to your public hostname (e.g. fragility.agenticop.io)." >&2
  exit 1
fi

if ! command -v certbot >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y certbot python3-certbot-nginx
fi

sudo tee "${NGINX_SITE}" >/dev/null <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${HOST};
    root ${SITE_ROOT};
    index index.html;
    location /.well-known/acme-challenge/ { root ${SITE_ROOT}; }
    location / { return 301 https://\$host\$request_uri; }
}
EOF

sudo ln -sf "${NGINX_SITE}" /etc/nginx/sites-enabled/fragility-public
sudo nginx -t
sudo systemctl reload nginx

sudo certbot --nginx -d "${HOST}" --non-interactive --agree-tos -m "${EMAIL}" --redirect

echo "OK: HTTPS enabled for https://${HOST}/"
echo "Renewal: certbot renew (systemd timer installed by certbot package)"
