from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
_cache = None


def load_days():
    global _cache
    if _cache is None:
        with open(os.path.join(DATA_DIR, 'days.json')) as f:
            _cache = json.load(f)
    return _cache


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        days = load_days()

        date = params.get('date', [None])[0]
        year = params.get('year', [None])[0]
        month = params.get('month', [None])[0]

        results = days

        if date:
            results = [d for d in results if d['date'] == date]
        else:
            if year:
                try:
                    y = int(year)
                    results = [d for d in results if d['year'] == y]
                except ValueError:
                    self._json_response(400, {"error": "Invalid year"})
                    return
            if month:
                try:
                    m = int(month)
                    results = [d for d in results if d['month'] == m]
                except ValueError:
                    self._json_response(400, {"error": "Invalid month"})
                    return

        self._json_response(200, {"days": results, "count": len(results)})

    def _json_response(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
