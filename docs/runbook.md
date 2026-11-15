# Running the research pipeline

Use WSL Ubuntu and Python 3.12. Commands below run from the repository root.
`scripts/run.sh` loads `.env` before Python starts, including `PYTHONHASHSEED=0`.
The local `.venv` is managed by uv; large files live in the configured data-drive
directory. Copy `.env.example` to `.env` when cloning on another machine.

## Install and prepare

```bash
bash scripts/setup-wsl.sh
bash scripts/run.sh doctor
bash scripts/run.sh prepare
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

Optional evaluation GPU offload needs a CUDA-enabled llama.cpp build; the CPU
build cannot offload even if a layer count is requested. Never place the training
judge on GPU during policy training. Shut down one judge before loading the other
if their combined memory use exceeds available RAM.

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

## Feasibility, saving and resumption

After publication, use development-only pilots:

```bash
bash scripts/run.sh memory-probe
bash scripts/run.sh train --pilot --arm theory --seed 42 --stop-after 1
bash scripts/run.sh train --pilot --arm theory --seed 42 --resume
```

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

For transfer, generate all source notes first with `--split transfer_source`
under separate run IDs for proposed/baseline checkpoints. Then:

```bash
bash scripts/run.sh transfer --source-runs theory-notes correctness-notes ordinary-notes
```

The recipient is the frozen unmodified base. Related/unrelated notes are truncated
to identical token lengths, capped at 1024 tokens; raw source notes are retained.
The four targets remain grouped by source for uncertainty. No target is exposed
to the source-note generation phase.

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
