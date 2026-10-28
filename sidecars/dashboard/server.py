#!/usr/bin/env python3
import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add parent scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
plugin_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, os.path.join(plugin_root, "scripts"))

from get_tokens import get_all_conversations, get_conversation

class TokenTrackerHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

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
                data = get_all_conversations()

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            return

        # Serve index.html
        if path == "/" or path == "/index.html":
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
        # Silence standard HTTP access logging to keep stdout clean
        pass

def main():
    port = int(os.environ.get("PORT", 61994))
    server = HTTPServer(("127.0.0.1", port), TokenTrackerHandler)
    print(f"Token Tracker UI running at http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
