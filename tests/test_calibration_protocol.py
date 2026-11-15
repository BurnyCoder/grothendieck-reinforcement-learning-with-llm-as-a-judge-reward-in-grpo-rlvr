"""Fixed-threshold development futility cannot turn an incomplete audit into a pass."""
from types import SimpleNamespace

import pytest

from grothendieck_rlvr import calibration
from grothendieck_rlvr.io import EventLog, read_json
from grothendieck_rlvr.schema import Verification


class FixtureJudge:
    """Synthetic opinions isolate stopping logic; they are not empirical judge evidence."""
    role, variant, identity = "fixture", "quoted", "fixture-identity"

    def __init__(self, directory, split, fail=False):
        self.log = EventLog(directory / "events.jsonl")
        self.calls = 0
        self.fail = fail
        self.preferred = {c["preferred"] for c in calibration.build_cases(split)["pairs"]}

    def assess(self, task, response):
        self.calls += 1
        positive = response in self.preferred and not self.fail
        return SimpleNamespace(quality=float(positive), novelty=float(positive),
                               novelty_credit={"raw_score": 4 if positive else 0,
                                               "effective_score": 4 if positive else 0,
                                               "eligible": positive, "withheld": False,
                                               "gate_reasons": [] if positive else ["theory_not_supported"]},
                               theory_validity="supported" if positive else "none")


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    """These tests cover scheduling, not the separately tested symbolic references."""
    monkeypatch.setenv("GROTH_ROOT", str(tmp_path))
    monkeypatch.setattr(calibration, "verify_answer", lambda *a: Verification(status="correct"))
    return tmp_path


def test_development_stops_when_fixed_novelty_threshold_is_unreachable(isolated):
    judge = FixtureJudge(isolated, "dev", fail=True)
    result = calibration.calibrate(judge, "dev")
    assert not result["passed"] and not result["complete"]
    assert result["stopping_reason"] == "development_threshold_unreachable"
    assert judge.calls == 4
    assert result["strata"]["novelty"]["preference_upper_bound"] == .75
    assert result["false_theory_suppression"] is None
    assert len(result["ordering"]) == 2 and not result["suppression"]
    assert calibration.calibrate(judge, "dev") == result
    assert judge.calls == 4
    assert not read_json(isolated / "calibration/fixture-quoted-dev.json")["passed"]


@pytest.mark.parametrize("split,fail", [("dev", False), ("audit", True)])
def test_success_needs_complete_suite_and_audit_never_stops_early(isolated, split, fail):
    judge = FixtureJudge(isolated, split, fail=fail)
    result = calibration.calibrate(judge, split)
    assert result["complete"] and result["passed"] is (not fail)
    assert judge.calls == 84
    assert len(result["ordering"]) == len(result["suppression"]) == 28
    assert result["stopping_reason"] == "complete"


def test_futility_bound_counts_remaining_false_theory_cases():
    cases = calibration.build_cases("dev")
    failed = [{"stratum": "novelty", "passed": False}]
    result = calibration.calibration_summary(cases, [], failed)
    assert result["strata"]["novelty"]["suppression_upper_bound"] == .875
    assert result["threshold_unreachable"] and not result["passed"]
