"""Serve Wizard's Chess on localhost and open it.

    python games/play_chess.py        # then play at http://localhost:8800

Pure stdlib. The game is entirely client-side; this just serves the file.
"""
from __future__ import annotations
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        path = "wizardchess.html"
        try:
            with open(os.path.join(HERE, path), "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except OSError:
            self.send_error(404)


def main(port: int = 8800):
    url = f"http://localhost:{port}"
    print(f"Wizard's Chess running at {url}  (Ctrl+C to quit)")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()


if __name__ == "__main__":
    main()
