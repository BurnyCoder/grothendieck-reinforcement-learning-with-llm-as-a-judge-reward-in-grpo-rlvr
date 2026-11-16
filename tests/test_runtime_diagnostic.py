"""Runtime repairs must be isolated development runs, never silent arm changes."""
import pytest

from grothendieck_rlvr import training
from grothendieck_rlvr.experiments import EXPLORATORY_PREFIX
from grothendieck_rlvr.io import read_json


def test_cache_diagnostic_requires_explicit_exploratory_pilot(tmp_path, monkeypatch):
    """Reject a runtime intervention before creating a comparative run directory."""
    monkeypatch.setenv("GROTH_ROOT", str(tmp_path))
    for pilot, exploratory in ((False, True), (True, False), (False, False)):
        with pytest.raises(ValueError, match="exploratory pilot"):
            training.train(pilot=pilot, exploratory=exploratory,
                           runtime_diagnostic="cache-release-v1")
    assert not (tmp_path / "runs").exists()


def test_cache_diagnostic_has_its_own_identity_and_longer_development_budget(tmp_path, monkeypatch):
    """A runtime probe cannot overwrite the ordinary pilot or partial comparative arm."""
    monkeypatch.setenv("GROTH_ROOT", str(tmp_path))
    monkeypatch.setattr(training, "validate_manifests", lambda: {"fixture": True})
    def stop(*args, **kwargs):
        raise RuntimeError("fixture stops before model loading")
    monkeypatch.setattr(training, "load_policy", stop)
    with pytest.raises(RuntimeError, match="before model loading"):
        training.train(pilot=True, exploratory=True, runtime_diagnostic="cache-release-v1")
    folder = tmp_path / "runs" / (EXPLORATORY_PREFIX + "pilot-cache-release-v1-theory-seed42")
    identity = read_json(folder / "run.json")
    assert identity["config"]["max_steps"] == 16
    assert identity["config"]["save_steps"] == 8
    assert identity["config"]["torch_empty_cache_steps"] == 1
    assert identity["runtime_diagnostic"]["id"] == "cache-release-v1"
    assert not (tmp_path / "runs" / (EXPLORATORY_PREFIX + "theory-seed42")).exists()
    assert not (tmp_path / "runs" / (EXPLORATORY_PREFIX + "pilot-theory-seed42")).exists()
