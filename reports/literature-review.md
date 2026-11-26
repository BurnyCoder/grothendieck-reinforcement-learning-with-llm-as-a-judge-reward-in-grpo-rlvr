# Literature review and source map

Updated 2026-11-15. The [state-of-the-art review](state-of-the-art-review.md)
contains the claim-by-claim synthesis and source/license audit. This document
organizes the research questions to avoid duplicating that synthesis.

## Which mathematical behavior is being optimized?

The historical motivation is concept formation and generality in
[McLarty's account of Grothendieck](https://ncatlab.org/nlab/files/McLartyRisingSea.pdf).
The closest formal environment found is
[FERMAT](https://arxiv.org/html/2511.14778v1), which represents mathematical
entities and symbolic production rules and studies interestingness functions.
Its formal entities differ from the explanations scored here. The present
project proposes measures of supported exposition and recipient transfer. The [current review](reviews/2026-11-26-scientific-audit.md) identifies which outcomes have been observed.

The [novelty/OOD amendment](amendments/2026-11-15-valid-novelty-and-ood.md)
explicitly tests useful departures from documented conventional approaches.
FERMAT's definition/conjecture production and productivity/comprehensibility
measures motivate checking what a construction enables, beyond its name or
unfamiliarity. Its results do not validate our natural-language novelty score;
the calibration and held-out evaluations must establish its local usefulness.

## How is behavior selected?

[DeepSeekMath](https://arxiv.org/html/2402.03300v3) supplies the original GRPO
method; [TRL](https://huggingface.co/docs/trl/grpo_trainer) supplies the maintained
implementation. [Dr. GRPO](https://arxiv.org/html/2503.20783v2) motivates removing
length and within-group standard-deviation normalization.
[Rubrics as Rewards](https://arxiv.org/html/2507.17746v1) is the direct precedent
for decomposed judgment. The additional correctness gate is a project design
choice. The maximum theory bonus and validity rule are hypotheses to test, not
values established by those papers.

## What would constitute evidence?

[Judge evaluation research](https://arxiv.org/abs/2306.05685) motivates testing
judge behavior rather than assuming it is correct. The protocol separates
training reward, a separate frozen judge, and verified recipient accuracy. The original qualification design uses a different model family for evaluation. Both active small-GPU judges are Qwen checkpoints. [Model lock](../configs/models.lock.json)
These measures can disagree, which is scientifically informative.

The observed development confusion between conventional generality and novelty
also motivates examining judgment order. [MT-Bench's published mathematical
judge prompts](https://github.com/lm-sys/FastChat/blob/main/fastchat/llm_judge/data/judge_prompts.jsonl)
request a comparison and explanation before the final rating.
[G-Eval](https://arxiv.org/pdf/2303.16634) instead supplies generated evaluation
steps and combines score probabilities; our implementation does not reproduce
that method. Neither source establishes that changing JSON field order will
repair this project's novelty judgments.
[Yamauchi et al.](https://arxiv.org/html/2506.13639v1) find little additional
benefit from explicit reasoning when detailed criteria and references are
present in their evaluated settings. Their tasks and evaluators differ from
ours. Any reasoning-order or decoding change here therefore needs its own
development experiment and fresh audit, not an assumed reliability improvement.
The [subsequent inference review](judge-inference-review.md) examines native
thinking and small-judge budget studies after the observed v4 failures. It
distinguishes pairwise preference, final-answer judging and our theory rubric.

The evaluation structure follows the separation of development and testing
discussed by [Lones](https://arxiv.org/html/2108.02497v4). Claims about a latent
mechanism would require additional evidence of the kind of distinction between
explanation and speculation emphasized by
[Lipton and Steinhardt](https://arxiv.org/html/1807.03341). None is promised here.

## Search scope and remaining uncertainty

The 2026-11-16 smaller-GPU amendment reuses the existing training/inference stack.
[Qwen's 0.8B model card](https://huggingface.co/Qwen/Qwen3.5-0.8B) and the
[2B](https://huggingface.co/unsloth/Qwen3.5-2B-GGUF) and
[4B](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF) quantized repositories supply
Apache-2.0 model artifacts. [Unsloth's guide](https://unsloth.ai/docs/models/qwen3.5/fine-tune)
supports the smaller policy and recommends its non-vLLM route for GRPO, while
cautioning against 4-bit QLoRA for this family. We retain BF16 policy training and
quantize frozen judges. [llama.cpp's pinned server interface](https://github.com/ggml-org/llama.cpp/blob/b1b770d90d94cad9e9ea5b993bdbc383a522fb28/tools/server/README.md)
provides explicit CUDA device/layer placement with automatic fitting disabled.
These sources support implementation choices, not an empirical claim that both
models fit this machine during GRPO or that the smaller judges are reliable.

The [exploratory continuation](amendments/2026-11-16-exploratory-single-judge.md)
tests whether learning remains useful with an unqualified judge. A follow-up
review read [Gao, Schulman and Hilton's full paper](https://proceedings.mlr.press/v202/gao23h/gao23h.pdf),
including its appendices. In their synthetic reward-model setting, stronger
optimization can raise proxy reward while reducing a separate model's reward.
This motivates independent behavioral checks here, not an assumption that our
errors are independent noise or that larger judges will solve them. Their model,
task and optimizer differ; no source code is imported. The current single-call
rubric remains the already-published instrument rather than a new prompt selected
from this paper.

Sources examined include primary research articles, official model cards,
training documentation and generator/verifier source files. The exact pipeline
was not identified in those sources. This search does not establish exhaustive
novelty. The supplied video and social-media passages are retained as motivation
with separate attribution; inaccessible commentary is not used to validate a
technical claim. Source-specific implementation observations and limitations are
recorded in the linked synthesis, and executable compatibility checks accompany
the locked dependencies.
