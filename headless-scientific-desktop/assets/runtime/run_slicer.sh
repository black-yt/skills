#!/usr/bin/env bash
# Ubuntu CPU desktop session: Slicer + Xvfb/Openbox + PyAutoGUI + optional recording.
set -Eeuo pipefail
ROOT=${CUA_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)}
PYTHON=${CUA_PYTHON:-/usr/bin/python3}
export CUA_PYTHON_LIB=${CUA_PYTHON_LIB:-/tmp/cua-python}
export PYTHONPATH="$CUA_PYTHON_LIB${PYTHONPATH:+:$PYTHONPATH}"
RUN_ID=${CUA_RUN_ID:-cua-$(date +%Y%m%d-%H%M%S)-$$}
[[ "$RUN_ID" =~ ^[a-zA-Z0-9._-]+$ ]] || { echo 'invalid CUA_RUN_ID' >&2; exit 1; }
ARTIFACT_ROOT=${CUA_ARTIFACT_DIR:-$(dirname "$ROOT")/artifacts}
RUN_DIR="$ARTIFACT_ROOT/$RUN_ID"
mkdir -p "$RUN_DIR"
SESSION_DIR=$(mktemp -d /tmp/cua-session-XXXXXX)
export HOME="$SESSION_DIR/home" XDG_RUNTIME_DIR="$SESSION_DIR/runtime"
export XDG_CACHE_HOME="$SESSION_DIR/cache" XDG_CONFIG_HOME="$SESSION_DIR/config"
export XAUTHORITY="$SESSION_DIR/Xauthority" XDG_SESSION_TYPE=x11
mkdir -p "$HOME" "$XDG_RUNTIME_DIR" "$XDG_CACHE_HOME" "$XDG_CONFIG_HOME"
chmod 700 "$XDG_RUNTIME_DIR"
touch "$XAUTHORITY"
export DISPLAY=${DISPLAY:-:99} LANG=C.UTF-8
export LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe
export QT_X11_NO_MITSHM=1 QT_OPENGL=software QT_QPA_PLATFORM=xcb
export LP_NUM_THREADS=${LP_NUM_THREADS:-2} OMP_NUM_THREADS=${OMP_NUM_THREADS:-4}
WIDTH=${CUA_SCREEN_WIDTH:-1440} HEIGHT=${CUA_SCREEN_HEIGHT:-900}

log() { printf '[cua %s] %s\n' "$(date -Is)" "$*"; }
stop_group() {
  local pid=${1:-} sig=${2:-TERM}
  [[ -n "$pid" ]] || return 0
  kill -"$sig" -- "-$pid" 2>/dev/null || true
}
cleanup() {
  local status=$?
  trap - EXIT INT TERM
  set +e
  stop_group "${RECORDER_PID:-}" INT
  if [[ -n "${RECORDER_PID:-}" ]]; then
    for _ in {1..30}; do kill -0 "$RECORDER_PID" 2>/dev/null || break; sleep .1; done
  fi
  for pid in "${SLICER_PID:-}" "${BRIDGE_PID:-}" "${OPENBOX_PID:-}" "${XVFB_PID:-}"; do stop_group "$pid"; done
  sleep .2
  for pid in "${SLICER_PID:-}" "${BRIDGE_PID:-}" "${OPENBOX_PID:-}" "${XVFB_PID:-}" "${RECORDER_PID:-}"; do stop_group "$pid" KILL; done
  wait 2>/dev/null
  "$PYTHON" - "$SESSION_DIR" <<'PY'
import shutil,sys
shutil.rmtree(sys.argv[1])
PY
  printf '%s\n' "$status" > "$RUN_DIR/exit-code"
  log "session ended; artifacts=$RUN_DIR"
  exit "$status"
}
trap cleanup EXIT
trap 'exit 0' INT TERM

ARCHIVE=${SLICER_ARCHIVE:-${CUA_SOFTWARE_DIR:-$(dirname "$ROOT")/software}/Slicer-5.12.4-linux-amd64.tar.gz}
if [[ -n "${SLICER_APP_DIR:-}" ]]; then
  SLICER_BIN="$SLICER_APP_DIR/Slicer"
else
  [[ -f "$ARCHIVE" ]] || { log "missing archive: $ARCHIVE; run prepare_software.sh in a CPU rjob first"; exit 1; }
  if [[ -f "$ARCHIVE.sha512" ]]; then
    (cd "$(dirname "$ARCHIVE")" && sha512sum -c "$(basename "$ARCHIVE").sha512")
  fi
  log 'extracting Slicer to temporary session disk'
  tar --no-same-owner -xzf "$ARCHIVE" -C "$SESSION_DIR"
  SLICER_BIN=$(find "$SESSION_DIR" -maxdepth 3 -name Slicer -type f -executable -print -quit)
fi
[[ -x "$SLICER_BIN" ]] || { log 'Slicer executable missing'; exit 1; }
if [[ "${CUA_INSTALL_RUNTIME:-1}" == 1 ]]; then
  bash "$ROOT/install_runtime.sh" > "$RUN_DIR/install.log" 2>&1
