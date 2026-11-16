# Exploratory single-call save/resume pilot

Generated from `reports/development/feasibility-exploratory-single-step*.json`. These development updates are excluded from every comparative initialization. A zero learning rate checks execution but does not demonstrate an adapter update.

| Boundary | Learning rate | Accuracy | C × theory | C × novelty | Mean reward |
|---|---|---|---|---|---|
| 1 | 0 | 0.3750 | 0.1328 | 0.0000 | 0.4414 |
| 2 | 1e-05 | 0.5000 | 0.2078 | 0.0000 | 0.6039 |

| Boundary | Resumed | Step seconds | Peak allocated GiB | Completed judge calls | Retries |
|---|---|---|---|---|---|
| 1 | False | 864.57 | 4.89 | 4 | 1 |
| 2 | True | 805.43 | 4.97 | 4 | 0 |

Theory and novelty means include zero for incorrect or invalidly formatted answers. Judge opinions remain unqualified. Request counts include completed invalid contracts; cache hits are not additional calls. Step intervals include generation, checking, judging and backward work; they are not stable throughput estimates or learning-effect estimates. See [runtime scenarios](../training-budget.md) and [interpretation](exploratory-single-v2-pilot-learnings.md).
