# calibration-training_judge-rubric-dev-c07b8d14

training_judge/rubric (dev, c07b8d14) failed: 0/3 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

Incomplete development suites stopped under the fixed futility rule. Upper bounds assume every remaining case succeeds solely to test attainability. Unobserved cases are not counted as measured successes or errors; no early pass is allowed.

| Observed check | Passed | Assessed | Rate |
|---|---|---|---|
| Higher theory score | 0 | 3 | 0.0000 |
| Higher novelty score | 0 | 3 | 0.0000 |
| Control-credit condition (recorded labels only) | 3 | 3 | 1.0000 |
| Complete preference contract (stored decision) | 0 | 3 | 0.0000 |

The component checks are descriptive. Correct score rankings alone do not satisfy the full novelty contract, which also checks the control-credit condition. Older records without an explicit control label are excluded only from that component, not from their stored acceptance decisions. No thresholds or outcomes are changed.

| Case | Preferred T | Control T | Preferred novelty | Control novelty | Control novelty expectation | Passed |
|---|---|---|---|---|---|---|
| novelty-dev-0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | Zero | False |
| novelty-dev-1 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | Zero | False |
| novelty-dev-2 | 0.0000 | 0.7000 | 0.0000 | 0.5000 | Positive, below preferred | False |

## Withheld novelty credit

| Case | Response | Pre-gate novelty (0–4) | Credited novelty (0–4) | Gate reasons |
|---|---|---|---|---|
| novelty-dev-0 | preferred | 4 | 0 | theory_not_supported |
| novelty-dev-0 | dispreferred | 1 | 0 | theory_not_supported, missing_use_evidence |
| novelty-dev-1 | preferred | 4 | 0 | theory_not_supported |
| novelty-dev-1 | dispreferred | 2 | 0 | theory_not_supported |
| novelty-dev-2 | preferred | 4 | 0 | theory_not_supported |

These are recorded gate applications, not independently verified mathematical errors. Pre-gate novelty is a model score in legacy protocols and a code-derived level in decomposed protocols. Stored opinions remain unchanged; acceptance checks use credited scores.

These are fixed constructed expectations, not human preference labels or verified novelty. Source: the matching identity in `reports/results.json`; full judgments are preserved in `reports/development/`. Case-level disagreements require interpretation, not silent score repair.
