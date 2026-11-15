# calibration-evaluation_judge-quoted-dev-ef8a300c

evaluation_judge/quoted (dev, ef8a300c) failed, with 2/4 observed preference checks passing and 0 false-theory cases assessed. The fixed futility rule stopped this incomplete development suite; the lowest stratum-wise best-possible final rates were 75.0% for preference and 100.0% for false-theory suppression. Unobserved cases are not counted as errors or successes.

| Observed check | Passed | Assessed | Rate |
|---|---|---|---|
| Higher theory score | 4 | 4 | 1.0000 |
| Higher novelty score | 4 | 4 | 1.0000 |
| Control-credit condition (recorded labels only) | 0 | 0 | Pending |
| Complete preference contract (stored decision) | 2 | 4 | 0.5000 |

The component checks are descriptive. Correct score rankings alone do not satisfy the full novelty contract, which also checks the control-credit condition. Older records without an explicit control label are excluded only from that component, not from their stored acceptance decisions. No thresholds or outcomes are changed.

| Case | Preferred T | Control T | Preferred novelty | Control novelty | Control novelty expectation | Passed |
|---|---|---|---|---|---|---|
| novelty-dev-0 | 0.8625 | 0.5875 | 0.5000 | 0.0000 | Zero | True |
| novelty-dev-1 | 0.9125 | 0.5625 | 0.7500 | 0.0000 | Zero | True |
| novelty-dev-2 | 1.0000 | 0.7250 | 1.0000 | 0.5000 | Zero | False |
| novelty-dev-3 | 0.9125 | 0.5375 | 0.7500 | 0.2500 | Zero | False |

These are fixed constructed expectations, not human preference labels or verified novelty. Source: the matching identity in `reports/results.json`; full judgments are preserved in `reports/development/`. Case-level disagreements require interpretation, not silent score repair.
