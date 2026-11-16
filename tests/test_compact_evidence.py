"""A bounded wire format must preserve credit and reject errors without repairing scores."""
import json

import pytest

from grothendieck_rlvr import compact_evidence, evidence
from grothendieck_rlvr.judge import Judge, JudgeFailure, assessment_schema
from grothendieck_rlvr.prompts import judge_system
from grothendieck_rlvr.schema import Assessment, Task


def fixture():
    """A concrete connection can receive modest credit without a further use."""
    return {"theory_validity": "supported", "novelty_comparison": {
        "reference_excerpt": "R0", "addition_evidence": ["C1"], "use_evidence": [],
        "relation": "beyond_reference"}, "criteria": {
            k: {"evidence": ["C1"], "rationale": "A valid connection.", "score": 1}
            for k in Assessment.weights}, "problems": []}


def test_compact_format_preserves_modest_and_developed_credit_and_validity_gate():
    candidate, reference = evidence.catalog("Method\nConnection", "C"), evidence.catalog("Reference", "R")
    raw = fixture()
    for validity in ("supported", "unsupported", "contradicted"):
        raw["theory_validity"] = validity
        assert compact_evidence.materialize(json.dumps(raw), candidate, reference) == \
            evidence.materialize(json.dumps(raw), candidate, reference)
    raw["theory_validity"] = "supported"
    assert compact_evidence.materialize(json.dumps(raw), candidate, reference).novelty == .25
    raw["criteria"]["constructive_novelty"]["score"] = 4
    raw["novelty_comparison"]["use_evidence"] = ["C1"]
    assert compact_evidence.materialize(json.dumps(raw), candidate, reference).novelty == 1


@pytest.mark.parametrize("invalid", ["rationale", "evidence_count", "problem_count", "problem_length", "pointer"])
def test_bounds_fail_explicitly_without_truncating_or_changing_opinions(invalid):
    raw = fixture()
    if invalid == "rationale":
        raw["criteria"]["constructive_novelty"]["rationale"] = "x" * 241
    if invalid == "evidence_count":
        raw["novelty_comparison"]["addition_evidence"] = ["C1"] * 4
    if invalid == "problem_count":
        raw["problems"] = ["Objection"] * 9
    if invalid == "problem_length":
        raw["problems"] = ["x" * 161]
    if invalid == "pointer":
        raw["criteria"]["constructive_novelty"]["evidence"] = ["C999"]
    with pytest.raises(ValueError):
        compact_evidence.materialize(json.dumps(raw), {"C0": "Method", "C1": "Connection"}, {"R0": "Reference"})


def test_wire_schema_and_prompt_constrain_format_without_changing_rubric():
    schema = compact_evidence.indexed_schema(assessment_schema(), {"C0": "Math"}, {"R0": "Reference"})
    criterion = schema["$defs"]["Criterion"]["properties"]
    assert criterion["rationale"]["maxLength"] == 240
    assert criterion["evidence"]["maxItems"] == 3
    assert schema["properties"]["problems"]["maxItems"] == 8
    for variant in ("quoted", "rubric"):
        original = judge_system(variant, "v7")
        compact = compact_evidence.indexed_system(original)
        assert compact.split("Return only JSON")[0] == original.split("Return only JSON")[0]
        assert ("I can illustrate the second approach" in compact) == (variant == "quoted")


def test_new_identity_retries_failures_but_does_not_reuse_legacy_cache(tmp_path, monkeypatch):
    legacy = Judge("http://127.0.0.1:8081", cache=tmp_path / "cache.sqlite", protocol="single-indexed-v1")
    compact = Judge("http://127.0.0.1:8081", cache=tmp_path / "cache.sqlite", protocol="single-compact-v1")
    assert legacy.identity != compact.identity
    task = Task(id="fixture", problem="Fixture", answer="1", family="gcd", split="dev", provenance={})
    calls = []
    def valid(*args):
        calls.append(args)
        return json.dumps(fixture())
    monkeypatch.setattr(legacy.client, "generate", valid)
    legacy.assess(task, "Method\nConnection")
    monkeypatch.setattr(compact.client, "generate", valid)
    assert compact.assess(task, "Method\nConnection").novelty == .25
    compact.assess(task, "Method\nConnection")
    assert len(calls) == 2
    bad = fixture()
    bad["criteria"]["constructive_novelty"]["rationale"] = "x" * 241
    def invalid(*args):
        calls.append(args)
        return json.dumps(bad)
    monkeypatch.setattr(compact.client, "generate", invalid)
    with pytest.raises(JudgeFailure, match="three attempts"):
        compact.assess(task.model_copy(update={"id": "invalid"}), "Method\nConnection")
    assert len(calls) == 5
