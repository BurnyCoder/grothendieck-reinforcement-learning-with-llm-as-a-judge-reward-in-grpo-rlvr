# Initial implementation review

2026-11-15. Scope: correctness, mathematical interfaces, dependency compatibility,
data isolation, recovery and reporting. This is a code review, not model validation.

* Candidate answers enter a bounded AST interpreter; Math-Verify receives symbolic
  objects rather than untrusted executable strings. Worker failures propagate.
* A single composite reward enforces the answer gate before TRL aggregation.
  Invalid judge output and fabricated evidence spans retry, then raise.
* Canonical instance keys cover permutation and superficial polynomial variants.
  Reference answers are independently checked during preparation. No target
  answers are included in policy or note-generation prompts.
* Main comparisons retain paired problem/seed structure; transfer retains all
  probes from a source together. Partial runs cannot produce a confirmatory claim.
* Checkpoint sidecars are written after the trainer save and cache backup. Recovery
  ignores incomplete newer checkpoints. Real optimizer recovery remains a pilot test.
* Model/runtime revisions and latest compatible package constraints are recorded.
  An initial old-Unsloth resolution was corrected before model loading.
* All model endpoints are loopback-only. Output examples are inserted as text in
  the website. Secrets and large caches are excluded from Git.
* Reporting derives metrics from saved records and labels missing experiments as
  pending. The paper carries the requested authorship and AI statement.

Outstanding model-backed checks: installed GPU imports, Unsloth/TRL integration,
judge schema behavior, calibration, maximum-length GRPO memory, optimizer/RNG
resumption and end-to-end model outputs. UI inspection was unavailable because the
in-app backend was absent and the available Windows browser was stopped by
URL-policy enforcement. HTTP endpoints can still be checked without browser use.

No claim of a fully validated training run is made at this stage. Any integration
fix will be published before the next model stage; substantive protocol changes
need dated amendments.

## Exploratory single-call continuation

2026-11-16. One additional pass reviewed the explicitly authorized qualification
exception, single-call identity, recovery, evaluation isolation and reporting.
The original training/audit gates remain present. The new flag requires a distinct
run prefix; input hashes freeze models, selection, manifests and settings across
arms. The prompt and reward semantics reuse the latest single-call instrument.
Context preflight has a separate identity, with no extra semantic judgment.

Regression checks cover the unchanged standard gate, explicit exploratory
selection, frozen identities/settings, one accepted call and cache isolation,
generation recovery, transfer separation, and preventing a complete exploratory
comparison from becoming confirmatory. Full results are in
[`verification-exploratory-single.xml`](verification-exploratory-single.xml).
Python lint, JavaScript syntax and dashboard metric tests also passed. The new
model-backed pilot remains required before long training; offline tests are not
evidence that noisy reward improves behavior. UI browser inspection remains
unverified for the previously documented environmental restriction.
