"""A saved partial progress file is not evidence of a currently running process."""
from grothendieck_rlvr import dashboard
from grothendieck_rlvr.io import atomic_json


def test_progress_distinguishes_terminal_results_without_claiming_a_process_is_live(tmp_path, monkeypatch):
    monkeypatch.setattr(dashboard, "root", lambda: tmp_path)
    folder = tmp_path / "calibration"
    for name, result_identity, passed in [("a-partial", None, False),
                                          ("b-failed", "b-failed", False),
                                          ("c-passed", "c-passed", True),
                                          ("d-stale", "other-identity", True)]:
        identity = {"judge": name, "cases": "fixture", "protocol": "fixture"}
        atomic_json(folder / f"{name}.progress.json", {"pairs_completed": 2})
        atomic_json(folder / f"{name}.lock.json", identity)
        if result_identity is not None:
            atomic_json(folder / f"{name}.json", {
                "identity": {**identity, "judge": result_identity}, "passed": passed, "complete": passed})
    rows = dashboard.calibration_progress()
    assert [row["status"] for row in rows] == ["partial", "failed", "passed", "partial"]
    assert [row["judge_identity"] for row in rows] == ["a-partial", "b-failed", "c-passed", "d-stale"]
    assert all(row["updated_at"].endswith("+00:00") for row in rows)
    assert all(row["pairs_completed"] == 2 for row in rows)
