"""Interrupted evaluation must never mix checkpoints, prompts or generation budgets."""
import json

import pytest

from grothendieck_rlvr import evaluation
from grothendieck_rlvr.schema import Task, Verification


@pytest.mark.parametrize("mutation", ["weights", "tokenizer", "budget", "task", "prompt"])
def test_generation_resume_rejects_changed_inputs(tmp_path, monkeypatch, mutation):
    """A completed fixture is reusable only while its effective inputs remain fixed."""
    monkeypatch.setenv("GROTH_ROOT", str(tmp_path))
    adapter = tmp_path / "adapter"
    adapter.mkdir()
    (adapter / "adapter_config.json").write_text("{}")
    (adapter / "adapter_model.safetensors").write_bytes(b"fixture weights")
    (adapter / "tokenizer_config.json").write_text("{}")
    task = Task(id="fixture", problem="Find gcd(12,18).", answer="6", family="gcd",
                split="dev", provenance={})
    monkeypatch.setattr(evaluation, "evaluation_tasks", lambda split: [task])
    calls = []
    class FixtureGenerator:
        def __init__(self, *args):
            calls.append("load")

        def generate(self, *args):
            return {"response": "<final>6</final>", "response_tokens": 3,
                    "prompt_tokens": 5, "seconds": 0.0}
    monkeypatch.setattr(evaluation, "PolicyGenerator", FixtureGenerator)
    evaluation.generate("fixture", adapter, split="dev")
    evaluation.generate("fixture", adapter, split="dev")
    assert calls == ["load"]
    if mutation == "weights":
        (adapter / "adapter_model.safetensors").write_bytes(b"different weights")
    elif mutation == "tokenizer":
        (adapter / "tokenizer_config.json").write_text('{"chat_template": "changed"}')
    elif mutation == "budget":
        original = evaluation.read_json
        monkeypatch.setattr(evaluation, "read_json", lambda p: {
            **original(p), "max_completion_length": 17} if p.name == "study.json" else original(p))
    elif mutation == "task":
        task.problem = "Find gcd(6,12)."
    else:
        original = evaluation.policy_messages
        monkeypatch.setattr(evaluation, "policy_messages", lambda *a, **k:
                            original(*a, **k) + [{"role": "user", "content": "Different instruction"}])
    with pytest.raises(ValueError, match="configuration changed"):
        evaluation.generate("fixture", adapter, split="dev")
    assert calls == ["load"]


@pytest.mark.parametrize("mutation", ["notes", "target", "budget"])
def test_transfer_resume_rejects_changed_inputs(tmp_path, monkeypatch, mutation):
    """Keep recipient outcomes paired with the same source notes and target tasks."""
    monkeypatch.setenv("GROTH_ROOT", str(tmp_path))
    sources = [Task(id=f"source-{i}", problem="Fixture", answer="6", family=family,
                    split="transfer_source", provenance={}) for i, family in
               enumerate(("gcd", "lcm", "polynomial_multiplication", "dice"))]
    target = sources[0].model_copy(update={"id": "target", "split": "transfer_target",
                                          "source_id": sources[0].id})
    monkeypatch.setattr(evaluation, "load_tasks", lambda s: sources if s == "transfer_source" else [target])
    folder = tmp_path / "evaluations" / "fixture-notes"
    folder.mkdir(parents=True)
    (folder / "generation-config.json").write_text('{"split": "transfer_source"}')
    rows = [{"task_id": t.id, "response": "<notes>Fixture notes.</notes>"} for t in sources]
    note_path = folder / "generations.jsonl"
    note_path.write_text("\n".join(map(json.dumps, rows)))
    calls = []
    class FixtureTokenizer:
        def encode(self, value, **kwargs):
            return list(map(ord, value))

        def decode(self, value):
            return "".join(map(chr, value))
    class FixtureGenerator:
        def __init__(self, *args, **kwargs):
            self.tokenizer = FixtureTokenizer()
            calls.append("load")

        def generate(self, *args):
            return {"response": "<final>6</final>"}
    monkeypatch.setattr(evaluation, "PolicyGenerator", FixtureGenerator)
    monkeypatch.setattr(evaluation, "verify_answer", lambda *a: Verification(status="correct"))
    evaluation.transfer(["fixture-notes"])
    if mutation == "notes":
        rows[0]["response"] = "<notes>Different fixture notes.</notes>"
        note_path.write_text("\n".join(map(json.dumps, rows)))
    elif mutation == "target":
        target.problem = "Changed target"
    else:
        original = evaluation.read_json
        monkeypatch.setattr(evaluation, "read_json", lambda p: {
            **original(p), "max_completion_length": 17} if p.name == "study.json" else original(p))
    with pytest.raises(ValueError, match="configuration changed"):
        evaluation.transfer(["fixture-notes"])
    assert calls == ["load"]
