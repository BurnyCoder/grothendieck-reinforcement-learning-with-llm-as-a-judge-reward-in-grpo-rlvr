# Correctness-gated mathematical theory building

Libor “Burny” Burian · 2026-11-16

## Abstract

We specify a local experiment testing whether correctness-gated rubric rewards improve useful mathematical theory building. A frozen Qwen judge assesses explanations; external arithmetic verifies final answers. Separate frozen judging and frozen-recipient transfer assess behavior. Qualified-study analysis status: pending. After calibration failures, a user-authorized exploratory continuation uses a single judge call despite unqualified rewards. Its results remain separate. No latent-space mechanism is established.

## Context, motivation and related work

Grothendieck's rising-sea metaphor motivates building structures until a specific question becomes a consequence. McLarty's account supplies the historical attribution [1]. We combine GRPO [2], Dr. GRPO normalization [3], and rubric rewards [4]. FERMAT [5] studies symbolic theory formation; this study instead scores natural-language explanations. The contribution is a correctness-gated experimental protocol and reusable environment, not a new optimizer.

## Method

Tasks come from pinned Reasoning Gym generators [6]. Training families are GCD, LCM, polynomial multiplication and dice probabilities. Semantic deduplication separates train, development, fresh, harder and unseen-family evaluation. One terminal final-answer field is checked by restricted arithmetic and Math-Verify [7]. Correctness C multiplies the entire reward: R=C(1+0.5T). Theory T is a six-criterion rubric score gated by supported validity. Constructive novelty receives 20% weight, judged relative to published conventional approaches. New objects, definitions, invariants, frameworks and distant mathematical connections earn that credit only when justified and useful. Historical originality and pretraining distribution are not inferred. Supporting excerpts are required. The two-call protocol separated conceptual analysis from overall validity and quality. Its historical fallback used eight specialist roles. That protocol derived novelty from explicit addition, application and consequence findings, and withholds novelty unless supported theory is declared beyond-reference with an excerpt identifying a concrete addition. Brief valid connections can earn one novelty point without a further worked use; developed mathematics can earn up to four. A reference argument establishing a connection is not itself a further application. Raw stage findings are retained; code derives combined scores and any substantive objection vetoes the bonus. Checklist-based judging [14] and decomposition [15] motivate auditable prerequisites; the checks do not certify mathematical entailment. Final-answer verification does not certify surrounding proofs.

## Models and training

The active smaller-model experiment selects Qwen3.5-0.8B BF16 LoRA, with a frozen Qwen3.5-2B Q4_K_M training judge resident on the same GPU. A frozen Qwen3.5-4B Q4_K_M evaluator runs on GPU after policy generation. All policy parameters and judge layers must fit on CUDA; tokenization, verification and logging remain CPU work. The earlier 2B-policy/9B-CPU-judge/Gemma-12B setup is postponed and preserved. Exact revisions and dependencies are locked. Unsloth's documented non-vLLM route [8] and TRL [9] implement training. The preregistration fixes group size, optimizer settings, sample budgets and fallback criteria. A pre-comparison runtime-budget amendment selects 64 optimizer updates for every training arm. The deferred qualification protocol is specialists-v1; per-role prompts, visible/reasoning budgets and dependencies are locked in its identity. Separate calls reuse the same frozen model and may share errors. Studies report setting-dependent benefits and failures of additional judging computation [12,13]; neither validates this novelty rubric. Failed feasibility or calibration is development evidence, not a negative test of the behavioral hypothesis.

## Experimental design and analysis

Compare ordinary and prompted unmodified models, correctness-only training, the proposed bonus, shuffled bonuses and a rubric-only ablation. The main trained comparison uses matched seeds. The primary measure is mean C*T from the frozen evaluation judge, with paired stratified problem-level bootstrap intervals and an accuracy noninferiority condition. Transfer resamples source problems while retaining their related probes. Single-seed findings are exploratory. No adaptive sample extension is allowed to obtain significance. A pre-judgment amendment adds a separate locked secondary set for graph connectivity, polygon geometry, rational matrix rank and modular inverses; it does not replace the primary split. Valid novelty is also reported separately. OOD means held out from project training, not necessarily from model pretraining.

