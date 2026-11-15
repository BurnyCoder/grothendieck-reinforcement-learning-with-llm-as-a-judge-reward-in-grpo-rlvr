# Matched training budget after the execution pilot

Date: 2026-11-15, before any comparative optimizer update or locked policy
evaluation. The unmodified Qwen3.5-2B checkpoint is frozen. Judge calibration
remains incomplete and continues to block comparative training.

Select **64 optimizer updates for every training arm and seed**, reducing the
original maximum of 256 as allowed by the preregistration's budget rule. Keep
all other training hyperparameters, seeds, prompts, task ordering, generation
budgets per update, reward variants and evaluation sizes fixed. Every arm uses
the final prescribed checkpoint; do not choose a checkpoint using test outcomes.
The unchanged warmup ratio applies to the new common update budget.

The [generated timing scenarios](../training-budget.md) use both recorded pilot
optimizer intervals. Repeating either interval at the original maximum leaves
insufficient time for the complete study: even the judge-scored training arms
alone exceed the one-week budget in that scenario. The selected budget gives
more room for correctness-only baselines, calibration, the primary evaluation,
the additional OOD suite and note transfer. It also brings the projected first
judge-scored run within the original approximate training-time target.

These scenarios are arithmetic planning aids, not steady-state measurements or
confidence intervals. The pilot used the earlier v3 judge and produced no
supported theory bonus; v4 latency and learned output lengths or reward density
can differ. The first interval includes initial execution overhead. Keep those
limitations visible, and update runtime estimates from recorded operation.

The tradeoff is less optimization and fewer distinct training prompts. Report
actual consumed examples and tokens. A negative result at this budget does not
establish failure with longer training. Do not extend the confirmatory runs in
response to their test scores; any later extension requires a dated amendment
and separate exploratory reporting. Preserve all negative and unfinished runs.
If the full sequence still exceeds the week, report unfinished comparisons
instead of reducing the locked evaluation sample or claiming a completed study.

The memory/runtime pilot supports retaining the preferred policy. Reducing the
matched update budget does not substitute a fallback model or retain pilot
updates. All arms and the frozen recipient start from the same selected base.
