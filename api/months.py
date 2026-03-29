from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
_cache = None


def load_months():
    global _cache
    if _cache is None:
        with open(os.path.join(DATA_DIR, 'months.json')) as f:
            _cache = json.load(f)
    return _cache


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        months = load_months()

        year = params.get('year', [None])[0]
        month = params.get('month', [None])[0]

        results = months
        if year:
            try:
                y = int(year)
                results = [m for m in results if m['year'] == y]
            except ValueError:
                self._json_response(400, {"error": "Invalid year"})
                return

        if month:
            try:
                mn = int(month)
                results = [m for m in results if m['month'] == mn]
            except ValueError:
                self._json_response(400, {"error": "Invalid month"})
                return

        self._json_response(200, {"months": results, "count": len(results)})

    def _json_response(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
