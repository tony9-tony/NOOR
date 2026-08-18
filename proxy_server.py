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
