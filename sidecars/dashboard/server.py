#!/usr/bin/env python3
import os
import sys
import json
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Unbuffered stdout/stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(line_buffering=True)

# Add parent scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
plugin_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, os.path.join(plugin_root, "scripts"))

from get_tokens import get_all_conversations, get_conversation, get_conversation_details

# Cache for /api/stats
_STATS_CACHE = {"timestamp": 0, "data": None}
CACHE_TTL = 3.0  # seconds

def get_cached_all_conversations():
    now = time.time()
    if _STATS_CACHE["data"] is not None and (now - _STATS_CACHE["timestamp"]) < CACHE_TTL:
        return _STATS_CACHE["data"]
    data = get_all_conversations()
    _STATS_CACHE["data"] = data
    _STATS_CACHE["timestamp"] = now
    return data

class TokenTrackerHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/details":
            cid = query.get("cid", [None])[0]
            if not cid:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing cid parameter"}).encode())
                return
            data = get_conversation_details(cid)
            if not data:
                self.send_response(404)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Conversation not found"}).encode())
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            return

        if path == "/api/stats":
            cid = query.get("cid", [None])[0]
            if cid:
                data = get_conversation(cid)
                if not data:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Conversation not found"}).encode())
                    return
            else:
                data = get_cached_all_conversations()

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            return

        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        # Default fallback: serve index.html
        html_path = os.path.join(script_dir, "index.html")
        if os.path.exists(html_path):
            with open(html_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        pass

def main():
    port_str = os.environ.get("ANTIGRAVITY_SIDECAR_WEB_PORT") or os.environ.get("PORT") or "61994"
    port = int(port_str)
    
    server = HTTPServer(("0.0.0.0", port), TokenTrackerHandler)
    print(f"Token Tracker UI listening on 0.0.0.0:{port} (ANTIGRAVITY_SIDECAR_WEB_PORT={os.environ.get('ANTIGRAVITY_SIDECAR_WEB_PORT')})", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
