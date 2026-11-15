# Correctness-gated mathematical theory building

Libor “Burny” Burian · 2026-11-15

## Abstract

We specify a local experiment testing whether correctness-gated rubric rewards improve useful mathematical theory building. A frozen Qwen judge assesses explanations; external arithmetic verifies final answers. Independent Gemma judgment and frozen-recipient transfer assess behavior. Primary analysis status: pending. No latent-space mechanism is established.

## Context, motivation and related work

Grothendieck's rising-sea metaphor motivates building structures until a specific question becomes a consequence. McLarty's account supplies the historical attribution [1]. We combine GRPO [2], Dr. GRPO normalization [3], and rubric rewards [4]. FERMAT [5] studies symbolic theory formation; this study instead scores natural-language explanations. The contribution is a correctness-gated experimental protocol and reusable environment, not a new optimizer.

## Method

Tasks come from pinned Reasoning Gym generators [6]. Training families are GCD, LCM, polynomial multiplication and dice probabilities. Semantic deduplication separates train, development, fresh, harder and unseen-family evaluation. One terminal final-answer field is checked by restricted arithmetic and Math-Verify [7]. Correctness C multiplies the entire reward: R=C(1+0.5T). Theory T is a six-criterion rubric score gated by supported validity. Constructive novelty receives 20% weight, judged relative to published conventional approaches. New objects, definitions, invariants, frameworks and distant mathematical connections earn that credit only when justified and useful. Historical originality and pretraining distribution are not inferred. Supporting excerpts are required. The two-call protocol separated conceptual analysis from overall validity and quality. Its selected fallback has eight specialist roles. Code derives novelty from explicit addition, application and consequence findings, and withholds novelty unless supported theory is declared beyond-reference with an excerpt identifying a concrete addition. Brief valid connections can earn one novelty point without a further worked use; developed mathematics can earn up to four. A reference argument establishing a connection is not itself a further application. Raw stage findings are retained; code derives combined scores and any substantive objection vetoes the bonus. Checklist-based judging [14] and decomposition [15] motivate auditable prerequisites; the checks do not certify mathematical entailment. Final-answer verification does not certify surrounding proofs.

## Models and training

Qwen3.5-2B BF16 LoRA is preferred; Qwen3.5-9B Q4_K_M judges training on CPU, and Gemma 4 12B UD-Q4_K_XL judges evaluation separately. Exact revisions and dependencies are locked. Unsloth's documented non-vLLM route [8] and TRL [9] implement training. The preregistration fixes group size, optimizer settings, sample budgets and fallback criteria. A pre-comparison runtime-budget amendment selects 64 optimizer updates for every training arm. The active instrument is specialists-v1; per-role prompts, visible/reasoning budgets and dependencies are locked in its identity. Separate calls reuse the same frozen model and may share errors. Studies report setting-dependent benefits and failures of additional judging computation [12,13]; neither validates this novelty rubric. Failed feasibility or calibration is development evidence, not a negative test of the behavioral hypothesis.

## Experimental design and analysis

Compare ordinary and prompted unmodified models, correctness-only training, the proposed bonus, shuffled bonuses and a rubric-only ablation. The main trained comparison uses matched seeds. The primary measure is mean C*T from frozen Gemma, with paired stratified problem-level bootstrap intervals and an accuracy noninferiority condition. Transfer resamples source problems while retaining their related probes. Single-seed findings are exploratory. No adaptive sample extension is allowed to obtain significance. A pre-judgment amendment adds a separate locked secondary set for graph connectivity, polygon geometry, rational matrix rank and modular inverses; it does not replace the primary split. Valid novelty is also reported separately. OOD means held out from project training, not necessarily from model pretraining.

## Results and claims

All tables and figures in this paper are generated from saved records. Pending cells indicate experiments without saved evaluation evidence. The machine-readable primary analysis reports pending. Implementation checks do not establish mathematical performance. Calibration cases are constructed expectations, not human preference evidence.

| Arm | Problems | Accuracy | C × theory | C × novelty |
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

## Development execution

Preserved development logs contain 205 completed judge responses and 10 requests without a completed response. These counts are generated from reports/development logs. Interrupted CPU and CUDA judging attempts and runtime changes are documented in dated amendments. CUDA loading succeeded, but slow decoding motivated a bounded thread-count diagnostic before recalibration. Partial judgments do not establish calibration reliability. Conventional arguments received nonzero novelty credit, including after the v3 clarification. The clean standalone Gemma retry completed judgments, including a rejected abbreviated quote and an accepted retry. V4 requests evidence before scores and supplies bounded validation feedback. V4 Gemma contrasts favored valid bridges but also assigned novelty to some conventional controls. Passive OpenMP waiting completed the observed requests without a transport failure; that short run does not establish sustained reliability. Qwen's subsequent partial v4 attempt also assigned no-theory verdicts to conventional generalized explanations. It was interrupted for a documented reasoning-mode development revision, without being declared a calibration pass or threshold failure. The later v5 attempt stopped after bounded retries repeated a contradiction between the declared reference relation and numerical novelty score; that calibration remained incomplete. V6 demonstrated a logged eligibility gate on that discrepancy, then was interrupted when the user clarified that brief valid connections should receive modest novelty credit. V7 implements that changed construct. Its first trial failed the control-credit conditions despite correct observed framework/control rankings. A later reference-scope amendment clarified commutative-polynomial and ordinary biased-probability baselines. That trial also failed: routine probability controls received zero novelty, but brief commutator connections remained uncredited and a brief subgroup connection tied a developed framework on novelty while scoring higher overall. A conventional invariant was cited as a use of the added connection; exact-excerpt validation cannot establish that semantic attribution. Historical results are retained, and the remaining model runs stay gated. The two-call decomposition subsequently failed development: it credited a brief commutator connection but overcredited conventional GCD/LCM mathematics and missed developed uses. The preserved stage findings and case report document these errors. The preregistered specialist fallback also failed quoted-Qwen development. Its roles emitted mathematical objections to omitted elementary steps, conventionality and perceived irrelevance, removing bonuses from valid frameworks and a brief connection. Selected exact checks of the disputed steps are preserved without rescoring the trial. The remaining specialist development configurations are diagnostic; they cannot bypass this failed gate. Related proof-verification studies discuss false rejection [16,17], but use different models and aggregation rules and do not qualify this instrument.

