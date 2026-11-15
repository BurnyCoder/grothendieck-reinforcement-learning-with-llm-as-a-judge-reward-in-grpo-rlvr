# Clarify the mathematical setting of the fixed references

Date: 2026-11-15. This development-informed amendment follows the
[failed v7 trial](../experiments/qwen-v7-learnings.md). Publish it, the changed
configuration and regenerated artifacts before further model inference.
No locked audit or comparative training has begun.

## Intervention and hypothesis

Keep rubric v7, historical framing v2, the modest-connection credit rule,
models, inference settings, score weights and all constructed cases unchanged.
Change only the polynomial and dice entries in
[`novelty-anchors.json`](../../configs/novelty-anchors.json), versioned as v3.

The polynomial reference now explicitly concerns commuting variables over a
commutative coefficient ring. It lists distributivity, coefficient collection
and convolution, binomial squares and difference of squares, with ordinary
substitutions and commutative cancellation. The prior phrase "standard
identities" did not specify that finite scope. A comparison with another
algebraic setting is assessed under the existing rubric; no departure receives
automatic credit merely because it is absent from the reference.

The dice reference now explicitly includes adding disjoint-event probabilities
and multiplying independent-event probabilities, with symbolic or biased
probabilities as well as uniform counting. This clarifies the conventional
method rather than adding another theory. Dynamic programming and generating
polynomials remain in the reference. No calibration answer or expected score
is included in either entry.

Hypothesis: stating these mathematical domains directly will help the judge
distinguish an additional relationship from a routine parameter change while
preserving modest credit for a valid brief connection. The observed v7 errors
also included demanding a further use after recognizing a brief connection;
the reference intervention may not repair that separate instruction failure.
This is an isolated input change, not a demonstrated causal explanation of
past failures or a guarantee of improved judging.

## Fixed measurement and decision rules

Retain the exact v7 development/audit case hashes, labels, order, thresholds
and futility rule. The
[pre-inference integrity record](../development/judge-reference-scope-v3.json)
checks the unchanged case hashes against the published v7 contract and records
the new judge identity. No old opinion is rescored, and no old calibration pass
can qualify the new identity. The identity already includes the complete
reference configuration; no caching or acceptance logic changes are needed.
The [template-capacity record](../development/judge-context-v7-anchors-v3.json)
checks the changed entries against the served Qwen template without inference.
It is a synthetic capacity check, not a guarantee for all tasks or retries.

Run one fresh Qwen quoted development attempt. Only a complete pass permits
the remaining Gemma quoted and Qwen rubric-only development checks under the
same references, followed by the untouched full audits. Any failure retains the
training block and is published. Do not weaken a threshold, rerun an unchanged
failed identity for a preferred outcome, or count unobserved cases as passing.
This amendment specifies only this trial; another intervention needs its own
rationale, dated record and publication.

Report the original compound acceptance result and the separate observed T
ranking, N ranking and control-credit checks. These diagnostic components do
not replace the acceptance criterion. Public template reuse can overfit both
the prompt and references, and audit values share these mathematical templates.
A successful audit would still not establish historical novelty, human
preference alignment, general novelty-judging ability or improvement of a
trained policy. The primary, secondary OOD and transfer tests remain unchanged.
