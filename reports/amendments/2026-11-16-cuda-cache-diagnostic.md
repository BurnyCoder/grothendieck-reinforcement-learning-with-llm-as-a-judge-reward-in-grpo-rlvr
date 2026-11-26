# Development diagnostic for CUDA allocator-cache growth

Registered 2026-11-16, after the interrupted first comparative training attempt
and before inference with the cache-release intervention.

## Observation and hypothesis

The preserved `exploratory-small-gpu-v2-theory-seed42` run accumulated CUDA
reserved memory across updates while peak allocated tensor memory stayed nearly
constant. Later steps took substantially longer. A stop request saved at the next
optimizer boundary. The generated [execution report](../experiments/exploratory-small-gpu-v2-memory-growth.md)
contains the recorded steps and timings; this is an incomplete run, not a complete
comparison or a negative finding about the theory reward.

[PyTorch distinguishes allocated tensor memory from reserved allocator memory](https://docs.pytorch.org/docs/2.14/notes/cuda.html#memory-management).
Its [empty-cache operation](https://docs.pytorch.org/docs/2.14/generated/torch.cuda.memory.empty_cache.html)
releases unused cached blocks to other GPU applications. It does not release live
tensors or establish that any particular memory-growth mechanism is responsible.
The working hypothesis is that releasing unused cache often enough will prevent
the observed accumulation while the policy shares the GPU with the judge.

Use the existing [Transformers training argument](https://huggingface.co/docs/transformers/v5.17.0/main_classes/trainer)
`torch_empty_cache_steps=1`. The pinned
[Trainer implementation](https://github.com/huggingface/transformers/blob/v5.17.0/src/transformers/trainer.py)
checks this condition inside `training_step`; with gradient accumulation, it can
therefore clear cache on each microbatch, not just once per optimizer update.
The pinned [TRL implementation](https://github.com/huggingface/trl/blob/v1.15.0/trl/trainer/grpo_trainer.py)
delegates that method to its parent. No optimizer, loss, model, rubric, judge
threshold, data, or sequence-length change is proposed here.

## Fixed development procedure

The versioned preset is [cache-release-v1](../../configs/runtime-diagnostics.json).
It requires `--pilot --exploratory`, theory reward and seed 42, and records its
complete preset in a separate run identity. It cannot modify a comparative arm
or overwrite the earlier two-update pilot.

- Start from the unmodified selected policy and a fresh language LoRA adapter.
- Use only the existing development manifest and the unchanged frozen 2B GPU
  training judge, including the same prompt, context, output and retry limits.
- Keep four completions, microbatch one, accumulation eight, the registered
  sequence lengths, learning rate, warmup fraction, loss, KL and data order.
- Run 16 optimizer updates with checkpoint saves every eight updates. Stop after
  the first complete checkpoint, then resume the same diagnostic to completion.
- Log both current and peak allocated/reserved policy memory. Sample whole-device
  memory separately; it includes the judge and other desktop GPU consumers.
- Preserve every prompt, response, reward, failure, checkpoint and timing. Discard
  all diagnostic updates from subsequent comparative initialization.

Commands, after publication:

```bash
bash scripts/run.sh train --exploratory --pilot --runtime-diagnostic cache-release-v1 --arm theory --seed 42 --stop-after 8
bash scripts/run.sh train --exploratory --pilot --runtime-diagnostic cache-release-v1 --arm theory --seed 42 --resume
```

## Decision and limits

The intervention passes this bounded execution check only if all updates and
resumption complete without OOM or exhausted infrastructure retries, the policy's
peak reserved memory remains at most 4.5 GiB, and the range of current reserved
memory across the final four updates is at most 0.5 GiB. These are development
resource criteria, separate from the unchanged judge calibration thresholds.
Inspect all logged memory and timing trajectories; do not infer improvement in
mathematical quality from this diagnostic. Report failure if any condition fails.
Changing the intervention or criteria requires a new dated diagnostic.

The earlier training attempt and this development probe use different tasks and
different warmup horizons. Their times do not estimate an isolated causal speedup.
The probe checks an operational hypothesis; it cannot guarantee every later run's
memory use. A pass would justify a separate published activation for all matched
training arms under a new identity, starting each arm again from the same original
checkpoint. The interrupted comparison's updates remain excluded. Existing
baseline generations may be reused only after verifying unchanged inference
bytes, task IDs, prompts and decoding settings, with explicit provenance.

No held-out mathematical scores were inspected to choose this intervention.
The original calibration gates, modest valid-connection credit, reward weights,
sample sizes, and 64-update comparative budgets remain unchanged.

**Record update, 2026-11-26.** The [independent audit](../reviews/2026-11-26-scientific-audit.md) recovered partial optimizer events. The required save/resume and end-of-run memory measurements were never reached. The original decision rule above remains the historical registration.
