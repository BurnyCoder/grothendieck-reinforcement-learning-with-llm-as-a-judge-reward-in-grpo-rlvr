# Implementation observations

## 2026-11-15: dependency resolution and provenance

Initial unconstrained resolution selected an old Unsloth release while maximizing
newer Torch/TRL/Transformers. This was caught by inspecting `uv.lock` before
installation completed or any model ran. The old package does not establish
Qwen3.5 support. The installer was interrupted; the project now requires the
current released Unsloth and honors its published compatibility ceilings.
Evidence: [Unsloth release metadata](https://pypi.org/pypi/unsloth/2026.11.4/json)
and [official package specification](https://github.com/unslothai/unsloth/blob/main/pyproject.toml).
The final exact environment is recorded in `uv.lock`; latest compatible means
compatible with this training implementation, not independently maximizing each
package version. This is an implementation issue, not a model feasibility result.

The llama.cpp release API's `target_commitish` differed from the commit actually
referenced by the release tag. The model/runtime lock records the checked-out
tag commit, verified by the built executable. The local CPU server compiled
successfully. No inference measurement is implied by a successful build.

Generator-source observations and corrected rounding instructions are documented
in the state-of-the-art review. No policy outputs informed these decisions.

## 2026-11-15: valid novelty and secondary task-family generalization

The user requested greater reward for valid conceptual novelty and more distant
mathematical content. Before any judge request, rubric v2 and its dated amendment
were implemented together: fixed conventional references, an explicit novelty
criterion, validity-gated component logs, constructed bridge/false-theory
calibration, and a separate locked OOD suite. The original primary manifests
remain byte-for-byte unchanged. The primary formula and acceptance thresholds
are retained; the revised meaning of T is disclosed rather than retroactively
editing the initial preregistration.

New tests were written first and failed for the absent novelty property,
calibration stratum and OOD module. Their passing results are archived in
`verification-novelty.xml`; full-suite evidence is in `verification.xml`.
These are software checks, not model performance results. The regenerated PDF
was rendered and all pages visually inspected. Local dashboard HTTP responses
were checked; browser UI inspection remains unverified for the previously
recorded environment limitation.

Inspecting Reasoning Gym's polygon generator showed that it only constrains the
known-angle sum below the full sum, which can leave a missing angle outside
the convex range. The OOD wrapper rejects these instances before locking and
records them in `data/ood.lock.json`. This source-level correction was selected
without policy outputs. Existing generators and SymPy operations were reused
instead of duplicating their implementations; independent reference algorithms
and bounded candidate parsing check the resulting scalar answers.

The pre-inference analysis review also found that transfer generation included
all registered controls, while reporting only computed contrasts against no
notes. A regression test first exposed the missing related/unrelated and
between-source contrasts. The shared source-clustered comparison now covers
all of them and requires complete matched coverage. Evidence is retained in
`verification-analysis.xml`. This completes the existing transfer analysis plan
rather than adding an outcome selected from results.

## 2026-11-15: verifier startup failure before first judgment

The first development-calibration process stopped on two verification timeouts
before contacting Gemma. Heavy concurrent dependency installation and model
hashing were using the data drive; hashing was suspended to reduce contention.
The parser's needless symbolic imports for scalar tasks were removed without
weakening resource limits. A failing precision regression also showed that
AST float conversion could accept an unequal decimal; exact literal parsing
corrects it. The [verifier clarification](amendments/2026-11-15-verifier-runtime.md)
records the grammar detail and sources. All original failure logs are preserved.

## 2026-11-15: serving identity and execution checks

Gemma's CPU development run produced a structured judgment, then was interrupted
during the following request because throughput had deteriorated. The complete
timestamped stream is preserved under `reports/development/`; one report command
derives its counts and durations. This does not establish a calibration pass.
The runtime amendment records the interpretation and planned evaluation offload.

Serving settings now participate in cache and calibration identity, and changed
development locks can be archived explicitly without resetting locked audits.
The initial regression tests exposed the missing runtime identity and override
guard. The old override test also started a server before failing; it was stopped
without issuing an inference request, and the test now forbids subprocess launch.
The passing runtime/workflow regression results are in `verification-runtime.xml`.

Official CUDA archives use the already-pinned source commit and independently
published SHA-256 values. The setup script verifies them before extraction.
CUDA availability and BF16 support are confirmed; policy backward/GRPO feasibility
remains to be measured. Full interpreter output is unbuffered through the CLI.

## 2026-11-15: native environment and pilot failure observability

The native WSL environment uses the same source checkout and exactly the same
package versions as the original environment; their complete `uv pip freeze`
outputs compare equal. The published inventory is `environment-native.txt`,
and workflow regression evidence is `verification-native-environment.xml`.
This is an installation check, not a controlled import-speed experiment.

Before the first optimizer update, inspection found that the reward callback
logged policy completions only after all verifier/judge calls succeeded. A
failure could therefore lose unassessed answers from that sampled batch. New
failure-injection tests reproduced the loss. The callback now records every
complete prompt/answer before verification or judging, without assigning a
reward in those observation records. Scoring and training settings are unchanged.
The in-flight pilot loaded the prior callback; the repair applies to subsequent
processes. Both execution versions remain distinguishable in publication history.

The first GRPO attempt then stopped during generation prefill, before any reward
call or optimizer update. Its traceback contains a literal carriage return in
the generated-module path. A byte check of the ignored `.env` confirmed CRLF on
the compiler-cache assignment; Bash's original `source .env` preserved that
character. A launcher regression reproduced the failure with a fake interpreter,
without loading a model. The shared loader now strips only end-of-line carriage
returns before sourcing configuration. Model versions and hyperparameters are
unchanged; no PyTorch patch or fallback policy is warranted by this failure.

The console, traceback, and derived failure record are retained under
`reports/development/`. The interrupted run directory is archived under the
artifact root, and the retry starts from the unchanged base because no complete
checkpoint exists. The LF/CRLF launcher and failure-preservation tests are in
`verification-launch-and-logging.xml`. The corrected GRPO execution still needs
to demonstrate generation, backward, saving and resumption.

## 2026-11-15: first saved GRPO boundary

The corrected pilot generated separate groups of answers, ran the external
verifier and CPU judge, completed backward, and saved a complete optimizer-boundary
checkpoint. The observed warmup learning rate was zero: this boundary establishes
execution and state saving, not a learned improvement. The next invocation
explicitly resumed that checkpoint. Its prompts are the next development tasks
and its reward-call counter continues from the saved value. It completed the
remaining boundary with finite loss/gradient metrics at a nonzero learning rate.
Direct tensor comparison confirms a parameter change; both checkpoint directories
contain adapter, optimizer, scheduler, RNG, trainer and judge-cache state.
The full execution log and derived recovery checks are preserved under
`reports/development/`. A single resumed step does not establish stable throughput
or a mathematical improvement. Pilot adapters are excluded from initialization.

Qwen development calibration was paused to give the pilot exclusive access to
the CPU judge and its cache during recovery. The partial v3 stream and its lock
are preserved. Some v3 judgments still overcredit conventional generalizations;
the longer reference clarification has not established a repair. No locked
audit or comparative experiment has run, and long training remains gated.
After pilot completion the unchanged development calibration was resumed from
its content-addressed cache. Gemma's registered CUDA runtime is now being loaded
with the policy stopped; successful serving and calibration remain separate checks.
