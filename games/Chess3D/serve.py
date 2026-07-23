"""Serve Wizard's Chess 3D on localhost. Run:  python serve.py
Then open http://localhost:8802  (needs to be served, not file://, for three.min.js)."""
import os, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
os.chdir(os.path.dirname(os.path.abspath(__file__)))
class H(SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_GET(self):
        if self.path=="/" : self.path="/Chess3D.html"
        return super().do_GET()
if __name__=="__main__":
    url="http://localhost:8802";print("Wizard's Chess 3D at",url,"(Ctrl+C to quit)")
    try: webbrowser.open(url)
    except Exception: pass
    ThreadingHTTPServer(("127.0.0.1",8802),H).serve_forever()
