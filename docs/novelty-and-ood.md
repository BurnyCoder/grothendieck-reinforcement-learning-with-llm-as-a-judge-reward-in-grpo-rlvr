# Valid novelty and out-of-distribution evaluation

The [dated amendment](../reports/amendments/2026-11-15-valid-novelty-and-ood.md)
is the protocol authority. The [README](../README.md#what-the-judge-rewards)
summarizes the rubric. Neither document claims historical discovery.

Two distinct questions are tested. **Conceptual departure** asks whether a
response develops useful mathematics beyond a fixed conventional reference.
**Task-family generalization** asks whether the trained behavior transfers to
families excluded from project training. A distant mathematical connection can
help the first without establishing the second. Neither identifies what was
absent from a pretrained model's corpus.

`schema.Assessment` implements the weighted score and validity gates;
`prompts/rubric-v8.txt` and the versioned stage prompts supply scoring anchors; `novelty-anchors.json`
defines the comparison references. Both judges use these same frozen rules.
The [decomposed protocol](decomposed-judges.md) first uses two calls, then eight
specialists if development fails. `judge_stages.py` derives constructive novelty
from declared additions, demonstrated uses and consequences. It preserves raw
findings and gates the entire bonus on supported validity without substantive
objections. Its combined score is derived; older raw numerical opinions are not
rewritten or rescored. Historical v7 behavior is described below.
`novelty_cases.py` constructs valid and deliberately false mathematical bridges.
The judge must distinguish actual mathematical utility from ornamental theory.
All positive scores require exact supporting excerpts, but excerpt validation
does not prove their contents. Wrong answers receive no reward regardless of
theory or novelty. Both components are logged separately for diagnosis.

The [v7 amendment](../reports/amendments/2026-11-15-modest-valid-connections.md)
retains `novelty_comparison`: an exact reference excerpt, candidate excerpts for
an addition and its use, and the declared relationship to the reference. Code
awards novelty credit only for supported theory declared `beyond_reference`
with an excerpt identifying a concrete addition. A brief valid connection can
receive credit without a further worked consequence, capped at 1 out of 4.
Higher credit requires demonstrated use. `novelty_credit` records raw and
effective 0–4 scores, the cap, eligibility, withheld credit and reasons; the raw
assessment remains unchanged.
Malformed records and fabricated excerpts still trigger bounded retries. The
reference is a fixed baseline plus routine variations, not every theorem in
classical mathematics. Conventional general theory remains eligible for the
other five criteria. These gates do not prove that the declarations are true.
Historical results are never reinterpreted through the newer reward contract.
Constructed calibration now compares developed frameworks with both brief valid
connections and zero-novelty reference controls; the cases explicitly declare
which expectation applies. All numerical thresholds remain fixed, but the
changed construct and case set require a new complete calibration and audit.

The [reference-scope refinement](../reports/amendments/2026-11-15-explicit-reference-scope.md)
keeps that construct and case set. Its polynomial baseline explicitly concerns
commutative polynomials, while its probability baseline includes ordinary
symbolic and biased event probabilities. The finite baseline is part of the
measurement specification and judge identity. These clarifications do not
certify novelty or change any earlier result.

`ood.py` reuses [Reasoning Gym](https://github.com/open-thought/reasoning-gym)
and [SymPy](https://docs.sympy.org/latest/modules/matrices/matrices.html).
Its secondary manifest has a separate lock and does not alter the original
primary or transfer manifests. Matrix references use elimination and a separate
nonzero-minor check; both use SymPy, so this is algorithmic cross-checking, not
independent software. Geometry rejects nonconvex missing angles that the
upstream generator can produce. Canonicalization and generator parameters are
recorded alongside every accepted instance.

Use run IDs ending in `-ood`, for example `theory-seed42-ood`. The report command
pairs these separately from primary runs. Additional uncertainty intervals are
descriptive secondary analyses, stratified by family, with no alternate success
threshold. All missing and unfinished runs remain explicit. A better judge
score alone cannot establish a useful new mathematical paradigm.
