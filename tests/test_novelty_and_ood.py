"""Regression contracts for valid novelty rewards and held-out mathematical families."""
import pytest

from grothendieck_rlvr.schema import Assessment, Criterion
from grothendieck_rlvr.reward import composite


def opinion(novelty, validity="supported"):
    """Hold mathematical quality fixed to isolate the novelty intervention."""
    return Assessment(theory_validity=validity, criteria={
        key: Criterion(score=novelty if key == "constructive_novelty" else 3,
                       evidence=["A justified construction."], rationale="Constructed test.")
        for key in Assessment.weights
    }, problems=[])


def test_supported_novelty_increases_reward_without_reversing_correctness():
    rewards = [composite(True, opinion(n)) for n in range(5)]
    assert rewards == sorted(set(rewards))
    assert rewards[-1] - rewards[0] == pytest.approx(.1)
    assert opinion(4).novelty == 1
    for validity in ("none", "unsupported", "contradicted"):
        assert opinion(4, validity).novelty == 0
        assert composite(True, opinion(4, validity)) == 1
    assert composite(False, opinion(4)) == 0


def test_novelty_calibration_contains_distant_bridges_and_false_counterparts():
    from grothendieck_rlvr.calibration import build_cases
    from grothendieck_rlvr.verifier_worker import check
    dev, audit = (build_cases(split) for split in ("dev", "audit"))
    assert {c["task"]["id"] for c in dev["pairs"]}.isdisjoint(
        c["task"]["id"] for c in audit["pairs"])
    for cases in (dev, audit):
        novel = [c for c in cases["pairs"] if c.get("stratum") == "novelty"]
        false = [c for c in cases["false_cases"] if c.get("stratum") == "novelty"]
        assert len(novel) == len(false) == 8
        assert len({c["task"]["family"] for c in novel}) == 4
        for case in novel + false:
            task = case["task"]
            for key in ("preferred", "dispreferred", "response"):
                if key in case:
                    answer = case[key].split("<final>")[1].split("</final>")[0]
                    assert check(task["family"], answer, task["answer"], task["metadata"])


def test_ood_manifests_are_reproducible_isolated_and_verifiable(tmp_path):
    from grothendieck_rlvr.ood import prepare_ood, OOD_FAMILIES, reference, canonical
    from grothendieck_rlvr.io import read_json
    from grothendieck_rlvr.schema import Task
    from grothendieck_rlvr.data import TRAIN_FAMILIES, UNSEEN_FAMILIES
    from grothendieck_rlvr.verifier_worker import check
    assert set(OOD_FAMILIES).isdisjoint(TRAIN_FAMILIES + UNSEEN_FAMILIES)
    lock = prepare_ood(tmp_path)
    assert prepare_ood(tmp_path) == lock
    tasks = [Task.model_validate(row) for row in read_json(tmp_path / "test_ood.json")]
    assert len(tasks) == 200
    assert len({canonical(task) for task in tasks}) == len(tasks)
    for task in tasks:
        assert task.split == "test_ood"
        assert reference(task) == int(task.answer)
        assert check(task.family, task.answer, task.answer, task.metadata)
        assert not check(task.family, str(int(task.answer) + 1), task.answer, task.metadata)
    manifest = tmp_path / "test_ood.json"
    manifest.write_text("[]")
    with pytest.raises(ValueError, match="changed"):
        prepare_ood(tmp_path)


def test_rubric_ablation_preserves_novelty_without_historical_framing():
    from grothendieck_rlvr.prompts import judge_system
    common, quoted = judge_system("rubric"), judge_system("quoted")
    assert quoted.endswith(common)
    assert "constructive_novelty (weight 0.20)" in common
    assert "Grothendieck" not in common and "softening liquid" not in common
    assert "softening liquid" in quoted


def test_secondary_results_cannot_satisfy_primary_acceptance():
    from grothendieck_rlvr.analysis import primary_comparison
    cfg = {"training_seeds": [42, 43, 44], "data_seed": 1, "bootstrap_samples": 20,
           "test_fresh_size": 1, "test_hard_size": 1, "test_unseen_size": 2, "test_ood_per_family": 1}
    evaluations = {}
    for seed in cfg["training_seeds"]:
        for arm in ("theory", "correctness"):
            evaluations[f"{arm}-seed{seed}-ood"] = [
                {"task_id": str(i), "split": "test_ood", "family": str(i), "judge_identity": "fixture",
                 "metric": .5 if arm == "theory" else 0, "novelty": 1 if arm == "theory" else 0,
                 "correct": True} for i in range(4)]
    assert primary_comparison(evaluations, cfg)["status"] == "pending"
    result = primary_comparison(evaluations, cfg, suffix="-ood", secondary=True)
    assert result["status"] == "secondary" and result["criteria_met"] is None
    assert result["novelty"]["difference"] == 1