fi
for command_name in Xvfb openbox scrot ffmpeg xdpyinfo setsid; do command -v "$command_name" >/dev/null; done

setsid Xvfb "$DISPLAY" -screen 0 "${WIDTH}x${HEIGHT}x24" -ac -nolisten tcp \
  +extension GLX +render -noreset > "$RUN_DIR/Xvfb.log" 2>&1 &
XVFB_PID=$!
for _ in {1..100}; do
  kill -0 "$XVFB_PID" 2>/dev/null || { log 'Xvfb failed'; exit 1; }
  xdpyinfo >/dev/null 2>&1 && break
  sleep .1
done
xdpyinfo >/dev/null 2>&1
setsid openbox > "$RUN_DIR/openbox.log" 2>&1 &
OPENBOX_PID=$!
glxinfo -B > "$RUN_DIR/glxinfo.txt" 2>&1

BRIDGE_HOST=${CUA_BRIDGE_HOST:-0.0.0.0} BRIDGE_PORT=${CUA_BRIDGE_PORT:-8765}
export CUA_TOKEN_FILE="$RUN_DIR/control.token"
(umask 077; "$PYTHON" -c 'import secrets; print(secrets.token_urlsafe(32))' > "$CUA_TOKEN_FILE")
setsid "$PYTHON" "$ROOT/desktop_server.py" --host "$BRIDGE_HOST" --port "$BRIDGE_PORT" \
  --token-file "$CUA_TOKEN_FILE" > "$RUN_DIR/bridge.log" 2>&1 &
BRIDGE_PID=$!
bridge_ready=0
for _ in {1..100}; do
  kill -0 "$BRIDGE_PID" 2>/dev/null || { log 'PyAutoGUI bridge failed; see bridge.log'; exit 1; }
  if "$PYTHON" - <<'PY' >/dev/null 2>&1
import os,urllib.request
from pathlib import Path
req=urllib.request.Request('http://127.0.0.1:'+os.getenv('CUA_BRIDGE_PORT','8765')+'/healthz',
 headers={'Authorization':'Bearer '+Path(os.environ['CUA_TOKEN_FILE']).read_text().strip()})
with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=1) as r:
 assert r.status==200
PY
  then bridge_ready=1; break; fi
  sleep .1
done
[[ "$bridge_ready" == 1 ]] || { log 'bridge readiness timed out'; exit 1; }

if [[ "${CUA_RECORD_SCREEN:-0}" == 1 ]]; then
  setsid ffmpeg -hide_banner -loglevel error -f x11grab -framerate "${CUA_RECORD_FPS:-5}" \
    -video_size "${WIDTH}x${HEIGHT}" -i "$DISPLAY.0" -c:v libx264 -threads 2 \
    -preset ultrafast -crf 30 -pix_fmt yuv420p -fs "${CUA_RECORD_MAX_BYTES:-268435456}" \
    -y "$RUN_DIR/screen.mp4" > "$RUN_DIR/ffmpeg.log" 2>&1 &
  RECORDER_PID=$!
fi
log "starting $SLICER_BIN"
# Slicer's supported startup-code option also avoids a blocking first-run popup.
setsid "$SLICER_BIN" --no-splash --python-code 'slicer.util.mainWindow().showMaximized()' \
  > "$RUN_DIR/slicer.stdout.log" 2> "$RUN_DIR/slicer.stderr.log" &
SLICER_PID=$!
"$PYTHON" - "$RUN_DIR" "$BRIDGE_HOST" "$BRIDGE_PORT" "$SLICER_PID" <<'PY'
import json,os,socket,sys
from pathlib import Path
run,host,port,pid=sys.argv[1:]
info={'host':socket.gethostbyname(socket.gethostname()),'port':int(port),'display':os.environ['DISPLAY'],
      'xauthority':os.environ['XAUTHORITY'],'python_lib':os.environ['CUA_PYTHON_LIB'],
      'slicer_pid':int(pid),'token_file':str(Path(run)/'control.token'),
      'size':[int(os.getenv('CUA_SCREEN_WIDTH','1440')),int(os.getenv('CUA_SCREEN_HEIGHT','900'))]}
Path(run,'session.json').write_text(json.dumps(info,indent=2))
print('DESKTOP_URL=http://'+info['host']+':'+port,flush=True)
print('SESSION_FILE='+str(Path(run,'session.json')),flush=True)
PY
# Session lifetime bound limits CPU/storage use. 0 explicitly permits an unlimited session.
MAX_SECONDS=${CUA_MAX_SECONDS:-3600}
started=$SECONDS
while kill -0 "$SLICER_PID" 2>/dev/null; do
  if (( MAX_SECONDS > 0 && SECONDS - started >= MAX_SECONDS )); then log 'session time limit reached'; exit 0; fi
  kill -0 "$BRIDGE_PID" 2>/dev/null || { log 'control bridge exited'; exit 1; }
  sleep 1
done
wait "$SLICER_PID"
