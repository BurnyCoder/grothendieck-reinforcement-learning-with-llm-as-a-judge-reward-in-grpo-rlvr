"""Archived negative calibration evidence must survive new runs and clean clones."""
import json

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


def test_development_examples_keep_the_candidate_bound_to_its_accepted_judgment(tmp_path, monkeypatch):
    """Retries retain the candidate; later unpaired records cannot inherit earlier text."""
    monkeypatch.setattr(reporting, "PROJECT", tmp_path)
    folder = tmp_path / "reports/development"
    folder.mkdir(parents=True)
    def request(candidate):
        return {"kind": "model_request", "request": {"messages": [{"role": "user", "content": json.dumps({
            "problem": "Fixture problem", "conventional_reference": "Fixture reference",
            "candidate_response": candidate})}]}}
    events = [request("First candidate"), {"kind": "judge_failure"}, request("First candidate"),
              {"kind": "judge_assessment", "task_id": "first"}, request("Second candidate"),
              {"kind": "judge_assessment", "task_id": "second"},
              {"kind": "judge_assessment", "task_id": "unpaired"}]
    (folder / "fixture.jsonl").write_text(''.join(json.dumps(event)+'\n' for event in events))
    rows = reporting.development_records()[0]["assessments"]
    assert [row.get("candidate_response") for row in rows] == ["First candidate", "Second candidate", None]
    assert rows[0]["problem"] == "Fixture problem"
    assert rows[0]["conventional_reference"] == "Fixture reference"
