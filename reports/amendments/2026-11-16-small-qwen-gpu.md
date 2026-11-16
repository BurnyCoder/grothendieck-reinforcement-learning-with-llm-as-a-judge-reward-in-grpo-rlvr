# Smaller Qwen3.5 models fully on GPU

Date: 2026-11-16, Europe/Berlin. Status at registration: no inference with the
new model combination has occurred. The user requested postponing the current
larger-model setup and prioritizing smaller/quantized Qwen3.5 models that can run
fully on GPU during training. This amendment is published with tested code before
the new pilot or comparative model runs.

## Question and scope

Does the same correctness-gated, single-call theory/novelty reward produce useful
behavior relative to correctness-only GRPO when the trainable policy and frozen
judge are small enough to stay on this machine's GPU? This is a model-scale and
runtime intervention, not a pure comparison of CPU versus GPU arithmetic. Both
the policy and judge change, so any difference from older development results
cannot identify the causal effect of GPU placement alone.

The original qualification study and `exploratory-single-v2` are deferred. The
[stop record](../development/exploratory-single-v2-postponed.json) preserves the
partial ordinary baseline; the prompted queue was stopped first. Completed
answers, pilot checkpoints and failed judgments remain available. The
[configuration archive](../../configs/history/exploratory-single-v2/README.md)
identifies the exact earlier code/configuration needed for later resumption.

## Models and rationale

| Role | New frozen choice | Runtime |
|---|---|---|
| Policy and frozen recipient | [Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B) | BF16 weights; policy trains language LoRA adapters on GPU; recipient stays unmodified |
| Training judge | [Qwen3.5-2B Q4_K_M](https://huggingface.co/unsloth/Qwen3.5-2B-GGUF) | Frozen llama.cpp GGUF, all layers on CUDA, resident alongside policy |
| Evaluation judge | [Qwen3.5-4B Q4_K_M](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF) | Frozen llama.cpp GGUF, all layers on CUDA, after policy generation exits |

Repository revisions and isolated download directories are in
[`models.lock.json`](../../configs/models.lock.json); content hashes are in
[`artifacts.lock.json`](../../configs/artifacts.lock.json). The prior 2B policy,
9B training judge and 12B Gemma evaluation judge are not part of this initial run.
No Phi or remote inference is introduced.

[Unsloth's Qwen3.5 guide](https://unsloth.ai/docs/models/qwen3.5/fine-tune) supports
the smaller policy and the non-vLLM GRPO route, while cautioning against Qwen3.5
4-bit QLoRA. Therefore the policy remains BF16 LoRA and only frozen judges use
4-bit quantization. Published fine-tuning memory figures do not establish GRPO
feasibility with a second resident model. The
[pinned llama.cpp server](https://github.com/ggml-org/llama.cpp/blob/b1b770d90d94cad9e9ea5b993bdbc383a522fb28/tools/server/README.md)
supports explicit GPU layers/device and disabling automatic memory fitting.
The registered launcher requests all layers and CUDA0, with fitting disabled.
Confirm full layer offload from server logs and CUDA placement of every policy
parameter; do not silently spill model layers to CPU. Tokenization, mathematical
verification, logging and command orchestration still use CPU.

## Fixed protocol and predictions

Use `exploratory-small-gpu-v1` and distinct run names, model directories, judge
identities and transfer artifacts. Retain the v7 rubric, indexed evidence,
reference anchors, six weights, quoted framing, one accepted judgment per
correct solution, modest credit for valid connections and `R=C(1+0.5T)`.
Keep bounded contract/transport retries; never reroll unfavorable valid scores.
Incorrect/invalid answers receive zero; unsupported theory receives no bonus.
Infrastructure failure remains an explicit failure rather than an incorrect answer.

Preserve the locked data, 64 updates per arm, four-completion groups, microbatch 1,
accumulation 8, completion limit 2,048, rank 16/alpha 32/dropout 0, learning rate
1e-5, 10% warmup, Dr. GRPO, no reward standard-deviation scaling and KL 0.04.
All comparative adapters start from the same unmodified 0.8B checkpoint. Policy
training prompts remain ordinary in both reward arms. Evaluation stays greedy,
with the original visible-output/context budgets. Judge request budgets and
deterministic decoding are unchanged; only frozen weights/runtime are replaced.

H1 remains improved mean verified-correctness-weighted theory quality relative
to correctness-only GRPO. The original +0.05 target, paired 95% interval and
three-percentage-point accuracy noninferiority margin remain descriptive targets
for this exploratory track. No improvement, worse correctness, or higher reward
without evaluation/transfer improvement count against the behavioral hypothesis.
No number of seeds converts unqualified judging into confirmatory evidence.

The 400 primary problems, separate 200 OOD problems, and 100-source/four-target
transfer design remain fixed. Preserve paired problem-level, stratum-aware
bootstrap analysis and source-clustered transfer intervals. The two frozen judges
now belong to the same Qwen family; the former cross-family check is deferred.
Correlated errors and weak small-model mathematical judgments are explicit
limitations. Verified recipient accuracy and correctness remain necessary checks.

The 80%/90% calibration thresholds and original labels are unchanged. Do not
claim calibration or open the locked audit to tune these smaller models. The
user's previously authorized noisy-judge experiment continues without requiring
a new calibration pass. Future qualification is a separately registered study.

## Execution and stopping rules

1. Publish this amendment, locked configuration, documentation and tested code.
2. Load the 2B judge fully on GPU. Measure a maximum-length backward pass with
   the 0.8B policy co-resident, then a four-completion-group pilot saving boundary
   one and resuming to a nonzero update at boundary two. Record total device
   memory separately from PyTorch's allocator, latency, outputs and recovery.
   Discard all pilot updates. An OOM, CPU model fallback or persistent contract
   failure blocks comparative runs until a dated repair; no silent size/budget change.
3. Publish feasibility evidence. Generate ordinary and rising-sea prompted 0.8B
   baselines, then train theory and correctness-only seed 42. Produce primary/OOD
   outputs and source notes, unload policy/judge, and score with the 4B evaluator.
4. Run the frozen 0.8B recipient on the fixed targets and conditions, with all
   source notes produced first. Publish the first comparison, including negative
   findings. Then continue matched seeds 43/44 and seed-42 shuffled/rubric controls.

Publish after each training/evaluation milestone. Preserve interrupted and failed
runs. Do not pick test checkpoints or extend sampling for significance. Measure
the smaller configuration before projecting its runtime; previous CPU timings do
not forecast this experiment. Retain the one-week planning budget and explicitly
report any unfinished experiments rather than reducing matched sample sizes.

Future larger models, alternative policy quantization, shorter outputs, different
judges or changed rubrics require dated amendments and separate identities. This
registration makes no speedup or learning claim before measurements exist.
