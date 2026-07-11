#!/usr/bin/env bash
# Enable HTTPS with Let's Encrypt on the GCE workbench VM (nginx + certbot).
#
# Prerequisites:
#   1. DNS A record: FRAGILITY_PUBLIC_HOST → this VM's external IP
#   2. Port 443 open (gce_enable_https.ps1 or https-server firewall tag)
#
# Usage:
#   sudo FRAGILITY_PUBLIC_HOST=hub.agenticop.io bash scripts/gce_install_https.sh
#
set -euo pipefail

HOST="${FRAGILITY_PUBLIC_HOST:-hub.agenticop.io}"
EMAIL="${FRAGILITY_CERTBOT_EMAIL:-admin@agenticop.io}"
SITE_ROOT="${FRAGILITY_PUBLIC_ROOT:-/var/www/fragility/public}"
NGINX_SITE="/etc/nginx/sites-available/fragility-public"
CERT_DIR="/etc/letsencrypt/live/${HOST}"

if [[ -z "${HOST}" ]]; then
  echo "Set FRAGILITY_PUBLIC_HOST to your public hostname (e.g. hub.agenticop.io)." >&2
  exit 1
fi

if ! command -v certbot >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y certbot
fi

sudo mkdir -p "${SITE_ROOT}/.well-known/acme-challenge"

# Port 80 only — ACME webroot (no redirect until cert exists).
sudo tee "${NGINX_SITE}" >/dev/null <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${HOST};
    root ${SITE_ROOT};
    location /.well-known/acme-challenge/ { root ${SITE_ROOT}; }
    location / { try_files \$uri \$uri/ =404; }
}
EOF

sudo ln -sf "${NGINX_SITE}" /etc/nginx/sites-enabled/fragility-public
sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
sudo nginx -t
sudo systemctl reload nginx

if [[ ! -f "${CERT_DIR}/fullchain.pem" ]]; then
  sudo certbot certonly --webroot -w "${SITE_ROOT}" -d "${HOST}" \
    --non-interactive --agree-tos -m "${EMAIL}" --keep-until-expiring
fi

# Full workbench site on 443 (replay viewers, /api proxy, /runs).
sudo tee "${NGINX_SITE}" >/dev/null <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${HOST};
    root ${SITE_ROOT};
    location /.well-known/acme-challenge/ { root ${SITE_ROOT}; }
    location / { return 301 https://\$host\$request_uri; }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${HOST};
    root ${SITE_ROOT};
    index index.html;
    ssl_certificate ${CERT_DIR}/fullchain.pem;
    ssl_certificate_key ${CERT_DIR}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    error_page 404 /404.html;
    location = /404.html { internal; }
    location / {
        try_files \$uri \$uri/ =404;
    }
    location /runs/ {
        alias ${SITE_ROOT}/runs/;
        autoindex on;
        add_header Cache-Control "no-store" always;
    }
    location /api/ {
        proxy_pass http://127.0.0.1:8765;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 30s;
    }
    add_header X-Fragility-Product "fde-workbench" always;
}
EOF

sudo nginx -t
sudo systemctl reload nginx
echo "OK: HTTPS enabled for https://${HOST}/"
echo "Renewal: sudo certbot renew (systemd timer from certbot package)"
