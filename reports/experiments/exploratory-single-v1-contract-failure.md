# First exploratory pilot: exact-quotation failure

This was a development execution check after explicit authorization to train
with an unqualified single-call judge. It did not reach an optimizer update or
produce a training-effect estimate. The
[immutable failure record](../development/feasibility-exploratory-single-v1-failure.json)
and [complete events](../development/exploratory-single-v1-pilot-failure.jsonl)
contain the configuration, raw policy outputs, judge requests, responses and
terminal exception. The report command regenerates counts and timings in
[development execution](development-runtime.md).

The first judged polynomial solution explained distributivity using LaTeX dollar
delimiters. The judge repeatedly reproduced a near quotation without those
delimiters. The output was valid JSON, but the claimed excerpt was not an exact
substring. The [closest-line diagnostic](../development/indexed-evidence-failure-diagnostic.json)
shows the original and purported spans. This comparison explains the transport
failure; it neither certifies the explanation nor repairs historical scores.

The existing validation-feedback retries did not resolve it. More repeated calls
would violate the bounded retry rule and would not test the requested single-call
experiment cleanly. Relaxing the check to fuzzy matches could conceal invented
evidence. The selected [repair](../amendments/2026-11-16-indexed-evidence.md)
instead uses constrained source-passage IDs and exact extraction in code. It
keeps evidence traceable while removing the need to reproduce mathematical
typography. Whether the judge selects relevant evidence and grades mathematics
well remains an empirical limitation, not a guarantee of this representation.

The original profile, failed run and calibration results remain intact. A new
identity starts the next pilot from the selected unmodified policy. Its eventual
training comparisons remain exploratory even if execution succeeds.
