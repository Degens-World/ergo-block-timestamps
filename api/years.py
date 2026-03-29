from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
_cache = None


def load_years():
    global _cache
    if _cache is None:
        with open(os.path.join(DATA_DIR, 'years.json')) as f:
            _cache = json.load(f)
    return _cache


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        years = load_years()

        year = params.get('year', [None])[0]
        if year:
            try:
                y = int(year)
                years = [yr for yr in years if yr['year'] == y]
            except ValueError:
                self._json_response(400, {"error": "Invalid year"})
                return

        self._json_response(200, {"years": years, "count": len(years)})

    def _json_response(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
