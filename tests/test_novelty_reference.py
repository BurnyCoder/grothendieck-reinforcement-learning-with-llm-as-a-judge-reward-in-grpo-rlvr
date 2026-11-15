"""Reject contradictory novelty decisions without substituting a mathematical verdict."""
import json
from copy import deepcopy

import pytest

from grothendieck_rlvr.io import EventLog, read_jsonl
from grothendieck_rlvr.judge import Judge, JudgeFailure
from grothendieck_rlvr.schema import Assessment, Task


CANDIDATE = "Define the construction. It yields another consequence. <final>6</final>"


def opinion(score=2, relation="beyond_reference", validity="supported"):
    """Synthetic assertions test transport contracts, not mathematical correctness."""
    return {
        "theory_validity": validity,
        "novelty_comparison": {
            "reference_excerpt": "use Euclid's algorithm",
            "addition_evidence": ["Define the construction."],
            "use_evidence": ["It yields another consequence."],
            "relation": relation,
        },
        "criteria": {key: {"evidence": ["Define the construction."], "rationale": "Fixture only",
                           "score": score if key == "constructive_novelty" else 3}
                     for key in Assessment.weights},
        "problems": [],
    }


@pytest.mark.parametrize("relation", ["within_reference", "unresolved"])
def test_positive_novelty_requires_explicit_departure(relation):
    with pytest.raises(ValueError, match="beyond_reference"):
        Assessment.model_validate(opinion(relation=relation))


@pytest.mark.parametrize("field", ["addition_evidence", "use_evidence"])
def test_positive_novelty_requires_construction_and_function_evidence(field):
    data = opinion()
    data["novelty_comparison"][field] = []
    with pytest.raises(ValueError, match="addition and use"):
        Assessment.model_validate(data)


def test_reference_and_candidate_excerpts_are_checked_against_separate_sources():
    reference = "Conventional reference: use Euclid's algorithm."
    valid = Assessment.model_validate(opinion())
    valid.validate_reference(reference)
    valid.validate_evidence(CANDIDATE)
    with pytest.raises(ValueError, match="conventional reference"):
        valid.validate_reference("Conventional reference: list divisors.")
    data = opinion()
    data["novelty_comparison"]["addition_evidence"] = ["use Euclid's algorithm"]
    with pytest.raises(ValueError, match="novelty_comparison.addition_evidence"):
        Assessment.model_validate(data).validate_evidence(CANDIDATE)


def test_conventional_general_theory_keeps_its_other_scores():
    conventional = Assessment.model_validate(opinion(score=0, relation="within_reference"))
    assert conventional.quality == pytest.approx(.6)
    assert conventional.novelty == 0
    for validity in ("none", "unsupported", "contradicted"):
        invalid = Assessment.model_validate(opinion(validity=validity))
        assert invalid.quality == invalid.novelty == 0


def test_inconsistent_response_is_retried_without_silently_capping_its_score(tmp_path, monkeypatch):
    judge = Judge("http://127.0.0.1:8081", log=EventLog(tmp_path / "events.jsonl"),
                  cache=tmp_path / "cache.sqlite")
    task = Task(id="reference-contract", problem="gcd(12,18)", answer="6", family="gcd",
                split="dev", provenance={})
    invalid, repaired = opinion(relation="within_reference"), opinion(score=0, relation="within_reference")
    replies = iter([json.dumps(invalid), json.dumps(repaired)])
    requests = []
    def generate(messages, *args):
        requests.append(deepcopy(messages))
        return next(replies)
    monkeypatch.setattr(judge.client, "generate", generate)
    assert judge.assess(task, CANDIDATE).quality == pytest.approx(.6)
    original, retry = [json.loads(messages[1]["content"]) for messages in requests]
    feedback = retry.pop("validation_feedback")
    assert retry == original
    assert "beyond_reference" in feedback["error"]
    assert json.loads(feedback["previous_assessment"]) == invalid
    assert sum(e["kind"] == "judge_assessment" for e in read_jsonl(tmp_path / "events.jsonl")) == 1


def test_invented_reference_never_enters_cache(tmp_path, monkeypatch):
    judge = Judge("http://127.0.0.1:8081", log=EventLog(tmp_path / "events.jsonl"),
                  cache=tmp_path / "cache.sqlite")
    task = Task(id="reference-contract", problem="gcd(12,18)", answer="6", family="gcd",
                split="dev", provenance={})
    data = opinion()
    data["novelty_comparison"]["reference_excerpt"] = "All classical mathematics is conventional."
    monkeypatch.setattr(judge.client, "generate", lambda *args: json.dumps(data))
    with pytest.raises(JudgeFailure, match="conventional reference"):
        judge.assess(task, CANDIDATE)
    assert judge.db.execute("SELECT count(*) FROM assessments").fetchone()[0] == 0
