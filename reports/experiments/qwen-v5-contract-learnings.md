# Qwen v5: an incomplete calibration after a score-consistency failure

Date: 2026-11-15. Development evidence only.

The [v5 protocol](../amendments/2026-11-15-explicit-reference-decisions.md)
reached a contract failure while grading the conventional probability
explanation. The judge declared `within_reference` and described its argument
as a routine variation, but assigned positive constructive novelty. Bounded
validation retries repeated that contradiction and the process terminated.
No contradictory assessment entered the cache or became a mathematical reward.

The [streamed events](../development/qwen-v5-contract-failure.jsonl),
[identity](../development/qwen-v5-contract-failure.lock.json),
[progress](../development/qwen-v5-contract-failure.progress.json) and
[traceback](../development/qwen-v5-contract-failure.traceback.txt) are preserved.
Counts and accepted opinions are generated in the development report.
The completed GCD, LCM and polynomial contrasts passed, including conventional
controls that retained supported theory but received no novelty credit. This
does not constitute a completed calibration. The probability contrast was not
completed; false-theory suppression was not measured. This is a contract
failure, not a threshold failure or a policy-performance result.

The rejected probability judgments provide a useful distinction: the declared
reference relationship and the rationale agree with the conventional label,
while the numerical novelty score disagrees. Exact-excerpt checks and retry
feedback did not make the model's two declarations consistent. The separate
reference decision improved auditability on these observed cases but did not
make the current execution protocol reliable. Repeated use of familiar public
templates limits the generality of that observation.

A possible repair is to make reference eligibility an explicit deterministic
gate in the reward calculation, analogous to the existing validity gate, while
preserving the raw opinion and logging withheld credit. That would change the
assessment-to-reward contract; it must be registered before a fresh run. It
must not be applied retroactively to turn this failed attempt into a pass.
Such a gate would enforce declared prerequisites, not decide whether the
mathematics actually lies beyond the reference. Wrong relationship or validity
judgments would remain possible and must still be tested. Long training and
locked audits remain blocked.