## Results and claims

All tables and figures in this paper are generated from saved records. Pending cells indicate experiments without saved evaluation evidence. The machine-readable primary analysis reports pending. Analysis status: pending. No matched trained arms have been evaluated. Implementation checks do not establish mathematical performance. Calibration cases are constructed expectations, not human preference evidence.

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
| exploratory-small-gpu-v2-ordinary | Pending | Pending | Pending | Pending |
| exploratory-small-gpu-v2-prompted | Pending | Pending | Pending | Pending |
| exploratory-small-gpu-v2-theory-seed42 | Pending | Pending | Pending | Pending |
| exploratory-small-gpu-v2-correctness-seed42 | Pending | Pending | Pending | Pending |

```json
{
  "status": "pending",
  "reason": "No matched trained arms have been evaluated"
}
```

## Generation execution

exploratory-small-gpu-v2-ordinary: 400/400 unique task outputs saved; mean recorded generation time 11.25 seconds per answer; last saved response 2026-11-16T04:21:45.066423+00:00. exploratory-small-gpu-v2-prompted: 400/400 unique task outputs saved; mean recorded generation time 11.98 seconds per answer; last saved response 2026-11-16T07:43:39.780525+00:00. These receipts verify saved task coverage and configuration, not answer correctness or theory quality. Mean times exclude startup, interrupted attempts and downtime. Sources: reports/generation/.

## Development execution

Preserved development logs contain 270 completed judge responses and 10 requests without a completed response. These counts are generated from reports/development logs. Interrupted CPU and CUDA judging attempts and runtime changes are documented in dated amendments. CUDA loading succeeded, but slow decoding motivated a bounded thread-count diagnostic before recalibration. Partial judgments do not establish calibration reliability. Conventional arguments received nonzero novelty credit, including after the v3 clarification. The clean standalone Gemma retry completed judgments, including a rejected abbreviated quote and an accepted retry. V4 requests evidence before scores and supplies bounded validation feedback. V4 Gemma contrasts favored valid bridges but also assigned novelty to some conventional controls. Passive OpenMP waiting completed the observed requests without a transport failure; that short run does not establish sustained reliability. Qwen's subsequent partial v4 attempt also assigned no-theory verdicts to conventional generalized explanations. It was interrupted for a documented reasoning-mode development revision, without being declared a calibration pass or threshold failure. The later v5 attempt stopped after bounded retries repeated a contradiction between the declared reference relation and numerical novelty score; that calibration remained incomplete. V6 demonstrated a logged eligibility gate on that discrepancy, then was interrupted when the user clarified that brief valid connections should receive modest novelty credit. V7 implements that changed construct. Its first trial failed the control-credit conditions despite correct observed framework/control rankings. A later reference-scope amendment clarified commutative-polynomial and ordinary biased-probability baselines. That trial also failed: routine probability controls received zero novelty, but brief commutator connections remained uncredited and a brief subgroup connection tied a developed framework on novelty while scoring higher overall. A conventional invariant was cited as a use of the added connection; exact-excerpt validation cannot establish that semantic attribution. Historical results are retained, and qualification remains unestablished. The two-call decomposition subsequently failed development: it credited a brief commutator connection but overcredited conventional GCD/LCM mathematics and missed developed uses. The preserved stage findings and case report document these errors. The preregistered specialist fallback also failed quoted-Qwen development. Its roles emitted mathematical objections to omitted elementary steps, conventionality and perceived irrelevance, removing bonuses from valid frameworks and a brief connection. Selected exact checks of the disputed steps are preserved without rescoring the trial. Rubric-only Qwen specialist development also failed: correct validity findings were vetoed by other roles, while a conventional calculation was mistaken for use of a brief connection. Quoted Gemma specialist development was deferred following the user's new execution instruction. Related proof-verification studies discuss false rejection [16,17], but use different models and aggregation rules and do not qualify this instrument.

evaluation_judge/quoted (dev, ef8a300c) failed: 2/4 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, 08145e59) failed: 1/3 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, ebe93e9d) failed: 6/9 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, a3fa911e) failed: 4/7 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, b33cb353) failed: 0/3 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/rubric (dev, c07b8d14) failed: 0/3 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

