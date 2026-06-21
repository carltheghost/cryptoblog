"""Localhost web server for the kalshibot dashboard.

    python -m kalshibot.webui            # then open http://localhost:8765

Stdlib only. Serves the dashboard and a tiny JSON API backed by SimEngine.
No real-money trading happens anywhere in this UI.
"""

from __future__ import annotations

import argparse
import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .engine import SimEngine
from .swarm import SwarmEngine

HERE = os.path.dirname(__file__)
ENGINE = SimEngine()
SWARM = SwarmEngine()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # quiet

    def _send(self, code, body, ctype="application/json"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        elif self.path in ("/swarm", "/swarm.html"):
            with open(os.path.join(HERE, "swarm.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        elif self.path == "/api/state":
            self._send(200, json.dumps(ENGINE.snapshot()))
        elif self.path == "/api/swarm":
            self._send(200, json.dumps(SWARM.snapshot()))
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        if self.path not in ("/api/control", "/api/swarm/control"):
            self._send(404, json.dumps({"error": "not found"}))
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            payload = {}
        target = SWARM if self.path == "/api/swarm/control" else ENGINE
        cmd = payload.get("cmd")
        if cmd == "start":
            target.start()
        elif cmd == "pause":
            target.pause()
        elif cmd == "reset":
            target.reset()
        elif cmd == "set_params":
            target.set_params(**{k: v for k, v in payload.items() if k != "cmd"})
        self._send(200, json.dumps({"ok": True}))


def main():
    ap = argparse.ArgumentParser(description="kalshibot localhost dashboard (paper/sim only)")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-open", action="store_true", help="don't auto-open the browser")
    args = ap.parse_args()

    url = f"http://localhost:{args.port}"
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"kalshibot dashboard running at {url}  (Ctrl+C to stop)")
    print(f"  single-agent deck : {url}/")
    print(f"  swarm command ctr : {url}/swarm")
    print("This is a SIMULATION / paper UI. No real orders are placed.")
    if not args.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
