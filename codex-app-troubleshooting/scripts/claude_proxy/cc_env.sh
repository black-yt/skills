# Bash only. Sourcing defines functions; it does not modify proxy variables or start a daemon.
CC_DIR="${CC_DIR:-$HOME/.cc}"

_cc_load_config() {
    [[ -f "$CC_DIR/cc_proxy.conf" ]] || { echo 'Missing cc_proxy.conf' >&2; return 1; }
    unset CC_NO_PROXY
    # This file is user-reviewed shell code, not an untrusted data file.
    source "$CC_DIR/cc_proxy.conf" || return 1
    [[ "$CC_PROXY_MODE" == direct || "$CC_PROXY_MODE" == chain ]] || return 1
    [[ "$CC_TARGET_HOST" =~ ^[A-Za-z0-9._-]+$ ]] || { echo 'Configure a valid target host' >&2; return 1; }
    local port
    for port in "$CC_TARGET_PORT" "$CC_LISTEN_PORT"; do
        [[ "$port" =~ ^[0-9]{1,5}$ ]] && ((10#$port > 0 && 10#$port < 65536)) || return 1
    done
    if [[ "$CC_PROXY_MODE" == chain ]]; then
        [[ "$CC_UPSTREAM_HOST" =~ ^[A-Za-z0-9._-]+$ ]] || return 1
        [[ "$CC_UPSTREAM_PORT" =~ ^[0-9]{1,5}$ ]] &&
            ((10#$CC_UPSTREAM_PORT > 0 && 10#$CC_UPSTREAM_PORT < 65536)) || return 1
    fi
}

_cc_save_env() {
    [[ ${_CC_SAVED:-0} == 1 ]] && return 0
    declare -gA _CC_VALUES=() _CC_WAS_SET=() _CC_EXPORTED=()
    local name declaration
    for name in http_proxy https_proxy HTTP_PROXY HTTPS_PROXY no_proxy NO_PROXY all_proxy ALL_PROXY; do
        if [[ -v $name ]]; then
            _CC_WAS_SET[$name]=1
            _CC_VALUES[$name]=${!name}
        fi
        declaration=$(declare -p "$name" 2>/dev/null) || declaration=''
        [[ "$declaration" =~ ^declare\ -[^[:space:]]*x ]] && _CC_EXPORTED[$name]=1
    done
    _CC_SAVED=1
    return 0
}

_cc_restore_env() {
    [[ ${_CC_SAVED:-0} == 1 ]] || return 0
    local name
    for name in http_proxy https_proxy HTTP_PROXY HTTPS_PROXY no_proxy NO_PROXY all_proxy ALL_PROXY; do
        if [[ ${_CC_WAS_SET[$name]:-0} == 1 ]]; then
            printf -v "$name" '%s' "${_CC_VALUES[$name]}"
            if [[ ${_CC_EXPORTED[$name]:-0} == 1 ]]; then export "$name"; else export -n "$name"; fi
        else
            unset "$name"
        fi
    done
    unset _CC_SAVED _CC_VALUES _CC_WAS_SET _CC_EXPORTED
}

_cc_manage() {
    CC_DIR="$CC_DIR" CC_PROXY_MODE="$CC_PROXY_MODE" \
    CC_TARGET_HOST="$CC_TARGET_HOST" CC_TARGET_PORT="$CC_TARGET_PORT" \
    CC_UPSTREAM_HOST="$CC_UPSTREAM_HOST" CC_UPSTREAM_PORT="$CC_UPSTREAM_PORT" \
    CC_LISTEN_PORT="$CC_LISTEN_PORT" python3 "$CC_DIR/cc_proxy.py" "$@"
}

cc_on() {
    [[ ${_CC_SAVED:-0} != 1 ]] || { echo 'Proxy already enabled in this shell; run cc_off first.'; return 0; }
    _cc_load_config || return 1
    if [[ "$CC_PROXY_MODE" == chain ]]; then _cc_manage start || return 1; fi
    _cc_save_env
    _CC_ACTIVE_MODE=$CC_PROXY_MODE
    _CC_ACTIVE_DIR=$CC_DIR
    local uri
    if [[ "$CC_PROXY_MODE" == direct ]]; then uri="http://$CC_TARGET_HOST:$CC_TARGET_PORT"
    else uri="http://127.0.0.1:$CC_LISTEN_PORT"; fi
    export http_proxy="$uri" https_proxy="$uri" HTTP_PROXY="$uri" HTTPS_PROXY="$uri"
    unset all_proxy ALL_PROXY
    if [[ -v CC_NO_PROXY ]]; then export no_proxy="$CC_NO_PROXY" NO_PROXY="$CC_NO_PROXY"; fi
    echo "Proxy enabled for this shell ($CC_PROXY_MODE); existing bypass preserved unless configured."
}

cc_off() {
    [[ $# == 0 || ($# == 1 && $1 == --keep-daemon) ]] || { echo 'Usage: cc_off [--keep-daemon]' >&2; return 2; }
    local mode=${_CC_ACTIVE_MODE:-} directory=${_CC_ACTIVE_DIR:-} result=0
    _cc_restore_env
    if [[ "$mode" == chain && ${1:-} != --keep-daemon ]]; then
        CC_DIR="$directory" python3 "$directory/cc_proxy.py" stop || result=$?
    fi
    unset _CC_ACTIVE_MODE _CC_ACTIVE_DIR
    echo 'Original shell proxy settings restored.'
    return "$result"
}

cc_status() {
    _cc_load_config || return 1
    local uri
    if [[ "$CC_PROXY_MODE" == chain ]]; then
        _cc_manage status || return 1
        uri="http://127.0.0.1:$CC_LISTEN_PORT"
    else uri="http://$CC_TARGET_HOST:$CC_TARGET_PORT"; fi
    printf 'mode=%s; probing configured route (HTTP response is not authentication)\n' "$CC_PROXY_MODE"
    curl --proxy "$uri" --noproxy '' --connect-timeout 5 --max-time 30 \
        -sS -o /dev/null -w 'api.anthropic.com http=%{http_code}\n' https://api.anthropic.com/v1/models
}
