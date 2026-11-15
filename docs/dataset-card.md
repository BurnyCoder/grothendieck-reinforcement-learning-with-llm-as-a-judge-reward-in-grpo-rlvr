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
Rubric v5 adds an explicit reference-comparison record and rejects inconsistent
positive novelty scores. It preserves the reward weights and calibration cases;
its mathematical grading reliability remains to be tested.

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
