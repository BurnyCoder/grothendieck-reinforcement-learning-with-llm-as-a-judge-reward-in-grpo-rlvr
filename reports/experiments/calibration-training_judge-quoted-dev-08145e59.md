# calibration-training_judge-quoted-dev-08145e59

training_judge/quoted (dev, 08145e59) failed, with 1/3 observed preference checks passing and 0 false-theory cases assessed. The fixed futility rule stopped this incomplete development suite; the lowest stratum-wise best-possible final rates were 75.0% for preference and 100.0% for false-theory suppression. Unobserved cases are not counted as errors or successes.

| Observed check | Passed | Assessed | Rate |
|---|---|---|---|
| Higher theory score | 2 | 3 | 0.6667 |
| Higher novelty score | 2 | 3 | 0.6667 |
| Control-credit condition (recorded labels only) | 0 | 0 | Pending |
| Complete preference contract (stored decision) | 1 | 3 | 0.3333 |

The component checks are descriptive. Correct score rankings alone do not satisfy the full novelty contract, which also checks the control-credit condition. Older records without an explicit control label are excluded only from that component, not from their stored acceptance decisions. No thresholds or outcomes are changed.

| Case | Preferred T | Control T | Preferred novelty | Control novelty | Control novelty expectation | Passed |
|---|---|---|---|---|---|---|
| novelty-dev-0 | 0.5250 | 0.6125 | 0.0000 | 0.2500 | Zero | False |
| novelty-dev-1 | 0.6625 | 0.5250 | 0.5000 | 0.0000 | Zero | True |
| novelty-dev-2 | 0.6375 | 0.6125 | 0.5000 | 0.2500 | Zero | False |

These are fixed constructed expectations, not human preference labels or verified novelty. Source: the matching identity in `reports/results.json`; full judgments are preserved in `reports/development/`. Case-level disagreements require interpretation, not silent score repair.
