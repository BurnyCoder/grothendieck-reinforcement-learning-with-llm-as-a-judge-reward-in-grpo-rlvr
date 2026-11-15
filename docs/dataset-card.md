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

Preregistered local Qwen/Gemma research on correctness-gated theory-building
rewards, including valid conceptual novelty relative to fixed reference approaches.
This repository publishes deterministic Reasoning Gym and SymPy-backed manifests,
provenance, model/runtime locks, protocol, code and generated research reports.
Model-generated results are pending unless explicitly recorded in saved results.
Development evidence includes failed Gemma and bounded-reasoning Qwen novelty
calibrations, as well as interrupted attempts. No comparative improvement is
established. Long training and locked audits remain blocked; the full negative
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
audits and comparative training stay blocked.

The registered v8 repair separates conceptual analysis from validity/quality
scoring, with an eight-specialist fallback if development qualification fails.
It retains modest credit, all thresholds, cases, labels and weights. Each role's
raw findings and latency are preserved; code derives novelty and aggregates the
reward. Complete matching development passes precede the full locked audits.
See `reports/amendments/2026-11-15-decomposed-judges.md`; neither new instrument
has yet qualified, and no comparative run has begun.

Source code and preregistration history:
https://github.com/BurnyCoder/grothendieck-reinforcement-learning-with-llm-as-a-judge-reward-in-grpo-rlvr

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
