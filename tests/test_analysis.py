"""Numerical tests check pairing and clustered inference, not implementation details."""
import pytest

from grothendieck_rlvr.analysis import paired_bootstrap, primary_comparison
from grothendieck_rlvr.calibration import build_cases
from grothendieck_rlvr.judge import local_url, assessment_schema
from grothendieck_rlvr.schema import Assessment
from grothendieck_rlvr.training import latest_complete_checkpoint


def test_constant_and_zero_differences_have_zero_uncertainty():
    assert paired_bootstrap([0]*20, ["a"]*10+["b"]*10, samples=100)["ci95"] == [0, 0]
    result = paired_bootstrap([[.1, .1]]*20, ["a"]*20, samples=100, hierarchical=True)
    assert result["difference"] == pytest.approx(.1)
    assert result["ci95"] == pytest.approx([.1, .1])


def test_primary_claim_requires_complete_three_seed_design():
    assert primary_comparison({}, {"training_seeds": [42, 43, 44]})["status"] == "pending"


def test_audit_is_separate_and_schema_enumerates_criteria():
    dev, audit = build_cases("dev"), build_cases("audit")
    assert {x["task"]["problem"] for x in dev["pairs"]}.isdisjoint(
        {x["task"]["problem"] for x in audit["pairs"]})
    assert set(assessment_schema()["properties"]["criteria"]["required"]) == set(Assessment.weights)


def test_no_remote_model_endpoint_or_credentials():
    for url in ("https://api.example.com", "http://127.0.0.1.evil.test", "http://user:secret@localhost:8081"):
        with pytest.raises(ValueError):
            local_url(url)


def test_recovery_ignores_incomplete_newer_checkpoint(tmp_path):
    complete = tmp_path / "checkpoint-8"
    complete.mkdir()
    (complete / "groth-state.json").write_text("{}")
    (tmp_path / "checkpoint-16").mkdir()
    assert latest_complete_checkpoint(tmp_path) == complete
