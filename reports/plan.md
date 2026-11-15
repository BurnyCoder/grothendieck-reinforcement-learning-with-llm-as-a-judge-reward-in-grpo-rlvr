# Implementation and experiment plan

Updated 2026-11-15. Authority: user-approved Qwen3.5/Gemma plan and
[preregistration](preregistration.md). This checklist is a status record, not
evidence of model performance.

- [x] Inspect workspace, local hardware and publication accounts.
- [x] Review relevant mathematics, rubric RL, theory formation and runtime sources.
- [x] Specify hypotheses, splits, reward, controls, calibration and analysis.
- [ ] Publish initial review, preregistration and README before model inference.
- [ ] Initialize uv/Python 3.12 project and lock compatible releases.
- [ ] Implement typed task, verification, judgment and reward interfaces.
- [ ] Build deterministic manifests with reference and overlap checks.
- [ ] Implement versioned quoted and rubric-only judge prompts and calibration.
- [ ] Implement Unsloth/TRL training, checkpoint/resume and feasibility probe.
- [ ] Implement unchanged-policy, independent-judge and transfer evaluation.
- [ ] Implement statistics, artifact-driven reports/PDF and dashboard/Pages.
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
