# Explicit reference decisions before novelty scoring

Date: 2026-11-15. Development-informed amendment; publish this protocol and its
implementation before inference. The failed bounded-reasoning result is already
public. No locked audit, comparative policy generation or comparative training
has begun.

## Motivation and hypothesis

The [Qwen reasoning failure](../experiments/qwen-reasoning-v4-learnings.md)
contains a novelty rationale that denies a substantive departure while assigning
positive novelty. Another opinion expands the supplied reference to reject a
classical framework that adds a functional mathematical construction. The
[Gemma failure](../experiments/gemma-v4-learnings.md) likewise shows that exact
quotations do not establish semantic rubric compliance. These are observed
development counterexamples, not population error estimates.

Hypothesis: requiring an explicit comparison before scoring, and checking the
consistency of the declared decision with the score, may improve adherence to
the intended reference-relative novelty criterion. This is a new development
configuration, not an isolated causal test of one prompt sentence. The
[checklist literature review](../judge-inference-review.md) motivates an
auditable decision structure; it supplies no guarantee for mathematical novelty.

## Fixed intervention

Rubric v5 separates mathematical validity, reference comparison and criterion
scoring. The conventional reference includes its listed methods and routine
variations, not all classical mathematics or their entire logical closure.
Established mathematics can qualify when an additional construction performs
demonstrated work. Routine generalization, pedagogical reformulation and a
boundary caveat without an additional working construction remain conventional.
These distinctions clarify the intended operational construct; they are not
claims about historical originality. In particular, the disputed polynomial
control's label is retained, not treated as an independently verified truth.

The structured assessment adds `novelty_comparison` before criterion scores:

- An exact excerpt from the supplied conventional reference.
- Exact candidate excerpts for an additional construction and its demonstrated use.
- A declared relation: `within_reference`, `beyond_reference` or `unresolved`.

Positive novelty requires `beyond_reference` and both sets of evidence. The
reference excerpt is checked against the reference, and candidate excerpts
against the candidate. Inconsistent or fabricated-evidence responses receive
the existing validation feedback and bounded retry; code never silently changes
a score. Retry exhaustion remains an infrastructure/contract failure, not a zero
mathematical reward. The model can still make a consistent but wrong declaration:
these checks validate attribution and internal consistency, not mathematical
entailment. Valid conventional theory keeps its other criterion scores.

The historical quotation, six weights, ordinal scales, reward formula, final
answer and theory-validity gates remain unchanged. All model revisions, runtime
settings, greedy decoding, native-reasoning and output budgets stay fixed.
Conventional-reference contents, development/audit cases, labels, ordering and
acceptance thresholds also remain fixed. No calibration examples or task
answers are added to the system prompt. The rubric-only ablation shares the
complete v5 rubric and schema; it removes only the historical framing.

The prompt and schema enter the existing judge identity, invalidating prior
cache/calibration reuse. Field ordering and the explicit
`reference-comparison-consistency-v1` validation protocol are identity-bound.
Historical events remain in their original schema and
reports read them without rewriting their opinions. Comparative training cannot
resume across a changed reward identity; the pilot remains excluded from every
experimental initialization.

## Validation, selection and stopping

Offline tests must reject incompatible positive novelty, missing evidence and
invented reference quotations; check retries and cache exclusion; and preserve
the correctness ordering and valid conventional-theory reward. These tests use
synthetic fixtures and do not establish model judgment quality.
The [template-capacity record](../development/judge-context-v5.json) checks the
loaded Qwen tokenizer and chat template without running inference. Its synthetic
candidate leaves room for the completion ceiling, but this does not guarantee
capacity for every task, retry or the other judge's tokenizer.

Run one fresh Qwen quoted development attempt first under the existing futility
rule. If it passes completely, run Gemma quoted and Qwen rubric-only development
attempts sequentially. Only complete passes for all required configurations
permit the untouched full audits; only those audits permit long training. A
failure remains a failure even if its rationale suggests an ambiguous label.
Record the precise failure and stop dependent runs. Any further development
revision requires a separately justified, dated amendment; do not continue
editing wording solely to obtain a pass on familiar templates.

Repeated development reuse can overfit these public templates. The existing
audit changes numbers while sharing mathematical templates, so even a pass
would not establish generalization to new failure types. Independent behavioral
and transfer evaluations remain necessary, and judge scores remain opinions.
Keep primary and secondary OOD analyses, initialization, matched training arms
and budgets unchanged. Refresh throughput before comparative training, as
already required by the native-reasoning amendment.
