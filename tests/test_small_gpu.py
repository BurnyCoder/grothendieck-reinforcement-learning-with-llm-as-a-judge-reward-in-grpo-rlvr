"""Smaller GPU experiments must preserve old artifacts and reject CPU model fallback."""
from types import SimpleNamespace

import pytest

from grothendieck_rlvr import models
from grothendieck_rlvr.budget import training_budget
from grothendieck_rlvr.experiments import EXPLORATORY_ID
from grothendieck_rlvr.io import PROJECT, read_json


def test_model_directories_keep_previous_weights_separate(tmp_path, monkeypatch):
    monkeypatch.setenv("GROTH_ROOT", str(tmp_path))
    monkeypatch.setattr(models, "read_json", lambda path: {
        "policy": {"artifact_subdir": "small-qwen-gpu-v1/policy"}, "training_judge": {}})
    assert models.model_directory("policy") == tmp_path / "models/small-qwen-gpu-v1/policy"
    assert models.model_directory("training_judge") == tmp_path / "models/training_judge"
    monkeypatch.setattr(models, "read_json", lambda path: {"policy": {"artifact_subdir": "../../other"}})
    with pytest.raises(ValueError, match="model directory"):
        models.model_directory("policy")


def test_policy_gpu_placement_rejects_cpu_or_meta_tensors():
    def model(*devices):
        return SimpleNamespace(parameters=lambda: iter(SimpleNamespace(device=SimpleNamespace(type=d)) for d in devices))
    models.require_cuda_policy(model("cuda", "cuda"))
    for placement in (("cuda", "cpu"), ("meta",)):
        with pytest.raises(RuntimeError, match="CUDA"):
            models.require_cuda_policy(model(*placement))


def test_training_runtime_allows_registered_gpu_but_rejects_silent_fallback(monkeypatch):
    runtime = {"backend": "cuda12.8", "gpu_layers": 999, "require_full_gpu": True, "fit": "off"}
    monkeypatch.setattr(models, "read_json", lambda path: {"training_judge": runtime})
    assert models.judge_runtime("training_judge") == runtime
    for mutation in ({"gpu_layers": 12}, {"backend": "cpu", "gpu_layers": 0}, {"fit": "on"}):
        monkeypatch.setattr(models, "read_json", lambda path, m=mutation: {"training_judge": {**runtime, **m}})
        with pytest.raises(ValueError, match="full GPU"):
            models.judge_runtime("training_judge")


def test_new_runtime_forecast_never_borrows_postponed_pilot_speed():
    records = [{"kind": "exploratory_single_grpo_boundary", "experiment": "exploratory-single-v2",
                "judge_identity": "old-cpu", "step_metrics": {"step_time": 800}}]
    cfg = read_json(PROJECT / "configs/study.json")
    assert training_budget(records, cfg, experiment_id="small-fixture")["exploratory_single"]["options"] == []
    records.append({"kind": "exploratory_single_grpo_boundary", "experiment": EXPLORATORY_ID,
                    "judge_identity": "new-gpu", "step_metrics": {"step_time": 100}})
    result = training_budget(records, cfg, experiment_id=EXPLORATORY_ID)
    assert result["exploratory_single"]["observed_step_seconds"] == [100]
    assert result["historical_exploratory"][0]["experiment"] == "exploratory-single-v2"
