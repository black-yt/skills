#!/usr/bin/env python3
"""Manual desktop control: screenshot/move/click/type/key; no model integration."""
import argparse
import json
import urllib.request
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('session', type=Path, help='path to artifacts/<run>/session.json')
parser.add_argument('--url', help='override URL, for example http://127.0.0.1:8765 after SSH forwarding')
operation = parser.add_mutually_exclusive_group()
operation.add_argument('--screenshot', type=Path)
operation.add_argument('--action', help='JSON object, e.g. {"type":"click","x":500,"y":400}')
args = parser.parse_args()
session = json.loads(args.session.read_text())
token = Path(session['token_file']).read_text().strip()
url = args.url or f'http://{session["host"]}:{session["port"]}'
headers = {'Authorization': f'Bearer {token}'}
if args.action:
    data = json.dumps(json.loads(args.action)).encode()
    headers['Content-Type'] = 'application/json'
    request = urllib.request.Request(url+'/action', data=data, headers=headers)
else:
    request = urllib.request.Request(url+('/screenshot' if args.screenshot else '/healthz'), headers=headers)
# Always bypass external proxies for this private desktop service.
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
with opener.open(request, timeout=30) as response:
    raw = response.read()
if args.screenshot:
    args.screenshot.write_bytes(raw)
    print(args.screenshot)
else:
    print(raw.decode())