training_judge/quoted (dev, 66721e0e) failed: 2/5 observed preference contracts passed; false-theory suppression was not measured. Incomplete suite; lowest stratum-wise final upper bounds: preference 75.0%, false-theory suppression 100.0%.

Incomplete development suites stopped under the fixed futility rule. Upper bounds assume every remaining case succeeds solely to test attainability. Unobserved cases are not counted as measured successes or errors; no early pass is allowed. No comparative conclusion follows.

A historical BF16 LoRA backward probe completed at 2560 tokens and microbatch 1, with peak allocated GPU memory 4.76 GiB and reserved memory 4.84 GiB. The measured forward/backward interval was 941.72 seconds, including first-use compilation. The synthetic repeated-token input checks execution and memory, not mathematical ability or steady-state throughput. A Qwen/Qwen3.5-0.8B BF16 LoRA backward probe completed at 2560 tokens and microbatch 1, with peak allocated GPU memory 2.02 GiB and reserved memory 2.41 GiB. The measured forward/backward interval was 78.12 seconds, including first-use compilation. The synthetic repeated-token input checks execution and memory, not mathematical ability or steady-state throughput. The initial GRPO attempt failed during generation prefill when a carriage return entered the compiler-cache path, before any optimizer update. Its failure log is preserved. A repaired GRPO pilot reached optimizer boundary 1 and saved its checkpoint, with peak allocated memory 4.89 GiB and reserved memory 6.08 GiB. Its recorded learning rate was 0; the sampled batch had verified accuracy 62.5% and mean supported theory 0. A warmup boundary does not demonstrate learning. The resumed pilot completed boundary 2 at learning rate 1e-05, with a recorded step interval of 480.66 seconds. Peak allocated memory was 4.97 GiB and reserved memory 6.25 GiB. Its batch accuracy was 50.0%, and mean supported theory was 0. Checkpoint recovery and a parameter change are feasibility evidence, not an improvement estimate. A single resumed interval is not a stable throughput benchmark. Pilot adapters are excluded from comparative initialization. A synthetic Gemma decoding diagnostic recorded 24 GPU layers: 9.04 tokens/s; 32 GPU layers: 8.74 tokens/s; 40 GPU layers: 4.47 tokens/s. The fastest measured setting used 24 GPU layers. These short upstream llama-bench measurements omit structured-output sampling. The offload sweep allocates the registered maximum context. They do not establish end-to-end judgment latency or calibration quality. A synthetic Gemma decoding diagnostic recorded 1 threads: 1.92 tokens/s; 4 threads: 5.49 tokens/s; 8 threads: 6.38 tokens/s. The fastest measured setting used 8 threads. These short upstream llama-bench measurements omit structured-output sampling. The thread sweep uses a smaller allocated context than the server. They do not establish end-to-end judgment latency or calibration quality. The exploratory-single-v1 pilot generated 8 policy completions but stopped after 3 requests failed the evidence contract, with 0 accepted judgments and 0 saved optimizer boundaries. Reproducing mathematical typography in exact quotations failed despite bounded validation feedback. This is an execution failure, not a learning result. The exploratory-small-gpu-v1 pilot generated 8 completions and exhausted 3 judge attempts on repetitive, truncated JSON. It accepted 0 assessments and saved 0 optimizer boundaries. Sampled whole-device usage peaked at 7666 MiB of 8151 MiB. This was an output-contract failure, not a GPU OOM or a learning result. The exploratory-single-v2 exploratory pilot saved boundary 1 from the selected base, with a step interval of 864.57 seconds, learning rate 0, batch accuracy 37.5%, mean theory 0.1328, mean novelty 0.0000, and 1 contract/transport retries. Peak allocated/reserved GPU memory was 4.89/6.10 GiB. Completed judge requests took 141.05–272.42 seconds, including unsuccessful contracts. The exploratory-small-gpu-v2 exploratory pilot saved boundary 1 from the selected base, with a step interval of 179.71 seconds, learning rate 0, batch accuracy 37.5%, mean theory 0.2438, mean novelty 0.1250, and 0 contract/transport retries. Peak allocated/reserved GPU memory was 2.34/3.72 GiB. Completed judge requests took 8.28–9.62 seconds, including unsuccessful contracts. The exploratory-single-v2 exploratory pilot saved boundary 2 after resumption, with a step interval of 805.43 seconds, learning rate 1e-05, batch accuracy 50.0%, mean theory 0.2078, mean novelty 0.0000, and 0 contract/transport retries. Peak allocated/reserved GPU memory was 4.97/6.25 GiB. Completed judge requests took 145.71–187.99 seconds, including unsuccessful contracts. Resumption changed 96/192 adapter tensors. These discarded pilot updates demonstrate execution, not improved mathematical ability. The exploratory-small-gpu-v2 exploratory pilot saved boundary 2 after resumption, with a step interval of 120.98 seconds, learning rate 1e-05, batch accuracy 0.0%, mean theory 0.0000, mean novelty 0.0000, and 0 contract/transport retries. Peak allocated/reserved GPU memory was 2.38/3.82 GiB. Resumption changed 96/192 adapter tensors. These discarded pilot updates demonstrate execution, not improved mathematical ability. During exploratory-small-gpu-v2 boundary 1, 188 whole-device samples recorded a peak of 7619 MiB out of 8151 MiB. This includes the judge and other GPU users; sampling can miss shorter peaks. During exploratory-small-gpu-v2 boundary 2, 129 whole-device samples recorded a peak of 6862 MiB out of 8151 MiB. This includes the judge and other GPU users; sampling can miss shorter peaks.

