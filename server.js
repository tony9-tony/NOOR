const http = require('http');
const fs = require('fs');
const path = require('path');

const FRONTEND_PORT = 5500;
const BACKEND_URL = 'http://localhost:8800';
const rootDir = __dirname;

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
  '.txt': 'text/plain; charset=utf-8'
};

function sendJson(res, statusCode, data) {
  const body = JSON.stringify(data);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
  });
  res.end(body);
}

function safeResolve(base, filePath) {
  const resolved = path.resolve(base, filePath);
  const relative = path.relative(base, resolved);
  if (relative.startsWith('..') || path.isAbsolute(relative)) {
    return null;
  }
  return resolved;
}

function serveStaticFile(res, requestedPath) {
  let normalizedPath = requestedPath === '/' ? '/rush.html' : requestedPath;
  normalizedPath = normalizedPath.split('?')[0];
  const safePath = safeResolve(rootDir, '.' + normalizedPath);

  if (!safePath) {
    res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Forbidden');
    return;
  }

  fs.readFile(safePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not Found');
      return;
    }

    const ext = path.extname(safePath).toLowerCase();
    res.writeHead(200, {
      'Content-Type': MIME_TYPES[ext] || 'application/octet-stream',
      'Cache-Control': 'no-store'
    });
    res.end(data);
  });
}

function forwardRequest(req, res) {
  const u = new URL(req.url, BACKEND_URL);
  const targetUrl = `${BACKEND_URL}${u.pathname}${u.search || ''}`;

  const headers = { ...req.headers };
  delete headers.host;

  const proxyReq = http.request(targetUrl, {
    method: req.method,
    headers
  }, (proxyRes) => {
    const statusCode = proxyRes.statusCode || 500;
    const responseHeaders = { ...proxyRes.headers };
    responseHeaders['Access-Control-Allow-Origin'] = '*';
    responseHeaders['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS';
    responseHeaders['Access-Control-Allow-Headers'] = 'Content-Type, Authorization';
    responseHeaders['Cache-Control'] = 'no-store';

    res.writeHead(statusCode, responseHeaders);
    proxyRes.pipe(res);
  });

  proxyReq.on('error', (error) => {
    console.error('Proxy error:', error.message);
    sendJson(res, 502, { message: 'Backend proxy error', error: error.message });
  });

  req.pipe(proxyReq);
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');

  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    });
    res.end();
    return;
  }

  if (url.pathname.startsWith('/api/')) {
    forwardRequest(req, res);
    return;
  }

  serveStaticFile(res, url.pathname);
});

server.listen(FRONTEND_PORT, () => {
  console.log(`Static frontend + API proxy running on http://localhost:${FRONTEND_PORT}`);
  console.log(`API requests are proxied to ${BACKEND_URL}`);
});
