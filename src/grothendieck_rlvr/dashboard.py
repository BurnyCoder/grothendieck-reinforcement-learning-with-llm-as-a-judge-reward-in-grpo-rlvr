"""Loopback dashboard serving the same static explorer used by GitHub Pages."""
import json
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from .io import PROJECT, read_json, read_jsonl, root


def calibration_progress() -> list[dict]:
    """Label persisted progress from matching results, without inferring process liveness."""
    records = []
    for path in sorted((root() / "calibration").glob("*.progress.json")):
        stem = path.name.removesuffix(".progress.json")
        lock_path, result_path = (path.with_name(stem + suffix) for suffix in (".lock.json", ".json"))
        identity = read_json(lock_path) if lock_path.exists() else {}
        result = read_json(result_path) if result_path.exists() else {}
        status = "partial"
        if identity and result.get("identity") == identity:
            status = "passed" if result.get("passed") and result.get("complete") else "failed"
        records.append({**read_json(path), "judge_identity": identity.get("judge"), "status": status,
                        "updated_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()})
    return records


def judge_progress() -> list[dict]:
    """Expose only compact stage records; a last event is not a process heartbeat."""
    paths = list((root() / "logs").glob("*.judge-progress.json"))
    paths += list((root() / "runs").glob("*/*.judge-progress.json"))
    return [read_json(path) for path in sorted(paths)]


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
                snapshot["calibration_progress"] = calibration_progress()
                snapshot["judge_progress"] = judge_progress()
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
