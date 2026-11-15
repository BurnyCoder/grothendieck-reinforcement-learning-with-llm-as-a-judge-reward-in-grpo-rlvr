# Implementation and experiment plan

Updated 2026-11-15. Authority: user-approved Qwen3.5/Gemma plan and
[preregistration](preregistration.md). This checklist is a status record, not
evidence of model performance.

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
- [ ] Run unit, integration and complete workflow checks before model runs.
- [ ] Publish implementation, manifests, paper and site to GitHub/Hugging Face.
- [ ] Calibrate both frozen judges and rubric-only variant.
- [ ] Run development feasibility pilot; freeze policy and training configuration.
- [ ] Evaluate unmodified ordinary and prompted policies.
- [ ] Train/evaluate theory-bonus seed 42 and correctness-only seed 42.
- [ ] Train/evaluate matched seeds 43 and 44, plus seed-42 controls.
- [ ] Evaluate note transfer and regenerate all analysis artifacts.
- [ ] Publish each milestone, including negative/unfinished outcomes.

All model steps are pending. The initial local constraints are recorded as
environment observations rather than experimental results. Publication and
calibration gates must be satisfied before long training. Week-budget decisions
use measured pilot throughput and are documented before comparison runs.

Implementation is present but model-backed integration remains unverified.
The initial review/preregistration commit is `bcf85b1` in
https://github.com/BurnyCoder/grothendieck-rlvr . The Hugging Face dataset repository
exists at https://huggingface.co/datasets/BurnyCoder/grothendieck-rlvr . Collection
creation returned an account-level daily rate limit and remains pending.
The in-app browser backend was unavailable; Windows browser inspection was
stopped by URL-policy enforcement. No UI validation success is claimed.
