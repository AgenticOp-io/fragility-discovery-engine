#!/usr/bin/env bash
# Idempotent: nginx + /var/www/fragility for public static site.
set -euo pipefail

SITE_ROOT="${FRAGILITY_PUBLIC_ROOT:-/var/www/fragility/public}"
NGINX_SITE="/etc/nginx/sites-available/fragility-public"

if ! command -v nginx >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nginx
fi

sudo mkdir -p "${SITE_ROOT}"
sudo chown -R "${USER}:${USER}" /var/www/fragility 2>/dev/null || true

sudo tee "${NGINX_SITE}" >/dev/null <<EOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    root ${SITE_ROOT};
    index index.html;
    location / {
        try_files \$uri \$uri/ =404;
    }
    add_header X-Fragility-Site "agenticop-branded" always;
}
EOF

sudo ln -sf "${NGINX_SITE}" /etc/nginx/sites-enabled/fragility-public
sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl reload nginx
echo "OK: nginx public site root=${SITE_ROOT}"
