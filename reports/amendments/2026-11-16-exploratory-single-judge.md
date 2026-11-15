# Exploratory training with an unqualified single-call judge

Date: 2026-11-16, Europe/Berlin. Recorded after the observed calibration failures
and before any training or evaluation in this new experiment. Artifact timestamps
use UTC. The user explicitly instructed: "do the training with single LLM as a
judge call per solution ... anyway as an experiment" if the thresholds cannot
be passed now, with larger judges reserved for future experiments.

## Scope and decision

The two-call repair and quoted-Qwen specialist configuration failed development.
Rubric-only specialist development also failed its fixed futility rule; its
complete terminal evidence is preserved in
[the case report](../experiments/qwen-v8-specialist-rubric-learnings.md).
The remaining quoted-Gemma specialist development is deferred under this new
instruction. It is not marked passed, failed or completed. No locked audit has
been opened or reset.

This amendment creates `exploratory-single-v1`, a separate experiment explicitly
allowed to train with unqualified judges. The original development and audit
requirements, acceptance thresholds, cases and historical scores remain intact.
No failed calibration is relabeled as successful. Neither ordinary `train` nor
locked-audit commands acquire a general bypass. The new CLI flag `--exploratory`
and a matching `exploratory-single-v1-` run prefix select this exception.

## Frozen instrument

Reuse the latest published single-call scoring prompt, rubric v7 with reference
v3 and the attributed rising-sea framing. This chronological choice is not a
selection of the highest-scoring calibration attempt. Its quoted Qwen predecessor
failed development; the exact Gemma configuration has not qualified either.
Keep all six weights, modest credit for a concrete valid connection, higher
credit for developed frameworks, the supported-validity gate, and
`R=C*(1+0.5*T)`. Incorrect or malformed final answers receive no theory judgment
and zero reward. Correctness-only training uses only the verifier.

The new `single-v1` protocol produces one accepted structured assessment per
correct solution, or reuses its exact cached assessment. It has no specialist
or synthesis calls. Bounded retries remain restricted to transport, schema or
evidence-contract failures; valid but unfavorable opinions are never rerolled.
The existing visible/reasoning budgets, model revisions and runtime settings are
unchanged. Complete served-template token checks reserve the full generation
budget before each request; no silent truncation is allowed. This preflight has
its own identity and does not rescore or reuse a differently identified legacy
opinion. All frozen identities are in
[`configs/exploratory-single-judge.json`](../../configs/exploratory-single-judge.json).

Qwen3.5-9B remains the CPU training judge. Gemma 4 12B supplies separate
single-call evaluation after policy generation, with the registered GPU offload.
No new model download, family or remote inference is introduced. Judge errors
may be systematic and correlated; "noisy" does not mean unbiased random noise.

## Question, comparisons and analysis

The exploratory question is whether this imperfect theory reward can improve
measured behavior relative to correctness-only GRPO at the available model scale.
The first comparison retains seed 42, the same selected unmodified Qwen3.5-2B
initialization, matched prompts and generation budgets, and 64 updates per arm.
Include ordinary and rising-sea prompted unchanged-policy baselines. Keep the
registered optimizer, LoRA, KL and normalization settings. Pilot updates remain
excluded from every comparative initialization.

Retain the 400-problem primary manifest, separate 200-problem OOD suite and
100-source/four-target transfer design. Report verified accuracy, the unqualified
Gemma correctness-weighted theory/novelty scores, response lengths, and verified
recipient transfer. Use the existing paired problem-level stratified bootstrap
and source-clustered transfer analysis. The original effect and accuracy targets
remain reference targets, not an alternative declaration of qualification.
No number of completed seeds can make this track confirmatory. A single seed
does not estimate between-seed variability; later matched seeds and controls
remain planned within the week, with unfinished work reported explicitly.

No improvement, reduced verified accuracy, or higher training reward without
independent/transfer improvement are possible negative outcomes. A higher Gemma
score alone is insufficient to establish more valid mathematical understanding.
Do not extend sampling to obtain significance, select the best test checkpoint,
or change the reward after seeing held-out results. Evaluate the final fixed-budget
checkpoint. Preserve unexpected outputs, invalid formats and unsuccessful runs.
Future result-informed repairs or larger-judge studies need separate amendments;
fresh held-out confirmation is required after using these results for selection.

## Execution, recovery and publication

Publish this amendment, tested implementation, frozen identities, README, paper
and site before new inference. Refresh the development-only save/resume pilot
with the single-call judge; retain the existing worst-length BF16 memory evidence
because policy architecture and sequence budgets are unchanged. Record actual
judge latency, throughput, peak memory and mathematical outputs. Publish the
pilot before long training and update runtime estimates from measured intervals.

Start each arm from the selected base. Save adapters, optimizer, scheduler, RNG,
data position, configuration and judge-cache state at optimizer boundaries.
Infrastructure failures terminate or resume explicitly; they are never assigned
incorrect-answer rewards. Nonfinite metrics stop execution. A disappointing
learning result is retained rather than silently converted into another arm.
Report each training/evaluation milestone and retain complete logs. Separate run
and transfer directories, identity checks and report fields prevent accidental
mixing with the original qualified-study analysis.

## Prior work and limitations

[Rubrics as Rewards](https://arxiv.org/html/2507.17746v1) motivates testing rubric
feedback in on-policy learning, but its tasks, models and rubrics differ.
[Gao, Schulman and Hilton](https://proceedings.mlr.press/v202/gao23h/gao23h.pdf)
observe divergence between optimized proxy rewards and a separate reward model
in a synthetic setting. That motivates keeping independent measurements; it
does not predict our outcome or validate either judge. No source code or prompt
from that paper is imported. Larger judges may improve the instrument, but this
is a future empirical question, not an assumption used to interpret this run.
