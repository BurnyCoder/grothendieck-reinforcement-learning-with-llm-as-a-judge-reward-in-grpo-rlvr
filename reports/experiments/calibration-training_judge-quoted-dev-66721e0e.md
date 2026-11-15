# calibration-training_judge-quoted-dev-66721e0e

training_judge/quoted (dev, 66721e0e) failed: 2/5 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

Incomplete development suites stopped under the fixed futility rule. Upper bounds assume every remaining case succeeds solely to test attainability. Unobserved cases are not counted as measured successes or errors; no early pass is allowed.

| Observed check | Passed | Assessed | Rate |
|---|---|---|---|
| Higher theory score | 3 | 5 | 0.6000 |
| Higher novelty score | 2 | 5 | 0.4000 |
| Control-credit condition (recorded labels only) | 2 | 5 | 0.4000 |
| Complete preference contract (stored decision) | 2 | 5 | 0.4000 |

The component checks are descriptive. Correct score rankings alone do not satisfy the full novelty contract, which also checks the control-credit condition. Older records without an explicit control label are excluded only from that component, not from their stored acceptance decisions. No thresholds or outcomes are changed.

| Case | Preferred T | Control T | Preferred novelty | Control novelty | Control novelty expectation | Passed |
|---|---|---|---|---|---|---|
| novelty-dev-0 | 0.6125 | 0.6125 | 0.2500 | 0.2500 | Zero | False |
| novelty-dev-1 | 0.5875 | 0.6500 | 0.2500 | 0.2500 | Zero | False |
| novelty-dev-2 | 0.7750 | 0.6125 | 1.0000 | 0.2500 | Positive, below preferred | True |
| novelty-dev-3 | 0.6500 | 0.5125 | 0.2500 | 0.0000 | Zero | True |
| novelty-dev-4 | 0.6125 | 0.5875 | 0.2500 | 0.2500 | Zero | False |

These are fixed constructed expectations, not human preference labels or verified novelty. Source: the matching identity in `reports/results.json`; full judgments are preserved in `reports/development/`. Case-level disagreements require interpretation, not silent score repair.
