"""Atomic artifacts and complete timestamped JSONL logs shared by every phase."""
import hashlib
import json
import os
import weakref
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

PROJECT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT / ".env")


def root() -> Path:
    """Large mutable artifacts live outside the source checkout, on the data drive."""
    result = Path(os.environ.get("GROTH_ROOT", PROJECT / "runs"))
    result.mkdir(parents=True, exist_ok=True)
    return result


def digest(value) -> str:
    """Stable content identity for configs, prompts, caches and task instances."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def atomic_json(path: Path, value) -> None:
    """Flush and atomically replace a small state file at a safe checkpoint boundary."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def read_json(path: Path):
    """Read a trusted configuration/artifact with an explicit encoding."""
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    """Read completed records; torn final log writes are errors, never silently lost data."""
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class EventLog:
    """Write the same full event to durable disk and untruncated stdout; never log env."""
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._handles = {}
        # Keep append handles open: reopening each streamed token is costly on WSL/NTFS.
        # Every event still flushes. Finalizers close streams on collection/process exit.
        # https://docs.python.org/3.12/library/weakref.html#finalizer-objects
        self._closers = []

    def _append(self, path: Path, line: str) -> None:
        """Append and flush one complete record; I/O failures propagate to the caller."""
        if path not in self._handles:
            handle = path.open("a", encoding="utf-8")
            self._handles[path] = handle
            self._closers.append(weakref.finalize(self, handle.close))
        self._handles[path].write(line + "\n")
        self._handles[path].flush()

    def close(self) -> None:
        """Release handles explicitly; subsequent events may reopen them in append mode."""
        for closer in self._closers:
            closer()
        self._handles.clear()
        self._closers.clear()

    def __getstate__(self):
        """A serialized reward callback must never carry live file descriptors."""
        return {"path": self.path}

    def __setstate__(self, state):
        self.__init__(state["path"])

    def emit(self, kind: str, **fields) -> dict:
        """Log prompts/responses as data, without recording authorization headers."""
        event = {"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **fields}
        line = json.dumps(event, ensure_ascii=False, allow_nan=False)
        self._append(self.path, line)
        if self.path.name == "events.jsonl" and kind in {
            "training_metrics", "reward_batch", "checkpoint", "judge_failure", "training_finished"}:
            self._append(self.path.with_name("metrics.jsonl"), line)
        print(line, flush=True)
        return event
