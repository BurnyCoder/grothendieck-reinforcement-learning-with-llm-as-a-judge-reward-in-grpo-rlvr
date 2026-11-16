---
license: apache-2.0
language:
- en
task_categories:
- text-generation
tags:
- mathematics
- reinforcement-learning
- reasoning-gym
---

# Grothendieck RLVR research artifacts

The single [research collection](https://huggingface.co/collections/BurnyCoder/grothendieck-rlvr-6afa2f0ab898f347b91b71e8)
links these artifacts and the frozen upstream models. Project-trained adapters
remain pending training.

Preregistered local Qwen/Gemma research on correctness-gated theory-building
rewards, including valid conceptual novelty relative to fixed reference approaches.
This repository publishes deterministic Reasoning Gym and SymPy-backed manifests,
provenance, model/runtime locks, protocol, code and generated research reports.
Model-generated results are pending unless explicitly recorded in saved results.
Development evidence includes failed Gemma and bounded-reasoning Qwen novelty
calibrations, as well as interrupted attempts. No comparative improvement is
established. Qualification-study training and locked audits remain blocked; the full negative
results and their limitations are preserved in `reports/experiments/`.
The v5 attempt stopped on repeated reference/score contradictions; v6 executed
an explicit eligibility gate and was interrupted after the user clarified the
intended scoring construct. Rubric v7 permits modest credit for brief valid
connections without a further worked use, with higher credit for developed
frameworks. Raw and credited scores, caps and reasons remain separate. Weights
remain fixed; changed calibration contrasts now distinguish brief connections
from zero-novelty reference controls. The fresh v7 attempt failed its fixed
futility gate: developed frameworks ranked higher, but the control-credit
conditions failed. False-theory suppression was not reached. The generated
reports separate those checks and preserve every raw opinion.
Reference version v3 subsequently clarifies the commutative-polynomial and
ordinary biased-probability baselines. The rubric, case hashes and thresholds
remained fixed. The fresh trial also failed: probability control credit improved,
but brief-connection credit and a framework/control ranking still disagreed with
the constructed expectations. A routine reference excerpt was incorrectly used
as evidence of an additional connection's application. Exact substring checks
cannot certify that semantic relationship. The negative result is preserved in
`reports/experiments/qwen-v7-reference-scope-learnings.md`; remaining calibration,
audits and qualification-study training stay blocked.

The registered v8 two-call repair failed its fixed development gate. It credited
a brief valid commutator connection, but overcredited routine GCD/LCM mathematics
and missed developed uses. Full findings are preserved in
`reports/experiments/qwen-v8-two-stage-learnings.md`. The already-published
eight-specialist fallback is now selected by
`reports/amendments/2026-11-15-specialist-activation.md`.
It retains modest credit, all thresholds, cases, labels and weights. Each role's
raw findings and latency are preserved; code derives novelty and aggregates the
reward. Complete matching development passes precede the full locked audits.
See `reports/amendments/2026-11-15-decomposed-judges.md`. Neither new instrument
had qualified at that stage, and comparative runs had not begun.

Quoted-Qwen specialist development subsequently failed its unchanged futility
gate. False mathematical objections vetoed valid frameworks and the brief
commutator connection. Full evidence, selected exact mathematical checks and
limitations are in `reports/experiments/qwen-v8-specialist-learnings.md`.
Role-level issue counts and timings are generated from the stored findings.
Rubric-only Qwen specialist development also failed its fixed gate. Quoted Gemma
specialist development is deferred under the user's new instruction. The
`2026-11-16-exploratory-single-judge` amendment authorizes a separate single-call
training experiment despite unqualified judges. It preserves the reward, modest
connection credit, weights, thresholds and saved failures. Explicit experiment
names and report fields separate it from the still-gated qualified study. Neither
judge scores nor completed training can retroactively establish calibration.
The first single-call pilot then stopped on an exact-quotation contract failure
before an optimizer update. The `2026-11-16-indexed-evidence` amendment introduces
constrained passage IDs and code-based exact extraction under a new identity,
retaining the same scoring rubric and unqualified interpretation. Both the
failed pilot and its original profile are archived.
The repaired development pilot subsequently completed saving and resumption,
advanced the task position and changed adapter parameters. Its discarded updates
are execution evidence only. The generated pilot report and boundary records
retain timings, reward components, retries and checkpoint state. Ordinary baseline
generation was stopped and its prompted queue cancelled when the user prioritized
the smaller GPU experiment. Partial outputs and the larger configuration are
preserved. Comparative training and scored held-out evaluation remain pending.

The active `exploratory-small-gpu-v2` profile retains a Qwen3.5-0.8B BF16 LoRA
policy, frozen Qwen3.5-2B Q4_K_M GPU training judge and separate Qwen3.5-4B Q4_K_M
GPU evaluator. All model layers must fit on GPU; the memory/backward/save-resume
checks have completed before comparisons. The same-family judges remain unqualified. The
9B/Gemma setup is postponed rather than merged into the new experiment's results.
The initial small-GPU pilot stopped on repeated truncated judge JSON before an
optimizer boundary. The compact-output amendment bounds assessment fields and
retains full streaming logs with persistent append handles. Its new identity
preserves the prior failure, scoring rules and unqualified interpretation.
The compact-output pilot saved, resumed and changed adapter weights, but its
resumed batch earned no task reward. This demonstrates execution and recovery,
not mathematical improvement. Its adapters are excluded from comparative
initialization; see `reports/experiments/exploratory-small-gpu-v2-pilot.md`.

Further work on 10B+, 100B+ and 1T+ models, advanced agentic RL, Lean, and more
directly quantified rewards replacing LLM judgments is explicitly postponed until
after the current experiment sequence. See `docs/future-research.md` for candidate
metrics and limitations; these directions do not change the active configuration.
If development diagnostics establish that the small policy cannot solve the
present tasks, the user-authorized fallback is a separate easier-mathematics
experiment, preserving these manifests for larger models. The current pilot
contains correct completions, so no difficulty change has been activated. See
`reports/amendments/2026-11-16-task-difficulty-fallback.md`.

Source code and preregistration history:
https://github.com/BurnyCoder/grothendieck-reinforcement-learning-with-llm-as-a-judge-reward-in-grpo-rlvr

The README's [model execution order](https://github.com/BurnyCoder/grothendieck-reinforcement-learning-with-llm-as-a-judge-reward-in-grpo-rlvr#model-execution-order)
details inference, LoRA training, CPU/GPU model transitions, independent scoring
and frozen-recipient transfer, distinguishing queued work from planned work.

Data schema, split sizes, generator settings, reference checks and semantic
deduplication are specified in `reports/preregistration.md` and `data/manifest.lock.json`.
Manifests retain the original generator question, seed, index and version.
Polynomial equation instructions normalize rounding to nearest four decimals.
No model-generated code is executed. Final-answer verification does not prove
the surrounding explanation.

Reasoning Gym source: https://github.com/open-thought/reasoning-gym (Apache-2.0).
Project code is Apache-2.0. Upstream models, software and the attributed historical
quotation retain their respective licenses/notices. See `NOTICE`.

These synthetic tasks test narrow behavioral hypotheses; they do not establish
new mathematical discoveries, human preference alignment, or a latent-space
mechanism. Constructed judge calibration is separate from the locked policy test.

The pre-judgment amendment in `reports/amendments/2026-11-15-valid-novelty-and-ood.md`
adds a separately locked `test_ood` suite (`data/ood.lock.json`) covering grid
connectivity, polygon geometry, rational matrix rank and modular inverses.
These families are held out from project training, not asserted absent from
pretraining. Original primary and transfer manifests are unchanged. Fixed
novelty references and the six-criterion rubric are versioned with the code.
