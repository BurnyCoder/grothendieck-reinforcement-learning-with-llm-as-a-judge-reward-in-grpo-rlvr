# Preregistration: correctness-gated theory building

Author: Libor “Burny” Burian. Registered 2026-11-15, before model inference.
This file's initial public Git commit is the registration timestamp. Amendments
must be separate dated files in `reports/amendments/`; do not overwrite history.

## Question, hypotheses and falsification

Does a Grothendieck-inspired rubric bonus improve useful mathematical theory
building without materially reducing answer accuracy? The mechanism motivating
this study is behavior selection through RL, not an established latent direction.
The method combines [GRPO](https://arxiv.org/html/2402.03300v3),
[Dr. GRPO normalization](https://arxiv.org/html/2503.20783v2) and
[rubric rewards](https://arxiv.org/html/2507.17746v1).

Primary H1: the proposed arm improves mean correctness-weighted independent
theory score by at least 0.05 over correctness-only GRPO, with a paired two-sided
95% interval whose lower bound exceeds zero. Accuracy must be noninferior:
the lower endpoint of the paired two-sided 95% interval for accuracy difference
must exceed -0.03. All three conditions are required. An interval containing
zero is inconclusive, not confirmation. An upper theory-score endpoint below
0.05 rules out the prespecified useful effect at this precision. Clear accuracy
inferiority contradicts the combined hypothesis.

Secondary H2: reusable notes from the proposed policy improve a frozen
recipient's verified accuracy compared with no notes, unrelated notes, and
baseline notes. This is exploratory and reported with intervals, without a
confirmatory significance claim. Higher training-judge scores without independent
improvement are consistent with proxy optimization. Neither outcome establishes
a latent-space mechanism.

## Data and locked splits

Use pinned Reasoning Gym generators. Train on 1,024 problems, balanced across
GCD, LCM, polynomial multiplication and dice probabilities. Development has 64
balanced problems. The locked primary set has 400 problems: 200 fresh standard
instances (50 per trained family), 100 harder instances (25 per trained family),
and 100 new-family instances (50 prime factorizations, 50 polynomial equations).

Standard GCD: 2–3 integers in 2–1000; LCM: 2–3 in 2–100; polynomial
multiplication: 2 factors, 2–3 terms, degree 0–2, coefficient magnitudes 1–8,
one variable x; dice: 3 dice, maximum size 20. Harder GCD: 4–5 integers in
1001–10000; harder LCM: 4–5 in 101–300; harder products: 3 factors, 3–4 terms,
degree 0–3, magnitudes 1–12; harder dice: 5 dice, maximum size 24.
New-family factorization uses 100–10000; equations use degree 1–3,
2–4 terms, coefficient magnitudes 1–10, all real roots to nearest four decimals.
Generator mistakes or degeneracies are filtered by deterministic checks before
any policy output and logged with reasons; no filtering based on model success.

Base generator seed 20261115; family and split seed intervals are disjoint by
at least 100000. Save source version, index, parameters, raw entry, normalized
problem, reference answer, canonical instance key, split and SHA-256 hashes.
Canonical keys collapse reordered GCD/LCM inputs, reordered dice, equivalent
polynomial instances, and superficial prompt variants. Deduplicate across all
splits, including transfer sources and targets. Archive manifests rather than
depending only on seeds. Lock before inference. Code must refuse training on
anything but the train split; development alone may inform fixes and feasibility.

Transfer uses 100 additional standard source tasks, balanced by family, each
with four fresh related tasks from that family. Generate all source notes before
exposing targets to the recipient. Source prompts contain no target questions or
answers. The source output must delimit reusable notes. A deterministic cyclic
derangement across families supplies unrelated notes, truncated to the same
recipient-token length as the corresponding related note. Report actual lengths
and shortfall. Recipient conditions use identical frozen selected-policy weights,
decoding seeds and target prompts except for the notes.

## Models and selection rule

All models run locally; only Qwen and Gemma. Preferred policy Qwen3.5-2B BF16
with LoRA; training judge Qwen3.5-9B GGUF Q4_K_M on CPU; independent judge
Gemma 4 12B GGUF UD-Q4_K_XL, loaded separately. Pin model revisions and hashes.
Disable thinking mode where the official chat template permits it; grade visible
answers, retaining all raw model outputs in logs. Freeze inference settings and
prompts before the locked audit. Do not train judge weights.

After code publication, a development feasibility pilot uses four-completion
groups, maximum prompt length 512 and maximum completion length 2048, backward
passes, saving and resume. Test an explicit maximum-length synthetic batch if
natural generations are shorter. Use microbatch 1 and gradient checkpointing.
Record GPU peak allocated/reserved memory, wall-clock throughput, judge latency,
valid answer fraction and a resumed optimizer update. Pilot updates are discarded.

Only unresolved memory/runtime failure or measured inability to fit the one-week
budget permits Qwen3-1.7B FP8 LoRA. Missing the 14-hour target alone does not.
Select one starting checkpoint and publish the decision before comparative runs;
all arms and transfer recipients start from those same unmodified base weights.
If the whole comparison cannot fit, report unfinished arms rather than silently
changing the scientific design. A budget-driven reduction from the maximum
256 updates requires a dated, pre-comparison amendment applying to all arms.

## Training and arms

LoRA rank 16, alpha 32, dropout 0; language modules only. Four completions per
prompt; per-device microbatch 1; gradient accumulation 8. Learning rate 1e-5,
linear scheduler, warmup ratio 0.1, AdamW, gradient clipping 1, maximum 256
optimizer updates. TRL `dr_grpo`, `scale_rewards=False`, KL coefficient 0.04,
epsilon 0.2, one update per rollout, no vLLM for Qwen3.5. Completion limit 2048,
prompt limit 512, temperature 1, top-p 1. Save at optimizer boundaries at least
every 8 steps and upon orderly termination. Resume state includes adapter,
optimizer, scheduler, RNG, data position, config and durable judge cache.

| Arm | Seeds | Intervention |
|---|---|---|
| Unmodified ordinary prompt | 42 | No training |
| Unmodified rising-sea prompt | 42 | Explicit useful-framework instruction |
| Correctness-only GRPO | 42, 43, 44 | R=C |
| Theory-bonus GRPO | 42, 43, 44 | R=C(1+0.5T) |
| Shuffled-bonus control | 42 | Permute T among correct completions within each reward batch |
| Rubric-only ablation | 42 | Same rubric, omit persona and quotations |

The shuffled control preserves batch reward marginals; batches with fewer than
two correct responses cannot be perturbed and their fraction must be reported.
Match policy initialization, task order (`data_seed=20261115`), update counts,
generation budgets and ordinary prompt across training arms. Evaluation uses
temperature 0 and one answer per problem. Report token budgets and actual lengths.
Use the final prespecified checkpoint, not the best test checkpoint.

## Reward and judge calibration

Require exactly one `<final>...</final>` answer. Invalid format and incorrect
answers receive zero. Task-specific checks plus bounded Math-Verify establish C;
parser crashes/timeouts are infrastructure failures with explicit retry/termination.
Only correct responses are sent for theory scoring. T is a weighted mean of
0–4 rubric scores divided by four, and is zero unless theory validity is
`supported`. Nonzero criterion scores require exact supporting response excerpts.
No verbosity, name-dropping or metaphor bonus. Full prompt and schema are versioned.

Weights: structural understanding .25; justified generality .25; problem as
consequence .20; reuse/connections .20; conceptual economy/exposition .10.
Validity states: none, supported, unsupported, contradicted. Invalid judge JSON,
missing evidence or network/service failure triggers bounded retries then a hard
failure; it never silently becomes a mathematical error or a zero-theory label.

Calibrate each exact judge and the rubric-only training-judge variant using
separate constructed development and locked audit cases. Each split contains
20 preference pairs and 20 deliberate false-theory cases, including padding,
irrelevant jargon and embedded grading instructions. Preference order is strict
T(useful explanation)>T(mechanical/padded/wrong-theory explanation); ties fail.
Pass requires at least 80% correct order and at least 90% false-theory bonuses
suppressed, separately for every required judge/prompt configuration. These are
constructed test expectations, not human preference evidence. Development may
inform prompt edits; use locked audit once. Failure blocks long training;
subsequent changes require a dated amendment and newly reserved audit cases.

## Analysis and uncertainty

For each locked problem i and training seed s, save C and independent judge T,
then compute M=C*T. Primary estimate is the mean paired proposed-minus-correctness
difference, first averaged across the three matched seeds within each problem,
then across problems. Report every seed and between-seed sample SD. Use 10000
stratified paired bootstrap resamples of problem IDs (fixed RNG seed 20261115),
retaining all seed outcomes for an ID together and preserving the three stratum
sizes. Report percentile 95% intervals. These intervals are conditional on the
three seeds; a separate hierarchical bootstrap resampling matched seed pairs
and problems is a sensitivity analysis, explicitly weak with only three seeds.

Accuracy noninferiority uses the same paired stratified resampling. Publish
stratum-specific accuracy, M, theory conditional on correctness, length, valid
format rate, failure counts and judge latency as secondary descriptive metrics.
Transfer resamples source IDs, keeping each source's four targets and all
conditions together. No treating generations, seeds or probes as independent
problem samples. No post-hoc exclusions of difficult or unfavorable outputs.
Corrected implementation errors invalidate and rerun affected comparisons with
an amendment. A failed model generation is recorded, not dropped from accuracy.
Infrastructure failures are separately enumerated and retried identically.

The first single-seed result is exploratory and cannot meet the confirmatory
claim. Other arms and subgroup analyses are descriptive; no uncorrected family
of confirmatory tests. Do not increase sample size merely to cross a threshold.
Report all runs, including failed pilots, zero-variance groups and negative results.

## Stop, publication and limitations

Stop on nonfinite losses, repeated infrastructure errors, audit failure, failed
checkpoint recovery or exhausted budget. A wrong answer alone is not an
infrastructure failure. Publish a milestone before each model stage and after
each run/evaluation; do not hide unsuccessful stages. All empirical numbers,
tables and figures are regenerated from saved machine-readable records.

Limitations include subjective and possibly correlated judges, quantization,
small models and synthetic families, uncertain contamination, only three seeds,
and potentially low power at the fixed sample size. No latent-space measurements
are included. See the [review](state-of-the-art-review.md) for primary sources.
