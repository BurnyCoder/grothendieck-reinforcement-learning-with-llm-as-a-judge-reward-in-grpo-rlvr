"""Loopback dashboard serving the same static explorer used by GitHub Pages."""
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from .io import PROJECT, read_json, read_jsonl, root


def serve_dashboard(port=8765):
    """Read compact training metrics without exposing logs, credentials or the rest of disk."""
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(PROJECT / "site"), **kwargs)

        def do_GET(self):
            if self.path == "/api/live":
                snapshot = read_json(PROJECT / "site/snapshot.json")
                snapshot["training"] = {p.parent.name: read_jsonl(p)
                                        for p in (root() / "runs").glob("*/metrics.jsonl")}
                payload = json.dumps(snapshot).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            super().do_GET()
    print(f"Live dashboard: http://127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
