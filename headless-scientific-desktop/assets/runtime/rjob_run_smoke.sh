#!/usr/bin/env bash
# Real Slicer acceptance test, entirely inside one CPU rjob.
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
export CUA_ROOT="$ROOT" CUA_RUN_ID="${CUA_RUN_ID:-slicer-acceptance-$(date +%Y%m%d-%H%M%S)}"
export CUA_ARTIFACT_DIR="${CUA_ARTIFACT_DIR:-$(dirname "$ROOT")/artifacts}"
export CUA_RECORD_SCREEN=1 CUA_MAX_SECONDS=240
archive=${SLICER_ARCHIVE:-${CUA_SOFTWARE_DIR:-$(dirname "$ROOT")/software}/Slicer-5.12.4-linux-amd64.tar.gz}
for _ in {1..90}; do [[ -f "$archive" ]] && break; sleep 1; done
[[ -f "$archive" ]] || { echo 'software preparation has not finished'; exit 1; }
bash "$ROOT/run_slicer.sh" &
desktop_pid=$!
trap 'kill -TERM "$desktop_pid" 2>/dev/null || true; wait "$desktop_pid" 2>/dev/null || true' EXIT
/usr/bin/python3 "$ROOT/verify_desktop.py" "$CUA_ARTIFACT_DIR/$CUA_RUN_ID"
kill -TERM "$desktop_pid"
wait "$desktop_pid"
/usr/bin/python3 - "$CUA_ARTIFACT_DIR/$CUA_RUN_ID" <<'PY'
import json,subprocess,sys
from pathlib import Path
p=Path(sys.argv[1]);video=p/'screen.mp4'
assert video.stat().st_size > 1000
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(video)]))
assert info['streams'][0]['codec_name']=='h264'
print('recording_seconds='+info['streams'][0]['duration'])
assert (p/'exit-code').read_text().strip()=='0'
print('real_slicer_acceptance=ok')
PY
