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

## Exploratory single-call pilot

These intervals use the current frozen single-call judge and remain separate from the historical non-thinking pilot above. They include generation, verification, judging and backward work; model loading and evaluation are excluded. Development prompts and few intervals cannot establish steady-state throughput. Future correctness, response lengths and retries affect runtime.

| Updates | One judge-scored arm (hours) | All judge-scored arms (hours) |
|---:|---:|---:|
| 32 | 7.16–7.69 | 35.80–38.43 |
| 64 | 14.32–15.37 | 71.59–76.85 |
| 128 | 28.64–30.74 | 143.19–153.70 |
| 256 | 57.28–61.48 | 286.38–307.40 |

Sources: `reports/development/feasibility-exploratory-single-*.json`. Judge identity: `b6add1897e852493e0cbea6a16a15a6bce81d2b1ef7e487b97386518ee6c545a`.

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
