# Development training-budget scenarios

Each future step repeats one observed development interval. These are scenarios, not confidence bounds.

Two intervals, including first-use overhead, used the v3 non-thinking judge. Neither the later reasoning-enabled judge nor the decomposed protocols are timed by these scenarios. Refresh development throughput before comparative training; future lengths, accuracy and theory density may differ. Excludes correctness-only runs, calibration, evaluation, transfer, loading and publication.

Selected matched budget: **64 optimizer updates per training arm**.

| Updates | One judge-scored arm (hours) | All judge-scored arms (hours) |
|---:|---:|---:|
| 32 | 4.27–6.22 | 21.36–31.11 |
| 64 | 8.55–12.44 | 42.73–62.22 |
| 128 | 17.09–24.89 | 85.45–124.43 |
| 256 | 34.18–49.77 | 170.90–248.86 |

Sources: `reports/development/feasibility-grpo-first-boundary.json` and `reports/development/feasibility-grpo-resumed-complete.json`. The reduction is preregistered in [the budget amendment](amendments/2026-11-15-training-budget.md). This is not a guarantee that the full study fits in one week.

## Current exploratory pilot: exploratory-small-gpu-v2

Only intervals from the current experiment enter this estimate. They remain separate from the historical non-thinking pilot above. They include generation, verification, judging and backward work; model loading and evaluation are excluded. Development prompts and few intervals cannot establish steady-state throughput. Future correctness, response lengths and retries affect runtime.

| Updates | One judge-scored arm (hours) | All judge-scored arms (hours) |
|---:|---:|---:|
| 32 | 1.08–1.60 | 5.38–7.99 |
| 64 | 2.15–3.19 | 10.75–15.97 |
| 128 | 4.30–6.39 | 21.51–31.95 |
| 256 | 8.60–12.78 | 43.02–63.90 |

Sources: `reports/development/feasibility-exploratory-small-gpu-v2-*.json`. Judge identity: `5a42dfae5ed77aa8f39c08e68d61f3cee6ece0a6038848dd9f91e11bf86948dc`.

## Postponed exploratory configurations

These recorded intervals are historical evidence, not forecasts for the smaller GPU experiment.

| Experiment | Judge identity | Observed step seconds |
|---|---|---:|
| exploratory-single-v2 | `b6add1897e852493e0cbea6a16a15a6bce81d2b1ef7e487b97386518ee6c545a` | 864.57 |
| exploratory-single-v2 | `b6add1897e852493e0cbea6a16a15a6bce81d2b1ef7e487b97386518ee6c545a` | 805.43 |

## Planned data exposure

One GPU, sequential pre-shuffled manifest, one GRPO iteration, completed fixed budget. Actual exposure must be checked against rollout logs.

The configured budget schedules 512 completions across 128 prompt occurrences, covering 128 distinct prompts from the 1024-prompt training manifest. All arms use this same order. These are configuration-derived counts, not completed training results.

| Training family | Distinct prompts scheduled |
|---|---:|
| dice | 23 |
| gcd | 32 |
| lcm | 39 |
| polynomial_multiplication | 34 |

Source: `data/train.json` and `configs/study.json`. Reducing optimizer updates also reduces task exposure; it does not merely shorten optimization on the full manifest.
