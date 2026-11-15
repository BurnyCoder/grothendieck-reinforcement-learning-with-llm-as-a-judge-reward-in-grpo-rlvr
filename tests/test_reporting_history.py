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


def test_request_latency_keeps_unfinished_calls_separate_from_observed_times():
    """An interrupted request has no measured completion time; do not impute zero."""
    records = [{"artifact": "reports/development/fixture.jsonl", "requests": 3,
                "completed_responses": 2, "incomplete_requests": 1,
                "response_seconds": [10.0, 30.0], "assessments": [{}], "judge_failures": 1},
               {"artifact": "reports/development/no-response.jsonl", "requests": 1,
                "completed_responses": 0, "incomplete_requests": 1,
                "response_seconds": [], "assessments": [], "judge_failures": 0}]
    rows = reporting.request_latency_rows(records)
    assert rows[1][1:] == ["2", "1", "1", "1", "20.00", "10.00–30.00"]
    assert rows[2][1:] == ["0", "0", "0", "1", "Pending", "Pending"]


def test_indexed_passages_are_reconstructed_in_published_examples(tmp_path, monkeypatch):
    """The explorer must show the original text rather than a serialized passage map."""
    monkeypatch.setattr(reporting, "PROJECT", tmp_path)
    folder = tmp_path / "reports/development"
    folder.mkdir(parents=True)
    payload = {"candidate_response": {"C0": "First\n", "C1": "Second"},
               "conventional_reference": {"R0": "Reference"}}
    events = [{"kind": "model_request", "request": {"messages": [{"content": json.dumps(payload)}]}},
              {"kind": "judge_assessment", "task_id": "fixture"}]
    (folder / "fixture.jsonl").write_text(''.join(json.dumps(e)+'\n' for e in events))
    example = reporting.development_records()[0]["assessments"][0]
    assert example["candidate_response"] == "First\nSecond"
    assert example["conventional_reference"] == "Reference"


def test_withheld_novelty_report_uses_stored_credit_without_rescoring_history():
    """Old records without credit metadata must not acquire a v6 gate retrospectively."""
    result = {"ordering": [{"id": "old-case"}, {"id": "new-case",
                "preferred_novelty_credit": {"raw_score": 3, "effective_score": 3, "withheld": False},
                "dispreferred_novelty_credit": {"raw_score": 1, "effective_score": 0,
                    "withheld": True, "gate_reasons": ["within_reference"]}}], "suppression": []}
    rows = reporting.withheld_novelty_rows(result)
    assert len(rows) == 2
    assert rows[1] == ["new-case", "dispreferred", "1", "0", "within_reference"]


def test_ranking_success_is_not_reported_as_a_pass_of_the_novelty_contract():
    """Correct ranks can coexist with both overcrediting and withholding a brief link."""
    result = {"ordering": [
        {"stratum": "novelty", "preferred": .8, "dispreferred": .6,
         "preferred_novelty": .75, "dispreferred_novelty": .25,
         "expected_control_novelty": "none", "passed": False},
        {"stratum": "novelty", "preferred": .8, "dispreferred": .6,
         "preferred_novelty": .75, "dispreferred_novelty": 0,
         "expected_control_novelty": "modest", "passed": False},
        {"stratum": "novelty", "preferred": .8, "dispreferred": .6,
         "preferred_novelty": .75, "dispreferred_novelty": .25, "passed": False},
    ]}
    rows = reporting.calibration_component_rows(result)
    assert [row[1:3] for row in rows[1:]] == [["3", "3"], ["3", "3"], ["0", "2"], ["0", "3"]]
    assert result["ordering"][2].get("expected_control_novelty") is None


def test_stage_report_preserves_objections_despite_a_supported_verdict(tmp_path, monkeypatch):
    """Expose conflicting declarations without overruling or relabeling them as facts."""
    monkeypatch.setattr(reporting, "PROJECT", tmp_path)
    folder = tmp_path / "reports/development"
    folder.mkdir(parents=True)
    issue = {"evidence": ["Fixture excerpt"], "rationale": "Fixture objection", "severity": "unsupported"}
    findings = [
        {"protocol": "two-stage-v1", "stage": "quality", "seconds": 12.0,
         "finding": {"validity": {"verdict": "supported", "issues": [issue]}, "criteria": {}}},
        {"protocol": "specialists-v1", "stage": "validity", "seconds": 8.0,
         "finding": {"verdict": "supported", "issues": []}},
        {"protocol": "specialists-v1", "stage": "validity", "seconds": 10.0,
         "finding": {"verdict": "contradicted", "issues": [issue, issue]}},
    ]
    events = [{"kind": "judge_stage_assessment", **finding} for finding in findings]
    (folder / "fixture.jsonl").write_text(''.join(json.dumps(event)+'\n' for event in events))
    records = reporting.development_records()
    assert records[0]["stages"][0]["finding"] == findings[0]["finding"]
    rows = reporting.stage_latency_rows(records)
    assert rows[1][1:] == ["two-stage-v1", "quality", "1", "1", "1", "1", "12.00"]
    assert rows[2][1:] == ["specialists-v1", "validity", "2", "1", "2", "0", "9.00"]


def test_exploratory_results_never_fill_the_qualified_comparison(tmp_path, monkeypatch):
    """Name isolation must survive the actual artifact-reading report entry point."""
    from grothendieck_rlvr.experiments import EXPLORATORY_PREFIX
    monkeypatch.setattr(reporting, "root", lambda: tmp_path)
    monkeypatch.setattr(reporting, "calibration_records", lambda: [])
    monkeypatch.setattr(reporting, "development_records", lambda: [])
    monkeypatch.setattr(reporting, "training_budget", lambda *a: {})
    for arm, value in [("theory", .8), ("correctness", .4)]:
        folder = tmp_path / "evaluations" / (EXPLORATORY_PREFIX + arm + "-seed42")
        folder.mkdir(parents=True)
        row = {"task_id": "fixture", "family": "gcd", "split": "test_fresh", "correct": True,
               "metric": value, "theory": value, "response_tokens": 10,
               "verification": {"status": "correct"}, "judge_identity": "same-fixture"}
        (folder / "scores.jsonl").write_text(json.dumps(row)+'\n')
    snapshot = reporting.collect()
    assert snapshot["primary"]["status"] == "pending"
    assert snapshot["exploratory_single"]["primary"]["status"] == "exploratory_uncalibrated"
    rows = reporting.table_rows(snapshot)
    standard = next(row for row in rows if row[0] == "theory-seed42")
    assert standard[1:] == ["Pending"] * 4
