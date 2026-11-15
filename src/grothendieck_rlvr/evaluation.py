"""Separate policy generation, frozen-judge assessment and recipient transfer phases."""
import re
import time
from pathlib import Path

from .data import load_tasks
from .io import PROJECT, EventLog, atomic_json, digest, read_json, read_jsonl, root
from .prompts import policy_messages
from .verify import verify_answer


class PolicyGenerator:
    """Frozen local policy inference using the same selected unmodified base or a saved adapter."""
    def __init__(self, log: EventLog, adapter: Path | None=None, seed=42):
        from .training import load_policy
        self.model, self.tokenizer = load_policy(seed, adapter=adapter)
        self.log = log
        self.config = read_json(PROJECT / "configs/study.json")

    def generate(self, messages, seed=42, max_tokens=None) -> dict:
        """Deterministic visible-output generation, fully streamed and then saved as one record."""
        import torch
        from transformers import TextStreamer, set_seed
        from .training import encoded_prompt
        actual = getattr(self.tokenizer, "tokenizer", self.tokenizer)
        encoded = encoded_prompt(self.tokenizer, messages).to("cuda")
        limit = self.config["max_completion_length"] if max_tokens is None else max_tokens
        if encoded["input_ids"].shape[-1] + limit > 8192:
            raise ValueError("Transfer prompt exceeds the registered recipient context budget")
        log = self.log
        class Stream(TextStreamer):
            def on_finalized_text(self, text, stream_end=False):
                if text:
                    log.emit("policy_chunk", content=text)
        set_seed(seed)
        self.log.emit("policy_request", messages=messages, seed=seed, max_new_tokens=limit)
        start = time.monotonic()
        with torch.inference_mode():
            output = self.model.generate(**encoded, do_sample=False, max_new_tokens=limit,
                                         streamer=Stream(actual, skip_prompt=True, skip_special_tokens=True),
                                         pad_token_id=actual.eos_token_id)
        tokens = output[0, encoded["input_ids"].shape[-1]:]
        response = actual.decode(tokens, skip_special_tokens=True)
        result = {"response": response, "response_tokens": len(tokens),
                  "prompt_tokens": int(encoded["input_ids"].shape[-1]), "seconds": time.monotonic()-start}
        self.log.emit("policy_response", **result)
        return result


def evaluation_tasks(split="test"):
    """Test strata remain labelled and are never mixed with development records."""
    if split == "test":
        return sum((load_tasks(s) for s in ("test_fresh", "test_hard", "test_unseen")), [])
    if split not in ("dev", "transfer_source", "transfer_target"):
        raise ValueError("Unsupported evaluation split")
    return load_tasks(split)


def generate(run_id: str, adapter: Path | None=None, rising=False, split="test", seed=42) -> dict:
    """Resume by completed task ID; a partial file cannot silently redefine the experiment."""
    directory = root() / "evaluations" / run_id
    directory.mkdir(parents=True, exist_ok=True)
    config = {"run_id": run_id, "adapter": str(adapter) if adapter else None, "rising": rising,
              "split": split, "seed": seed, "models": read_json(PROJECT / "configs/models.lock.json")}
    path = directory / "generation-config.json"
    if path.exists() and read_json(path) != config:
        raise ValueError("Generation configuration changed for existing run")
    atomic_json(path, config)
    saved = read_jsonl(directory / "generations.jsonl")
    done = {row["task_id"] for row in saved}
    log = EventLog(directory / "events.jsonl")
    records = EventLog(directory / "generations.jsonl")
    tasks = evaluation_tasks(split)
    pending = [t for t in tasks if t.id not in done]
    if pending:
        generator = PolicyGenerator(log, adapter, seed)
        for task in pending:
            messages = policy_messages(task, rising=rising, request_notes=split == "transfer_source")
            result = generator.generate(messages, seed)
            records.emit("generation", task_id=task.id, family=task.family, split=task.split,
                         prompt=messages, **result)
    return {"run_id": run_id, "completed": len(tasks), "split": split}


