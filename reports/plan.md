# Implementation and experiment plan

Updated 2026-11-15. Authority: user-approved Qwen3.5/Gemma plan and
[preregistration](preregistration.md), amended before judgments by the
[valid-novelty/OOD protocol](amendments/2026-11-15-valid-novelty-and-ood.md).
This checklist is a status record, not
evidence of model performance.

Development judging motivated a [v3 novelty-boundary clarification](amendments/2026-11-15-novelty-reference-boundary.md).
The v2 and v3 attempts are preserved. The
[v4 evidence protocol](amendments/2026-11-15-judge-evidence-protocol.md) now requires
evidence before scoring and explicit validation feedback on retries. Development
calibration checks novelty first and can stop when the fixed thresholds become
unreachable. Untouched full locked audits remain required. No comparative run has begun.

- [x] Inspect workspace, local hardware and publication accounts.
- [x] Review relevant mathematics, rubric RL, theory formation and runtime sources.
- [x] Specify hypotheses, splits, reward, controls, calibration and analysis.
- [x] Publish initial review, preregistration and README before model inference.
- [x] Initialize uv/Python 3.12 project and lock compatible releases.
- [x] Implement typed task, verification, judgment and reward interfaces.
- [x] Build deterministic manifests with reference and overlap checks.
- [x] Implement versioned quoted and rubric-only judge prompts and calibration.
- [x] Implement Unsloth/TRL training, checkpoint/resume and feasibility probe.
- [x] Implement unchanged-policy, independent-judge and transfer evaluation.
- [x] Implement statistics, artifact-driven reports/PDF and dashboard/Pages.
- [x] Add constructive novelty to the versioned judge prompt and reward schema.
- [x] Add conventional reference anchors and explicit rejection of false/decorative novelty.
- [x] Add constructed calibration contrasts for useful distant mathematical bridges.
- [x] Implement a separately locked OOD suite and component-level reporting.
- [x] Run offline reward, verifier, isolation, recovery, novelty/OOD and reporting checks.
- [ ] Exercise model-backed training, resumption, evaluation and complete workflow.
- [x] Exercise development GRPO generation, backward, checkpoint saving and resumption.
- [x] Publish initial implementation, manifests, paper and site to GitHub/Hugging Face.
- [x] Publish the tested novelty/OOD amendment and regenerated artifacts before judgments.
- [ ] Complete development calibration, then audit both frozen judges and rubric-only variant.
- [x] Complete development execution pilot and freeze the unmodified policy checkpoint.
- [x] Freeze the matched comparative update budget from development timing evidence.
- [ ] Evaluate unmodified ordinary and prompted policies.
- [ ] Train/evaluate theory-bonus seed 42 and correctness-only seed 42.
- [ ] Train/evaluate matched seeds 43 and 44, plus seed-42 controls.
- [ ] Evaluate note transfer and regenerate all analysis artifacts.
- [ ] Evaluate all frozen comparison checkpoints on the separate OOD suite.
- [ ] Publish each milestone, including negative/unfinished outcomes.

