# Judge inference: evidence and limits

Reviewed 2026-11-15 after development calibration errors. This supplements the
[source map](literature-review.md), without treating benchmark findings as local
measurements or a validated repair.

[Jayarao et al., sections 3–4 and appendices](https://arxiv.org/html/2509.13332v1)
compare Qwen3 native thinking with non-thinking on pairwise RewardBench tasks.
Thinking improves many reported comparisons, while task-specific rubrics are
competitive on safety. The modes also use different sampling settings; their
estimated FLOPs are not this laptop's wall-clock latency. The study does not
test absolute scores for mathematical novelty or these quantized Qwen3.5/Gemma
judges. It motivates a local development test, not a guaranteed improvement.

[SLMJury, sections 3–4 and appendices](https://arxiv.org/html/2606.07810v1)
reports task-dependent budget effects and different rankings across binary
correctness, human-scored summaries and model-scored conversations. Its binary
oracle compares extracted final answers; both short and reasoned prompts tell
judges to ignore candidate reasoning when deciding correctness. Budget, prompt
and sometimes sampling change together. That task differs from assessing a
valid explanation's conceptual contribution. Its tested debate protocol does
not improve binary judging, which provides no basis for adding debate here.
Its framework and model rankings are not adopted; our external verifier already
handles final-answer correctness.

Google documents Gemma's native thinking switch and separate thought delimiters
in its [thinking guide](https://ai.google.dev/gemma/docs/capabilities/thinking).
Qwen likewise documents the chat-template switch in its
[model card](https://huggingface.co/Qwen/Qwen3.5-9B). These establish supported
interfaces, not novelty-grading reliability. The
[bounded development amendment](amendments/2026-11-15-bounded-judge-reasoning.md)
specifies the local experiment and its unchanged acceptance gates.

No code, datasets or model weights from these papers are imported. Primary
paper text, methods, results and appendix prompts were examined; empirical
claims above remain scoped to the studies' own designs. No model outside the
user-authorized Qwen and Gemma families is selected.

## Rubric execution and semantic limits

[RULERS, sections 3–4 and appendix A](https://arxiv.org/html/2601.08654v1)
combines locked checklists, extractive evidence checks and a fitted score mapping
for essay and summarization evaluation. Its ablations attribute much of the
reported agreement to distributional calibration using human scores. This
project has no comparable human-scored sample, so those gains do not justify
post-hoc remapping our constructed labels. The checklist design motivates
making prerequisite decisions explicit; it does not establish that an LLM will
classify mathematical concepts correctly. The full paper and appendix prompts
were examined; no implementation or prompt text is copied.

Our current exact-excerpt checks establish attribution, not whether the excerpt
supports a criterion. The observed disagreement between a novelty rationale and
its numerical score is a separate semantic failure. V5 rejected incompatible
decisions but exhausted retries on a conventional probability argument. The
[v6 gate](amendments/2026-11-15-declared-novelty-eligibility.md) instead computes
eligibility from the declarations and retains raw scores for inspection. It
cannot independently certify mathematical truth. Fresh development calibration
under the new identity is required before audit; historical outcomes remain fixed.
