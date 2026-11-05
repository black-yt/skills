#!/usr/bin/env bash
set -eo pipefail

: "${CLUSTER_PROXY_SETUP_URL:?set CLUSTER_PROXY_SETUP_URL from an approved ignored configuration}"
: "${META_BOT_DIR:?set META_BOT_DIR to an approved metabot checkout}"

HTTP_PROXY_SCRIPT="${HTTP_PROXY_SCRIPT:-${META_BOT_DIR}/tools/http_proxy/http_proxy.sh}"
if [[ ! -f "$HTTP_PROXY_SCRIPT" ]]; then
  echo "HTTP proxy script does not exist: $HTTP_PROXY_SCRIPT" >&2
  exit 2
fi

unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
# Complete the download before sourcing; process substitution hides curl failures.
proxy_setup="$(curl -fsSL --connect-timeout 15 --max-time 120 "$CLUSTER_PROXY_SETUP_URL" 2>/dev/null)" || {
  echo "cluster proxy setup download failed" >&2
  exit 2
}
bash -n <<< "$proxy_setup" 2>/dev/null || {
  echo "cluster proxy setup syntax is invalid" >&2
  exit 2
}
source <(printf '%s\n' "$proxy_setup")
unset proxy_setup

if [[ -n "${http_proxy:-}" || -n "${https_proxy:-}" ]]; then
  echo "cluster proxy=configured"
else
  echo "cluster proxy=missing" >&2
  exit 2
fi

exec bash "$HTTP_PROXY_SCRIPT"
