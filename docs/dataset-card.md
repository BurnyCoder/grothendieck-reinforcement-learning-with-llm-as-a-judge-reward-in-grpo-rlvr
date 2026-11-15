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
rewards. This repository publishes deterministic Reasoning Gym manifests,
provenance, model/runtime locks, protocol, code and generated research reports.
Model-generated results are pending unless explicitly recorded in saved results.

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
