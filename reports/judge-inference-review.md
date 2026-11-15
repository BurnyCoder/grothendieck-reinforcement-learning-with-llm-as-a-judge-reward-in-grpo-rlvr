# Judge inference: evidence and limits

## Exact evidence transport after the first exploratory pilot

The [archived failure](development/feasibility-exploratory-single-v1-failure.json)
shows that purported quotations can fail literal matching even after validation
feedback. The [indexed-evidence amendment](amendments/2026-11-16-indexed-evidence.md)
replaces copying with constrained source-passage selection, keeping the scoring
rubric. RULERS' discussion of deterministic-verification brittleness motivates
distinguishing this execution issue from semantic judge quality.
[Source-location citation extraction](https://platform.claude.com/docs/en/build-with-claude/citations#how-citations-work)
provides a relevant representation pattern. Our implementation uses local JSON
schemas and exact Python lookup only; it does not adopt another model or an API.
Source membership is checked mechanically. Relevance and mathematical validity
remain unqualified model opinions. No paper's reported reliability is transferred
to this implementation.

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

The user's subsequent clarification permits modest credit for a brief valid
connection without a further worked consequence. The
[v7 amendment](amendments/2026-11-15-modest-valid-connections.md) implements that
construct with a capped contribution, preserving raw opinions. Neither the cap
nor an exact quotation settles whether an added relationship lies beyond the
fixed reference. Those semantic decisions still need calibration.

## Novelty-specific judge instability

[Sternlicht et al.](https://arxiv.org/html/2610.02022v1) vary prompts, retrieval,
reasoning and aggregation for research-idea novelty judgments. Their results
depend on the evaluator and on whether ideas are human-authored or generated;
retrieval and extra reasoning provide no uniform repair. The generated pool has
weak novelty labels, with a limited expert check rather than exhaustive human
validation. Some prompt variants also change the stated decision task, so their
differences are not purely wording effects. This study concerns originality
relative to scientific literature, not our finite-reference mathematical rubric
or quantized local models. We infer that passing familiar constructed templates
is insufficient evidence of reliable novelty scoring on policy outputs. The
full paper, methods, results and appendix prompts were examined; no code or
prompt text is imported, and the active v7 calibration remains unchanged.

## Decomposing the judgment task

[DnA-Eval, sections 3–5 and appendices](https://aclanthology.org/2025.coling-main.156.pdf)
separates aspect ratings and external aggregation. Its benchmarks and ablations
motivate testing decomposition; additional calls cost more, and gains vary across
settings. It uses pairwise ratings and sometimes generated aspects and weights.
Our proposed two-call/specialist instruments retain fixed criteria and weights
with pointwise scoring, so this is an adaptation rather than a replication.
Neither its results nor correlated opinions from repeated use of one model
establish local mathematical validity. The full paper and appendices were reviewed;
no code or prompts are copied. The [dated amendment](amendments/2026-11-15-decomposed-judges.md)
specifies the unchanged qualification gates.

## False objections under additional verification

This follow-up review was conducted after specialist activation on 2026-11-15.
It informs interpretation, not a retrospective justification or alteration of the
running protocol. Both papers' main text, methods, results and appendices were read;
no prompts, code, datasets or weights were imported.

[Naik et al., sections 3–4 and appendices](https://arxiv.org/pdf/2604.02450v1)
distinguish finding errors from reliably accepting valid proofs. Prompts optimized
for error detection also reject correct proofs. Their final instrument combines
diverse prompts with threshold voting, selected using development/holdout data;
it differs from this project's mandatory mathematical veto. Their Qwen models
are larger than our frozen quantized judge, and the task is proof validity,
not constructive novelty. The study supports investigating false objections
alongside missed errors, but does not qualify our instrument or authorize
averaging away its validity failures. Its reported gains cannot be assumed to
transfer to the present model, token budgets or rubric.

[Huang et al., sections 2–3 and appendix A](https://arxiv.org/pdf/2511.21522v1)
study rejection whenever any verification call finds an error. They report
better error detection but also unwarranted rejections from smaller models.
Some evaluation labels are model-generated; author case reviews should not be
treated as independent certificates. We checked a specific appendix assertion:
Case 6 calls its proof correct despite that proof identifying a union-based
set map with a linear map over the two-element field and treating a fixed full
set as implying singleton neighborhoods.

Our counterexample sets every student's neighborhood to the full student set
S. Then f(X)=S for nonempty X and f(empty)=empty. For distinct singleton sets
A and B, f(A symmetric-difference B)=S, whereas
f(A) symmetric-difference f(B)=empty. Also f(S)=S, yet neighborhoods are not
singletons. These refute those proof steps, not the problem's conclusion.
The [exact finite-set check](development/literature-pessimistic-case6-check.json)
records the construction without model inference. This narrow discrepancy is
not a reanalysis of the paper's benchmark or a claim about every author label.

The implication for this project is to preserve and inspect concrete alleged
errors, including disagreements with constructed expectations. Neither source
justifies silently relabeling a calibration case, rerunning a failed audit,
or treating a model objection as established mathematical fact.
