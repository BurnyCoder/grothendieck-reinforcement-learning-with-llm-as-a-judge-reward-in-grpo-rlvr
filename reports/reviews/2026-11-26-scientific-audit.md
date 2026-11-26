# Independent scientific audit

Libor “Burny” Burian · 26 November 2026

## Research verdict

H1 remains pending. The archive has no completed, matched three-seed comparison between the qualified theory-bonus and correctness-only arms. H2 remains untested. There are no frozen-recipient outcomes under the registered note conditions. The available behavioral comparison concerns two prompts applied to the same frozen pretrained policy.

## Baseline scoring

The ordinary prompt passed 148/400 problems (37.00%) and the rising-sea prompt passed 131/400 (32.75%). Prompted minus ordinary accuracy was -4.25 percentage points (paired 95% percentile interval -8.50 to +0.00). Both prompts passed 99 problems, ordinary alone 49, prompted alone 32 and neither 220. Invalid formats accounted for 177 ordinary and 189 prompted answers. The stricter form check retained 148/400 and 131/400 respectively (zero changes for reduced fractions, expanded products and rounded roots in both arms). Its paired difference was -4.25 points (95% interval -8.50 to +0.00). All 400 problems retained their original stratum weights in 10,000 paired resamples. This retrospective prompt contrast is conditional on these strata, one checkpoint and one decoding setup. The primary interval includes zero. Theory and novelty are unmeasured.

[Scoring protocol](../amendments/2026-11-26-cpu-baseline-audit.md) · [Paired and per-family results](../../results/scientific-audit/baseline-summary.json) · [Ordinary records](../../results/scientific-audit/ordinary.json) · [Prompted records](../../results/scientific-audit/prompted.json) · [Raw generation receipts](../generation/README.md)

| Locked stratum | Ordinary correct / total | Prompted correct / total |
|---|---|---|
| test_fresh | 70/200 | 70/200 |
| test_hard | 11/100 | 7/100 |
| test_unseen | 67/100 | 54/100 |

