# Exploratory single-call save/resume pilot: exploratory-small-gpu-v2

Generated from `reports/development/feasibility-exploratory-small-gpu-v2-step*.json`. These development updates are excluded from every comparative initialization. A zero learning rate checks execution but does not demonstrate an adapter update.

| Boundary | Learning rate | Accuracy | C × theory | C × novelty | Mean reward |
|---|---|---|---|---|---|
| 1 | 0 | 0.3750 | 0.2438 | 0.1250 | 0.4969 |
| 2 | 1e-05 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

| Boundary | Resumed | Step seconds | Peak allocated GiB | Completed judge calls | Retries |
|---|---|---|---|---|---|
| 1 | False | 179.71 | 2.34 | 3 | 0 |
| 2 | True | 120.98 | 2.38 | 0 | 0 |

Theory and novelty means include zero for incorrect or invalidly formatted answers. Judge opinions remain unqualified. Request counts include completed invalid contracts; cache hits are not additional calls. Step intervals include generation, checking, judging and backward work; they are not stable throughput estimates or learning-effect estimates. The boundaries use different development batches, so their accuracies do not measure a learning trend. A parameter update with zero task reward can reflect restored optimizer momentum and the KL term; it does not establish learning from that batch. See [runtime scenarios](../training-budget.md) and the [dated amendments](../amendments/).
