"""Serve Wizard's Chess: Spellbound on localhost. Run:  python serve.py
Then open http://localhost:8801  (or just double-click Spellbound.html)."""
import os, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
HERE=os.path.dirname(os.path.abspath(__file__))
class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_GET(self):
        try:
            data=open(os.path.join(HERE,"Spellbound.html"),"rb").read()
            self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length",str(len(data)));self.end_headers();self.wfile.write(data)
        except OSError: self.send_error(404)
if __name__=="__main__":
    url="http://localhost:8801";print("Spellbound at",url,"(Ctrl+C to quit)")
    try: webbrowser.open(url)
    except Exception: pass
    ThreadingHTTPServer(("127.0.0.1",8801),H).serve_forever()