## Exploratory continuation with a single judge

The dated amendment explicitly permits training without calibration qualification. It retains the latest published single-call rubric v7, fixed references, modest connection credit, weights, correctness gate and training settings. Following an exact-quotation execution failure, a new identity retains context preflight and replaces quotation copying with constrained passage IDs. Code extracts original source text; this follows the general source-location citation idea [19], using only local Qwen/Gemma. After the smaller judge repeatedly exhausted its output budget, a separate identity bounds rationale length and evidence/problem lists in the wire format without changing scoring rules. It does not verify that a selected passage entails the judge's claim. Each correct solution receives one accepted structured assessment; only output or transport failures permit bounded retries. Separate names and checkpoint identities keep these runs out of the qualified study. The initial comparison is theory bonus versus correctness-only at seed 42, with ordinary and rising-sea prompted baselines. The current 4B Qwen evaluator's scores are also unqualified. Both judges share a model family and may share systematic errors. The larger CPU setup was postponed at the user's request after a partial ordinary baseline; its saved outputs are not pooled with the smaller-policy comparison. The model-size change also changes the reward instrument, so historical timing or scores cannot isolate a CPU-versus-GPU effect. Held-out correctness and recipient transfer are therefore particularly useful checks, while judged theory remains a potentially biased proxy. Reward-model overoptimization has been observed in a distinct synthetic reward-model setting [18]; it does not determine this experiment's outcome. All uncertainty remains exploratory even if later seeds or nominal targets agree. Larger, better judges are future experiments requiring new frozen identities and fresh held-out confirmation. Analysis status: pending. No matched trained arms have been evaluated.

