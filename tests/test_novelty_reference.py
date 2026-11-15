"""Keep raw judge opinions while enforcing declared novelty eligibility in reward code."""
import json

import pytest

from grothendieck_rlvr.io import EventLog, read_jsonl
from grothendieck_rlvr.judge import Judge, JudgeFailure
from grothendieck_rlvr.schema import Assessment, Task
from grothendieck_rlvr.reward import CompositeReward


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
    data = opinion(relation=relation)
    assessment = Assessment.model_validate(data)
    assert assessment.model_dump() == data
    assert assessment.novelty == 0
    assert assessment.quality == pytest.approx(.6)
    assert assessment.novelty_credit == {
        "raw_score": 2, "effective_score": 0, "eligible": False,
        "score_cap": 0, "withheld": True, "gate_reasons": [relation],
    }


@pytest.mark.parametrize("field,credited", [("addition_evidence", 0), ("use_evidence", 1)])
def test_a_valid_connection_without_further_use_has_a_modest_credit_cap(field, credited):
    data = opinion()
    data["novelty_comparison"][field] = []
    assessment = Assessment.model_validate(data)
    assert assessment.novelty == credited / 4
    assert assessment.quality == pytest.approx(.6 + .05*credited)
    assert assessment.novelty_credit["score_cap"] == credited
    assert assessment.novelty_credit["gate_reasons"] == [f"missing_{field}"]
    assert assessment.model_dump() == data


def test_brief_connection_credit_is_positive_but_cannot_match_a_developed_framework():
    data = opinion(score=4)
    developed = Assessment.model_validate(data)
    data["novelty_comparison"]["use_evidence"] = []
    brief = Assessment.model_validate(data)
    assert brief.novelty == .25 < developed.novelty
    assert brief.quality < developed.quality
    assert brief.novelty_credit["eligible"] is True
    assert brief.novelty_credit["withheld"] is True
    assert brief.criteria["constructive_novelty"].score == 4


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


def test_withheld_credit_is_visible_in_fresh_and_cached_events(tmp_path, monkeypatch):
    judge = Judge("http://127.0.0.1:8081", protocol="legacy", log=EventLog(tmp_path / "events.jsonl"),
                  cache=tmp_path / "cache.sqlite")
    task = Task(id="reference-contract", problem="gcd(12,18)", answer="6", family="gcd",
                split="dev", provenance={})
    raw = opinion(relation="within_reference")
    requests = []
    def generate(messages, *args):
        requests.append(messages)
        return json.dumps(raw)
    monkeypatch.setattr(judge.client, "generate", generate)
    assert judge.assess(task, CANDIDATE).quality == pytest.approx(.6)
    assert judge.assess(task, CANDIDATE).model_dump() == raw
    assert len(requests) == 1
    events = read_jsonl(tmp_path / "events.jsonl")
    assert [e["kind"] for e in events] == ["judge_assessment", "judge_cache_hit"]
    for event in events:
        assert event["assessment"] == raw
        assert event["novelty_credit"]["withheld"] is True
        assert event["novelty_credit"]["gate_reasons"] == ["within_reference"]
        assert event["novelty"] == 0
        assert event["theory"] == pytest.approx(.6)


def test_eligibility_protocol_changes_cache_identity(tmp_path, monkeypatch):
    from grothendieck_rlvr import judge as module
    judge = Judge("http://127.0.0.1:8081", cache=tmp_path / "cache.sqlite")
    monkeypatch.setattr(module, "ASSESSMENT_PROTOCOL", "different-reward-contract")
    changed = Judge("http://127.0.0.1:8081", cache=tmp_path / "cache.sqlite")
    assert changed.identity != judge.identity


def test_reward_callback_uses_effective_credit_and_retains_raw_opinion(tmp_path, monkeypatch):
    judge = Judge("http://127.0.0.1:8081", protocol="legacy", log=EventLog(tmp_path / "judge.jsonl"),
                  cache=tmp_path / "cache.sqlite")
    task = Task(id="reference-contract", problem="gcd(12,18)", answer="6", family="gcd",
                split="dev", provenance={})
    raw = opinion(score=4, relation="within_reference")
    monkeypatch.setattr(judge.client, "generate", lambda *args: json.dumps(raw))
    callback = CompositeReward(judge, EventLog(tmp_path / "reward.jsonl"))
    rewards = callback([CANDIDATE, "<final>5</final>"], [task.model_dump()] * 2)
    assert rewards == pytest.approx([1.3, 0.0])
    rows = [e for e in read_jsonl(tmp_path / "reward.jsonl") if e["kind"] == "rollout"]
    assert rows[0]["assessment"] == raw
    assert rows[0]["novelty_credit"]["withheld"]
    assert rows[0]["novelty_credit"]["raw_score"] == 4
    assert rows[1]["assessment"] is rows[1]["novelty_credit"] is None


def test_invented_reference_never_enters_cache(tmp_path, monkeypatch):
    judge = Judge("http://127.0.0.1:8081", protocol="legacy", log=EventLog(tmp_path / "events.jsonl"),
                  cache=tmp_path / "cache.sqlite")
    task = Task(id="reference-contract", problem="gcd(12,18)", answer="6", family="gcd",
                split="dev", provenance={})
    data = opinion()
    data["novelty_comparison"]["reference_excerpt"] = "All classical mathematics is conventional."
    monkeypatch.setattr(judge.client, "generate", lambda *args: json.dumps(data))
    with pytest.raises(JudgeFailure, match="conventional reference"):
        judge.assess(task, CANDIDATE)
    assert judge.db.execute("SELECT count(*) FROM assessments").fetchone()[0] == 0
