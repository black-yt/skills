#!/usr/bin/env python3
"""Offline Linux/WSL bundle checks: temporary homes, fake credentials and loopback only."""

import json
import os
from pathlib import Path
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import unittest


SCRIPTS = Path(__file__).resolve().parents[1]
PACKAGE = SCRIPTS / 'claude_proxy'


class EchoConnect(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(3)
        data = b''
        try:
            while b'\r\n\r\n' not in data:
                chunk = self.request.recv(4096)
                if not chunk:
                    return
                data += chunk
            self.server.requests.append(data)
            self.request.sendall(b'HTTP/1.1 200 Connection established\r\n\r\nREADY')
            while chunk := self.request.recv(65536):
                self.request.sendall(chunk)
            self.request.sendall(b'TAIL')
        except OSError:
            pass


class LocalServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


@unittest.skipUnless(sys.platform == 'linux', 'Requires Linux/WSL process identity checks')
class HelperTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='agent-helper-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.user_home = self.root / 'isolated-home'
        self.directory = self.user_home / '.cc'
        self.environment = {k: v for k, v in os.environ.items() if not k.startswith('CC_')}
        self.environment['CC_DIR'] = str(self.directory)
        self.environment['PYTHONDONTWRITEBYTECODE'] = '1'
        self.install()

    def run_command(self, args, expected=0, environment=None):
        result = subprocess.run(args, env=environment or self.environment, cwd=self.root,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def install(self, *args, expected=0):
        return self.run_command([sys.executable, str(PACKAGE / 'install.py'),
                                 '--user-home', str(self.user_home), *args], expected)

    def manager(self, action, expected=0):
        return self.run_command(['bash', str(self.directory / 'cc_proxy.sh'), action], expected)

    def config(self, mode='direct', upstream_port=10805, listen_port=26751):
        (self.directory / 'cc_proxy.conf').write_text(
            f'CC_PROXY_MODE={mode}\nCC_UPSTREAM_HOST=127.0.0.1\n'
            f'CC_UPSTREAM_PORT={upstream_port}\nCC_TARGET_HOST=target.example\n'
            f'CC_TARGET_PORT=26751\nCC_LISTEN_PORT={listen_port}\n')

    def test_install_is_complete_and_preserves_existing_files(self):
        for name in ['cc_env.sh', 'cc_proxy.sh', 'cc_proxy.py', 'cc_proxy_chain.py', 'cc_proxy.conf']:
            self.assertTrue((self.directory / name).is_file(), name)
        self.assertFalse((self.user_home / '.bashrc').exists())
        self.assertFalse((self.user_home / '.claude').exists())
        self.assertFalse((self.user_home / '.claude.json').exists())
        self.config()
        original = (self.directory / 'cc_proxy.conf').read_bytes()
        self.install()
        self.assertEqual((self.directory / 'cc_proxy.conf').read_bytes(), original)
        self.assertTrue((self.directory / 'cc_proxy.conf.new').is_file())

    def test_optional_migration_and_invalid_seed(self):
        credentials = self.root / 'private-fixture.json'
        credentials.write_text('{"accessToken":"FICTIONAL_TEST_ONLY"}')
        seed = self.root / 'seed.json'
        seed.write_text('{"userID":"fictional-account"}')
        settings = self.root / 'settings.json'
        settings.write_text('{"theme":"dark"}')
        state = self.user_home / '.claude.json'
        state.write_text('{"localPreference":42}')
        self.install('--credentials', str(credentials), '--identity-seed', str(seed),
                     '--settings', str(settings))
        self.assertEqual(json.loads(state.read_text()), {'localPreference': 42, 'userID': 'fictional-account'})
        self.assertTrue(list(self.user_home.glob('.claude.json.bak-*')))
        self.assertEqual((self.user_home / '.claude/.credentials.json').stat().st_mode & 0o777, 0o600)
        settings.write_text('{"theme":"light"}')
        self.install('--settings', str(settings))
        self.assertEqual(json.loads((self.user_home / '.claude/settings.json').read_text())['theme'], 'dark')
        state.write_text('invalid json')
        self.install('--identity-seed', str(seed), expected=2)
        self.assertEqual(state.read_text(), 'invalid json')

    def test_shell_restores_unset_empty_and_unexported_values(self):
        self.config()
        script = r'''
set -eu
unset http_proxy HTTPS_PROXY NO_PROXY
HTTP_PROXY='prior $(touch accidental-execution)'
export -n HTTP_PROXY
export https_proxy=''
export no_proxy='localhost,.private.example'
export ALL_PROXY='socks5://prior.example:1080'
source "$CC_DIR/cc_env.sh"
[[ ! -v http_proxy ]]
cc_on
[[ $HTTP_PROXY == http://target.example:26751 && ! -v ALL_PROXY ]]
cc_on
cc_off
[[ ! -v http_proxy && ! -v HTTPS_PROXY && ! -v NO_PROXY ]]
[[ $HTTP_PROXY == 'prior $(touch accidental-execution)' && -v https_proxy && -z $https_proxy ]]
[[ $(declare -p HTTP_PROXY) == 'declare -- '* ]]
[[ $ALL_PROXY == socks5://prior.example:1080 && $no_proxy == localhost,.private.example ]]
cc_off
'''
        self.run_command(['bash', '--noprofile', '--norc', '-c', script])
        self.assertFalse((self.root / 'accidental-execution').exists())

    def test_manual_chain_loads_config_and_relays_half_closed_stream(self):
        with LocalServer(('127.0.0.1', 0), EchoConnect) as server:
            server.requests = []
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            with socket.socket() as probe:
                probe.bind(('127.0.0.1', 0))
                listen_port = probe.getsockname()[1]
            self.config('chain', server.server_address[1], listen_port)
            try:
                self.manager('start')
                self.manager('status')
                self.manager('start')
                self.install(expected=2)
                with socket.create_connection(('127.0.0.1', listen_port), timeout=3) as client:
                    payload = b'fixture-payload' * 1000
                    client.sendall(payload)
                    client.shutdown(socket.SHUT_WR)
                    received = b''
                    while chunk := client.recv(65536):
                        received += chunk
                    self.assertEqual(received, b'READY' + payload + b'TAIL')
                self.assertTrue(server.requests)
                self.assertTrue(all(r.startswith(b'CONNECT target.example:26751 HTTP/1.1\r\n') for r in server.requests))
                self.run_command(['bash', '-c', 'source "$CC_DIR/cc_env.sh"; cc_on && cc_off --keep-daemon'])
                self.manager('status')
                # Recovery must not depend on a still-valid configuration file.
                (self.directory / 'cc_proxy.conf').unlink()
            finally:
                try:
                    self.manager('stop')
                finally:
                    server.shutdown()
                    thread.join(timeout=3)
            self.manager('status', expected=1)

    def test_manual_entry_does_not_start_direct_mode_or_signal_unrelated_pid(self):
        self.config()
        self.manager('start', expected=2)
        self.assertFalse((self.directory / 'cc_proxy_chain.pid').exists())
        unrelated = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])
        try:
            record = {'pid': unrelated.pid, 'starttime': 'invalid', 'boot_id': 'invalid'}
            (self.directory / 'cc_proxy_chain.pid').write_text(json.dumps(record))
            self.manager('stop', expected=2)
            self.assertIsNone(unrelated.poll())
        finally:
            unrelated.terminate()
            unrelated.wait(timeout=5)

    def test_github_wrapper_keeps_token_out_of_argv(self):
        fake_tools = self.root / 'fake-tools'
        fake_tools.mkdir()
        gh = fake_tools / 'gh'
        gh.write_text('#!/bin/sh\nprintf "%s\\n" FICTIONAL_TEST_TOKEN\n')
        gh.chmod(0o700)
        curl = fake_tools / 'real-curl'
        curl.write_text('#!' + sys.executable + '\nimport os,sys,json\nfrom pathlib import Path\n'
                        'Path(os.environ["TEST_CURL_CAPTURE"]).write_text(json.dumps({'
                        '"argv":sys.argv[1:],"stdin":sys.stdin.read() if "--config" in sys.argv else ""}))\n')
        curl.chmod(0o700)
        capture = self.root / 'captured.json'
        environment = {**self.environment, 'PATH': str(fake_tools) + os.pathsep + os.environ['PATH'],
                       'CODEX_REAL_CURL': str(curl), 'TEST_CURL_CAPTURE': str(capture)}
        wrapper = [sys.executable, str(SCRIPTS / 'github_api_curl.py')]
        self.run_command([*wrapper, '-fsSL', 'https://api.github.com/repos/example/example'], environment=environment)
        data = json.loads(capture.read_text())
        self.assertIn('FICTIONAL_TEST_TOKEN', data['stdin'])
        self.assertNotIn('FICTIONAL_TEST_TOKEN', ' '.join(data['argv']))
        for args in [['-v', 'https://api.github.com/x'], ['-o', 'https://api.github.com/x'],
                     ['https://api.github.com/x', 'https://example.com/x']]:
            self.run_command([*wrapper, *args], expected=2, environment=environment)
        self.run_command([*wrapper, 'https://example.com/download'], environment=environment)
        self.assertEqual(json.loads(capture.read_text())['stdin'], '')


if __name__ == '__main__':
    unittest.main(verbosity=2)