```json
{
  "profile": {
    "id": "exploratory-small-gpu-v2",
    "amendment": "reports/amendments/2026-11-16-compact-gpu-judge.md",
    "authorization": "User requested prioritizing smaller/quantized Qwen3.5 models fully on GPU on 2026-11-16; earlier authorization for exploratory single-call judging despite failed qualification remains in effect.",
    "calibration_required": false,
    "interpretation": "Exploratory small-model GPU study with unqualified same-family judges; prior larger-model runs are deferred and not pooled.",
    "judge_protocol": "single-compact-v1",
    "rubric_version": "v7",
    "reference_version": "v3",
    "initial_arms": [
      "ordinary",
      "prompted",
      "theory-seed42",
      "correctness-seed42"
    ],
    "input_hashes": {
      "configs/study.json": "f6ff5203056f5f5eeb555f4c69f608dd3dc746562f2ee2a783668ab5292225e6",
      "configs/models.lock.json": "29a7152a84fea4d2b86e5229c1140e80685c583c07a7c6a5a352faba3af223d9",
      "configs/policy-selection.json": "0c841de481c145140df1c2b78bb820eb3174033994fea365294616e7105e44af",
      "configs/judge-runtime.json": "24a881eb8dba6760208b3eb1f928429a054a710c68e344b786e5fbae51fcc434",
      "data/manifest.lock.json": "d68e3c4c8759bc298f51aa9d4758e7701ae58374aca1733226a4db7387157a7c",
      "data/ood.lock.json": "11d75a026b7aab76c1e154a8172846c4735962f370fca2191606c4bff82eb062",
      "configs/artifacts.lock.json": "7fce628b3e3786c6c39b3ecb82a281b3f6c197cd1c38a44762fed06a55957b21"
    },
    "judge_identities": {
      "training_judge": {
        "quoted": "5a42dfae5ed77aa8f39c08e68d61f3cee6ece0a6038848dd9f91e11bf86948dc",
        "rubric": "3d0a631c8910f56dba0a111bd0c86565a0f875a2bd9c0fd1a2977b65a19807bb"
      },
      "evaluation_judge": {
        "quoted": "f99f76537c11d98dff3653e4076644d8d3f3f62fa4c6e8f194526ad485a342e0"
      }
    },
    "evidence_protocol": "compact-evidence-v1",
    "logging_protocol": "persistent-append-flush-each-event-v1"
  },
  "primary": {
    "status": "pending",
    "reason": "No matched trained arms have been evaluated"
  },
  "secondary_ood": {
    "status": "pending",
    "reason": "No matched trained arms have been evaluated"
  },
  "transfer": {
    "summaries": {},
    "versus_no_notes": {},
    "versus_unrelated": {},
    "between_note_sources": {},
    "interpretation": "exploratory; source-clustered, unadjusted paired intervals"
  }
}
```

## Transfer evaluation

Recipient accuracy is compared with no notes, unrelated notes of matched length, and notes from other frozen source policies. Paired uncertainty resamples source problems with all four targets retained. Comparisons require complete matching source and target coverage. The machine-readable report publishes each source policy's related-minus-unrelated contrast and all pairs of note-source policies, with unadjusted exploratory intervals.

| Note condition | Probes | Recipient accuracy |
|---|---|---|
| Registered transfer conditions | Pending | Pending |

## Discussion and limitations

Judge scores are imperfect proxies. The current training and evaluation judges share the Qwen family and may share biases or training data; the cross-family comparison is deferred. Quantization can change judgments. Synthetic elementary tasks limit external validity. The constructed audit changes numerical instances while sharing mathematical templates with development; it does not establish generalization to unseen failure types. Fixed small-seed comparisons may be inconclusive. Reusable exposition is not equivalent to historically novel mathematics. Higher training scores without independent or transfer improvement are consistent with proxy optimization. Do not infer a latent mechanism from behavioral scores alone. Development/test separation and scoped claims follow methodological guidance [10,11].

## Postponed research directions

After the current experiment sequence, the user requests trials with 10B+, 100B+ and 1T+ parameter models, advanced agentic RL, Lean-based formal feedback, and explicit quantitative rewards replacing LLM judging where feasible. These are future research intentions, not implemented methods or results. Candidate measures include token/compute costs, checked consequences, dependency-based reuse and held-out transfer. Exact calculation does not establish that a metric captures conceptual novelty, generality or understanding. docs/future-research.md documents candidate measures, source links and required controls. Each direction needs a new registered protocol; the current small-model experiment and reward remain unchanged. If prespecified development diagnostics find that the small policy cannot solve the current tasks, a separate easier-mathematics experiment is authorized, preserving the present tasks for larger models. Difficulty must not be selected on held-out scores or changed within a comparison. The current pilot contains correct completions, so this fallback is not activated. The dated task-difficulty amendment records the diagnosis and separation requirements.

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

[18] [Gao, Schulman and Hilton, Scaling Laws for Reward Model Overoptimization](https://proceedings.mlr.press/v202/gao23h.html)

[19] [Anthropic, source-location citation representation (documentation only)](https://platform.claude.com/docs/en/build-with-claude/citations)

AI statement: Codex wrote this codebase and paper from the exact specification provided by a human. Human cleanup and rewriting are in progress.
