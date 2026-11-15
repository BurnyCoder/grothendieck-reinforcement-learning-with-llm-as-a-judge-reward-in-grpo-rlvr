"""Archived negative calibration evidence must survive new runs and clean clones."""
from grothendieck_rlvr import reporting
from grothendieck_rlvr.io import atomic_json


def test_calibration_history_is_retained_without_duplicate_snapshots(tmp_path, monkeypatch):
    """One failed result can exist in the publication snapshot and local archive."""
    project, runtime = tmp_path / "project", tmp_path / "runtime"
    monkeypatch.setattr(reporting, "PROJECT", project)
    monkeypatch.setattr(reporting, "root", lambda: runtime)
    failed = {"passed": False, "identity": "old-fixture"}
    current = {"passed": True, "identity": "new-fixture"}
    atomic_json(project / "reports/development/calibration-failed.json", failed)
    atomic_json(runtime / "calibration/history/old/judge-dev.json", failed)
    atomic_json(runtime / "calibration/current-dev.json", current)
    atomic_json(runtime / "calibration/current-dev.lock.json", {"identity": "lock-only"})
    atomic_json(runtime / "calibration/current-dev.progress.json", {"observed": 1})
    assert reporting.calibration_records() == [failed, current]
    # A clone without the artifact drive must still report the published failure.
    monkeypatch.setattr(reporting, "root", lambda: tmp_path / "absent-runtime")
    assert reporting.calibration_records() == [failed]
