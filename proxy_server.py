import http.server
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
