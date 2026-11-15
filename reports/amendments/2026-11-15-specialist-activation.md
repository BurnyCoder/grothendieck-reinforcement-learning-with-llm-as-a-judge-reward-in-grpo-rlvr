# Activate the preregistered specialist fallback

Date: 2026-11-15. This activation follows the conditional decision in the
[decomposed-judge amendment](2026-11-15-decomposed-judges.md), published before
the two-call experiment. It changes the selected protocol to `specialists-v1`.
It does not revise either protocol's prompts, schemas, aggregation, model,
runtime, cases, labels, reference descriptions, weights or acceptance thresholds.

The first required two-call configuration, quoted Qwen, failed the registered
development futility rule. Its [saved result](../development/calibration-qwen-v8-two-stage-dev.json)
and [failure analysis](../experiments/qwen-v8-two-stage-learnings.md) are preserved.
The remaining two-call configurations are not run: any required development
failure activates the fallback. No two-call partial result qualifies it.

The complete specialist specification and tested implementation were already
published in [PR 36](https://github.com/BurnyCoder/grothendieck-reinforcement-learning-with-llm-as-a-judge-reward-in-grpo-rlvr/pull/36).
The [original integrity record](../development/judge-decomposed-protocol-integrity.json)
fixes all specialist identities. The
[activation check](../development/judge-specialist-activation.json) verifies
that the selected identities and case/reference hashes still match that record.
The full offline test suite passed with the specialist protocol selected;
its [machine-readable result](../verification-specialist-activation.xml) checks
implementation behavior, not mathematical calibration.
This activation and the archived outcome must be published to GitHub, Hugging
Face and Pages before specialist inference begins.

Run fresh development in the registered order: Qwen quoted, Qwen rubric-only,
then Gemma quoted. Every configuration must completely pass. Only then freeze
the instrument and run all full locked audits. A failed audit blocks training
and cannot be rerun for qualification. A further repair requires a dated amendment
and newly reserved audit cases. A failed specialist development attempt is also
retained; no additional repair is specified by this activation.

All specialist calls remain sequential and reuse the frozen local weights.
Every specialist sees the original candidate. Only development receives another
role's proposed additions, as untrusted hypotheses. Code aggregates the findings;
substantive mathematical objections veto the theory bonus. Valid brief connections
retain modest credit. Missing or invalid outputs cause bounded retries or explicit
failure, never an invented score. Existing stage caches support interruption recovery.

Measure this protocol's runtime separately. Its qualification is an empirical
question; decomposition is motivated by [DnA-Eval](https://aclanthology.org/2025.coling-main.156/),
not a reliability guarantee. The fixed comparative budgets and evaluation sizes
remain unchanged. If qualification succeeds, refresh pilot throughput and recovery,
discard pilot updates, and follow the registered experiments. Report unfinished
work if the remaining week is insufficient.
