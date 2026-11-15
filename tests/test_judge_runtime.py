"""Runtime changes invalidate calibration; serving cannot silently override the lock."""
import pytest

from grothendieck_rlvr import models
from grothendieck_rlvr.io import EventLog, atomic_json, read_json
from grothendieck_rlvr.judge import Judge


def test_runtime_changes_judge_identity(tmp_path, monkeypatch):
    """A cache/audit identity must distinguish CPU and partial GPU evaluation."""
    judge = Judge("http://127.0.0.1:8082", "evaluation_judge",
                  log=EventLog(tmp_path / "events.jsonl"), cache=tmp_path / "cache.sqlite")
    original = models.judge_runtime
    monkeypatch.setattr(models, "judge_runtime", lambda role: {**original(role), "gpu_layers": 0})
    changed = Judge("http://127.0.0.1:8082", "evaluation_judge",
                    log=EventLog(tmp_path / "changed.jsonl"), cache=tmp_path / "cache.sqlite")
    assert judge.identity != changed.identity


def test_training_judge_cannot_offload_and_unregistered_override_is_rejected(monkeypatch):
    """Reject configuration drift before opening either weights or a server."""
    monkeypatch.setattr(models.subprocess, "run", lambda *a, **k: pytest.fail("Must reject before launch"))
    with pytest.raises(ValueError, match="CPU"):
        models.serve("training_judge", gpu_layers=1)
    with pytest.raises(ValueError, match="registered"):
        models.serve("evaluation_judge", gpu_layers=2)


def test_runtime_receipt_prevents_unregistered_requests(tmp_path, monkeypatch):
    """An old/manual launch cannot be treated as the newly calibrated runtime."""
    from grothendieck_rlvr import judge as module
    monkeypatch.setattr(module, "root", lambda: tmp_path)
    client = module.LocalChat("http://127.0.0.1:8082", "evaluation_judge",
                              EventLog(tmp_path / "log.jsonl"), runtime={"backend": "cuda12.8"})
    with pytest.raises(module.JudgeFailure, match="runtime differs"):
        client.generate([])


def test_only_development_lock_can_be_archived(tmp_path, monkeypatch):
    """Keep previous evidence and preserve the prohibition on audit resets."""
    from grothendieck_rlvr import calibration
    monkeypatch.setattr(calibration, "root", lambda: tmp_path)
    judge = Judge("http://127.0.0.1:8082", "evaluation_judge",
                  log=EventLog(tmp_path / "events.jsonl"), cache=tmp_path / "cache.sqlite")
    lock = tmp_path / "calibration/evaluation_judge-quoted-dev.lock.json"
    atomic_json(lock, {"judge": "previous", "cases": "previous"})
    monkeypatch.setattr(calibration, "verify_answer", lambda *a: type("Verdict", (), {"correct": True})())
    def stop_before_judgment(*args):
        raise RuntimeError("fixture stop before inference")
    monkeypatch.setattr(judge, "assess", stop_before_judgment)
    with pytest.raises(RuntimeError, match="fixture stop"):
        calibration.calibrate(judge, "dev", restart_development=True)
    assert read_json(lock)["judge"] == judge.identity
    archived = list((tmp_path / "calibration/history").glob("*/*.json"))
    assert len(archived) == 1 and read_json(archived[0])["judge"] == "previous"
    with pytest.raises(ValueError, match="audits remain immutable"):
        calibration.calibrate(judge, "audit", restart_development=True)
