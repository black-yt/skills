#!/usr/bin/env bash
# Run in an authorized download container; cache one verified official archive.
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
DEST=${CUA_SOFTWARE_DIR:-$ROOT/software}
archive_name=${SLICER_ARCHIVE_NAME:-Slicer-5.12.4-linux-amd64.tar.gz}
expected=${SLICER_SHA512:-ac76c5061a8fff20d4e59732855f74360930fd4891450085bcbc6a8eb1a1f4ade9a1ca4fc633142661b714dbe8c4604306079f9546e52053faa5e6f99410cf76}
download_url=${SLICER_DOWNLOAD_URL:-https://slicer-packages.kitware.com/api/v1/file/6aa1bec1ce9de556d3010212/download}
total_size=${SLICER_SIZE_BYTES:-498717156}
chunk_size=${CUA_DOWNLOAD_CHUNK_BYTES:-524288}
parallel=${CUA_DOWNLOAD_PARALLEL:-64}
[[ "$archive_name" =~ ^[a-zA-Z0-9][a-zA-Z0-9._-]*$ && "$expected" =~ ^[0-9a-fA-F]{128}$ ]] || exit 2
[[ "$total_size" =~ ^[1-9][0-9]*$ && "$chunk_size" =~ ^[1-9][0-9]*$ && "$parallel" =~ ^[1-9][0-9]*$ ]] || exit 2
(( parallel <= 64 )) || { echo 'parallel must be between 1 and 64' >&2; exit 2; }
mkdir -p "$DEST"
archive="$DEST/$archive_name"
if [[ -f "$archive" ]] && printf '%s  %s\n' "$expected" "$archive" | sha512sum -c -; then
  printf '%s  %s\n' "$expected" "$archive_name" > "$archive.sha512"
  echo software_already_cached
  exit 0
fi

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
started=$SECONDS
# Use a distinct parts directory per immutable archive version. One preparer per cache.
parts="$DEST/.$archive_name.parts"
mkdir -p "$parts"
/usr/bin/python3 - "$parts" "$total_size" "$chunk_size" "$download_url" <<'PYCFG'
import json, sys
from pathlib import Path
p = Path(sys.argv[1]); size, chunk = map(int, sys.argv[2:4]); url = sys.argv[4]
with (p/'curl.conf').open('w') as out:
    first = True
    for index, start in enumerate(range(0, size, chunk)):
        end = min(start+chunk, size)-1
        target = p/f'{index:05d}'
        if target.exists() and target.stat().st_size == end-start+1:
            continue
        if not first:
            out.write('next\n')
        first = False
        out.write('fail\nsilent\nshow-error\nconnect-timeout = 20\nmax-time = 120\nretry = 2\n')
        # A server ignoring Range must not download one full archive per request.
        out.write(f'max-filesize = {end-start+1}\n')
        out.write(f'url = {json.dumps(url)}\nrange = "{start}-{end}"\noutput = {json.dumps(str(target))}\n')
PYCFG
if [[ -s "$parts/curl.conf" ]]; then
  (
    ulimit -c 0
    # Older curl cannot enforce max-filesize when Content-Length is absent.
    # Bash's per-file limit (KiB) bounds each output even for chunked responses.
    ulimit -f "$(( (chunk_size+1023)/1024 ))"
    timeout 900 curl --parallel --parallel-immediate --parallel-max "$parallel" --fail --silent --show-error \
      --config "$parts/curl.conf" > "$DEST/download.log" 2>&1
  )
fi
/usr/bin/python3 - "$parts" "$archive.part" "$total_size" "$chunk_size" <<'PYJOIN'
import shutil, sys
from pathlib import Path
p = Path(sys.argv[1]); size, chunk = map(int, sys.argv[3:5])
with open(sys.argv[2], 'wb') as out:
    for index, start in enumerate(range(0, size, chunk)):
        part = p/f'{index:05d}'
        if part.stat().st_size != min(chunk, size-start):
            raise RuntimeError('incomplete range: '+str(part))
        with part.open('rb') as src:
            shutil.copyfileobj(src, out)
PYJOIN
printf '%s  %s\n' "$expected" "$archive.part" | sha512sum -c -
mv "$archive.part" "$archive"
printf '%s  %s\n' "$expected" "$archive_name" > "$archive.sha512"
/usr/bin/python3 - "$parts" <<'PYCLEAN'
import shutil, sys
shutil.rmtree(sys.argv[1])
PYCLEAN
printf 'download_seconds=%s\nsoftware_ready\n' "$(( SECONDS-started ))"
