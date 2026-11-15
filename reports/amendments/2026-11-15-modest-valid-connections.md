# Modest credit for brief valid mathematical connections

Date: 2026-11-15. This amendment follows the user's explicit clarification:
"Allow modest credit for a valid connection", including a brief connection to
another mathematical setting without a further worked consequence. The question
was raised after observing development disagreement about the polynomial
control. This is a development-informed change of the intended construct, not
an independent validation of that control's numerical score.

Publish this amendment, tested code, changed cases and documentation before v7
model inference. No locked audit or comparative policy experiment has begun.

## Meaning of novelty credit

The fixed conventional references remain the baseline. Routine substitutions,
equivalent notation, ornamental terminology and unsupported or false claims
earn no novelty. A concrete, valid relationship to an additional object or
mathematical setting may receive modest credit even without a further worked
application. For example, a valid boundary connection is different from merely
saying that assumptions matter. More developed, useful frameworks earn more.
Historical originality or absence from pretraining is still not inferred.

Rubric v7 changes the lowest positive novelty anchor to cover a brief valid
connection, organizing observation or definition. The higher anchors retain
requirements for demonstrated mathematical operation, consequences and reusable
frameworks. Historical framing v2 clarifies that brief valid connections can
receive modest credit; the supplied quotation and attribution are unchanged.
Elementary valid relationships need not be rebuilt from axioms;
unsupported essential claims still fail the global theory-validity gate.

## Deterministic credit rule

Keep the raw six-criterion assessment and reference comparison. The maximum
credited novelty score is:

- 0 when theory is not supported, the relation is not `beyond_reference`, or
  no excerpt identifies the added construction or concrete relationship;
- 1 when those prerequisites hold but no further use is demonstrated;
- 4 when the prerequisites and demonstrated-use evidence are present.

Credited novelty is the smaller of the raw 0–4 score and this cap; N divides it
by four. Supported T combines the other five normalized criteria and 0.20*N.
Otherwise T=0. R=C*(1+0.5*T) and all six weights remain fixed. No code rule raises
a raw score. `novelty_credit` records the cap, raw and effective scores,
eligibility, withheld credit and reasons. Exact excerpt validation remains
mandatory. These gates cannot establish whether the claimed connection or its
use is mathematically sound; that remains a fallible model assessment.

The rubric tells the judge not to use an ordinary reference application as
evidence that an unrelated new connection has been developed. Mere names earn
zero. The quoted and rubric-only variants share this entire scoring contract.
The identity-bound protocol becomes `tiered-novelty-eligibility-v2`.

## Changed constructed calibration expectations

The original polynomial controls include a valid statement about noncommuting
products and commutators. Under the clarified construct they should receive
some novelty, while the quadratic-algebra framework should receive more. The
corresponding control with decorative renaming retains this valid statement;
the name itself earns nothing. Neither original case is retroactively rescored.

Add brief valid subgroup connections for GCD and LCM, a brief parity-character
connection for dice, and a purely conventional polynomial control with the
commutator remark removed. This produces 12 novelty contrasts: five with a
modest-credit control and seven with a zero-novelty control. The original 20
general-theory contrasts and 28 false-theory cases remain. A complete suite now
contains 92 assessments before retries. These counts and labels are recorded
in the generated [contract manifest](../development/judge-v7-calibration-contract.json).

Each novelty contrast requires higher T and higher N for the developed
framework. A modest-credit control additionally requires N>0; a routine or
decorative-only control requires N=0. These are ordinal preference expectations,
not exact human cardinal ratings. The registered preference and false-theory
thresholds remain 80% and 90% within each stratum. The changed suite and rules
use `graded-connections-development-futility-v2`; the code computes the exact
remaining-case bound from the new denominators. No early success is permitted.

The previous v6 attempt is retained as interrupted in response to this user
clarification, not a full pass or a futility failure. Its component results
remain interpretable under its original stricter rule. Do not pool v6 and v7
scores or substitute the new labels into the earlier result.

## Sequence, tests and limits

Test the positive connection allowance, cap, absence/invalidity gates, raw-record
preservation, strict developed-over-brief ordering and changed calibration
expectations.
The [template-capacity check](../development/judge-context-v7.json) uses the
loaded Qwen template and a synthetic maximum-length candidate without inference;
it does not guarantee capacity for every task, retry or tokenizer.

Publish before one fresh Qwen quoted development attempt; only
a complete pass permits the Gemma quoted and Qwen rubric-only development
attempts, followed by the untouched full audits under v7. Every required audit
must pass before long training. Models, inference budgets and runtime settings
remain fixed. Failed or interrupted runs remain public evidence.

Repeated use of public development templates can overfit the instrument. Audit
instances change values while sharing mathematical templates, so a pass does
not establish generalization to new failure types. The user supplied a scoring
preference, not human ratings of these examples. The behavioral hypothesis and
primary/OOD/transfer evaluation plans remain unchanged, with the updated rubric
frozen before comparative outcomes exist. A later change must remain separately
documented; this clarification does not validate past scores or a latent-space
mechanism.
