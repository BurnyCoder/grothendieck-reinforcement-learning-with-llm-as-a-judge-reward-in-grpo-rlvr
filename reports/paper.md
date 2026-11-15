# Correctness-gated mathematical theory building

Libor “Burny” Burian · 2026-11-15

## Abstract

We specify a local experiment testing whether correctness-gated rubric rewards improve useful mathematical theory building. A frozen Qwen judge assesses explanations; external arithmetic verifies final answers. Independent Gemma judgment and frozen-recipient transfer assess behavior. Primary analysis status: pending. No latent-space mechanism is established.

## Context, motivation and related work

Grothendieck's rising-sea metaphor motivates building structures until a specific question becomes a consequence. McLarty's account supplies the historical attribution [1]. We combine GRPO [2], Dr. GRPO normalization [3], and rubric rewards [4]. FERMAT [5] studies symbolic theory formation; this study instead scores natural-language explanations. The contribution is a correctness-gated experimental protocol and reusable environment, not a new optimizer.

## Method

Tasks come from pinned Reasoning Gym generators [6]. Training families are GCD, LCM, polynomial multiplication and dice probabilities. Semantic deduplication separates train, development, fresh, harder and unseen-family evaluation. One terminal final-answer field is checked by restricted arithmetic and Math-Verify [7]. Correctness C multiplies the entire reward: R=C(1+0.5T). Theory T is a weighted rubric score gated by supported validity. Supporting excerpts are required. Final-answer verification does not certify surrounding proofs.

## Models and training

Qwen3.5-2B BF16 LoRA is preferred; Qwen3.5-9B Q4_K_M judges training on CPU, and Gemma 4 12B UD-Q4_K_XL judges evaluation separately. Exact revisions and dependencies are locked. Unsloth's documented non-vLLM route [8] and TRL [9] implement training. The preregistration fixes group size, optimizer settings, sample budgets and fallback criteria. Failed feasibility or calibration is development evidence, not a negative test of the behavioral hypothesis.

## Experimental design and analysis

Compare ordinary and prompted unmodified models, correctness-only training, the proposed bonus, shuffled bonuses and a rubric-only ablation. The main trained comparison uses matched seeds. The primary measure is mean C*T from frozen Gemma, with paired stratified problem-level bootstrap intervals and an accuracy noninferiority condition. Transfer resamples source problems while retaining their related probes. Single-seed findings are exploratory. No adaptive sample extension is allowed to obtain significance.

## Results and claims

All tables and figures in this paper are generated from saved records. Pending cells indicate experiments without saved evaluation evidence. The machine-readable primary analysis reports pending. Implementation checks do not establish mathematical performance. Calibration cases are constructed expectations, not human preference evidence.

| Arm | Problems | Accuracy | C × theory | Theory | correct |
|---|---|---|---|---|
| ordinary | Pending | Pending | Pending | Pending |
| prompted | Pending | Pending | Pending | Pending |
| correctness-seed42 | Pending | Pending | Pending | Pending |
| theory-seed42 | Pending | Pending | Pending | Pending |
| correctness-seed43 | Pending | Pending | Pending | Pending |
| theory-seed43 | Pending | Pending | Pending | Pending |
| correctness-seed44 | Pending | Pending | Pending | Pending |
| theory-seed44 | Pending | Pending | Pending | Pending |
| shuffled-seed42 | Pending | Pending | Pending | Pending |
| rubric-seed42 | Pending | Pending | Pending | Pending |

```json
{
  "status": "pending",
  "reason": "No matched trained arms have been evaluated"
}
```

## Discussion and limitations

Judge scores are imperfect proxies and the two model families may share biases or training data. Quantization can change judgments. Synthetic elementary tasks limit external validity, and fixed small-seed comparisons may be inconclusive. Reusable exposition is not equivalent to historically novel mathematics. Higher training scores without independent or transfer improvement are consistent with proxy optimization. Do not infer a latent mechanism from behavioral scores alone. Development/test separation and scoped claims follow methodological guidance [10,11].

## Conclusion

The protocol tests whether an explicit interpretation of rising-sea theory building can supply useful training feedback while preserving mathematical accuracy. Its outcome must be read from the recorded comparisons; the motivating philosophical analogy is not itself evidence.

## Appendix: reproducibility and unfinished work

The repository contains the dated preregistration, model and data locks, full prompts, configurations, tests, and commands. reports/plan.md tracks unfinished experiments. Complete prompts and outputs are retained in timestamped logs. Checkpoints preserve optimizer, scheduler, RNG, data position and judge-cache state. No candidate code is executed.

## References

[1] [McLarty, The Rising Sea](https://ncatlab.org/nlab/files/McLartyRisingSea.pdf)

[2] [DeepSeekMath](https://arxiv.org/abs/2402.03300)

[3] [Understanding R1-Zero-Like Training](https://arxiv.org/abs/2503.20783)

[4] [Rubrics as Rewards](https://arxiv.org/abs/2507.17746)

[5] [Learning Interestingness in Automated Mathematical Theory Formation](https://arxiv.org/abs/2511.14778)

[6] [Reasoning Gym](https://github.com/open-thought/reasoning-gym)

[7] [Math-Verify](https://github.com/huggingface/Math-Verify)

[8] [Unsloth Qwen3.5 guide](https://unsloth.ai/docs/models/qwen3.5/fine-tune)

[9] [TRL GRPO](https://huggingface.co/docs/trl/grpo_trainer)

[10] [Lones, How to avoid machine learning pitfalls](https://arxiv.org/abs/2108.02497)

[11] [Lipton and Steinhardt, Troubling Trends](https://arxiv.org/abs/1807.03341)

AI statement: Codex wrote this codebase and paper from the exact specification provided by a human. Human cleanup and rewriting are in progress.
