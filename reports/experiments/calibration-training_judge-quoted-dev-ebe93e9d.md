# calibration-training_judge-quoted-dev-ebe93e9d

training_judge/quoted (dev, ebe93e9d) failed: 6/9 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

Incomplete development suites stopped under the fixed futility rule. Upper bounds assume every remaining case succeeds solely to test attainability. Unobserved cases are not counted as measured successes or errors; no early pass is allowed.

| Observed check | Passed | Assessed | Rate |
|---|---|---|---|
| Higher theory score | 8 | 9 | 0.8889 |
| Higher novelty score | 8 | 9 | 0.8889 |
| Control-credit condition (recorded labels only) | 7 | 9 | 0.7778 |
| Complete preference contract (stored decision) | 6 | 9 | 0.6667 |

The component checks are descriptive. Correct score rankings alone do not satisfy the full novelty contract, which also checks the control-credit condition. Older records without an explicit control label are excluded only from that component, not from their stored acceptance decisions. No thresholds or outcomes are changed.

| Case | Preferred T | Control T | Preferred novelty | Control novelty | Control novelty expectation | Passed |
|---|---|---|---|---|---|---|
| novelty-dev-0 | 0.6625 | 0.5625 | 0.5000 | 0.0000 | Zero | True |
| novelty-dev-1 | 0.6625 | 0.4125 | 0.5000 | 0.0000 | Zero | True |
| novelty-dev-2 | 0.7250 | 0.5250 | 0.7500 | 0.0000 | Positive, below preferred | False |
| novelty-dev-3 | 0.7125 | 0.4875 | 0.7500 | 0.0000 | Zero | True |
| novelty-dev-4 | 0.6625 | 0.3875 | 0.5000 | 0.0000 | Zero | True |
| novelty-dev-5 | 0.7000 | 0.4375 | 0.5000 | 0.0000 | Zero | True |
| novelty-dev-6 | 0.7500 | 0.4750 | 0.7500 | 0.0000 | Positive, below preferred | False |
| novelty-dev-7 | 0.7125 | 0.4375 | 0.7500 | 0.0000 | Zero | True |
| novelty-dev-8 | 0.6625 | 0.7000 | 0.5000 | 0.5000 | Positive, below preferred | False |

## Withheld novelty credit

| Case | Response | Pre-gate novelty (0–4) | Credited novelty (0–4) | Gate reasons |
|---|---|---|---|---|
| novelty-dev-0 | dispreferred | 1 | 0 | within_reference |
| novelty-dev-2 | dispreferred | 1 | 0 | within_reference, missing_use_evidence |

These are recorded gate applications, not independently verified mathematical errors. Pre-gate novelty is a model score in legacy protocols and a code-derived level in decomposed protocols. Stored opinions remain unchanged; acceptance checks use credited scores.

These are fixed constructed expectations, not human preference labels or verified novelty. Source: the matching identity in `reports/results.json`; full judgments are preserved in `reports/development/`. Case-level disagreements require interpretation, not silent score repair.
