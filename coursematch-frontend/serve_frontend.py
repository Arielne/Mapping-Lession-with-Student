from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent / "dist"
HOST = "127.0.0.1"
PORT = 5173


class SpaHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        requested = ROOT / self.path.lstrip("/")
        if self.path != "/" and not requested.exists():
            self.path = "/index.html"
        super().do_GET()


if __name__ == "__main__":
    if not ROOT.exists():
        raise SystemExit("dist chua ton tai. Hay chay npm.cmd run build truoc.")

    os.chdir(ROOT)
    server = ThreadingHTTPServer((HOST, PORT), SpaHandler)
    print(f"CourseMatch frontend running at http://{HOST}:{PORT}")
    server.serve_forever()
