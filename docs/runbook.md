# Running the research pipeline

Use WSL Ubuntu and Python 3.12. Commands below run from the repository root.
`scripts/run.sh` loads `.env` before Python starts, including `PYTHONHASHSEED=0`.
The shared loader accepts LF and Windows CRLF line endings without changing the
configuration file or printing its contents. This prevents carriage returns from
entering compiler-cache and interpreter paths.
The local `.venv` is managed by uv; large files live in the configured data-drive
directory. Copy `.env.example` to `.env` when cloning on another machine.
`UNSLOTH_COMPILE_LOCATION` also directs Unsloth's generated modules to the project
artifact directory; the default local generated-cache folder is ignored by Git.
This follows the installed, pinned `unsloth_zoo/compiler.py` environment option.

If the checkout is on a Windows mount and cold imports are slow, the same
`uv.lock` can install a project-specific virtual environment under WSL's native
filesystem. Set `UV_PROJECT_ENVIRONMENT=/home/your-user/projects/grothendieck-rlvr-runtime/.venv`
in the ignored `.env`, then rerun `scripts/setup-wsl.sh`. `scripts/run.sh` uses
that interpreter while keeping this checkout as the source. The default remains
the local `.venv`; model caches, logs and checkpoints remain under `GROTH_ROOT`.
For direct Python/pytest/Ruff commands below, substitute the configured venv path.
See [uv's environment-path documentation](https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path)
and [Microsoft's filesystem guidance](https://learn.microsoft.com/en-us/windows/wsl/filesystems).

## Install and prepare

```bash
bash scripts/setup-wsl.sh
bash scripts/run.sh doctor
bash scripts/run.sh prepare
bash scripts/run.sh prepare-ood
.venv/bin/python -m pytest -q
.venv/bin/ruff check src tests
```

The lock file honors Unsloth's current release compatibility ceilings. Run
`uv sync --locked --extra train` for an exact repeat; do not update dependencies
between experimental arms. Data preparation archives full generator entries,
checks references and canonical overlap, and creates a manifest lock. Re-running
preparation validates existing files instead of replacing locked data.

Download the pinned models without running them:

```bash
bash scripts/run.sh download
bash scripts/run.sh hash-models
```

Build the exact llama.cpp commit in `configs/models.lock.json`. The CPU route:

```bash
git clone https://github.com/ggml-org/llama.cpp /mnt/d/AI/grothendieck-rlvr/tools/llama.cpp
git -C /mnt/d/AI/grothendieck-rlvr/tools/llama.cpp checkout b1b770d90d94cad9e9ea5b993bdbc383a522fb28
cmake -S /mnt/d/AI/grothendieck-rlvr/tools/llama.cpp -B /mnt/d/AI/grothendieck-rlvr/tools/llama.cpp/build -DGGML_CUDA=OFF -DLLAMA_BUILD_TESTS=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build /mnt/d/AI/grothendieck-rlvr/tools/llama.cpp/build --target llama-server -j 8
```

Evaluation GPU offload uses the official CUDA 12.8 binaries at the same commit:

```bash
bash scripts/setup-judge-cuda.sh
bash scripts/run.sh serve --role evaluation_judge
```

The archive checksums are pinned in `configs/llama-binaries.lock.json`. Serving
parameters are frozen in `configs/judge-runtime.json` and included in judge/cache
identities. The CLI rejects an inconsistent `--gpu-layers` override. A changed
backend, offload count, or KV precision requires development recalibration and a
matching audit; old results remain separate. The CPU build cannot offload even
if a layer count is requested. Never place the training judge on GPU. Stop the
evaluation judge before loading the policy, and generate policy outputs before
loading the evaluation judge. Preserve interrupted development logs and locks.

## Publication gate

Publish the review and preregistration first. Then publish tested implementation,
locked manifests and dependencies, prompts, initial paper and site to GitHub and
the project's Hugging Face dataset repository **before model inference**. Model
downloads and offline software tests are not model inference. Never upload `.env`,
tokens, venvs or caches. Do not replace missing results with synthetic metrics.

## Calibrate the frozen judges

In a dedicated terminal, start a judge (foreground process; stop with Ctrl-C):

```bash
bash scripts/run.sh serve --role training_judge
```

In another terminal:

```bash
bash scripts/run.sh calibrate --role training_judge --variant quoted --split dev
bash scripts/run.sh calibrate --role training_judge --variant rubric --split dev
```

Development calibration can motivate a documented prompt change. Once fixed,
run each locked audit exactly once. Restart the server with `--role
evaluation_judge` and calibrate its quoted variant. Run `--split audit` for all
three required configurations. Failure blocks long training. Changed inputs
cannot silently reuse an audit: preregister an amendment and reserve fresh cases.
After a dated development amendment, `--split dev --restart-development` archives
the previous development lock/results before starting the changed configuration.
It cannot reset an audit. An interrupted run with unchanged inputs resumes from
its content-addressed cache without this flag.

The [v4 protocol](../reports/amendments/2026-11-15-judge-evidence-protocol.md)
checks novelty cases first and may stop development as failed when the remaining
cases cannot reach the unchanged thresholds. Partial observed rates and their
denominators are reported explicitly. Audit runs always complete the fixed suite;
only a full pass with matching judge and protocol identities authorizes training.
Evidence-format retries include validation feedback, with at most three total
attempts. An infrastructure failure still terminates, rather than reducing reward.

The [bounded-reasoning amendment](../reports/amendments/2026-11-15-bounded-judge-reasoning.md)
sets `judge_reasoning_budget_tokens` per role in `configs/study.json`. A positive
value enables the native thought channel and adds that allowance to the existing
assessment-token ceiling; zero retains the original non-thinking request.
The current development attempt uses 512 reasoning tokens and 2,048 total tokens.
All thought chunks are logged, but only visible JSON enters the rubric parser.
Changing this setting invalidates that role's calibration and cache identity.
Publish configuration changes before inference and keep old results separate.

## Feasibility, saving and resumption

After publication, use development-only pilots:

```bash
bash scripts/run.sh memory-probe
bash scripts/run.sh train --pilot --arm theory --seed 42 --stop-after 1
bash scripts/run.sh train --pilot --arm theory --seed 42 --resume
```

The separately preregistered execution diagnostic is
`bash scripts/run.sh benchmark-judge`. Stop policy and judge processes first.
It records synthetic Gemma decoding timings for the fixed thread-count sweep
under the artifact root's `benchmarks/` directory; it never supplies reward scores.
See the [diagnostic protocol](../reports/amendments/2026-11-15-judge-thread-diagnostic.md).
The separate [offload sweep](../reports/amendments/2026-11-15-evaluation-offload-diagnostic.md)
uses `bash scripts/run.sh benchmark-judge --sweep offload` and the full registered
context. A selected offload change requires publication and recalibration.

The registered evaluation server uses passive OpenMP waiting after a sustained
serving slowdown; the training server retains library defaults. The CLI enforces
these environment settings before launching the model. Each request also has a
total streaming deadline, not merely a per-chunk inactivity timeout. Expired
requests close their stream, retain partial logs and follow bounded retries.
See the [development amendment](../reports/amendments/2026-11-15-judge-stream-deadline.md).
Changes to these settings invalidate prior calibration identities. Archive and
restart changed development calibration with `--restart-development`; locked
audits cannot be reset.

The synthetic maximum-length backward probe measures memory and does not retain
updates. The two-step GRPO pilot checks four completions, real verifier/judge
calls, optimizer state, saving and resumption. Record memory, validity, latency
and throughput in `reports/experiments/`; publish the policy-selection decision
in `configs/policy-selection.json` only after both checks pass. Pilot adapters
are discarded as initialization: every real arm loads the unmodified base.

A completed checkpoint contains TRL adapter/optimizer/scheduler/RNG/trainer
state, plus `groth-state.json` and a consistent SQLite judge-cache snapshot.
Resumption ignores a newer incomplete checkpoint. Ctrl-C or SIGTERM requests
an optimizer-boundary save; a power loss resumes from the last complete boundary.
No bitwise GPU determinism claim is made. The fallback needs measured failure
evidence and an explicit dated implementation/configuration amendment.

The dashboard computes throughput from the change in TRL's cumulative token
count over the latest optimizer interval, including judging. It does not divide
the cumulative count by the restarted process's elapsed time. Missing intervals
remain unavailable. Its metric contracts can be checked with
`node --test tests/dashboard.test.mjs` (Node is optional for this check).

## Comparative runs and independent evaluation

After passing audit and freezing the policy selection:

```bash
bash scripts/run.sh train --arm theory --seed 42
bash scripts/run.sh train --arm theory --seed 42 --resume
bash scripts/run.sh generate --run-id theory-seed42 --adapter /mnt/d/AI/grothendieck-rlvr/runs/theory-seed42/adapter
```

Stop the policy process before loading the evaluation judge. With Gemma serving:

```bash
bash scripts/run.sh evaluate --run-id theory-seed42
```

Repeat for correctness-only seeds 42/43/44 and theory seeds 43/44; run shuffled
and rubric arms with seed 42. Use the exact run IDs in the preregistration so
the report generator pairs them. Generate the unmodified baselines with
`generate --run-id ordinary` and `generate --run-id prompted --rising`.
No adapter means the frozen unmodified selected policy. Development snapshots
use `--split dev` and a distinct run ID, never the primary test run ID.
Generation resumption checks adapter/tokenizer content hashes, the dependency
lock, exact prompts, task manifest and generation budget. A path alone cannot
identify a checkpoint. Transfer likewise binds recipient records to the source
notes, source configurations, target tasks and token limits. Changed inputs
require a separate run; existing records are retained rather than silently mixed.

Run the separate broader-family suite with the same checkpoint and a `-ood`
suffix. This leaves the original primary evaluation intact:

```bash
bash scripts/run.sh generate --run-id ordinary-ood --split test_ood
bash scripts/run.sh evaluate --run-id ordinary-ood
bash scripts/run.sh generate --run-id theory-seed42-ood --split test_ood --adapter /mnt/d/AI/grothendieck-rlvr/runs/theory-seed42/adapter
bash scripts/run.sh evaluate --run-id theory-seed42-ood
```

Repeat the OOD commands for the matched checkpoints and baselines; include
`--rising` only for the prompted baseline. The report command keeps secondary
OOD comparisons, per-family scores and constructive novelty separate from
the primary success test. See [the amendment](../reports/amendments/2026-11-15-valid-novelty-and-ood.md).

For transfer, generate all source notes first with `--split transfer_source`
under separate run IDs for proposed/baseline checkpoints. Then:

```bash
bash scripts/run.sh transfer --source-runs theory-notes correctness-notes ordinary-notes
```

The recipient is the frozen unmodified base. Related/unrelated notes are truncated
to identical token lengths, capped at 1024 tokens; raw source notes are retained.
The four targets remain grouped by source for uncertainty. No target is exposed
to the source-note generation phase.
Reports include related versus unrelated notes, each condition versus no notes,
and pairs of note-source policies. Paired intervals require every registered
source and its four matching targets; partial runs retain descriptive summaries.

## Reports and dashboard

```bash
bash scripts/run.sh report
bash scripts/run.sh dashboard --port 8765
```

Open `http://127.0.0.1:8765`. The same `site/` directory is published by GitHub
Pages. One report command regenerates result JSON, README tables, figures,
individual/consolidated experiment reports and `reports/paper.pdf`. All empirical
numbers derive from saved artifacts. Full response logs stay under the data-drive
root; publish archival research logs separately from the small website snapshot.

Publish after every completed training/evaluation milestone and preserve failures.
Do not treat an infrastructure exception as a mathematical error. For the exact
metrics, seed treatment and stopping rules see the preregistration.