def evaluate(run_id: str, judge) -> dict:
    """Run only after generation, allowing evaluation-model GPU offload separately."""
    directory = root() / "evaluations" / run_id
    config = read_json(directory / "generation-config.json")
    tasks = {t.id: t for t in evaluation_tasks(config["split"])}
    rows = read_jsonl(directory / "generations.jsonl")
    if len({r["task_id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate generated task records")
    output = directory / "scores.jsonl"
    previous = read_jsonl(output)
    if any(r["judge_identity"] != judge.identity for r in previous):
        raise ValueError("Evaluation judge changed within a run")
    done = {row["task_id"] for row in previous}
    log = EventLog(output)
    for row in rows:
        if row["task_id"] in done:
            continue
        task = tasks[row["task_id"]]
        verdict = verify_answer(task, row["response"])
        assessment = judge.assess(task, row["response"]) if verdict.correct else None
        quality = assessment.quality if assessment else 0.0
        log.emit("evaluation", task_id=task.id, family=task.family, split=task.split,
                 correct=verdict.correct, verification=verdict.model_dump(), theory=quality,
                 metric=float(verdict.correct)*quality, assessment=assessment.model_dump() if assessment else None,
                 response_tokens=row["response_tokens"], judge_identity=judge.identity,
                 response=row["response"], prompt=row["prompt"])
    scored = read_jsonl(output)
    summary = {"run_id": run_id, "expected": len(tasks), "scored": len(scored),
               "complete": len(scored) == len(tasks), "judge_identity": judge.identity}
    atomic_json(directory / "status.json", summary)
    return summary


def extract_notes(response: str) -> str:
    """Malformed/missing notes become an empty-note condition and are retained in analysis."""
    matches = re.findall(r"<notes>(.*?)</notes>", response, flags=re.S)
    return matches[0].strip() if len(matches) == 1 else ""


def transfer(source_run_ids: list[str], seed=42) -> dict:
    """A frozen unmodified recipient receives notes without exposing targets to note writers."""
    sources = load_tasks("transfer_source")
    targets = load_tasks("transfer_target")
    source_map = {t.id: t for t in sources}
    directory = root() / "transfer"
    directory.mkdir(parents=True, exist_ok=True)
    config = {"source_runs": source_run_ids, "seed": seed,
              "policy": read_json(PROJECT / "configs/models.lock.json")["policy"]}
    if (directory / "config.json").exists() and read_json(directory / "config.json") != config:
        raise ValueError("Transfer configuration changed; requires a separate amended run")
    atomic_json(directory / "config.json", config)
    note_sets = {}
    for run in source_run_ids:
        path = root() / "evaluations" / run
        if read_json(path / "generation-config.json")["split"] != "transfer_source":
            raise ValueError("Notes must have been generated on isolated source tasks")
        records = read_jsonl(path / "generations.jsonl")
        if {r["task_id"] for r in records} != set(source_map):
            raise ValueError("Generate every source note before recipient evaluation")
        note_sets[run] = {r["task_id"]: extract_notes(r["response"]) for r in records}
    log = EventLog(directory / "events.jsonl")
    scores = EventLog(directory / "scores.jsonl")
    done = {(r["condition"], r["task_id"]) for r in read_jsonl(scores.path)}
    generator = PolicyGenerator(log, adapter=None, seed=seed)
    tokenizer = getattr(generator.tokenizer, "tokenizer", generator.tokenizer)
    ordered = sorted(sources, key=lambda t: (t.family, t.id))
    # Equal family sizes make a one-family rotation a deterministic cross-family derangement.
    offset = len(ordered) // 4
    unrelated = {s.id: ordered[(i+offset) % len(ordered)].id for i, s in enumerate(ordered)}
    for target in targets:
        conditions = {"no_notes": (None, None)}
        for run, notes in note_sets.items():
            related = tokenizer.encode(notes[target.source_id], add_special_tokens=False)
            other = tokenizer.encode(notes[unrelated[target.source_id]], add_special_tokens=False)
            # Trim both directions to the same token count; never pad with answer-bearing target data.
            length = min(len(related), len(other), 1024)
            conditions[f"{run}:notes"] = (tokenizer.decode(related[:length]), unrelated[target.source_id])
            conditions[f"{run}:unrelated"] = (tokenizer.decode(other[:length]), unrelated[target.source_id])
        for condition, (notes, other_id) in conditions.items():
            if (condition, target.id) in done:
                continue
            result = generator.generate(policy_messages(target, notes=notes), seed)
            verdict = verify_answer(target, result["response"])
            scores.emit("transfer", task_id=target.id, source_id=target.source_id, family=target.family,
                        condition=condition, correct=verdict.correct, verification=verdict.model_dump(),
                        notes=notes, unrelated_source_id=other_id,
                        notes_tokens=len(tokenizer.encode(notes or "", add_special_tokens=False)), **result)
    summary = {"conditions": 1 + 2*len(source_run_ids), "target_count": len(targets),
               "records": len(read_jsonl(scores.path)), "config_hash": digest(config)}
    atomic_json(directory / "summary.json", summary)
    return summary
