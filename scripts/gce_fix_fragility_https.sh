#!/usr/bin/env bash
# One-time fix: TLS vhost for fragility.agenticop.io (hub already has :443).
set -euo pipefail

SITE_ROOT="/var/www/fragility/public"
HOST="fragility.agenticop.io"
EMAIL="${FRAGILITY_CERTBOT_EMAIL:-admin@agenticop.io}"

if ! command -v certbot >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y certbot
fi

# Preserve IP fallback on :80
if [[ ! -f /etc/nginx/sites-available/fragility-default-ip ]]; then
  sudo cp /etc/nginx/sites-available/fragility-public /etc/nginx/sites-available/fragility-default-ip
  sudo ln -sf /etc/nginx/sites-available/fragility-default-ip /etc/nginx/sites-enabled/fragility-default-ip
fi

sudo mkdir -p "${SITE_ROOT}/.well-known/acme-challenge"

if [[ ! -f "/etc/letsencrypt/live/${HOST}/fullchain.pem" ]]; then
  sudo certbot certonly --webroot -w "${SITE_ROOT}" -d "${HOST}" \
    --non-interactive --agree-tos -m "${EMAIL}" --keep-until-expiring
fi

sudo tee /etc/nginx/sites-available/fragility-public >/dev/null <<EOF
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
    ssl_certificate     /etc/letsencrypt/live/${HOST}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${HOST}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    root ${SITE_ROOT};
    index index.html;
    error_page 404 /404.html;
    location = /404.html { internal; }
    location / { try_files \$uri \$uri/ =404; }
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

sudo ln -sf /etc/nginx/sites-available/fragility-public /etc/nginx/sites-enabled/fragility-public
sudo nginx -t
sudo systemctl reload nginx

echo "OK: https://${HOST}/"
echo | openssl s_client -connect 127.0.0.1:443 -servername "${HOST}" 2>/dev/null | openssl x509 -noout -subject -dates
