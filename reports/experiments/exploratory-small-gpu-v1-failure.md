# exploratory-small-gpu-v1: judge output-budget failure

Generated from `reports/development/feasibility-small-gpu-v1-truncation.json`.

| Measure | Recorded value |
|---|---|
| Policy completions | 8 |
| Judge attempts | 3 |
| Accepted assessments | 0 |
| Saved optimizer boundaries | 0 |
| Sampled whole-device peak / capacity MiB | 7666 / 8151 |
| Request 1 seconds | 130.53 |
| Request 2 seconds | 142.26 |
| Request 3 seconds | 185.94 |

The frozen small judge repeated rationale text until its unchanged token budget ended inside a JSON string. Existing retries exhausted; invalid output was not converted to a reward. No optimizer boundary was reached. Full prompts, responses and failures remain in [reports/development/exploratory-small-gpu-v1-pilot-failure.jsonl](../../reports/development/exploratory-small-gpu-v1-pilot-failure.jsonl).

The memory number samples the whole device, including the judge and other GPU users. It is not the policy allocator peak. No GPU OOM was observed; a successful backward probe does not establish full GRPO recovery. Request time includes transport and logging, not only model decoding.

The [dated repair](../amendments/2026-11-16-compact-gpu-judge.md) adds bounded output fields and persistent append logging under a separate identity. It preserves the rubric, modest connection credit and qualification thresholds. Whether that repair completes training is a subsequent measurement, not a conclusion from this failed attempt.