The protocol was publicly merged after the responses existed and before scoring. Exposure of this holdout now matters for subsequent adaptive choices. An initial run under system Python lacked symbolic dependencies, recorded infrastructure failures and withheld the paired estimate. The frozen verifier in the locked environment resolved the answers. Its terminal-tag and supported-grammar checks can reject mathematically intelligible text. The strict sensitivity addresses only the three prespecified form rules. Neither scorer checks the proof. [Incomplete attempt](../../results/scientific-audit/attempts/system-python/baseline-summary.json) · [Math-Verify](https://github.com/huggingface/Math-Verify) · [Reasoning Gym polynomial prompt](https://github.com/open-thought/reasoning-gym/blob/v0.1.25/reasoning_gym/algebra/polynomial_multiplication.py)

## Data and generalization

Independent exact checks covered 2,188 locked tasks. The audit used prime valuations, bounded-sum inclusion–exclusion, polynomial interpolation, rational isolation of real roots, grid flood fill, polygon angle sums, exact rank and modular inverses. Replaying generation in an empty directory reproduced the locked task and rejection records. The overall study configuration hash changed with later amendments, while the task records stayed identical. The manifests list each split and family. Canonicalization checks equality under the documented within-family transformations, including polynomial variable renaming, common equation scale and grid symmetries. Shared templates, mathematical skills, possible semantic similarities beyond those keys, and pretraining exposure remain possible. Harder settings test parameter ranges. Unseen families and secondary OOD are defined relative to project training. [Independent checks and exceptions](../../results/scientific-audit/manifests.json) · [Generator replay](../../results/scientific-audit/generator-replay.json) · [Audit implementation](../../src/grothendieck_rlvr/audit_math.py) · [Generator implementation](https://github.com/open-thought/reasoning-gym/tree/v0.1.25)

## Instrument qualification

Each row is one terminal development record. A tie fails strict preference. The attainable ceiling credits every unobserved novelty pair with a hypothetical pass. Hashes, case versions and adaptive reuse prevent treating these partly repeated examples as independent trials.

| Development log | Passed / observed | Quality ties | Scheduled novelty pairs | Ceiling | Suppression cases observed |
|---|---|---|---|---|---|
| gemma-passive-v4-dev.jsonl | 2/4 | 0 | 8 | 0.750 | 0 |
| qwen-reasoning512-v4-dev.jsonl | 1/3 | 0 | 8 | 0.750 | 0 |
| qwen-v7-anchors-v3-dev.jsonl | 6/9 | 0 | 12 | 0.750 | 0 |
| qwen-v7-dev.jsonl | 4/7 | 0 | 12 | 0.750 | 0 |
| qwen-v8-specialists-dev.jsonl | 0/3 | 3 | 12 | 0.750 | 0 |
| qwen-v8-specialists-rubric-dev.jsonl | 0/3 | 2 | 12 | 0.750 | 0 |
| qwen-v8-two-stage-dev.jsonl | 2/5 | 1 | 12 | 0.750 | 0 |

[Component reanalysis](../../results/scientific-audit/calibration.json) · [Distinct and overlapping transcript events](../../results/scientific-audit/transcripts.json). Unreached suppression rates are undefined. Other interrupted versions have partial records and no terminal gate result.

## Method and mathematical claims

For correct solutions the theory-arm reward is 1 + 0.5T, where T is the weighted six-criterion rubric after the validity and applicable reference-relative novelty gates. Other solutions earn zero. A correctness-only arm gives C. The shuffled control permutes bonuses among eligible completions and can leave assignments fixed. TRL subtracts the prompt-group mean, omits standard-deviation scaling when scale_rewards is disabled, and divides the masked token sum by the fixed completion length times the batch size for dr_grpo. The configured reference-policy KL penalty remains active. This implements the two normalization changes described by Liu et al. The original paper's beta-zero experiment and the project's positive-beta run have different objectives. Rubrics as Rewards motivates graded feedback. This project selected its own items, weights and correctness gate. A separate same-family evaluator does not supply independent human labels. [Training code](../../src/grothendieck_rlvr/training.py) · [Reward code](../../src/grothendieck_rlvr/reward.py) · [DeepSeekMath §4](https://arxiv.org/html/2402.03300v3) · [Dr. GRPO §3 and Appendix G](https://arxiv.org/html/2503.20783v2) · [Pinned TRL trainer](https://github.com/huggingface/trl/blob/v1.15.0/trl/trainer/grpo_trainer.py) · [Rubrics as Rewards](https://arxiv.org/html/2507.17746v1)

For positive n the subgroup generated by 2n and 3n is nℤ because 3n − 2n = n. It contains n+1 exactly when n = 1. The subgroup intersection 2nℤ ∩ 3nℤ is 6nℤ. Any nonempty intersection of their translates is a translate of 6nℤ. Over the reals the algebra with e² = 1 has multiplication matrix [[a,b],[b,a]] for a+be. Its determinant a²−b² is multiplicative and equals (a+b)(a−b). No additional isomorphism premise is needed for that equality. For noncommuting a and b the extra term in (a+b)(a−b) is ba−ab. Merely computing the commutative expansion does not apply the proposed noncommutative observation. For independent dice the parity character factors in expectation. Taking the two dice equal shows why dependence can invalidate the product. These derivations adjudicate the actual saved cases. An objection about missing exposition can still be reasonable when the algebra is correct. [Candidates, objection text and symbolic checks](../../results/scientific-audit/objections.json) · [Case definitions](../../src/grothendieck_rlvr/novelty_cases.py)

## Execution and chronology

The comparative attempt logged 13/64 updates and the cache-release diagnostic logged 7/16. The diagnostic stopped before the required save/resume boundary. The records cannot establish a cache-release benefit. The qualified reward comparison and frozen-recipient transfer experiment lack outcome data. The project-specific correctness-gated rubric measures a judge's opinion. The training loss uses Dr. GRPO length and variance choices with a separate positive KL penalty. See the dated scientific review for raw evidence and errata.

| Discarded pilot | Step | Rollouts | Accuracy | C × theory | Mean reward | Step seconds |
|---|---|---|---|---|---|---|
| pilot-theory-seed42 | 1 | 8 | 0.625 | 0.0000 | 0.6250 | 699.93 |
| pilot-theory-seed42 | 2 | 8 | 0.500 | 0.0000 | 0.5000 | 480.66 |
| exploratory-single-v2-pilot-theory-seed42 | 1 | 8 | 0.375 | 0.1328 | 0.4414 | 864.57 |
| exploratory-single-v2-pilot-theory-seed42 | 2 | 8 | 0.500 | 0.2078 | 0.6039 | 805.43 |
| exploratory-small-gpu-v2-pilot-theory-seed42 | 1 | 8 | 0.375 | 0.2437 | 0.4969 | 179.71 |
| exploratory-small-gpu-v2-pilot-theory-seed42 | 2 | 8 | 0.000 | 0.0000 | 0.0000 | 120.98 |

The diagnostic's observed peak reserved memory was 3.846 GiB. This prefix stayed below the registered 4.5 GiB ceiling. Its final four scheduled updates and the 0.5 GiB range criterion were never observed. No checkpoint or resumed invocation is recorded for the diagnostic. [Registered resource criteria](../amendments/2026-11-16-cuda-cache-diagnostic.md)

Pilot monitoring window 1 contains 188 whole-device samples with a maximum of 7619 MiB.

Pilot monitoring window 2 contains 129 whole-device samples with a maximum of 6862 MiB.

pilot-theory-seed42 changed 96/192 tensors between the first two checkpoints. The maximum absolute parameter change was 1.0013237e-05.

exploratory-single-v2-pilot-theory-seed42 changed 96/192 tensors between the first two checkpoints. The maximum absolute parameter change was 1.0013207e-05.

exploratory-small-gpu-v2-pilot-theory-seed42 changed 96/192 tensors between the first two checkpoints. The maximum absolute parameter change was 1.0004062e-05.

| Milestone | Recorded timestamp | Evidence |
|---|---|---|
| Original registration commit | 2026-11-15T07:58:23+01:00 | bcf85b145aee |
| ordinary baseline, last saved answer | 2026-11-16T04:21:45.066423+00:00 | generation log |
| prompted baseline, last saved answer | 2026-11-16T07:43:39.780525+00:00 | generation log |
| Last comparative optimizer update | 2026-11-16T08:32:01.740625+00:00 | training log |
| Cache-release registration commit | 2026-11-16T16:45:48+01:00 | f495506f5699 |
| First cache diagnostic update | 2026-11-16T15:52:35.587174+00:00 | training log |
| Last cache diagnostic update | 2026-11-16T15:58:00.789529+00:00 | training log |
| CPU scoring protocol commit | 2026-11-26T12:54:51+01:00 | 3e2d4bea0d56 |

Times retain their recorded UTC offsets. [Generation events and save timestamps](../../results/scientific-audit/generation.json) · [Public scoring protocol merge](https://github.com/BurnyCoder/grothendieck-reinforcement-learning-with-llm-as-a-judge-reward-in-grpo-rlvr/pull/56)

The checkpoints establish that parameters changed. Different development batches, optimizer state and KL regularization preclude a learning-effect estimate. Reserved allocator bytes, allocated tensor bytes and sampled whole-device use measure different quantities. Time comparisons also confound task difficulty, decoding length, judge latency and host load. [Per-update events and device windows](../../results/scientific-audit/execution.json) · [PyTorch allocator definitions](https://docs.pytorch.org/docs/2.14/notes/cuda.html#memory-management) · [Git chronology and dated amendments](../../results/scientific-audit/chronology.json)

## Decision rules, corrections and evidence limits

H1 requires a mean C × theory gain ≥ 0.05, a strictly positive lower 95% bound and an accuracy lower bound strictly above −0.03. Average matched seeds within problem for the primary interval. Hierarchical seed resampling is a sensitivity check with only three seed pairs. A theory upper bound below 0.05 rules out the target gain on this interval. A lower bound at or below zero alone leaves positive gains possible. A missed noninferiority criterion alone cannot establish inferiority. The previous analyzer could accept invented IDs with correct counts. The repaired entry point matches the locked problems, seeds, checkpoint provenance and qualification. H2 uses matched note conditions and resamples source problems with their four target probes together. Targets are assigned by family and generation order. Unrelated notes come from another family, so any eventual contrast could reflect topical relevance rather than reuse of a source-specific construction. The ordinary-note and correctness-policy conditions address different comparisons. Cross-source intervals are exploratory and unadjusted. [Registration](../preregistration.md) · [Synthetic defect replay](../../results/scientific-audit/eligibility-regression.json) · [Regression tests](../../tests/test_scientific_audit.py) · [Paired resampling](https://aclanthology.org/W04-3250/)

The [file and passage index](../../results/scientific-audit/inventory.json) identifies the original Git blobs and the public dataset card. The [claim register](2026-11-26-claim-register.json) records evidence, corrections and implications. The [original Hub inventory](../../results/scientific-audit/hub-inventory.json) exposed missing adapter tensors and a trainer card that named its base model as None. The archived bytes and [corrected checkpoint cards](../../results/scientific-audit/checkpoint-cards.json) restore the evidence and attribution. [Dated source-access receipts](../../results/scientific-audit/source-access.json) record URL reachability. A source establishing how an algorithm works cannot validate a local effect size. The archive cannot resolve unlogged activity, pretraining exposure, general human agreement, historical novelty or the exact provenance of all supplied social and video wording. These remain unverified. Dated registrations and raw model utterances remain available as historical evidence. [Source provenance](../../docs/rising-sea-quotations.md)
