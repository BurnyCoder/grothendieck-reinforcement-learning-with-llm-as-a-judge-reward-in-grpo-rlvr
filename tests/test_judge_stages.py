"""Deterministic stage contracts; fixtures are not evidence of semantic judge accuracy."""
from copy import deepcopy

import pytest

from grothendieck_rlvr.judge_stages import (
    ConceptFinding, QualityFinding, Issue, CriterionFinding, aggregate, stage_specs, validate_stage,
)
from grothendieck_rlvr.schema import Assessment


CANDIDATE = "Reference argument. A valid connection. Its operation. Another consequence. A reusable framework. Boundary. Result."
REFERENCE = "Use the reference argument."


def findings(level=1):
    """An evidence declaration at each level isolates the aggregation contract."""
    reference = {"reference_excerpt": REFERENCE, "addition_evidence": ["A valid connection."],
                 "relation": "beyond_reference", "rationale": "Additional relationship.", "issues": []}
    development = {
        "operation_evidence": ["Its operation."] if level >= 2 else [],
        "dependency_rationale": "The operation applies the addition." if level >= 2 else "Only establishes the connection.",
        "operation_uses_addition": level >= 2,
        "consequence_evidence": ["Another consequence."] if level >= 3 else [],
        "substantial_departure": level >= 3,
        "boundary_evidence": ["Boundary."] if level >= 3 else [],
        "framework_evidence": ["A reusable framework."] if level >= 4 else [],
        "problem_recovery_evidence": ["Result."] if level >= 4 else [],
        "reusable_framework": level >= 4, "issues": [],
    }
    validity = {"evidence": ["A valid connection."], "rationale": "Supported.",
                "verdict": "supported", "issues": []}
    criteria = {key: {"evidence": ["Reference argument."], "rationale": "Fixture.", "score": 3}
                for key in Assessment.weights if key != "constructive_novelty"}
    return {"concepts": ConceptFinding(reference=reference, development=development),
            "quality": QualityFinding(validity=validity, criteria=criteria)}


@pytest.mark.parametrize("level", [1, 2, 3, 4])
def test_levels_preserve_modest_credit_and_developed_ordering(level):
    result = aggregate(findings(level))
    assert result.novelty == level / 4
    assert result.quality == pytest.approx(.6 + .05 * level)
    result.validate_evidence(CANDIDATE)
    result.validate_reference(REFERENCE)


def test_routine_origin_argument_cannot_be_promoted_by_nonempty_excerpt():
    data = findings(4)
    data["concepts"].development.operation_uses_addition = False
    data["concepts"].development.operation_evidence = ["Reference argument."]
    assert aggregate(data).novelty == .25
    assert aggregate(data).novelty_comparison.use_evidence == []


@pytest.mark.parametrize("relation", ["within_reference", "unresolved"])
def test_reference_uncertainty_only_removes_novelty(relation):
    data = findings(4)
    data["concepts"].reference.relation = relation
    assert aggregate(data).novelty == 0
    assert aggregate(data).quality == pytest.approx(.6)


@pytest.mark.parametrize("severity", ["unsupported", "contradicted"])
def test_any_substantive_issue_blocks_all_theory_credit(severity):
    data = findings(4)
    data["concepts"].development.issues = [Issue(evidence=["Another consequence."],
        severity=severity, rationale="An essential mathematical problem.")]
    result = aggregate(data)
    assert result.theory_validity == severity
    assert result.quality == result.novelty == 0


def test_specialists_and_two_calls_have_identical_aggregation_semantics():
    data = findings(4)
    specialists = {"validity": data["quality"].validity, "reference": data["concepts"].reference,
                   "development": data["concepts"].development}
    specialists.update({key: CriterionFinding(rating=value, issues=[])
                        for key, value in data["quality"].criteria.items()})
    assert aggregate(specialists) == aggregate(data)
    specialists["conceptual_economy"].issues = [
        Issue(evidence=["Boundary."], severity="contradicted", rationale="False boundary.")]
    assert aggregate(specialists).quality == 0


def test_exact_excerpts_and_required_declarations_are_checked():
    data = findings(3)
    for finding in data.values():
        validate_stage(finding, CANDIDATE, REFERENCE)
    bad = deepcopy(data["concepts"])
    bad.reference.reference_excerpt = "An invented baseline."
    with pytest.raises(ValueError, match="reference"):
        validate_stage(bad, CANDIDATE, REFERENCE)
    bad = deepcopy(data["concepts"])
    bad.development.operation_evidence = ["Invented support."]
    with pytest.raises(ValueError, match="candidate"):
        validate_stage(bad, CANDIDATE, REFERENCE)
    bad = deepcopy(data["quality"])
    bad.criteria["structural_understanding"].evidence = []
    with pytest.raises(ValueError, match="Positive"):
        validate_stage(bad, CANDIDATE, REFERENCE)


def test_protocols_have_two_and_eight_roles_with_one_declared_dependency():
    two = stage_specs("two-stage-v1", "quoted")
    eight = stage_specs("specialists-v1", "quoted")
    assert [s.name for s in two] == ["concepts", "quality"]
    assert len(eight) == 8
    assert [(s.name, s.dependencies) for s in eight if s.dependencies] == [("development", ("reference",))]
    assert not any(s.dependencies for s in two)
    for quoted, rubric in zip(eight, stage_specs("specialists-v1", "rubric"), strict=True):
        assert "softening liquid" in quoted.system and "softening liquid" not in rubric.system
        assert quoted.system.endswith(rubric.system)
        assert quoted.max_tokens == (512 if quoted.name in Assessment.weights else 1024)
        assert quoted.reasoning_tokens == (256 if quoted.name in Assessment.weights else 512)


def test_missing_stage_is_an_error_not_a_zero_reward():
    with pytest.raises(ValueError, match="stage"):
        aggregate({"concepts": findings()["concepts"]})
