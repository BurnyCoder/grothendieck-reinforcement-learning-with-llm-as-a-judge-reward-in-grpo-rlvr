# Specialist development calibration

Date: 2026-11-15. Status: failed under the registered development futility rule.
The [saved result](../development/calibration-qwen-v8-specialists-dev.json) and
[generated case table](calibration-training_judge-quoted-dev-b33cb353.md) supply
all rates, observed counts and the best-possible final bound. The unobserved
general-theory and false-theory cases are not counted as successes or errors.
No qualification or training result is claimed.

Full timestamped requests, streamed outputs, rejected and accepted findings are
preserved in the [trial log](../development/qwen-v8-specialists-dev.jsonl), with
its [identity lock](../development/qwen-v8-specialists-dev.lock.json).
The generated [runtime report](development-runtime.md) separates request timings,
accepted stage timings and issue declarations. An excerpt validation failure
triggered the bounded retry; it was not treated as a semantic score or as an
incorrect final answer. Every completed combined assessment was vetoed by a
declared mathematical issue.

## Intervention and controls

The [activation amendment](../amendments/2026-11-15-specialist-activation.md)
selected the previously published specialist protocol after the required
two-call configuration failed. It uses the same frozen Qwen model, reference
descriptions, development cases, labels, rubric weights and acceptance gates.
The roles run sequentially. Only the development role sees another role's
proposed additions, explicitly marked as untrusted. No role sees the paired
answer or its calibration label. The aggregation has no synthesis model.

This is a development intervention, not a controlled estimate of the causal
effect of decomposition across models, seeds or unseen problem types. The
first trial and all failed judgments remain part of the record.

## Observed mathematical disagreements

In the GCD example, the validity role objects that the general pair
`2n, 3n` does not match the requested instance. Substituting the common scale
does match it. The economy role's later objection explicitly acknowledges the
matching substitution while still classifying the presentation as a
contradiction. The development role also treats the omitted substitution as
an unsupported mathematical claim. These are objections to a valid elementary
specialization, rather than counterexamples to the asserted framework.

In the LCM example, the development role recognizes the subgroup construction,
the use of cosets for shifted schedules, a further consequence and its boundary.
It nevertheless reports an unsupported claim because the common scale is not
explicitly substituted into the final instance. The validity role independently
raises the same omission. Both receive the original response, but development
does not receive the validity finding. Similar objections in this record do not
provide an estimate of statistical dependence between role errors.

The code preserves these mathematical objections and applies the specified
veto. It does not treat an overall `supported` verdict, positive criterion
scores or our subsequent disagreement as permission to erase an issue. Exact
source excerpts establish attribution, not the truth of the judge's objection.

The polynomial validity role accepts the quadratic-algebra framework in its
overall verdict but objects that its norm calculation needs another explicit
expansion or an isomorphism argument. The stated norm and evaluation maps
already reduce this step to the elementary difference-of-squares identity.
The [exact arithmetic and symbolic checks](../development/specialist-objection-math-check.json),
with [reproduction code](../development/check_specialist_objections.py), confirm
the disputed substitutions, quotient-ring product and composition identity.
They check these selected steps; they neither certify every explanatory claim
nor override the recorded judge findings.

The polynomial generality role provides a particularly direct mismatch: it
describes the zero-divisor statement as mathematically correct, but emits an
unsupported issue because it regards that boundary as irrelevant. Relevance
can affect a criterion rating; the registered mathematical-validity gate is
not an exposition-preference gate. The code nevertheless preserves and applies
the role's declared issue rather than reclassifying it after observing the result.

The conventional GCD and LCM controls also receive beyond-reference
classifications for routine divisibility and prime-exponent arguments. The LCM
development role then calls the standard prime-exponent fact unsupported because
it is not a new conceptual addition and does not develop a framework. This
confuses novelty with validity, despite the prompt explicitly separating them.
These observations continue the reference boundary failure seen in the
[two-call trial](qwen-v8-two-stage-learnings.md).
Recognizing an added framework and correctly distinguishing it from routine
reference mathematics are separate requirements.

The brief commutator control receives an addition finding and the lowest
positive pre-gate novelty level. Its development role nevertheless emits an
unsupported issue for lacking further mathematical work. This violates the
modest-credit construct: a valid connection does not need an additional worked
consequence at that level. The mandatory veto removes its credited novelty.
The stored `missing_use_evidence` flag describes the additional cap at the
modest level; under the current rules, that flag alone does not remove modest
credit. In this trial, unsupported theory sets the cap to zero first.
The two-call trial credited this same connection. This is a case-level change
under the protocol intervention, not a population estimate of decomposition's
effect; the two attempts stopped after different sets of observed cases.

## Interpretation and next gate

The [follow-up literature review](../judge-inference-review.md#false-objections-under-additional-verification)
discusses false rejection under additional verification. It was conducted after
activation and does not retrospectively justify or change this experiment.
The current evidence does not establish that specialist judging is reliable,
that more calls are intrinsically better, or that the training objective improves
policy behavior. No semantic judgment is rerolled to obtain a preferred result.

The registered full-development and locked-audit gates still control progression.
Quoted Qwen's failure blocks every audit and comparative training run. The
[execution clarification](../amendments/2026-11-15-specialist-development-matrix.md)
requires completing the remaining rubric-only Qwen and quoted Gemma development
configurations as diagnostic evidence, without using their results to bypass
this failure. A further instrument repair would require a separately published
amendment; this trial's prompts and opinions remain unchanged.
Observed runtime belongs to this protocol; earlier single-call training estimates
cannot be reused. No sampling budget, threshold or label is relaxed to fit the
remaining time. The terminal report must retain unobserved stages of the research
as unfinished work.
