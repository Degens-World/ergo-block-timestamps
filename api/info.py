from http.server import BaseHTTPRequestHandler
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from api._utils import load_index


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        index = load_index()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(index, indent=2).encode())
