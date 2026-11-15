# Execute declared novelty eligibility in reward code

Date: 2026-11-15. Development-informed amendment. Publish this protocol and its
tested implementation before fresh inference. No locked audit, comparative
policy generation or comparative training has begun.

## Observed problem and hypothesis

The [v5 attempt](../experiments/qwen-v5-contract-learnings.md) stopped because
all permitted retries paired a within-reference decision with positive novelty.
The reference classification was compatible with the constructed control label,
but the numerical score contradicted it. This is one observed failure pattern,
not evidence of reliable classification on the full suite.

Hypothesis: executing the eligibility rule in code can prevent this particular
contradiction from awarding novelty or exhausting retries. Whether the complete
instrument distinguishes useful bridges from conventional or false theory
remains an empirical question. The [literature review](../judge-inference-review.md)
motivates explicit prerequisites. We adopt neither a learned score mapping nor
human-agreement claims from that literature.

## Fixed assessment-to-reward contract

Preserve every raw criterion score, rationale, excerpt and declaration. Define
eligibility E to require all of:

- `theory_validity == supported`;
- `novelty_comparison.relation == beyond_reference`;
- nonempty `addition_evidence` and `use_evidence`.

For raw novelty score s_N in {0,1,2,3,4}, effective normalized novelty is
N = E * s_N / 4. For supported theory, T is the unchanged weighted sum of the
other five normalized scores plus 0.20*N. Otherwise T=0. The scalar remains
R=C*(1+0.5*T). Holding eligibility and all other scores fixed, increasing valid
novelty increases reward. Conventional supported theory keeps its other scores.

This replaces the v5 cross-field exception with an explicit eligibility gate.
Positive raw novelty can now be retained even when it earns zero credit. Each
assessment, cache hit, rollout and evaluation records `novelty_credit`, containing
the raw and effective 0–4 scores, eligibility, withheld flag and gate reasons.
Calibration result rows also retain this information. The dashboard presents
these records beside the unchanged raw opinion. Historical results keep their
original stored scores; v5 is not retrospectively declared a pass.

Exact nonempty excerpt validation, required fields, score bounds and positive
criterion evidence checks remain strict. Fabricated excerpts, invalid JSON,
transport failures and verifier failures still retry or terminate. The new gate
does not excuse a malformed assessment or turn an infrastructure failure into
an incorrect answer. It enforces declarations, not mathematical truth: a false
`beyond_reference` or `supported` decision can still award an undeserved bonus.

Rubric v6 adds an explanation of this gate to v5. The reference boundary, ordinal
anchors, six weights and quoted passage are unchanged. Models, inference/runtime
settings, references, cases, labels, case order and numerical thresholds remain
fixed. The new `declared-novelty-eligibility-v1` protocol and prompt are bound
into cache, calibration and run identities. The ablation uses the same gate and
rubric, removing only historical framing. This is a changed reward instrument,
not an isolated causal test of the added prompt paragraph.

## Validation and decision rules

Offline tests first reproduce the old failure, then require transparent
withholding for within-reference, unresolved and missing-construction/use
decisions; retention of other theory credit; preserved raw records on cache
hits and rollouts; rejection of fabricated evidence; and invalidation of the
old identity. Existing correctness, unsupported-theory, monotonicity and
recovery checks still apply. These fixtures do not validate LLM judgment.
The [template-capacity record](../development/judge-context-v6.json) checks the
loaded Qwen template without inference, using a synthetic maximum-length
candidate. Its remaining space is not a guarantee for all tasks or retries.

Run one fresh Qwen quoted development attempt. Only a complete pass permits
the Gemma quoted and Qwen rubric-only development attempts, followed by the
untouched complete audits. Apply existing gates to effective T and N, the
quantities used in reward. Report raw/effective differences separately. A pass
therefore concerns the combined code-and-judge instrument, not the model's
internal score consistency. Preserve all failures and stop dependent runs.

Repeated development use risks overfitting public mathematical templates; the
audit changes values but shares those templates. No claim of independent human
validation follows. Keep primary, secondary OOD, transfer and matched training
budgets unchanged. Refresh throughput before comparative runs. This amendment
does not establish that the full comparison sequence fits the remaining week.
