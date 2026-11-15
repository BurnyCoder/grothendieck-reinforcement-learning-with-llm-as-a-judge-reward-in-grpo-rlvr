"""Archive a completed exploratory pilot invocation before resumption changes its summary.

Run through the project's WSL virtual environment with PYTHONPATH=src. This reads
saved evidence only; it never starts a model, changes a score or selects a checkpoint.
Python file hashing: https://docs.python.org/3.12/library/hashlib.html#hashlib.file_digest
"""
import argparse
import hashlib
import json
from pathlib import Path

from grothendieck_rlvr.experiments import EXPLORATORY_ID
from grothendieck_rlvr.io import PROJECT, atomic_json, digest, read_json, read_jsonl


def archive(directory: Path) -> dict:
    """Require a complete boundary and preserve each invocation separately and immutably."""
    summary = read_json(directory / "summary.json")
    identity = read_json(directory / "run.json")
    if not summary["pilot"] or summary["experiment"] != EXPLORATORY_ID:
        raise ValueError("Only the exploratory development pilot belongs in this archive")
    events = read_jsonl(directory / "events.jsonl")
    start = max(i for i, event in enumerate(events) if event["kind"] == "training_started")
    invocation = events[start:]
    if invocation[-1]["kind"] != "training_finished" or invocation[-1]["step"] != summary["step"]:
        raise ValueError("Wait for this invocation to finish before archiving its evidence")
    folder = directory / f"checkpoint-{summary['step']}"
    state = read_json(folder / "groth-state.json")
    if not state["complete"] or state["identity_hash"] != digest(identity):
        raise ValueError("Checkpoint identity is incomplete or inconsistent")
    required = ("adapter_model.safetensors", "optimizer.pt", "scheduler.pt", "rng_state.pth",
                "trainer_state.json", "groth-state.json", "judge-cache.sqlite")
    if any(not (folder / name).is_file() for name in required):
        raise ValueError("Checkpoint is missing required recovery state")
    metrics = [e for e in invocation if e["kind"] == "training_metrics" and "step_time" in e["metrics"]]
    if len(metrics) != 1 or metrics[0]["step"] != summary["step"]:
        raise ValueError("Archive each single-boundary pilot invocation separately")
    rollouts = [e for e in invocation if e["kind"] == "rollout"]
    if len(rollouts) != identity["config"]["gradient_accumulation_steps"]:
        raise ValueError("Pilot rollout count does not match the fixed generation budget")
    record = {**summary, "kind": "exploratory_single_grpo_boundary",
              "judge_identity": identity["judge"], "configuration": identity["config"],
              "resumed_from": invocation[0]["resumed_from"],
              "step_metrics": metrics[0]["metrics"],
              "reward_batch": next(e for e in invocation if e["kind"] == "reward_batch"),
              "checkpoint_state": state, "checkpoint_files": sorted(p.name for p in folder.iterdir()),
              "task_groups": {str(call): sorted({e["task_id"] for e in rollouts if e["reward_call"] == call})
                              for call in sorted({e["reward_call"] for e in rollouts})},
              "judge_seconds": [e["seconds"] for e in invocation if e["kind"] == "model_response"],
              "judge_failures": sum(e["kind"] == "judge_failure" for e in invocation),
              "pilot_updates_excluded_from_comparisons": True}
    with (folder / "adapter_model.safetensors").open("rb") as handle:
        record["adapter_sha256"] = hashlib.file_digest(handle, "sha256").hexdigest()
    if summary["step"] == 2:
        from safetensors import safe_open
        previous = directory / "checkpoint-1/adapter_model.safetensors"
        with safe_open(previous, framework="pt", device="cpu") as first, \
                safe_open(folder / "adapter_model.safetensors", framework="pt", device="cpu") as second:
            if set(first.keys()) != set(second.keys()):
                raise ValueError("Adapter structure changed across resumption")
            changes = [float((first.get_tensor(k)-second.get_tensor(k)).abs().max()) for k in first.keys()]
        record.update(changed_tensors=sum(c > 0 for c in changes), adapter_tensors=len(changes),
                      maximum_parameter_change=max(changes))
    destination = PROJECT / f"reports/development/feasibility-exploratory-single-step{summary['step']}.json"
    if destination.exists() and read_json(destination) != record:
        raise ValueError("Refusing to overwrite different archived pilot evidence")
    atomic_json(destination, record)
    log_path = destination.with_name(f"exploratory-single-pilot-step{summary['step']}.jsonl")
    log_text = "".join(json.dumps(e, ensure_ascii=False, allow_nan=False)+"\n" for e in invocation)
    if log_path.exists() and log_path.read_text(encoding="utf-8") != log_text:
        raise ValueError("Refusing to overwrite different archived pilot events")
    log_path.write_text(log_text, encoding="utf-8")
    return {"artifact": str(destination), "step": summary["step"], "judge_identity": identity["judge"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    print(json.dumps(archive(parser.parse_args().run_directory), indent=2))
