"""Thin Unsloth + TRL orchestration with optimizer-boundary recovery.

https://unsloth.ai/docs/models/qwen3.5/fine-tune
https://huggingface.co/docs/trl/grpo_trainer
https://huggingface.co/docs/transformers/main_classes/trainer
"""
import inspect
import math
import os
import signal
import time
from pathlib import Path

from .calibration import require_calibration
from .data import load_tasks, validate_manifests
from .io import PROJECT, EventLog, atomic_json, digest, read_json, root
from .judge import Judge
from .prompts import policy_messages
from .reward import CompositeReward


def load_policy(seed=42, adapter: Path | None=None, training=False):
    """Import Unsloth first, use BF16, and keep every vision parameter frozen."""
    from unsloth import FastLanguageModel
    import torch
    from transformers import set_seed
    cfg = read_json(PROJECT / "configs/study.json")
    set_seed(seed)
    path = root() / "models/policy"
    if not (path / "config.json").exists():
        raise RuntimeError("Download the pinned policy checkpoint before model loading")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(adapter or path), dtype=torch.bfloat16, load_in_4bit=False,
        max_seq_length=cfg["max_prompt_length"] + cfg["max_completion_length"] if training else 8192,
        fast_inference=False,
    )
    if training and adapter is None:
        model = FastLanguageModel.get_peft_model(
            model, r=cfg["lora_rank"], lora_alpha=cfg["lora_alpha"], lora_dropout=cfg["lora_dropout"],
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            bias="none", use_gradient_checkpointing="unsloth", random_state=seed,
        )
    for name, parameter in model.named_parameters():
        if "visual" in name or "vision" in name:
            parameter.requires_grad_(False)
    if training:
        FastLanguageModel.for_training(model)
    else:
        model.requires_grad_(False)
        FastLanguageModel.for_inference(model)
    return model, tokenizer


def encoded_prompt(tokenizer, messages, max_length=None):
    """Use the model's own chat template, explicitly requesting visible nonthinking output."""
    actual = getattr(tokenizer, "tokenizer", tokenizer)
    text = actual.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    encoded = actual(text, return_tensors="pt", add_special_tokens=False)
    if max_length is not None and encoded["input_ids"].shape[-1] > max_length:
        raise ValueError("Prompt exceeds registered budget; refusing silent truncation")
    return encoded


def latest_complete_checkpoint(directory: Path) -> Path:
    """Ignore partially written checkpoints after a crash; prefer the newest complete one."""
    candidates = [p for p in directory.glob("checkpoint-*") if (p / "groth-state.json").exists()]
    if not candidates:
        raise FileNotFoundError("No complete optimizer-boundary checkpoint exists")
    return max(candidates, key=lambda p: int(p.name.split("-")[-1]))


