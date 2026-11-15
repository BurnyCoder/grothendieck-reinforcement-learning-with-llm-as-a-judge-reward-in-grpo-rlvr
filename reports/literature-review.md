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
project therefore measures supported exposition and recipient transfer, not
discovery of a new mathematical theory.

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
training reward, independent-family judgment, and verified recipient accuracy.
These measures can disagree, which is scientifically informative.

The evaluation structure follows the separation of development and testing
discussed by [Lones](https://arxiv.org/html/2108.02497v4). Claims about a latent
mechanism would require additional evidence of the kind of distinction between
explanation and speculation emphasized by
[Lipton and Steinhardt](https://arxiv.org/html/1807.03341). None is promised here.

## Search scope and remaining uncertainty

Sources examined include primary research articles, official model cards,
training documentation and generator/verifier source files. The exact pipeline
was not identified in those sources. This search does not establish exhaustive
novelty. The supplied video and social-media passages are retained as motivation
with separate attribution; inaccessible commentary is not used to validate a
technical claim. Source-specific implementation observations and limitations are
recorded in the linked synthesis, and executable compatibility checks accompany
the locked dependencies.
