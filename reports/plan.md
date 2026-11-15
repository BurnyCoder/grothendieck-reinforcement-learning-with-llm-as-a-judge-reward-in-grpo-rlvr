# Implementation and experiment plan

Updated 2026-11-15. Authority: user-approved Qwen3.5/Gemma plan and
[preregistration](preregistration.md), amended before judgments by the
[valid-novelty/OOD protocol](amendments/2026-11-15-valid-novelty-and-ood.md).
This checklist is a status record, not
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
- [x] Add constructive novelty to the versioned judge prompt and reward schema.
- [x] Add conventional reference anchors and explicit rejection of false/decorative novelty.
- [x] Add constructed calibration contrasts for useful distant mathematical bridges.
- [x] Implement a separately locked OOD suite and component-level reporting.
- [x] Run offline reward, verifier, isolation, recovery, novelty/OOD and reporting checks.
- [ ] Exercise model-backed training, resumption, evaluation and complete workflow.
- [x] Publish initial implementation, manifests, paper and site to GitHub/Hugging Face.
- [x] Publish the tested novelty/OOD amendment and regenerated artifacts before judgments.
- [ ] Complete development calibration, then audit both frozen judges and rubric-only variant.
- [ ] Run development feasibility pilot; freeze policy and training configuration.
- [ ] Evaluate unmodified ordinary and prompted policies.
- [ ] Train/evaluate theory-bonus seed 42 and correctness-only seed 42.
- [ ] Train/evaluate matched seeds 43 and 44, plus seed-42 controls.
- [ ] Evaluate note transfer and regenerate all analysis artifacts.
- [ ] Evaluate all frozen comparison checkpoints on the separate OOD suite.
- [ ] Publish each milestone, including negative/unfinished outcomes.

Model downloads and artifact hashes are complete. Development Gemma judging has
started but is incomplete; the interrupted CPU attempt is retained. Evaluation
GPU offload and the policy backward probe are being checked under the
[runtime amendment](amendments/2026-11-15-judge-runtime.md). No calibration pass,
policy evaluation or training result is claimed. Initial local constraints are
environment observations rather than comparative experimental results. Publication and
calibration gates must be satisfied before long training. Week-budget decisions
use measured pilot throughput and are documented before comparison runs.

Implementation is present but model-backed integration remains unverified.
The initial review/preregistration commit is `bcf85b1` in
https://github.com/BurnyCoder/grothendieck-reinforcement-learning-with-llm-as-a-judge-reward-in-grpo-rlvr . The Hugging Face dataset repository
exists at https://huggingface.co/datasets/BurnyCoder/grothendieck-rlvr . Collection
creation returned an account-level daily rate limit and remains pending.
The in-app browser backend was unavailable; Windows browser inspection was
stopped by URL-policy enforcement. No UI validation success is claimed.
