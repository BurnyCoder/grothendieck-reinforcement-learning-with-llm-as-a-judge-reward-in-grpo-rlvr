# calibration-training_judge-quoted-dev-a3fa911e

training_judge/quoted (dev, a3fa911e) failed, with 4/7 observed preference checks passing and 0 false-theory cases assessed. The fixed futility rule stopped this incomplete development suite; the lowest stratum-wise best-possible final rates were 75.0% for preference and 100.0% for false-theory suppression. Unobserved cases are not counted as errors or successes.

| Observed check | Passed | Assessed | Rate |
|---|---|---|---|
| Higher theory score | 7 | 7 | 1.0000 |
| Higher novelty score | 7 | 7 | 1.0000 |
| Control-credit condition (recorded labels only) | 4 | 7 | 0.5714 |
| Complete preference contract (stored decision) | 4 | 7 | 0.5714 |

The component checks are descriptive. Correct score rankings alone do not satisfy the full novelty contract, which also checks the control-credit condition. Older records without an explicit control label are excluded only from that component, not from their stored acceptance decisions. No thresholds or outcomes are changed.

| Case | Preferred T | Control T | Preferred novelty | Control novelty | Control novelty expectation | Passed |
|---|---|---|---|---|---|---|
| novelty-dev-0 | 0.6625 | 0.5625 | 0.5000 | 0.0000 | Zero | True |
| novelty-dev-1 | 0.6625 | 0.4125 | 0.5000 | 0.0000 | Zero | True |
| novelty-dev-2 | 0.7250 | 0.5625 | 0.7500 | 0.0000 | Positive, below preferred | False |
| novelty-dev-3 | 0.7125 | 0.4875 | 0.7500 | 0.2500 | Zero | False |
| novelty-dev-4 | 0.6625 | 0.3875 | 0.5000 | 0.0000 | Zero | True |
| novelty-dev-5 | 0.7000 | 0.4375 | 0.5000 | 0.0000 | Zero | True |
| novelty-dev-6 | 0.6375 | 0.5125 | 0.5000 | 0.0000 | Positive, below preferred | False |

## Withheld novelty credit

| Case | Response | Pre-gate novelty (0–4) | Credited novelty (0–4) | Gate reasons |
|---|---|---|---|---|
| novelty-dev-0 | dispreferred | 1 | 0 | within_reference |
| novelty-dev-2 | dispreferred | 1 | 0 | within_reference, missing_use_evidence |

These are recorded gate applications, not independently verified mathematical errors. Pre-gate novelty is a model score in legacy protocols and a code-derived level in decomposed protocols. Stored opinions remain unchanged; acceptance checks use credited scores.

These are fixed constructed expectations, not human preference labels or verified novelty. Source: the matching identity in `reports/results.json`; full judgments are preserved in `reports/development/`. Case-level disagreements require interpretation, not silent score repair.
