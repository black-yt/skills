#!/usr/bin/env bash
# Manual entry point: load the reviewed configuration without changing parent-shell proxies.
set -euo pipefail
export CC_DIR="${CC_DIR:-$HOME/.cc}"
action=${1:-status}
if (( $# > 1 )) || [[ ! $action =~ ^(start|stop|status)$ ]]; then
    echo 'Usage: bash cc_proxy.sh [start|stop|status]' >&2
    exit 2
fi
if [[ "$action" == start ]]; then
    source "$CC_DIR/cc_env.sh"
    _cc_load_config
    if [[ "$CC_PROXY_MODE" != chain ]]; then
        echo 'Direct mode uses no relay; use cc_on in the target shell.' >&2
        exit 2
    fi
    _cc_manage start
else
    # Stop/status must still work if the configuration was removed or edited.
    exec python3 "$CC_DIR/cc_proxy.py" "$action"
fi
