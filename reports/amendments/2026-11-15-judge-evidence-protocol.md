# Evidence-first judgment and bounded development calibration

Date: 2026-11-15. Development-informed change, published before v4 inference.
No locked judge audit or comparative training/evaluation has begun. The BF16
policy pilot has completed a saved and resumed optimizer update; its adapters
remain excluded from comparative initialization.

The clean standalone Gemma v3 attempt produced a shortened evidence quote with
an inserted ellipsis. Exact-substring validation rejected it. A subsequent
request with the same deterministic settings did produce an acceptable response;
identical settings are not a bitwise-determinism guarantee. The accepted
conventional GCD and LCM explanations received no novelty credit. Qwen's earlier
v3 development observations still overcredited conventional arguments. These
observations are neither a completed calibration nor population error estimates.
Full requests, responses, failures and interrupted output are preserved in
[`development/calibration-gemma-v3-standalone.jsonl`](../development/calibration-gemma-v3-standalone.jsonl).
Latency and accepted scores are regenerated in the
[development report](../experiments/development-runtime.md).

## Protocol change

Rubric v4 keeps all six criteria, weights, ordinal anchors, conventional references,
validity gates and quotations. Each criterion now emits exact evidence and a
concise rationale before its numeric score. An excerpt must be one contiguous
candidate substring; multiple fragments require separate array entries. A
validation failure supplies its location and previous invalid assessment in
the next request. This is contract-repair feedback, not a request for a higher
score. The original problem, candidate, reference and externally verified
correctness remain unchanged. Prior assessments are untrusted. At most three
total attempts are permitted; persistent failures terminate rather than become
zero rewards. Only the latest feedback is retained, bounding context growth.
Transport failures do not introduce invented validation feedback.

The [published MT-Bench prompts](https://github.com/lm-sys/FastChat/blob/main/fastchat/llm_judge/data/judge_prompts.jsonl)
also request explanation before ratings. This motivates a development test;
it does not establish that ordering improves our judges. The
[literature review](../literature-review.md#what-would-constitute-evidence)
discusses contrary and setting-dependent evidence. Pydantic preserves declared
field order in its [JSON schema](https://docs.pydantic.dev/latest/concepts/models/#field-ordering).
The ordered fields and repair protocol are explicitly included in judge identity,
so old opinions and calibration results cannot silently pass the new gates.

## Calibration scheduling and stopping

Keep every constructed case, mathematical label, split and acceptance threshold.
Within both case lists, test novelty contrasts before the general-theory cases.
Require at least 80% preference accuracy and 90% false-theory suppression in
each stratum. As previously specified, a novelty preference requires both a
higher composite theory score for the justified bridge and zero novelty credit
for its conventional counterpart.

Development runs may stop as failed when even success on every remaining case
would not reach a required threshold. For each metric and stratum, the exact
upper bound is `(observed passes + untested cases) / planned cases`. Save all
observations, denominators and bounds with `complete: false` and the explicit
stopping reason. This cannot accept a partial run or extend sampling to obtain
success. Rates from partial runs are labeled as observed partial rates. Locked
audits still run the complete fixed suite and cannot be restarted through the
development-reset option. A completed pass must match both the judge identity
and the calibration protocol/case identity.

This change reduces wasted development inference when failure is already
determined. It is not sequential significance testing and does not alter the
primary behavioral hypotheses, confidence intervals or acceptance targets.
Publish negative development results and any later protocol amendment. Existing
audit cases share mathematical templates with development cases, an acknowledged
limitation; passing them does not establish broad mathematical reliability.
