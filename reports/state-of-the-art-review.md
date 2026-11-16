# Literature and implementation review

Reviewed 2026-11-15. This is a research protocol, not evidence that the proposed
reward improves mathematical understanding. Numbers describing this project's
design are proposed settings; measured results will be generated from artifacts.

## Question and nearest existing work

Can a correctness-gated, evidence-bearing rubric reward improve reusable
mathematical explanations and downstream problem solving? The proposed
contribution is an experiment combining existing components, not a new policy
optimizer or a demonstration of mechanistic latent-space steering.

| Source | Relevant finding or design | Reuse and boundary |
|---|---|---|
| [DeepSeekMath, §4](https://arxiv.org/html/2402.03300v3) | GRPO uses within-prompt sampled rewards without a separate learned critic. | Use TRL's implementation; do not reproduce the original training scale or claim its results transfer to this setup. |
| [Understanding R1-Zero-Like Training, §3 and Appendix G](https://arxiv.org/html/2503.20783v2) | Dr. GRPO removes response-length normalization and group reward standard-deviation normalization to address identified biases. | Explicit `dr_grpo` and unscaled rewards. Our nonzero KL coefficient is a design choice; the paper's reported configuration uses zero KL. |
| [Rubrics as Rewards](https://arxiv.org/html/2507.17746v1) | Explicit weighted criteria supply RL feedback beyond directly verifiable domains. Experiments concern scientific and medical tasks. | Reuse rubric decomposition; add an external mathematical correctness gate. The authors do not establish that rubrics prevent reward hacking. |
| [Learning Interestingness in Automated Mathematical Theory Formation](https://arxiv.org/html/2511.14778v1), [FERMAT code](https://github.com/trishullab/Fermat) | Formalizes concept discovery and theorem proving and learns interestingness heuristics using evolutionary search with abstraction. | Closest conceptual precedent for theory formation. Our natural-language explanations are not its formal symbolic discoveries and have weaker validity guarantees. |
| [Learning Formal Mathematics From Intrinsic Motivation](https://proceedings.neurips.cc/paper_files/paper/2024/hash/4b8001fc75f0532827472ea5a16af9ca-Abstract-Conference.html) | Studies self-generated formal mathematical tasks and proofs. | Related motivation; we retain externally generated problems and do not claim autonomous discovery. |
| [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) | Evaluates LLM judges and documents biases including verbosity and position. | Require adversarial constructed calibration, independent-family evaluation, and length diagnostics. Cross-family judging does not guarantee independence or mathematical truth. |

## Grothendieck and attribution

[Colin McLarty, *The Rising Sea: Grothendieck on simplicity and generality I*](https://ncatlab.org/nlab/files/McLartyRisingSea.pdf)
discusses building broad concepts until particular questions yield as consequences.
Its opening quotation cites *Récoltes et Semailles*, pages 552–553, and McLarty
states that its translations are his. The user-supplied nut/water passage is
included in the judge prompt with that attribution. The rubric is our research
operationalization: it cannot establish how Grothendieck would personally grade
a particular answer. Useful definitions, explicit assumptions, demonstrated
consequences, and economy are rewarded; abstraction without mathematical work is
not. Originality in the historical sense is unnecessary.

The user also supplied a lecture paraphrase titled *Linear algebra and vector
analysis: Rising Sea*, commentary associated with
[3Blue1Brown's video](https://www.youtube.com/watch?v=LKrwhjOI8Nc), and a
[social-media discussion](https://x.com/littmath/status/2109653733470572878).
These are distinct commentary sources, not direct Grothendieck quotations. The
[complete user-supplied passages](../docs/rising-sea-quotations.md) preserve all
wording with separate attributions and source-check notes. The lecture handout
and nLab entry were located; the supplied lecture version has small differences.
The video transcript and social-media wording have not been independently
authenticated. This commentary archive is not additional judge-prompt content
or empirical evidence for the training method.

## Reusable software and source audit

* [Reasoning Gym](https://github.com/open-thought/reasoning-gym), Apache-2.0:
  reuse its generators, with recorded versions, parameters and seeds. Source
  inspection found `Random(seed + index)`; disjoint indices alone are insufficient
  if split seed intervals overlap. Canonical mathematical instance deduplication
  is required. Its native scores can be fractional or permissive, so our binary
  verifier does not reuse those scores as correctness labels.
* [Polynomial equations generator](https://github.com/open-thought/reasoning-gym/blob/main/reasoning_gym/algebra/polynomial_equations.py):
  generated answers use Python rounding, while its instruction says rounding
  down. Normalize the task instruction to nearest four decimal places; record
  the modification. Reject degenerate identities and verify reference roots.
* [Polynomial multiplication generator](https://github.com/open-thought/reasoning-gym/blob/main/reasoning_gym/algebra/polynomial_multiplication.py):
  monomials originate in a set. Fix `PYTHONHASHSEED`, archive complete manifests,
  and pin dependencies; seeds alone are not a sufficient reproducibility record.
* [Math-Verify](https://github.com/huggingface/Math-Verify), Apache-2.0 with
  component notices: use gold-first equivalence checks. Candidate expressions
  must pass a restricted arithmetic grammar before symbolic handling. Bound
  expression size and run verification in a resource-limited subprocess.
  Generated code is never executed.
* [TRL GRPO documentation](https://huggingface.co/docs/trl/grpo_trainer): reuse
  trainer, loss and checkpoint machinery. Supply one composite reward so the
  correctness gate survives aggregation. The effective generation batch must
  be divisible by the number of completions per prompt. Explicitly configure
  loss, scaling, KL and lengths rather than depending on library defaults.
* [Unsloth Qwen3.5 guide](https://unsloth.ai/docs/models/qwen3.5/fine-tune):
  documents GRPO with `fast_inference=False`, Transformers v5, and BF16 LoRA.
  It cautions against Qwen3.5 4-bit QLoRA. Its fine-tuning memory table does not
  guarantee GRPO memory requirements. Local forward, backward and resumption
  measurements determine feasibility.
* [llama.cpp server](https://github.com/ggml-org/llama.cpp/tree/master/tools/server),
  MIT: local GGUF serving and schema-constrained JSON. API compatibility does
  not mean remote API use. Bind to loopback only and pin its release/commit.

## Model provenance and selection

The preferred policy is [Qwen/Qwen3.5-2B](https://huggingface.co/Qwen/Qwen3.5-2B).
Use frozen [Qwen3.5-9B Q4_K_M](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF)
for training judgment and
[Gemma 4 12B UD-Q4_K_XL](https://huggingface.co/unsloth/gemma-4-12b-it-GGUF)
for independent assessment. Model repository metadata lists Apache-2.0;
retain repository license files and exact revisions with downloads. The
[Gemma 4 model card](https://ai.google.dev/gemma/docs/core/model_card_4)
provides architecture and intended-use context. Quantization may change judgment
quality; calibration applies to these exact quantized artifacts.

[Unsloth FP8 RL](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide/fp8-reinforcement-learning)
describes Qwen3-1.7B as a small-memory route. It is an explicitly conditional
fallback, not the default. Availability of newer large Qwen releases does not
establish feasibility on this laptop. No other model family is permitted.

## Scientific validity and claim audit

[Lones v4](https://arxiv.org/html/2108.02497v4) motivates separating development
from final testing and avoiding repeated test-driven selection.
[Lipton and Steinhardt](https://arxiv.org/html/1807.03341) motivate distinguishing
mechanistic explanation from speculation. The
[NeurIPS checklist](https://neurips.cc/public/guides/PaperChecklist) informs
limitations, reproducibility and uncertainty reporting.

The primary metric is a proxy: correctness-weighted *Gemma-assessed* theory
quality. A verified final answer does not verify the explanation. Constructed
judge tests are not human preference data. Fresh generator instances cannot
exclude pretraining contamination of the mathematical ideas. Held-out task
families provide a narrower generalization test than new mathematical domains.
Transfer accuracy supplies an additional behavioral check, not a proof of
understanding or a latent-space mechanism. The exact combination has not been
found in the reviewed sources; this is not an exhaustive novelty claim.

No source's published benchmark number is treated as a local measurement.
The later [judge-inference review](judge-inference-review.md) adds primary
studies of native reasoning and budget-dependent judging. Their settings do not
validate this project's novelty criterion; the local calibration gates remain.

The pre-judgment novelty amendment adds a project-specific criterion; this is
an experimental design choice, not a metric established by a cited paper.
[FERMAT sections 3–5](https://arxiv.org/html/2511.14778v1) constructs definitions
and conjectures, checks them using formal backends, and evaluates recovery of
curated mathematical entities. Its comparisons show that simple novelty alone
is not a sufficient interestingness objective in that setting. We therefore
require justified utility and consequences, while acknowledging that our
natural-language judge supplies weaker validity evidence than formal checking.
The additional OOD suite uses existing [Reasoning Gym generators](https://github.com/open-thought/reasoning-gym)
and [SymPy matrix operations](https://docs.sympy.org/latest/modules/matrices/matrices.html)
and [modular inverses](https://docs.sympy.org/latest/modules/core.html#sympy.core.intfunc.mod_inverse).
These held-out families do not establish out-of-pretraining generalization.
No code from papers is copied where an existing library implements the method.
Runtime and task-source compatibility will be checked against the locked release,
with deviations documented before comparative results.

## Smaller GPU initial experiment

The [small-GPU amendment](amendments/2026-11-16-small-qwen-gpu.md) changes scale
and placement while reusing the same methods, manifests and reward rubric. It
does not introduce a new optimization algorithm or establish that small judges
are interchangeable with larger ones. Same-family Qwen training/evaluation
judges can share errors; the frozen-recipient accuracy comparison therefore
remains necessary. Previous CPU-judge timings are retained as historical
measurements, not extrapolated to the new model combination. Implementation
sources and license checks appear in the [literature review](literature-review.md).

## A distinct route: verified mathematical construction

[ALPS, sections 3–4 and appendices](https://arxiv.org/html/2608.15979v1) asks for
a triviality proof or a finite presentation of a nontrivial model of an
equational law. Its construction channel checks both entailment of the law and
satisfiability with distinct elements, using complete prover saturation;
triviality is checked through Lean. This motivates checking that proposed
objects satisfy their specification without becoming degenerate. It does not
validate our natural-language score or establish historical originality of a
successful construction. Appendix H reports repeated solver passes, so the
headline counts should not be treated as a matched causal comparison of prompt
conditions. The full paper and appendices were reviewed. No code, prompts or
data are imported; adopting this different task and verification interface
would require a separate experiment. The current locked OOD suite is unchanged.