def train(arm="theory", seed=42, resume=False, pilot=False, stop_after=None) -> dict:
    """Every experiment starts from the same base; only reward treatment and seed differ."""
    if arm not in ("theory", "correctness", "shuffled", "rubric"):
        raise ValueError("Unknown training arm")
    if not pilot:
        require_calibration()
        selection = read_json(PROJECT / "configs/policy-selection.json")
        if selection["policy"] != read_json(PROJECT / "configs/models.lock.json")["policy"]:
            raise RuntimeError("Selected checkpoint differs from the model lock")
    cfg = read_json(PROJECT / "configs/study.json")
    if pilot:
        cfg = {**cfg, "max_steps": 2, "save_steps": 1}
    manifest = validate_manifests()
    run_id = f"{'pilot-' if pilot else ''}{arm}-seed{seed}"
    directory = root() / "runs" / run_id
    directory.mkdir(parents=True, exist_ok=True)
    log = EventLog(directory / "events.jsonl")
    judge = None if arm == "correctness" else Judge(
        os.environ.get("GROTH_JUDGE_URL", "http://127.0.0.1:8081"),
        variant="rubric" if arm == "rubric" else "quoted", log=log)
    identity = {"arm": arm, "seed": seed, "config": cfg, "manifest": digest(manifest),
                "model": read_json(PROJECT / "configs/models.lock.json")["policy"],
                "judge": judge.identity if judge else None}
    config_path = directory / "run.json"
    if config_path.exists() and read_json(config_path) != identity:
        raise RuntimeError("Run configuration changed; use an amended experiment identifier")
    if config_path.exists() and not resume:
        raise RuntimeError("Existing run requires explicit --resume; cannot overwrite evidence")
    atomic_json(config_path, identity)
    model, tokenizer = load_policy(seed, training=True)
    import torch
    from datasets import Dataset
    from transformers import TrainerCallback
    from trl import GRPOConfig, GRPOTrainer
    tasks = load_tasks("dev" if pilot else "train")
    actual = getattr(tokenizer, "tokenizer", tokenizer)
    for task in tasks:
        encoded_prompt(tokenizer, policy_messages(task), cfg["max_prompt_length"])
    dataset = Dataset.from_list([{"prompt": policy_messages(t), "task_record": t.model_dump()} for t in tasks])
    reward = CompositeReward(judge, log, "correctness" if arm == "correctness" else arm, seed)
    checkpoint = latest_complete_checkpoint(directory) if resume else None
    if checkpoint:
        state = read_json(checkpoint / "groth-state.json")
        if state["identity_hash"] != digest(identity):
            raise RuntimeError("Checkpoint configuration mismatch")
        reward.calls = state["reward_calls"]
        if judge:
            import sqlite3
            with sqlite3.connect(checkpoint / "judge-cache.sqlite") as saved:
                saved.backup(judge.db)
    stopping = {"requested": False}
    def request_stop(signum, frame):
        stopping["requested"] = True
        log.emit("stop_requested", signal=signum, action="save at next optimizer boundary")
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    started = time.monotonic()

    class StateCallback(TrainerCallback):
        """Trainer saves optimizer/RNG/data position; sidecar adds reward/cache/config state."""
        def on_log(self, args, state, control, logs=None, **kwargs):
            values = logs or {}
            if any(isinstance(v, float) and not math.isfinite(v) for v in values.values()):
                raise FloatingPointError("Nonfinite trainer metric")
            log.emit("training_metrics", step=state.global_step, metrics=values,
                     elapsed_seconds=time.monotonic()-started,
                     peak_gpu_allocated_bytes=torch.cuda.max_memory_allocated(),
                     peak_gpu_reserved_bytes=torch.cuda.max_memory_reserved())

        def on_step_end(self, args, state, control, **kwargs):
            if stopping["requested"] or (stop_after is not None and state.global_step >= stop_after):
                control.should_save = True
                control.should_training_stop = True
            return control

        def on_save(self, args, state, control, **kwargs):
            folder = directory / f"checkpoint-{state.global_step}"
            if judge:
                judge.checkpoint(folder / "judge-cache.sqlite")
            atomic_json(folder / "groth-state.json", {
                "identity_hash": digest(identity), "reward_calls": reward.calls,
                "global_step": state.global_step, "epoch": state.epoch,
                "data_seed": cfg["data_seed"], "complete": True,
            })
            log.emit("checkpoint", step=state.global_step, path=str(folder), status="complete")

    args = dict(output_dir=str(directory), run_name=run_id, max_steps=cfg["max_steps"],
                per_device_train_batch_size=cfg["per_device_train_batch_size"],
                gradient_accumulation_steps=cfg["gradient_accumulation_steps"], num_generations=cfg["num_generations"],
                learning_rate=cfg["learning_rate"], warmup_ratio=cfg["warmup_ratio"], lr_scheduler_type="linear",
                loss_type="dr_grpo", scale_rewards=False, beta=cfg["beta"], epsilon=.2,
                max_completion_length=cfg["max_completion_length"], temperature=1.0, top_p=1.0,
                num_iterations=1, bf16=True, gradient_checkpointing=True, max_grad_norm=1.0,
                optim="adamw_torch", weight_decay=0.0, seed=seed, data_seed=cfg["data_seed"],
                save_steps=cfg["save_steps"], save_total_limit=3, save_only_model=False,
                logging_steps=1, report_to="none", remove_unused_columns=False,
                use_vllm=False, dataloader_num_workers=0, shuffle_dataset=False)
    # Manifests already use data_seed order. TRL v1.15's RepeatSampler otherwise uses
    # args.seed (not data_seed): https://github.com/huggingface/trl/blob/v1.15.0/trl/trainer/grpo_trainer.py
    # Newer TRL removed max_prompt_length; explicit token checking above preserves its contract.
    fields = inspect.signature(GRPOConfig).parameters
    if "max_prompt_length" in fields:
        args["max_prompt_length"] = cfg["max_prompt_length"]
    if "chat_template_kwargs" in fields:
        args["chat_template_kwargs"] = {"enable_thinking": False}
    trainer = GRPOTrainer(model=model, processing_class=actual, reward_funcs=reward,
                          args=GRPOConfig(**args), train_dataset=dataset, callbacks=[StateCallback()])
    torch.cuda.reset_peak_memory_stats()
    log.emit("training_started", identity=identity, resumed_from=str(checkpoint) if checkpoint else None)
    result = trainer.train(resume_from_checkpoint=str(checkpoint) if checkpoint else None)
    trainer.save_model(str(directory / "adapter"))
    actual.save_pretrained(directory / "adapter")
    summary = {"run_id": run_id, "step": trainer.state.global_step, "metrics": result.metrics,
               "elapsed_seconds": time.monotonic()-started,
               "peak_gpu_allocated_bytes": torch.cuda.max_memory_allocated(),
               "peak_gpu_reserved_bytes": torch.cuda.max_memory_reserved(),
               "completed": trainer.state.global_step == cfg["max_steps"], "pilot": pilot}
    atomic_json(directory / "summary.json", summary)
    log.emit("training_finished", **summary)
    return summary


def memory_probe(seed=42) -> dict:
    """Development-only worst-length backward check, with no adapter update retained."""
    model, tokenizer = load_policy(seed, training=True)
    import torch
    cfg = read_json(PROJECT / "configs/study.json")
    length = cfg["max_prompt_length"] + cfg["max_completion_length"]
    token = getattr(tokenizer, "tokenizer", tokenizer).encode(" mathematics", add_special_tokens=False)[0]
    ids = torch.full((1, length), token, dtype=torch.long, device="cuda")
    labels = ids.clone()
    labels[:, :cfg["max_prompt_length"]] = -100
    torch.cuda.reset_peak_memory_stats()
    start = time.monotonic()
    loss = model(input_ids=ids, attention_mask=torch.ones_like(ids), labels=labels).loss
    loss.backward()
    torch.cuda.synchronize()
    if not torch.isfinite(loss):
        raise FloatingPointError("Worst-length backward loss is not finite")
    result = {"kind": "maximum_length_backward", "length": length, "microbatch": 1,
              "seconds": time.monotonic()-start, "loss": float(loss.detach().cpu()),
              "peak_gpu_allocated_bytes": torch.cuda.max_memory_allocated(),
              "peak_gpu_reserved_bytes": torch.cuda.max_memory_reserved(), "pilot_updates_discarded": True}
    atomic_json(root() / "feasibility/memory.json", result)
    return result
