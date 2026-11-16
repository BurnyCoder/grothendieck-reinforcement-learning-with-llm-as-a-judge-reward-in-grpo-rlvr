# Deferred research roadmap

Recorded 2026-11-16 at the user's request. **All work below is postponed until
after the current small-GPU experiment sequence.** Continue the published
feasibility, baseline, matched training, OOD and transfer work first. This roadmap
does not modify its frozen models, reward, thresholds, sample sizes or analysis.
It registers intentions, not results or a fully specified future experiment.

## Larger models

Try **10B+, 100B+ and 1T+ parameter models**, using available Qwen/Gemma models for
policy and/or judge roles. These are target scales, not claims that suitable
checkpoints at every scale currently exist or fit the present GPU. For sparse
mixture-of-experts models, report both total and active parameters. Plan hardware,
quantization, memory, throughput and compute budgets before selecting checkpoints.
Keep inference local unless that constraint is explicitly changed later.

Vary policy size and judge size separately where feasible, retain smaller-model
baselines, and compare quality at both matched task exposure and reported compute
cost. Larger models are a hypothesis about improved behavior or judgment, not a
guarantee of calibration. Use fresh frozen identities and held-out confirmation.

If the small-policy experiment needs the user's
[simpler-task fallback](../reports/amendments/2026-11-16-task-difficulty-fallback.md),
retain the current problems and their harder/OOD variants for these larger-model
studies. Preserve their manifests and all prior outcomes. Keep results separated
by difficulty; use new held-out confirmation when earlier outcomes informed
development. The fallback is conditional and has not changed the active data.

## More advanced agentic RL

Study multi-step mathematical investigation: propose a definition or invariant,
test examples and counterexamples, use symbolic/proof tools, revise the proposal,
derive consequences, and maintain a reusable library. Separate policy actions
from tool observations and evaluate complete trajectories as well as final answers.
Specify credit assignment, tool-call and token budgets, stopping rules and recovery.
Compare against the current single-response GRPO and matched-compute tool-use
baselines; test each added mechanism with an ablation. TRL documents
[tool-calling GRPO and environment integration](https://huggingface.co/docs/trl/main/en/grpo_trainer#tool-calling-with-grpo);
compatibility with the project's future pinned runtime must be tested.
The supplied [AGrI passage](rising-sea-quotations.md#artificial-grothendieck-intelligence-agri)
also motivates investigating coordinated research agents. That proposal remains
part of this postponed direction, not an implemented capability of the current run.

## Lean and formal mathematical feedback

Use [Lean's proof checker](https://lean-lang.org/doc/reference/latest/Introduction/)
to validate formal definitions, lemmas and their consequences under explicit
assumptions. Investigate [LeanDojo](https://github.com/lean-dojo/LeanDojo) as an
existing interface for interacting with Lean and extracting proof data; review
the then-selected versions and licenses before reuse. Pin Lean and its mathematical
library, inspect dependencies/axioms, reject proof placeholders and unapproved
axioms, and check that formal statements express the intended task.

Investigate scoring abstract structures in Lean by how fundamental they are:
how much they use fundamental axioms to construct novel, deeper, more fundamental
structures versus how much they combine more high-level theorems.

Run any future generated tactics in a bounded, isolated environment. The present
pipeline still does not execute generated code. A checked proof establishes the
formal statement relative to its assumptions; it does not establish conceptual
importance, historical novelty or useful exposition.

## More exact quantification in place of LLM-as-a-judge rewards

Aim to operationalize every current criterion with explicit formulas and
independently checkable evidence, reducing or replacing learned judgment. Treat
a token-length penalty as an example of a directly computable quantity, not as
evidence that short text is better mathematics. TRL supports
[custom programmatic rewards](https://huggingface.co/docs/trl/main/en/grpo_trainer#using-a-custom-reward-function).
The following are candidate measurements to investigate, not validated replacements:

| Construct | Candidate computable evidence | Main limitation to test |
|---|---|---|
| Correctness and validity | Checked answers and Lean proofs with approved assumptions | A wrong formalization can prove the wrong claim |
| Structure and definitions | Dependency graphs showing which introduced objects support checked results | Counts can reward unnecessary definitions |
| Generality and boundaries | Parameterized theorems, explicit domains and held-out instantiation success | Finite tests cannot establish an unrestricted theorem |
| Problem as a consequence | A checked derivation from proposed lemmas to the original statement | Restating the answer as a lemma is not useful abstraction |
| Reuse and connections | Checked downstream applications and frozen-recipient transfer accuracy | Task selection can make reuse look artificially strong |
| Economy and exposition | Token counts, redundancy, derivation length and compute cost | These do not fully measure clarity or motivation |
| Constructive novelty | Canonicalized formal comparison against a fixed reference library | Syntactic distance is not semantic or historical novelty |

Distinguish exact computation of a defined quantity from validity as a measure of
the intended construct. Transfer accuracy is measured with sampling uncertainty;
semantic novelty may remain only partially operationalized. Publish that residual
uncertainty instead of claiming that all theory-building qualities are exact.

Before activating this work, preregister formulas, normalization, weights, caps,
reference libraries, data splits and acceptance/falsification criteria. Preserve
correctness priority and modest credit for valid connections. Compare the current
LLM judge, programmatic-only and hybrid rewards, including adversarial cases for
padding, artificial lemma splitting, vacuous generality and circular reuse. Report
each component, cost and uncertainty; do not add a length penalty to the current run.

## Activation

Each direction needs a dated amendment, source/license review, feasibility checks,
frozen identities, matched controls and suitable held-out data before execution.
Use the [living plan](../reports/plan.md) to record sequencing and unfinished work.
None of these postponed ideas is a reason to delay the current small-model run.
