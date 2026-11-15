# Protocol amendment: valid conceptual novelty and broader mathematics

Date: 2026-11-15. Reason: the user explicitly requested additional reward for
novel but valid concepts and more out-of-distribution mathematics. This is
specified before any judge assessment, policy output or comparative result.
The Gemma server has been loaded; no judgment request has been issued. The
original preregistration is retained unchanged as the historical record.

## Reward and operational definition

The reward remains R=C(1+0.5T), with externally verified final-answer correctness
C and supported theory quality T. Rubric version v2 uses weights 20% structure,
20% justified generality, 15% derivation of the problem, 15% reuse/connections,
10% conceptual economy, and 20% constructive novelty. Each criterion is scored
0–4. Novelty can concern definitions, objects, invariants, relationships,
theories, frameworks, ways of thinking, connections, or substantive content of
a proposed subfield/paradigm. A name or aspiration earns no credit.

Novelty is relative to the frozen task-family references in
`configs/novelty-anchors.json`. It is not historical originality and does not
measure distance from unknown pretraining data. Established mathematics can
earn novelty credit when it supplies a useful departure from these references.
The judge must identify the addition, justify its mathematical work and quote
supporting text. Larger conceptual departures can receive more credit when
their assumptions, bridge, consequences and limits are demonstrated. Renaming,
length and unfamiliar terminology do not establish a departure.

A substantive false novelty-bearing claim invalidates the whole theory bonus;
unsupported constructions cannot earn it. Correct conventional explanations
can earn all five other components, but cannot earn the novelty component
merely for correctness. This intentionally changes the original statement that
an entirely conventional framework could receive the maximum total bonus.
The maximum reward and correctness ordering remain unchanged. The ordinary
training prompt is unchanged across training arms; the explicit-prompt baseline
now asks for justified nonstandard concepts/connections as well as generality.
The quotation/persona ablation keeps the entire v2 rubric and reference anchors.

## Calibration additions

Retain each split's original 20 preference pairs and 20 false-theory cases.
Add eight novelty pairs and eight false novel-theory cases to both development
and audit, using distinct problem parameters and identifiers. The four
mathematical bridges are integer lattices for GCD, coset intersections for LCM,
quadratic-algebra norms for polynomial multiplication, and parity characters
for probability. These are established constructions and public constructed
expectations, not evidence of historical discoveries or human preferences.

For novelty pairs require greater total theory quality and greater supported
novelty for the bridge, with zero novelty for the conventional/cosmetically
renamed response. Require at least 80% preference ordering and at least 90%
false-theory suppression **separately in both the original and novelty strata**.
All three frozen judge/prompt configurations must pass. Parameter changes do not
make audit templates independent of development templates; report this limit.
No audit is silently reused after changes. The judge output budget increases
from 1024 to 1536 tokens to accommodate six evidence-bearing criteria; its
context remains 8192. Identity hashes include prompt, references, weights,
schema, model revision, runtime and decoding configuration.

## Broader held-out task families

Keep all original manifests and the 400-problem primary evaluation unchanged.
Add an independently locked secondary `test_ood` manifest: 50 problems each for
largest grid component, convex polygon missing angle, rational matrix rank,
and modular inverse. No task from these families enters training, development
selection, or the transfer-note source pool. Use seed 20261116 with disjoint
per-family index intervals; lock generator parameters and versions before use.
Run the same frozen final checkpoints and ordinary task prompt on this suite.

Reuse Reasoning Gym's Apache-2.0 grid/polygon generators and SymPy's rank/inverse
operations. Independently check references using union-find, angle sums,
nonzero minors, and residue enumeration. Reject impossible convex polygon
angles before locking; preserve rejection records. Canonicalization removes
grid rotations/reflections, polygon angle-order duplicates, matrix row/column
permutations and identical modular instances. This is not a proof of complete
semantic inequivalence between all tasks. Freshness refers to generator
instances; OOD refers to this project's training families.

## Hypotheses, analysis and falsification

Primary H1 remains improvement in frozen-Gemma mean C*T of at least 0.05 over
correctness-only GRPO, a paired 95% interval excluding zero, and accuracy
noninferiority within three percentage points, across seeds 42/43/44. T now
means the v2 rubric and must be identical across all compared arms. The first
single-seed result remains exploratory. All budgets, training hyperparameters,
initialization, controls, stopping rules and no-significance-chasing rules stay.

The original secondary H2 concerning recipient transfer remains unchanged.
Secondary H3: the intervention improves correctness-weighted supported novelty
C*N, where N is the novelty criterion divided by four. Secondary H4: benefits
extend to the additional held-out families. Report C*N, C*T and accuracy with
paired problem-level bootstrap intervals retaining matched seed observations;
stratify the secondary OOD suite by family. Report per-family descriptive scores
and between-seed variation. These additional intervals are unadjusted secondary
analyses and cannot rescue a failed primary endpoint. Nonpositive estimated
effects fail the corresponding directional prediction; intervals spanning zero
are inconclusive rather than evidence of improvement. Higher Qwen scores
without Gemma/transfer improvement support proxy-optimization concerns.

The hypothesis concerns behavior and useful transfer, not historical invention,
new subfields, out-of-pretraining generalization, or an established latent-space
mechanism. Relevant precedent and caveats: [FERMAT](https://arxiv.org/html/2511.14778v1),
[rubric rewards](https://arxiv.org/html/2507.17746v1), and
[evaluation pitfalls](https://arxiv.org/html/2108.02497v4).
