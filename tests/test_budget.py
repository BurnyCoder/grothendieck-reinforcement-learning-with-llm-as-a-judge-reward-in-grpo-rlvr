"""Runtime forecasts must not pool pilot intervals from different reward instruments."""
import pytest

from grothendieck_rlvr.budget import training_budget
from grothendieck_rlvr.experiments import EXPLORATORY_ID
from grothendieck_rlvr.io import PROJECT, read_json


def test_single_call_runtime_is_separate_from_historical_nonthinking_pilot():
    old = {"kind": "grpo_first_saved_boundary", "step_metrics": {"step_time": 10}}
    new = [{"kind": "exploratory_single_grpo_boundary", "experiment": EXPLORATORY_ID,
            "judge_identity": "same", "step_metrics": {"step_time": seconds}}
           for seconds in (100, 200)]
    result = training_budget([old, *new], read_json(PROJECT / "configs/study.json"))
    assert result["observed_step_seconds"] == [10]
    assert result["exploratory_single"]["observed_step_seconds"] == [100, 200]
    assert result["exploratory_single"]["options"][1]["one_judged_arm_hours"] == pytest.approx(
        [64 * 100 / 3600, 64 * 200 / 3600])
    assert training_budget([old], read_json(PROJECT / "configs/study.json"))["exploratory_single"]["options"] == []
    new[1]["judge_identity"] = "changed"
    with pytest.raises(ValueError, match="different judge identities"):
        training_budget(new, read_json(PROJECT / "configs/study.json"))
