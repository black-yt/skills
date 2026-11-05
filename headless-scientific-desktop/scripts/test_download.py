#!/usr/bin/env python3
"""Small localhost protocol checks; no Slicer download or third-party packages."""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'assets/runtime/prepare_software.sh'
DATA = bytes((i*17+i//512) % 256 for i in range(4096))
CHUNK = 512


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='desktop-download-')
        self.dest = Path(self.tmp.name) / 'cache with spaces'
        self.dest.mkdir()
        self.requests = []
        self.ignore_range = False
        self.unknown_size = False
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                request_range = self.headers.get('Range')
                outer.requests.append(request_range)
                if request_range and not outer.ignore_range:
                    start, end = map(int, request_range.removeprefix('bytes=').split('-'))
                    body = DATA[start:end+1]
                    self.send_response(206)
                    self.send_header('Content-Range', f'bytes {start}-{end}/{len(DATA)}')
                else:
                    body = DATA
                    self.send_response(200)
                if not outer.unknown_size:
                    self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_):
                pass

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.tmp.cleanup()

    def run_download(self, **extra):
        env = {k: v for k, v in os.environ.items()
               if k.lower() not in ('http_proxy', 'https_proxy', 'all_proxy')
               and not k.startswith(('CUA_', 'SLICER_'))}
        env.update(CUA_SOFTWARE_DIR=str(self.dest), SLICER_ARCHIVE_NAME='fixture.tar.gz',
                   SLICER_SHA512=hashlib.sha512(DATA).hexdigest(),
                   SLICER_SIZE_BYTES=str(len(DATA)), CUA_DOWNLOAD_CHUNK_BYTES=str(CHUNK),
                   CUA_DOWNLOAD_PARALLEL='2',
                   SLICER_DOWNLOAD_URL=f'http://127.0.0.1:{self.server.server_port}/file')
        env.update(extra)
        return subprocess.run(['bash', str(SCRIPT)], env=env, capture_output=True,
                              text=True, timeout=30)

    def test_range_resume_and_checksum(self):
        parts = self.dest / '.fixture.tar.gz.parts'
        parts.mkdir()
        (parts / '00000').write_bytes(DATA[:CHUNK])
        result = self.run_download()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.dest / 'fixture.tar.gz').read_bytes(), DATA)
        self.assertNotIn(f'bytes=0-{CHUNK-1}', self.requests)
        self.assertEqual(len(self.requests), len(DATA)//CHUNK-1)
        self.assertFalse(parts.exists())
        self.assertTrue((self.dest / 'fixture.tar.gz.sha512').exists())

    def test_valid_cache_avoids_network_and_proxy_setup(self):
        (self.dest / 'fixture.tar.gz').write_bytes(DATA)
        result = self.run_download(CUA_PROXY_SETUP_URL='http://127.0.0.1:1/not-allowed')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.requests, [])
        self.assertIn('software_already_cached', result.stdout)

    def test_checksum_failure_does_not_publish_archive(self):
        result = self.run_download(SLICER_SHA512='0'*128)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.dest / 'fixture.tar.gz').exists())

    def test_ignored_range_fails_without_writing_full_archives(self):
        self.ignore_range = True
        result = self.run_download()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.dest / 'fixture.tar.gz').exists())
        parts = self.dest / '.fixture.tar.gz.parts'
        self.assertTrue(all(p.stat().st_size <= CHUNK for p in parts.glob('[0-9]*')))

    def test_unknown_length_ignored_range_is_bounded_on_older_curl(self):
        self.ignore_range = self.unknown_size = True
        result = self.run_download()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.dest / 'fixture.tar.gz').exists())
        parts = self.dest / '.fixture.tar.gz.parts'
        ceiling = ((CHUNK+1023)//1024)*1024
        self.assertTrue(all(p.stat().st_size <= ceiling for p in parts.glob('[0-9]*')))


if __name__ == '__main__':
    unittest.main(verbosity=2)
