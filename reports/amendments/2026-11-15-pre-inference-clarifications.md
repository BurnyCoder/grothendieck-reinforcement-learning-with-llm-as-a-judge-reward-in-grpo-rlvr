# Pre-inference implementation clarifications

2026-11-15. Written before any model inference or experimental result.
The hypotheses, acceptance criteria, task counts, seeds and reward formula are unchanged.

1. Transfer note pairs are truncated on both sides to the shorter recipient-token
   length, with a cap of 1024 tokens. This makes related/unrelated lengths exactly
   matched without repeating unrelated text or inventing padding. Full source
   notes are retained. Recipient inference has an 8192-token context ceiling;
   training keeps the registered prompt/completion limits. This additional
   note-length choice was not explicit in the original registration.
2. Training reads the already deterministically shuffled manifest without further
   trainer shuffling. Inspection of the pinned
   [TRL sampler](https://github.com/huggingface/trl/blob/v1.15.0/trl/trainer/grpo_trainer.py)
   found that it uses the policy seed rather than `data_seed`. Disabling that
   second shuffle enforces the registered matched prompt order across arms/seeds.
3. Package selection explicitly requires the current released Unsloth and honors
   its compatibility ceilings. The resolved exact environment is `uv.lock`.
   An older unconstrained resolution was interrupted before installation/model use.

These are pre-inference engineering choices, not changes selected from comparative
results. The OS restart interrupted downloads and installation, not training.
Saved manifests and the completed offline test report survived; processes were
resumed using the same locked versions and model revisions.
