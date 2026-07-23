"""Serve Wizard's Chess on localhost. Run:  python serve.py
Then play at http://localhost:8800  (or just open WizardsChess.html directly).
Pure Python standard library — no installs needed."""
import os, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
HERE = os.path.dirname(os.path.abspath(__file__))
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        try:
            with open(os.path.join(HERE, "WizardsChess.html"), "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers(); self.wfile.write(data)
        except OSError:
            self.send_error(404)
if __name__ == "__main__":
    url = "http://localhost:8800"
    print("Wizard's Chess at", url, " (Ctrl+C to quit)")
    try: webbrowser.open(url)
    except Exception: pass
    ThreadingHTTPServer(("127.0.0.1", 8800), H).serve_forever()
