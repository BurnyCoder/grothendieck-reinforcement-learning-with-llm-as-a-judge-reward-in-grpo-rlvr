"""An explicitly authorized noisy-reward experiment cannot qualify the original study."""
from types import SimpleNamespace

import pytest

from grothendieck_rlvr import analysis, evaluation, training
from grothendieck_rlvr.experiments import EXPLORATORY_PREFIX, experiment_profile, validate_judge
from grothendieck_rlvr.io import read_json


def test_exploratory_names_require_explicit_selection():
    name = EXPLORATORY_PREFIX + "theory-seed42"
    assert experiment_profile(True, name)["judge_protocol"] == "single-indexed-v1"
    with pytest.raises(ValueError, match="track"):
        experiment_profile(False, name)
    with pytest.raises(ValueError, match="track"):
        experiment_profile(True, "theory-seed42")
    assert experiment_profile(False, "theory-seed42") is None
    with pytest.raises(ValueError, match="track"):
        experiment_profile(False, "exploratory-single-v1-ordinary")


def test_exploratory_judge_must_match_its_frozen_single_call_identity():
    profile = experiment_profile(True)
    identity = profile["judge_identities"]["training_judge"]["quoted"]
    judge = SimpleNamespace(role="training_judge", variant="quoted", protocol="single-indexed-v1", identity=identity)
    validate_judge(judge, profile)
    judge.protocol = "specialists-v1"
    with pytest.raises(ValueError, match="single-call"):
        validate_judge(judge, profile)
    judge.protocol, judge.identity = "single-indexed-v1", "changed"
    with pytest.raises(ValueError, match="identity"):
        validate_judge(judge, profile)


def test_exploratory_arms_cannot_silently_change_training_budget(monkeypatch):
    from grothendieck_rlvr import experiments
    original = experiments.read_json
    monkeypatch.setattr(experiments, "read_json", lambda path: {
        **original(path), "max_steps": 128} if path.name == "study.json" else original(path))
    with pytest.raises(ValueError, match="input lock changed"):
        experiment_profile(True)


def test_standard_training_still_requires_calibration(monkeypatch):
    def block():
        raise RuntimeError("qualification fixture")
    monkeypatch.setattr(training, "require_calibration", block)
    with pytest.raises(RuntimeError, match="qualification fixture"):
        training.train()


def test_exploratory_training_records_separate_identity_before_model_loading(tmp_path, monkeypatch):
    monkeypatch.setenv("GROTH_ROOT", str(tmp_path))
    monkeypatch.setattr(training, "require_calibration", lambda: pytest.fail("Exploratory exception is explicit"))
    monkeypatch.setattr(training, "validate_manifests", lambda: {"fixture": True})
    def stop(*args, **kwargs):
        raise RuntimeError("fixture stops before GPU loading")
    monkeypatch.setattr(training, "load_policy", stop)
    with pytest.raises(RuntimeError, match="before GPU"):
        training.train(arm="correctness", exploratory=True)
    config = read_json(tmp_path / "runs" / (EXPLORATORY_PREFIX + "correctness-seed42") / "run.json")
    assert config["experiment"]["calibration_required"] is False
    assert config["config"]["judge_protocol"] == "single-indexed-v1"
    assert config["config"]["max_steps"] == 64
    assert not (tmp_path / "runs/correctness-seed42").exists()


def test_uncalibrated_three_seed_result_never_becomes_confirmatory():
    cfg = {"training_seeds": [42, 43, 44], "data_seed": 9, "bootstrap_samples": 100,
           "test_fresh_size": 1, "test_hard_size": 1, "test_unseen_size": 1}
    evaluations = {}
    for seed in cfg["training_seeds"]:
        for arm, metric in [("theory", .9), ("correctness", .5)]:
            evaluations[f"{arm}-seed{seed}"] = [
                {"task_id": split, "family": "fixture", "split": split,
                 "judge_identity": "same", "metric": metric, "correct": True}
                for split in ("test_fresh", "test_hard", "test_unseen")]
    result = analysis.primary_comparison(evaluations, cfg, exploratory=True)
    assert result["status"] == "exploratory_uncalibrated"
    assert result["criteria_met"] is None
    assert result["metric"]["difference"] == pytest.approx(.4)


def test_generation_track_is_locked_and_wrong_mode_does_not_load_model(tmp_path, monkeypatch):
    monkeypatch.setenv("GROTH_ROOT", str(tmp_path))
    monkeypatch.setattr(evaluation, "evaluation_tasks", lambda split: [])
    name = EXPLORATORY_PREFIX + "ordinary"
    evaluation.generate(name, exploratory=True)
    config = read_json(tmp_path / "evaluations" / name / "generation-config.json")
    assert config["experiment"] == experiment_profile(True)
    with pytest.raises(ValueError, match="track"):
        evaluation.generate(name)
    profile = experiment_profile(True)
    profile["authorization"] = "Changed fixture profile"
    monkeypatch.setattr(evaluation, "experiment_profile", lambda *a: profile)
    with pytest.raises(ValueError, match="configuration changed"):
        evaluation.generate(name, exploratory=True)


def test_transfer_cannot_mix_exploratory_and_standard_sources(tmp_path, monkeypatch):
    monkeypatch.setenv("GROTH_ROOT", str(tmp_path))
    monkeypatch.setattr(evaluation, "load_tasks", lambda split: [])
    with pytest.raises(ValueError, match="track"):
        evaluation.transfer([EXPLORATORY_PREFIX + "ordinary-notes"])
