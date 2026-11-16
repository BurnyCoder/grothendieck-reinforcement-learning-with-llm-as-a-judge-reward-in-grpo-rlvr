"""Persistent append streams retain complete, immediately readable recovery evidence."""
import json
import pickle
from pathlib import Path

from grothendieck_rlvr.io import EventLog


def test_logger_reuses_handles_flushes_complete_events_and_reopens_after_close(tmp_path, monkeypatch, capsys):
    original = Path.open
    opens = []
    def counted(path, *args, **kwargs):
        if args and args[0] == "a":
            opens.append(path)
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "open", counted)
    path = tmp_path / "events.jsonl"
    log = EventLog(path)
    first = log.emit("model_chunk", delta={"content": "π\nλ"})
    second = log.emit("model_chunk", delta={"content": "complete " * 1000})
    assert [json.loads(line) for line in path.read_text().splitlines()] == [first, second]
    assert opens == [path]
    assert [json.loads(line) for line in capsys.readouterr().out.splitlines()] == [first, second]
    log.close()
    third = log.emit("training_metrics", step=1, metrics={"loss": .1})
    assert opens == [path, path, path.with_name("metrics.jsonl")]
    assert json.loads(path.with_name("metrics.jsonl").read_text()) == third
    copied = pickle.loads(pickle.dumps(log))
    copied.emit("model_chunk", delta={"content": "after serialization"})
    assert len(path.read_text().splitlines()) == 4
    copied.close()
    log.close()
