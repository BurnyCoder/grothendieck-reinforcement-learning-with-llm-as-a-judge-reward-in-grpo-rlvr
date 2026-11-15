# Decomposed judge development and registered specialist fallback

Date: 2026-11-15. Registered after the failed v7/reference-v3 development trial,
before either protocol in this amendment performs mathematical inference.
Authority: the user's approved two-call judge and eight-specialist fallback plan.

## Question and falsification

Can separating conceptual comparison from overall scoring repair the observed
brief-connection and dependency-attribution failures, while preserving false-theory
suppression? Exact excerpts alone did not settle whether the cited mathematics
actually applied an added connection. Prior failures remain archived and unchanged.

The hypothesis is supported for operational qualification only if all three
required configurations pass complete development and locked audit suites. A
threshold failure falsifies qualification of that instrument on the constructed
suite. It does not falsify the untested training hypothesis or establish human
preference alignment. Errors between roles using the same weights can correlate.

The fixed acceptance contract remains at least 80% preference ordering and at
least 90% false-theory suppression **in each stratum**, with the existing strict
novelty ordering and modest-versus-zero control-credit conditions. Development
cases, labels, order, reference v3, audit cases, six weights, model revisions,
runtime settings and policy/evaluation manifests are unchanged. No expected
calibration answer or label enters any judge request. No earlier outcome is rescored.

## Registered instruments

`two-stage-v1` uses rubric v8 and two isolated conversations: `concepts` returns
reference comparison and development; `quality` returns overall validity and the
five non-novelty ratings. Neither sees the other's output. Each call has a visible
allowance of 1,536 tokens and a native reasoning budget of 512 tokens.

If any required development configuration fails its fixed threshold, activate
`specialists-v1`: validity; reference comparison; development/consequences; and one
call for each of the five non-novelty criteria. The development call alone receives
the reference call's proposed addition, explicitly untrusted and to be checked
against the original candidate. All roles receive the original candidate and
task context. They never receive a competing candidate, expected label or another
role's numerical score. The three analysis roles have 1,024 visible plus 512
reasoning tokens; criterion roles have 512 visible plus 256 reasoning tokens.

Both instruments reuse the selected frozen Qwen on CPU for training judgments
and Gemma for separate evaluation. Calls are sequential. Every quoted role
includes the same user-supplied Grothendieck passage; every rubric-only role omits
historical framing. The fallback is a different measurement identity and requires
fresh development results for all configurations, including previously passing ones.

## Deterministic scoring

The reference role identifies the concrete addition separately from the method
used to obtain the requested answer. An existing classical connection may lie
beyond the finite reference. Establishing that connection does not demonstrate
an application of it. The development role records the direction of dependence
and exact excerpts for operations, consequences, framework, original-problem
recovery and assumptions/boundaries.

Novelty is derived in code: 0 without a supported beyond-reference addition;
1 for a concrete valid addition without demonstrated use; 2 for a demonstrated
operation using it; 3 additionally requires substantial departure, a further
consequence and justified assumptions/boundaries; 4 additionally requires a
coherent reusable framework and recovery of the original problem. Missing higher
requirements retain the lower eligible level. A bare name receives no credit.
There is no unrestricted synthesis judge or vote over scores.

The overall validity verdict must be supported. Any substantive mathematical
issue reported by any stage vetoes the theory bonus: contradicted takes
precedence over unsupported. Absence of novelty/development and uncertainty about
the finite reference are not substantive mathematical issues. Reference uncertainty
removes only novelty. Code retains every raw stage opinion and its provenance;
the combined novelty score is derived, not an extra raw model rating.

The existing reward remains `C*(1+0.5*T)` with weights 20/20/15/15/10/20 percent.
Final-answer verification remains separate. Schema/evidence/context/transport
failures get bounded retries or terminate the rollout; they never become reward zero.

## Qualification, recovery and budget

Publish the tested implementation and this amendment to GitHub/Hugging Face before
inference. Run Qwen quoted development, Qwen rubric-only development, then Gemma
quoted development. Threshold failure ends that instrument's sequence; archive
its evidence, publish fallback activation and repeat all development under the
specialist identity. Ordinary service interruptions resume the same identity;
they do not count as a mathematical threshold failure. Repeated output-contract
failure must be reported as an implementation/instrument failure, not a pass.

Only complete matching passes of all three configurations authorize any locked
audit. All three full audits must pass before comparative training. Audits cannot
stop early or be reset. A failed audit is retained and retired; another instrument
requires a dated amendment and newly reserved audit cases. An unsuccessful
specialist development attempt is preserved; further repair needs a new amendment.

Stage prompts, ordered schemas, dependencies, budgets, aggregation implementation,
context policy and runtime enter the judge identity. Every successful stage is
committed to SQLite before proceeding and included in existing checkpoint backups.
On interruption, reuse matching stages and generate only missing ones. Context
checks use the served chat template/tokenizer and reserve the full output budget;
neither candidates nor retries are silently truncated. Raw streams and stage
timings are timestamped. Dashboard records describe the last event, not liveness.

After qualification, repeat a development-only checkpoint/resume timing pilot
under the selected instrument, discarding its updates. Keep the frozen base,
64-update arms, seeds, primary/OOD/transfer sizes and statistical analysis. Evaluate
ordinary/prompted baselines, then theory/correctness seed 42, matched seeds 43/44,
and shuffled/rubric seed 42 controls. Publish each training/evaluation milestone.
The old single-call timing estimate is obsolete. More calls may exceed the week;
report unfinished arms rather than weaken thresholds, shrink locked evaluation,
or extend sampling in response to significance.

## Source and limitations

[DnA-Eval](https://aclanthology.org/2025.coling-main.156/) motivates separate
assessment and external score aggregation. Its full paper and appendices were
reviewed. It uses pairwise aspect ratings and sometimes generated criteria/weights;
we retain fixed criteria, fixed weights and pointwise assessments. Its results
do not establish reliability of these quantized mathematical novelty judges.
No external code, prompts or datasets are copied. See the
[inference review](../judge-inference-review.md) for the scoped comparison.