Model downloads and artifact hashes are complete. The maximum-length BF16 LoRA
backward probe passed; the repaired four-completion GRPO pilot completed
checkpoint resumption and a nonzero parameter update. Its first boundary had
a zero warmup learning rate. These are execution checks, not learning evidence;
pilot updates are excluded from comparative initialization.
The [policy selection](../configs/policy-selection.json) freezes the preferred
Qwen3.5-2B base revision for every arm and the transfer recipient. No fallback
is selected. The [budget amendment](amendments/2026-11-15-training-budget.md)
selects 64 updates uniformly before any comparative run. Judge calibration remains a gate.
Development judging by both models has started but is incomplete;
the initial GRPO attempt failed during generation on a CRLF configuration-path
bug, now repaired and regression-tested, before its first optimizer update;
the interrupted CPU attempts are retained. Evaluation
GPU offload loaded successfully; an initial slow attempt was interrupted. The
[thread diagnostic](amendments/2026-11-15-judge-thread-diagnostic.md) completed
without supporting a lower thread count. The clean standalone retry completed
judgments, including a rejected excerpt and accepted retry. The initial slowdown
remains unexplained. Runtime provenance follows the
[runtime amendment](amendments/2026-11-15-judge-runtime.md). No calibration pass,
policy evaluation or comparative training result is claimed. Initial local constraints are
environment observations rather than comparative experimental results. Publication and
calibration gates must be satisfied before long training. The observed v3
development judgments still assign novelty to some conventional arguments;
the clarification has not established a successful repair. Week-budget decisions
use measured pilot throughput and are documented before comparison runs.
The initial v4 novelty contrasts passed, while full calibration remains incomplete.
The [registered runtime diagnostic](amendments/2026-11-15-evaluation-offload-diagnostic.md)
compared additional GPU offload at full context without improving measured
speed. The resumed calibration subsequently stalled again. The
[stream-deadline amendment](amendments/2026-11-15-judge-stream-deadline.md)
registers passive OpenMP waiting for evaluation and a total streaming deadline.
The new development run stopped under the fixed futility rule after nonzero
novelty was assigned to conventional polynomial and probability controls.
See the [failure analysis](experiments/gemma-v4-learnings.md) and generated
case table. False-theory cases were not reached. Long training and locked audit
remain blocked; the behavioral hypothesis is untested. That failure motivated
testing Qwen's existing v4 protocol before choosing a general inference revision.
Qwen's existing v4 development run subsequently passed its observed novelty
contrasts but incorrectly treated conventional generalized explanations as
offering no theory. It was interrupted for a documented diagnostic revision,
not declared a completed pass or threshold failure. The
[bounded-reasoning amendment](amendments/2026-11-15-bounded-judge-reasoning.md)
keeps the rubric, references, cases and thresholds while enabling a capped native
reasoning phase for both judges. Run Qwen quoted development first, then the
remaining required variants if it passes, followed by untouched locked audits.
Preserve all failed and interrupted opinions as development evidence.
That Qwen reasoning attempt has now failed the unchanged futility gate; see its
[failure analysis](experiments/qwen-reasoning-v4-learnings.md). The remaining
variants under that protocol will not run. Investigate explicit comparison with
the fixed conventional reference before choosing a numerical novelty score;
publish a further amendment before new inference. Acceptance gates remain fixed.
The [v5 amendment](amendments/2026-11-15-explicit-reference-decisions.md)
implements this explicit decision and consistency check. It clarifies the finite
reference boundary while preserving all cases, labels, ordering and thresholds.
Test Qwen quoted development first, then the remaining variants only on a full
pass. Schema compliance alone cannot establish valid novelty discrimination.
That attempt ended in a repeated score-consistency contract failure before the
probability contrast completed. Preserve its
[negative execution result](experiments/qwen-v5-contract-learnings.md).
The [v6 amendment](amendments/2026-11-15-declared-novelty-eligibility.md)
implements a declared-eligibility gate while retaining raw opinions. It withholds
the novelty component for unmet prerequisites and logs the reason, preserving
the other supported-theory components. Publish before one fresh Qwen quoted
development attempt; keep remaining variants and untouched audits conditional
on complete development passes. Evaluate the combined code-and-judge instrument,
and separately report differences between raw and effective novelty. Do not
reinterpret the v5 attempt as a completed pass or a threshold failure.

V6 was subsequently interrupted after the user's explicit clarification that a
brief valid mathematical connection should receive modest novelty credit even
without a further worked consequence. Its observations are preserved in the
[interruption report](experiments/qwen-v6-interruption-learnings.md). The
[v7 amendment](amendments/2026-11-15-modest-valid-connections.md) implements a
one-point cap for such connections and higher credit for developed frameworks.
It changes the constructed calibration expectations and adds contrasts to retain
zero credit for routine methods and decorative terminology. Publish all changes
before a fresh Qwen quoted development attempt, then the other variants and full
audits only after complete development passes. Historical rates are not rescored.

The fresh v7 attempt subsequently failed the fixed futility gate; see its
[failure analysis](experiments/qwen-v7-learnings.md). Its developed frameworks
ranked above the controls, but the modest-versus-zero control-credit conditions
failed. No false-theory case was reached. Preserve this distinction in reporting
and retain the failed run unchanged. Clarify the mathematical scope of the
conventional references in a separate published amendment before new inference;
do not change the user preference, cases, labels or acceptance thresholds.
The [reference-scope amendment](amendments/2026-11-15-explicit-reference-scope.md)
now specifies that isolated intervention. Reference version v3 clarifies
commutative polynomial methods and ordinary biased-probability calculations;
rubric v7 and all cases remain unchanged. Publish before one fresh Qwen quoted
development trial. Its result determines whether the remaining checks proceed.

Implementation is present but model-backed integration remains unverified.
The initial review/preregistration commit is `bcf85b1` in
https://github.com/BurnyCoder/grothendieck-reinforcement-learning-with-llm-as-a-judge-reward-in-grpo-rlvr . The Hugging Face dataset repository
exists at https://huggingface.co/datasets/BurnyCoder/grothendieck-rlvr . Collection
creation returned an account-level daily rate limit and remains pending.
The in-app browser backend was unavailable; Windows browser inspection was
stopped by URL-policy enforcement. No UI validation success is claimed.
