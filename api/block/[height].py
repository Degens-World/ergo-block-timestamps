from http.server import BaseHTTPRequestHandler
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from api._utils import lookup_block


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            height_str = self.path.split('/')[-1].split('?')[0]
            height = int(height_str)
            if height < 1:
                raise ValueError
        except (ValueError, IndexError):
            self._json_response(400, {"error": "Invalid height parameter"})
            return

        result = lookup_block(height)
        if result is None:
            self._json_response(404, {"error": f"Block {height} not found"})
            return

        self._json_response(200, result)

    def _json_response(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
