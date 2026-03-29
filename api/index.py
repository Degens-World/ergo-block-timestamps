from http.server import BaseHTTPRequestHandler
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from api._utils import load_index

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ergo Block Timestamps API</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 720px; margin: 40px auto; padding: 0 20px; color: #e0e0e0; background: #1a1a2e; line-height: 1.6; }
  h1 { color: #fff; }
  h2 { color: #ccc; margin-top: 2em; }
  a { color: #6db3f2; }
  code { background: #16213e; padding: 2px 6px; border-radius: 3px; font-size: 0.95em; }
  pre { background: #16213e; padding: 16px; border-radius: 6px; overflow-x: auto; border: 1px solid #2a2a4a; }
  .endpoint { margin: 1em 0; }
  .method { color: #4ecca3; font-weight: bold; }
  .stats { background: #16213e; padding: 16px; border-radius: 6px; border: 1px solid #2a2a4a; margin: 1em 0; }
  .stats span { color: #4ecca3; font-weight: bold; }
  hr { border: none; border-top: 1px solid #2a2a4a; margin: 2em 0; }
  footer { color: #666; font-size: 0.85em; margin-top: 3em; }
</style>
</head>
<body>
<h1>Ergo Block Timestamps API</h1>
<p>Free, public API for looking up Ergo blockchain block heights to timestamps. Updated hourly.</p>

<div class="stats">
  <strong>Dataset:</strong> <span>{total_blocks:,}</span> blocks &mdash; heights {first_height:,} to <span>{latest_height:,}</span>
</div>

<h2>Endpoints</h2>

<div class="endpoint">
<p><span class="method">GET</span> <code>/api/block/:height</code></p>
<p>Look up a single block by height.</p>
<pre>curl {base_url}/api/block/1752521

{{
  "height": 1752521,
  "timestamp_ms": 1774800957664,
  "datetime": "2026-03-29T16:15:57.664000"
}}</pre>
</div>

<div class="endpoint">
<p><span class="method">GET</span> <code>/api/blocks?from=X&amp;to=Y</code></p>
<p>Look up a range of blocks. Maximum 1,000 per request.</p>
<pre>curl {base_url}/api/blocks?from=1752000&amp;to=1752010

{{
  "blocks": [
    {{"height": 1752000, "timestamp_ms": ..., "datetime": "..."}},
    ...
  ],
  "count": 11
}}</pre>
</div>

<div class="endpoint">
<p><span class="method">GET</span> <code>/api/info</code></p>
<p>Get dataset metadata: latest height, total blocks, year boundaries.</p>
<pre>curl {base_url}/api/info</pre>
</div>

<hr>

<h2>CORS</h2>
<p>All endpoints return <code>Access-Control-Allow-Origin: *</code> &mdash; call directly from any frontend.</p>

<h2>Source</h2>
<p>Data and code: <a href="https://github.com/Degens-World/ergo-block-timestamps">github.com/Degens-World/ergo-block-timestamps</a></p>

<footer>
  <p>A <a href="https://degens.world">degens.world</a> community tool for the Ergo ecosystem.</p>
</footer>
</body>
</html>"""


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        index = load_index()
        host = self.headers.get('host', 'ergo-block-timestamps.vercel.app')
        base_url = f"https://{host}"
        page = HTML.format(
            total_blocks=index['total_blocks'],
            first_height=index['first_height'],
            latest_height=index['latest_height'],
            base_url=base_url,
        )
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(page.encode())
