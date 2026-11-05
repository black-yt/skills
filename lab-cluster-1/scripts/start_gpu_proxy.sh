#!/usr/bin/env bash
set -eo pipefail

: "${CLUSTER_PROXY_SETUP_URL:?set CLUSTER_PROXY_SETUP_URL from an approved ignored configuration}"
: "${META_BOT_DIR:?set META_BOT_DIR to an approved metabot checkout}"

HTTP_PROXY_SCRIPT="${HTTP_PROXY_SCRIPT:-${META_BOT_DIR}/tools/http_proxy/http_proxy.sh}"
if [[ ! -f "$HTTP_PROXY_SCRIPT" ]]; then
  echo "HTTP proxy script does not exist: $HTTP_PROXY_SCRIPT" >&2
  exit 2
fi

unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
source <(curl -fsSL "$CLUSTER_PROXY_SETUP_URL")

if [[ -n "${http_proxy:-}" || -n "${https_proxy:-}" ]]; then
  echo "cluster proxy=configured"
else
  echo "cluster proxy=missing" >&2
  exit 2
fi

exec bash "$HTTP_PROXY_SCRIPT"
