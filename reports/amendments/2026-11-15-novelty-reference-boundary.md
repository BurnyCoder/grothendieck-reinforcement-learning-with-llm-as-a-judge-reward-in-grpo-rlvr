# Development refinement of the novelty reference boundary

Date: 2026-11-15. Both judges have produced development assessments, and neither
has completed calibration. No locked judge audit, policy evaluation, or GRPO
optimizer update has been completed. This is a development-informed amendment.

Both initial judges awarded positive novelty to the same conventional divisibility
proof. Their exact scores, supporting text and latency are generated from saved
logs in [`experiments/development-runtime.md`](../experiments/development-runtime.md).
The explanation is mathematically useful, but its argument is already covered
by the supplied Euclidean/common-divisor reference. This is a concrete example
of overcrediting novelty, not a measured population error rate. The incomplete
v2 attempts remain published and their cached opinions cannot pass v3 gates.
The completed Qwen log also contains an LCM assessment that awards novelty while
describing the argument as a conventional prime-exponent method. That observation
reinforces the need to distinguish useful generality from conceptual departure;
it does not change the calibration cases or acceptance thresholds.

Rubric v3 explicitly includes standard correctness arguments, routine parameter
substitutions, scaling, direct special cases and equivalent notation within the
conventional reference. It requires comparison with every listed approach and
identification of an additional mathematical construction and its function.
The GCD reference spells out the standard common-divisor preservation argument
without providing a calibration problem's numerical answer. Useful conventional
theory continues to earn the other criteria. A valid, functional bridge to a
different structure remains eligible for novelty credit.

The judge is also asked for shorter rationales and decisive excerpts. This
reduces repeated exposition in assessments; it does not change candidate length
preferences, score weights, the correctness gate, validity gate, schema or reward
formula. Full raw responses remain logged, and supporting excerpts still require
exact matching. Response-length limits in the protocol are unchanged.

Calibration cases, audit labels and thresholds are unchanged. Development must
be rerun with the revised prompt for each required judge/variant before the
untouched locked audits. This refinement used development evidence only; it does
not establish that the revised prompt succeeds. Comparative model initialization,
hyperparameters, locked tasks and analysis rules remain unchanged.
