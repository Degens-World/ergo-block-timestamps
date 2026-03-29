from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from api._utils import lookup_block

MAX_RANGE = 1000


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)

        try:
            from_h = int(params.get('from', [None])[0])
            to_h = int(params.get('to', [None])[0])
        except (TypeError, ValueError):
            self._json_response(400, {"error": "Required: ?from=N&to=M (integers)"})
            return

        if from_h < 1 or to_h < 1:
            self._json_response(400, {"error": "Heights must be positive"})
            return

        if from_h > to_h:
            self._json_response(400, {"error": "'from' must be <= 'to'"})
            return

        if to_h - from_h + 1 > MAX_RANGE:
            self._json_response(400, {"error": f"Range too large. Maximum {MAX_RANGE} blocks per request."})
            return

        blocks = []
        for h in range(from_h, to_h + 1):
            result = lookup_block(h)
            if result:
                blocks.append(result)

        self._json_response(200, {"blocks": blocks, "count": len(blocks)})

    def _json_response(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
