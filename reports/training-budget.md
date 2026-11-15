# Development training-budget scenarios

Each future step repeats one observed development interval. These are scenarios, not confidence bounds.

Two intervals, including first-use overhead; v3 judge protocol. Future lengths, accuracy, theory and v4 latency may differ. Excludes correctness-only runs, calibration, evaluation, transfer, loading and publication.

Selected matched budget: **64 optimizer updates per training arm**.

| Updates | One judge-scored arm (hours) | All judge-scored arms (hours) |
|---:|---:|---:|
| 32 | 4.27–6.22 | 21.36–31.11 |
| 64 | 8.55–12.44 | 42.73–62.22 |
| 128 | 17.09–24.89 | 85.45–124.43 |
| 256 | 34.18–49.77 | 170.90–248.86 |

Sources: `reports/development/feasibility-grpo-first-boundary.json` and `reports/development/feasibility-grpo-resumed-complete.json`. The reduction is preregistered in [the budget amendment](amendments/2026-11-15-training-budget.md). This is not a guarantee that the full study fits in one week.

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
