#!/usr/bin/env python3
"""PyAutoGUI desktop HTTP interface. No model calls or agent loop."""
from __future__ import annotations

import argparse
import hmac
import io
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class Desktop:
    def __init__(self):
        # DISPLAY/XAUTHORITY must exist before importing PyAutoGUI.
        import pyautogui
        self.gui = pyautogui
        self.gui.PAUSE = 0.05
        # Remote desktops have no human mouse; coordinates are checked below.
        self.gui.FAILSAFE = False
        self.width, self.height = self.gui.size()
        self.lock = threading.Lock()

    def xy(self, point):
        x, y = int(point['x']), int(point['y'])
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError('coordinates are outside the screen')
        return x, y

    def screenshot(self):
        with self.lock:
            buffer = io.BytesIO()
            self.gui.screenshot().save(buffer, format='PNG')
            return buffer.getvalue()

    def execute(self, action):
        if not isinstance(action, dict):
            raise ValueError('action must be an object')
        kind = action.get('type')
        with self.lock:
            if kind in ('click', 'double_click', 'move'):
                x, y = self.xy(action)
                if kind == 'move':
                    self.gui.moveTo(x, y)
                else:
                    button = action.get('button', 'left')
                    if button not in ('left', 'right', 'middle'):
                        raise ValueError('unsupported mouse button')
                    self.gui.click(x, y, clicks=2 if kind == 'double_click' else 1,
                                   interval=0.1, button=button)
            elif kind == 'drag':
                start, end = self.xy(action['start']), self.xy(action['end'])
                self.gui.moveTo(*start)
                self.gui.dragTo(*end, duration=0.3, button='left')
            elif kind == 'scroll':
                ticks = max(-20, min(20, int(action['ticks'])))
                self.gui.scroll(ticks)  # positive means up, matching PyAutoGUI
            elif kind == 'keypress':
                keys = action['keys']
                if isinstance(keys, str):
                    keys = [keys]
                if not isinstance(keys, list) or not keys:
                    raise ValueError('keys must be a key name or a non-empty list')
                keys = [str(key).lower() for key in keys]
                if any(key not in self.gui.KEYBOARD_KEYS for key in keys):
                    raise ValueError('unknown PyAutoGUI key name')
                self.gui.hotkey(*keys)
            elif kind == 'type':
                text = action['text']
                if not isinstance(text, str) or len(text) > 10000 or not text.isascii():
                    raise ValueError('type accepts at most 10000 ASCII characters')
                self.gui.write(text, interval=0.01)
            elif kind == 'wait':
                time.sleep(max(0, min(10, float(action.get('seconds', 1)))))
            else:
                raise ValueError('unsupported action type')
            return list(self.gui.position())


class Handler(BaseHTTPRequestHandler):
    def authorized(self):
        if not self.server.token:
            return True
        supplied = self.headers.get('Authorization', '')
        return hmac.compare_digest(supplied, 'Bearer ' + self.server.token)

    def reply(self, status, body, content_type='application/json'):
        if content_type == 'application/json':
            body = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self.authorized():
            self.reply(401, {'error': 'unauthorized'})
            return
        desktop = self.server.desktop
        if self.path == '/healthz':
            self.reply(200, {'ok': True, 'backend': 'pyautogui',
                             'display': os.environ['DISPLAY'], 'size': [desktop.width, desktop.height]})
        elif self.path == '/screenshot':
            try:
                self.reply(200, desktop.screenshot(), 'image/png')
            except Exception as exc:
                self.reply(500, {'error': str(exc)})
        elif self.path == '/position':
            with desktop.lock:
                self.reply(200, {'position': list(desktop.gui.position())})
        else:
            self.reply(404, {'error': 'not_found'})

    def do_POST(self):
        if not self.authorized():
            self.reply(401, {'error': 'unauthorized'})
            return
        if self.path != '/action':
            self.reply(404, {'error': 'not_found'})
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > 65536:
                raise ValueError('request body must be 1–65536 bytes')
            payload = json.loads(self.rfile.read(length))
            position = self.server.desktop.execute(payload)
            self.reply(200, {'ok': True, 'position': position})
        except (KeyError, ValueError, TypeError, OverflowError) as exc:
            self.reply(400, {'error': str(exc)})
        except Exception as exc:
            self.reply(500, {'error': str(exc)})

    def log_message(self, format, *args):
        # Never log authorization headers or action text.
        print(format % args, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default=os.getenv('CUA_BRIDGE_HOST', '127.0.0.1'))
    parser.add_argument('--port', type=int, default=int(os.getenv('CUA_BRIDGE_PORT', '8765')))
    parser.add_argument('--display', default=os.getenv('DISPLAY', ':99'))
    parser.add_argument('--token-file', default=os.getenv('CUA_TOKEN_FILE', ''))
    args = parser.parse_args()
    os.environ['DISPLAY'] = args.display
    token = Path(args.token_file).read_text().strip() if args.token_file else os.getenv('CUA_TOKEN', '')
    if args.host not in ('127.0.0.1', 'localhost', '::1') and not token:
        parser.error('a token file is required for a non-localhost bind')
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.token = token
    server.desktop = Desktop()
    print(f'backend=pyautogui display={args.display} size={server.desktop.width}x{server.desktop.height}', flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
