"""Explicitly separate the authorized noisy-judge experiment from the qualified study."""
from .io import PROJECT, digest, read_json

EXPLORATORY_ID = "exploratory-single-v1"
EXPLORATORY_PREFIX = EXPLORATORY_ID + "-"


def experiment_profile(exploratory=False, run_id=None):
    """Require both an explicit CLI choice and a distinct artifact namespace."""
    if run_id is not None and run_id.startswith(EXPLORATORY_PREFIX) != exploratory:
        raise ValueError("Run name and explicitly selected experiment track disagree")
    if not exploratory:
        return None
    profile = read_json(PROJECT / "configs/exploratory-single-judge.json")
    if profile["id"] != EXPLORATORY_ID or profile["calibration_required"] is not False:
        raise ValueError("Unsupported exploratory experiment profile")
    if profile["judge_protocol"] != "single-v1":
        raise ValueError("Exploratory track requires the frozen single-call protocol")
    for path, expected in profile["input_hashes"].items():
        if digest(read_json(PROJECT / path)) != expected:
            raise ValueError(f"Exploratory input lock changed: {path}; amend before starting another arm")
    return profile


def validate_judge(judge, profile):
    """No runtime or prompt change can silently enter an exploratory arm or its evaluation."""
    if profile is None:
        return
    if judge.protocol != "single-v1":
        raise ValueError("Exploratory experiment requires a single-call judge")
    expected = profile["judge_identities"][judge.role][judge.variant]
    if judge.identity != expected:
        raise ValueError("Exploratory judge identity changed; publish a new experiment profile")
