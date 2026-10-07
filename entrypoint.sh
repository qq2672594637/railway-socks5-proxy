#!/bin/sh
set -eu

: "${PROXY_PORT:=1080}"
: "${PROXY_USER:?Set PROXY_USER in Railway Variables}"
: "${PROXY_PASSWORD:?Set PROXY_PASSWORD in Railway Variables}"

exec python3 /opt/http_proxy.py \
  --listen 0.0.0.0 \
  --port "$PROXY_PORT" \
  --username "$PROXY_USER" \
  --password "$PROXY_PASSWORD"