evaluation_judge/quoted (dev, ef8a300c) failed: 2/4 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, 08145e59) failed: 1/3 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, ebe93e9d) failed: 6/9 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, a3fa911e) failed: 4/7 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, b33cb353) failed: 0/3 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, 66721e0e) failed: 2/5 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

Incomplete development suites stopped under the fixed futility rule. Upper bounds assume every remaining case succeeds solely to test attainability. Unobserved cases are not counted as measured successes or errors; no early pass is allowed. No comparative conclusion follows.

A recorded BF16 LoRA backward probe completed at 2560 tokens and microbatch 1, with peak allocated GPU memory 4.76 GiB and reserved memory 4.84 GiB. The measured forward/backward interval was 941.72 seconds, including first-use compilation. The synthetic repeated-token input checks execution and memory, not mathematical ability or steady-state throughput. The initial GRPO attempt failed during generation prefill when a carriage return entered the compiler-cache path, before any optimizer update. Its failure log is preserved. A repaired GRPO pilot reached optimizer boundary 1 and saved its checkpoint, with peak allocated memory 4.89 GiB and reserved memory 6.08 GiB. Its recorded learning rate was 0; the sampled batch had verified accuracy 62.5% and mean supported theory 0. A warmup boundary does not demonstrate learning. The resumed pilot completed boundary 2 at learning rate 1e-05, with a recorded step interval of 480.66 seconds. Peak allocated memory was 4.97 GiB and reserved memory 6.25 GiB. Its batch accuracy was 50.0%, and mean supported theory was 0. Checkpoint recovery and a parameter change are feasibility evidence, not an improvement estimate. A single resumed interval is not a stable throughput benchmark. Pilot adapters are excluded from comparative initialization. A synthetic Gemma decoding diagnostic recorded 24 GPU layers: 9.04 tokens/s; 32 GPU layers: 8.74 tokens/s; 40 GPU layers: 4.47 tokens/s. The fastest measured setting used 24 GPU layers. These short upstream llama-bench measurements omit structured-output sampling. The offload sweep allocates the registered maximum context. They do not establish end-to-end judgment latency or calibration quality. A synthetic Gemma decoding diagnostic recorded 1 threads: 1.92 tokens/s; 4 threads: 5.49 tokens/s; 8 threads: 6.38 tokens/s. The fastest measured setting used 8 threads. These short upstream llama-bench measurements omit structured-output sampling. The thread sweep uses a smaller allocated context than the server. They do not establish end-to-end judgment latency or calibration quality.

## Transfer evaluation

Recipient accuracy is compared with no notes, unrelated notes of matched length, and notes from other frozen source policies. Paired uncertainty resamples source problems with all four targets retained. Comparisons require complete matching source and target coverage. The machine-readable report publishes each source policy's related-minus-unrelated contrast and all pairs of note-source policies, with unadjusted exploratory intervals.

| Note condition | Probes | Recipient accuracy |
|---|---|---|
| Registered transfer conditions | Pending | Pending |

## Discussion and limitations

Judge scores are imperfect proxies and the two model families may share biases or training data. Quantization can change judgments. Synthetic elementary tasks limit external validity. The constructed audit changes numerical instances while sharing mathematical templates with development; it does not establish generalization to unseen failure types. Fixed small-seed comparisons may be inconclusive. Reusable exposition is not equivalent to historically novel mathematics. Higher training scores without independent or transfer improvement are consistent with proxy optimization. Do not infer a latent mechanism from behavioral scores alone. Development/test separation and scoped claims follow methodological guidance [10,11].

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

[12] [Explicit Reasoning Makes Better Judges](https://arxiv.org/abs/2509.13332)

[13] [SLMJury](https://arxiv.org/abs/2606.07810)

[14] [RULERS: Locked Rubrics and Evidence-Anchored Scoring](https://arxiv.org/abs/2601.08654)

[15] [DnA-Eval: Decomposition and Aggregation](https://aclanthology.org/2025.coling-main.156/)

[16] [Naik et al., Do We Need Frontier Models to Verify Mathematical Proofs?](https://arxiv.org/abs/2604.02450v1)

[17] [Huang et al., Pessimistic Verification for Open Ended Math Questions](https://arxiv.org/abs/2511.21522v1)

AI statement: Codex wrote this codebase and paper from the exact specification provided by a human. Human cleanup and rewriting are in progress.
