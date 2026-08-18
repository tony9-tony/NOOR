<<<<<<< HEAD
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, urlunparse
from urllib import request as urlrequest
from pathlib import Path
import mimetypes
import os
import urllib.parse

PORT = 5500
BACKEND_URL = "http://localhost:8800"
ROOT_DIR = Path(__file__).resolve().parent

class ProxyHandler(BaseHTTPRequestHandler):
    server_version = "RushProxy/1.0"

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def do_PUT(self):
        self._handle_request()

    def do_PATCH(self):
        self._handle_request()

    def do_DELETE(self):
        self._handle_request()

    def _handle_request(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith('/api/'):
            self._proxy_to_backend()
            return

        self._serve_static_file(parsed.path)

    def _proxy_to_backend(self):
        target = BACKEND_URL + self.path
        body = None
        content_length = self.headers.get('Content-Length')
        if content_length and int(content_length) > 0:
            body = self.rfile.read(int(content_length))

        req = urlrequest.Request(target, data=body, method=self.command)

        for header, value in self.headers.items():
            if header.lower() == 'host':
                continue
            if header.lower() == 'content-length' and body is None:
                continue
            req.add_header(header, value)

        try:
            with urlrequest.urlopen(req, timeout=30) as resp:
                status = resp.status
                headers = resp.headers
                self.send_response(status)
                for key, value in headers.items():
                    if key.lower() == 'transfer-encoding':
                        continue
                    if key.lower() == 'content-encoding':
                        continue
                    self.send_header(key, value)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                body_bytes = resp.read()
                self.wfile.write(body_bytes)
        except Exception as exc:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(f'{{"message":"Backend proxy error","error":"{exc}"}}'.encode('utf-8'))

    def _serve_static_file(self, request_path):
        raw_path = request_path or '/'
        if raw_path == '/':
            raw_path = '/rush.html'

        parsed = urlparse(raw_path)
        safe_path = (ROOT_DIR / parsed.path.lstrip('/')).resolve()
        try:
            if ROOT_DIR not in safe_path.parents and safe_path != ROOT_DIR:
                raise Exception('Forbidden path')
            if safe_path.is_dir():
                safe_path = safe_path / 'index.html'
            if not safe_path.exists():
                raise FileNotFoundError
        except Exception:
            self.send_error(403, 'Forbidden')
            return

        try:
            mime_type, _ = mimetypes.guess_type(str(safe_path))
            if mime_type is None:
                mime_type = 'application/octet-stream'

            with safe_path.open('rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(content)
        except Exception:
            self.send_error(404, 'Not Found')


if __name__ == '__main__':
    httpd = ThreadingHTTPServer(('0.0.0.0', PORT), ProxyHandler)
    print(f'Serving static frontend and proxying /api/* to {BACKEND_URL} on http://localhost:{PORT}')
    httpd.serve_forever()
=======
﻿import http.server
import socketserver
import urllib.request
import urllib.error
import os

PORT = 5501
BACKEND_URL = "http://localhost:8800"
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_ROOT, **kwargs)

    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def do_PUT(self):
        self.handle_request('PUT')

    def do_DELETE(self):
        self.handle_request('DELETE')

    def do_OPTIONS(self):
        self.handle_request('OPTIONS')

    def handle_request(self, method):
        if self.path.startswith('/api/'):
            self.proxy_request(method)
        else:
            if method == 'GET':
                super().do_GET()
            else:
                self.send_error(405, f"Method {method} not allowed on static files")

    def proxy_request(self, method):
        url = f"{BACKEND_URL}{self.path}"
        headers = {k: v for k, v in self.headers.items() if k.lower() != 'host'}
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                self.send_response(response.status)
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for key, value in e.headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            print(f"Proxy Error: {e}")
            self.send_error(500, f"Proxy Error: {e}")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        print(f"Proxy server running on http://localhost:{PORT}")
        httpd.serve_forever()
>>>>>>> d37caff37801a89c18f3383b9bf04a99eab2d446
