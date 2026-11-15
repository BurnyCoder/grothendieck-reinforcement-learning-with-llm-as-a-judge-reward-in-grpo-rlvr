"""Source pointers must materialize exact evidence without changing score semantics."""
import json

import pytest

from grothendieck_rlvr.evidence import catalog, indexed_schema, materialize, indexed_system
from grothendieck_rlvr.judge import Judge, assessment_schema
from grothendieck_rlvr.prompts import judge_system
from grothendieck_rlvr.schema import Assessment


def wire_assessment():
    """A modest connection is valid even without a further demonstrated consequence."""
    return {"theory_validity": "supported", "novelty_comparison": {
        "reference_excerpt": "R0", "addition_evidence": ["C1"], "use_evidence": [], "relation": "beyond_reference"},
        "criteria": {key: {"evidence": ["C1"] if key == "constructive_novelty" else [],
                           "rationale": "Fixture", "score": 1 if key == "constructive_novelty" else 0}
                     for key in Assessment.weights}, "problems": []}


def test_lossless_catalog_and_exact_materialization_with_modest_credit():
    candidate = 'Use $x^2$ here.\r\nA commutator measures the failure of multiplication to commute.\n'
    reference = 'Multiply polynomials.\nCollect coefficients.'
    candidates, references = catalog(candidate, "C"), catalog(reference, "R")
    assert ''.join(candidates.values()) == candidate
    assert ''.join(catalog("a" * 1000, "C").values()) == "a" * 1000
    assessment = materialize(json.dumps(wire_assessment()), candidates, references)
    assessment.validate_evidence(candidate)
    assessment.validate_reference(reference)
    assert assessment.novelty == .25
    assert assessment.criteria["constructive_novelty"].evidence == [candidates["C1"]]
    assert assessment.novelty_comparison.reference_excerpt == references["R0"]
    raw = wire_assessment()
    raw["theory_validity"] = "contradicted"
    assert materialize(json.dumps(raw), candidates, references).quality == 0


def test_unknown_cross_source_and_blank_pointers_fail_explicitly():
    candidates, references = catalog("Math\nConnection\n\n", "C"), catalog("Reference", "R")
    for invalid in ("C999", "R0", "Connection", "C2"):
        raw = wire_assessment()
        raw["criteria"]["constructive_novelty"]["evidence"] = [invalid]
        with pytest.raises(ValueError):
            materialize(json.dumps(raw), candidates, references)
    raw = wire_assessment()
    raw["novelty_comparison"]["reference_excerpt"] = "C0"
    with pytest.raises(ValueError):
        materialize(json.dumps(raw), candidates, references)


def test_wire_schema_limits_pointers_and_transport_preserves_rubric_and_quotes():
    candidates, references = catalog("Math\nConnection\n\n", "C"), catalog("Reference", "R")
    schema = indexed_schema(assessment_schema(), candidates, references)
    assert schema["$defs"]["Criterion"]["properties"]["evidence"]["items"]["enum"] == ["C0", "C1"]
    assert schema["$defs"]["NoveltyComparison"]["properties"]["reference_excerpt"]["enum"] == ["R0"]
    for variant in ("quoted", "rubric"):
        original = judge_system(variant, "v7")
        changed = indexed_system(original)
        assert changed.split("Return only JSON")[0] == original.split("Return only JSON")[0]
        assert changed.split("If validation_feedback")[1] == original.split("If validation_feedback")[1]
    assert "I can illustrate the second approach" in indexed_system(judge_system("quoted", "v7"))
    assert "I can illustrate the second approach" not in indexed_system(judge_system("rubric", "v7"))


def test_indexed_protocol_accepts_one_call_and_reuses_only_its_own_cache(tmp_path, monkeypatch):
    from grothendieck_rlvr.schema import Task
    old = Judge("http://127.0.0.1:8081", cache=tmp_path / "cache.sqlite", protocol="single-v1")
    judge = Judge("http://127.0.0.1:8081", cache=tmp_path / "cache.sqlite", protocol="single-indexed-v1")
    task = Task(id="fixture", problem="Fixture", answer="1", family="gcd", split="dev", provenance={})
    calls = []
    def generate(messages, max_tokens, schema):
        calls.append(messages)
        payload = json.loads(messages[-1]["content"])
        assert payload["candidate_response"]["C1"] == "Connection"
        return json.dumps(wire_assessment())
    monkeypatch.setattr(judge.client, "generate", generate)
    assert old.identity != judge.identity
    assert not judge.stages and judge.client.check_context
    assert judge.assess(task, "Math\nConnection").novelty == .25
    assert judge.assess(task, "Math\nConnection").novelty == .25
    assert len(calls) == 1
