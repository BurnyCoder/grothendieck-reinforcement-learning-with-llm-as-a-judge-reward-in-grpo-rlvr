"""Behavioral contracts for reward gates, parsing and data isolation (no models)."""
import pytest

from grothendieck_rlvr.schema import Assessment, Criterion, Task
from grothendieck_rlvr.reward import composite, permute_correct
from grothendieck_rlvr.verify import verify_answer, VerifierFailure
from grothendieck_rlvr.data import canonical_key, assert_disjoint


def task(family="gcd", answer="6", **metadata):
    return Task(id="test", problem="A test problem", answer=answer, family=family,
                split="dev", provenance={}, metadata=metadata)


def assessment(validity="supported", score=4, excerpt="A reusable fact."):
    return Assessment(theory_validity=validity, novelty_comparison={
        "reference_excerpt": "Fixture reference", "addition_evidence": [excerpt],
        "use_evidence": [excerpt], "relation": "beyond_reference"}, criteria={
        name: Criterion(score=score, evidence=[excerpt] if score else [], rationale="Test fixture")
        for name in Assessment.weights
    }, problems=[])


def test_correctness_dominates_every_theory_score():
    for validity in ("none", "unsupported", "contradicted", "supported"):
        a = assessment(validity)
        assert composite(False, a) == 0
        assert 1 <= composite(True, a) <= 1.5
    assert composite(True, assessment()) == 1.5
    assert composite(True, assessment("contradicted")) == 1
    assert composite(True, None) == 1


@pytest.mark.parametrize("text", ["6", "<final>6</final><final>6</final>",
    "<final>6</final> trailing answer", "<final>6", "<final>__import__('os')</final>"])
def test_malformed_answer_does_not_get_credit(text):
    assert verify_answer(task(), text).status == "invalid_format"


def test_only_delimited_answer_is_scored():
    assert verify_answer(task(), "The answer is 6. <final>5</final>").status == "incorrect"
    assert verify_answer(task(), "Explanation. <final>6</final>").correct


def test_decimal_values_are_compared_exactly_without_binary_float_rounding():
    assert verify_answer(task(), "<final>6.0000000000000000000001</final>").status == "incorrect"
    assert verify_answer(task("dice", "1/2"), "<final>0.5000000000000000000001</final>").status == "incorrect"


def test_mathematical_equivalence_and_factor_completeness():
    for answer in ("12/2", "6.0", "(9-3)", "2**2+2"):
        assert verify_answer(task(), f"<final>{answer}</final>").correct
    assert verify_answer(task("dice", "1/2"), "<final>2/4</final>").correct
    p = task("polynomial_multiplication", "x**2-1", variables=["x"])
    assert verify_answer(p, "<final>(x-1)*(x+1)</final>").correct
    f = task("prime_factorization", "2 × 2 × 3", number=12)
    assert verify_answer(f, "<final>2**2*3</final>").correct
    assert not verify_answer(f, "<final>2*6</final>").correct
    e = task("polynomial_equations", "-1.0, 1.0")
    assert verify_answer(e, "<final>1, -1</final>").correct
    assert not verify_answer(e, "<final>1</final>").correct


def test_expression_limits_and_code_rejection():
    for expression in ("x.__class__", "x**1000000", "9**9**9", "f(x)", "[6][0]", "nan", "0x6", "1e-1001"):
        assert verify_answer(task(), f"<final>{expression}</final>").status == "invalid_format"


def test_invalid_judge_assessment_fails_instead_of_becoming_zero():
    with pytest.raises(ValueError):
        assessment().validate_evidence("Unrelated response")
    with pytest.raises(ValueError):
        assessment(score=5)
    with pytest.raises(ValueError):
        Assessment(theory_validity="supported", criteria={}, problems=[])


def test_bonus_permutation_preserves_correct_reward_marginals():
    values = [0.2, 0.8, 0.6, 0.1]
    changed = permute_correct(values, [True, True, False, True], seed=42)
    assert sorted(changed[i] for i in [0, 1, 3]) == sorted(values[i] for i in [0, 1, 3])
    assert changed[2] == 0
    assert permute_correct([0, 0], [False, False], seed=42) == [0, 0]


def test_semantic_duplicates_and_split_overlap():
    a = task(numbers=[12, 18])
    b = a.model_copy(update={"id": "another", "split": "test_fresh", "metadata": {"numbers": [18, 12]}})
    assert canonical_key(a) == canonical_key(b)
    with pytest.raises(ValueError, match="overlap"):
        assert_disjoint([a, b])


def test_worker_failure_is_not_an_incorrect_answer(monkeypatch):
    import grothendieck_rlvr.verify as module
    def fail(*args, **kwargs):
        raise TimeoutError("injected infrastructure failure")
    monkeypatch.setattr(module, "run_worker", fail)
    with pytest.raises(VerifierFailure):
        verify_answer(task(), "<final>6</final>")
