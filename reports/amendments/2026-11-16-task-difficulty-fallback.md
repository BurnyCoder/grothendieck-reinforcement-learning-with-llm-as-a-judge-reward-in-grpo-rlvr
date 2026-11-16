# Conditional simpler-mathematics fallback

Recorded 2026-11-16 after the user's instruction to try simpler mathematics if the
current small Qwen cannot solve the present problems, retaining the present tasks
for the postponed larger models. This records a conditional next step. It does
not change the active experiment, its data, reward, judge or acceptance criteria.

## Current evidence and decision

The [small-GPU development pilot](../experiments/exploratory-small-gpu-v2-pilot.md)
contains verified correct completions, alongside an all-incorrect resumed batch.
It therefore does not establish that this policy cannot solve any current tasks.
Continue the registered small-model sequence. A single zero-reward batch is not
sufficient evidence to activate a difficulty change.

## Diagnose on development data

If training produces persistently unusable correctness rewards, check the fixed
development tasks and recorded rollouts. Separate mathematical errors, missing
or malformed final answers, verifier failures and judge failures. Infrastructure
failures remain explicit errors; they do not count as mathematical inability.
Do not select task difficulty using primary, OOD or transfer-test scores.

Before an additional diagnostic, publish its task IDs, decoding settings,
completion budget and decision rule. Use complete prespecified development
coverage and report all outcomes, including correct solutions. Do not repeatedly
sample or choose subsets until a desired diagnosis appears. A zero observed
success rate under a stated budget is evidence about that configuration, not a
proof of universal inability.

## If the difficulty fallback is needed

First simplify the existing generators: smaller integers for GCD/LCM, fewer and
lower-degree polynomial terms, or fewer dice with smaller face counts. Reuse
[Reasoning Gym](https://github.com/open-thought/reasoning-gym) through the existing
[task-generation interface](../../src/grothendieck_rlvr/data.py). If necessary,
add elementary arithmetic families with exact independent verification. Choose
tasks that still permit useful general rules and valid connections.

Publish a dated experiment specification with exact parameters, seeds, verifiers,
reference solutions, disjoint manifests, matched baselines/controls and analysis
before new runs. Give the easier study a separate identity and new held-out data;
do not overwrite the active manifests, relabel completed runs, or pool results
across difficulties. Keep correctness gating, rubric weights, modest credit for
valid connections and calibration thresholds unchanged.

Preserve the current tasks, their difficulty levels and recorded failures for the
[postponed larger-model experiments](../../docs/future-research.md). They may
serve as a fixed comparison suite; any results used for development cannot also
be claimed as untouched confirmation. Report task difficulty alongside all
scores. Better performance on easier problems alone is not evidence of an
improvement on the original task distribution.
