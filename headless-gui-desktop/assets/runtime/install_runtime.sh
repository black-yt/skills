#!/usr/bin/env bash
# Installs only inside an isolated rjob/container, never on the development host.
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PYTHON=${CUA_PYTHON:-/usr/bin/python3}
PY_LIB=${CUA_PYTHON_LIB:-/tmp/cua-python}
PACKAGE_CACHE=${CUA_PACKAGE_CACHE:-${CUA_SOFTWARE_DIR:-$(dirname "$ROOT")/software}/python-packages}
export DEBIAN_FRONTEND=noninteractive
export no_proxy="${no_proxy:-${NO_PROXY:-}},${CUA_NO_PROXY_EXTRA:-localhost,127.0.0.1}"
export NO_PROXY="$no_proxy"

packages=(ca-certificates curl xvfb openbox x11-utils xauth scrot ffmpeg mesa-utils
  python3 python3-pip python3-wheel python3-setuptools python3-tk python3-pil
  libgl1-mesa-dri libegl1 libglu1-mesa libpulse-mainloop-glib0
  libxkbcommon-x11-0 libxcb-xinerama0 libxcb-cursor0 libnss3 libasound2
  qt5dxcb-plugin libsm6 fonts-dejavu-core)
if ! dpkg-query -W -f='${Status}\n' "${packages[@]}" 2>/dev/null | awk 'BEGIN {ok=1} !/install ok installed/ {ok=0} END {exit !ok}'; then
  [[ "$EUID" == 0 ]] || { echo 'Missing apt packages; install only in an authorized root container.' >&2; exit 1; }
  apt-get -o Acquire::Retries=2 -o Acquire::http::Timeout=30 update -qq
  apt-get -o Acquire::Retries=2 -o Acquire::http::Timeout=30 install -y -qq --no-install-recommends "${packages[@]}"
fi
mkdir -p "$PY_LIB"
export PYTHONPATH="$PY_LIB${PYTHONPATH:+:$PYTHONPATH}"
if ! "$PYTHON" -c 'import importlib.util; assert importlib.util.find_spec("pyautogui")' 2>/dev/null; then
  if [[ ! -f "$PACKAGE_CACHE/.ready" ]]; then
    [[ "${CUA_OFFLINE:-0}" != 1 ]] || { echo 'Offline package cache missing; prepare Python packages in a network-enabled container first.' >&2; exit 1; }
    mkdir -p "$PACKAGE_CACHE"
    if [[ -n "${CUA_PROXY_SETUP_URL:-}" ]]; then
      setup_file=$(mktemp)
      trap 'unlink "$setup_file"' EXIT
      sleep 5
      curl --noproxy '*' -fsSL --connect-timeout 10 --max-time 30 "$CUA_PROXY_SETUP_URL" -o "$setup_file"
      bash -n "$setup_file"
      set +u
      source "$setup_file" >/dev/null 2>&1
      set -u
    fi
    "$PYTHON" -m pip download --disable-pip-version-check --no-cache-dir --no-deps --no-build-isolation \
      --dest "$PACKAGE_CACHE" --requirement "$ROOT/requirements.txt" > "$PACKAGE_CACHE/download.log" 2>&1
    touch "$PACKAGE_CACHE/.ready"
  fi
  "$PYTHON" -m pip install --disable-pip-version-check --no-cache-dir --no-index \
    --find-links "$PACKAGE_CACHE" --no-deps --no-build-isolation \
    --target "$PY_LIB" --requirement "$ROOT/requirements.txt" > "$PY_LIB/install.log" 2>&1
fi
printf 'python_runtime=%s\npython_lib=%s\n' "$PYTHON" "$PY_LIB"
