# Single-call judging with indexed source evidence

Date: 2026-11-16, Europe/Berlin. Written after the first exploratory pilot's
output-contract failure and before inference under this repair. This extends
the [authorized exploratory continuation](2026-11-16-exploratory-single-judge.md);
its hypotheses, comparisons, analysis, stopping rules and limitations still apply.

## Observed execution failure

The `exploratory-single-v1` pilot exhausted bounded retries on its first judged
solution because the judge altered mathematical typography in a purported exact
quotation. No optimizer boundary was completed. Preserve the
[failure artifact](../development/feasibility-exploratory-single-v1-failure.json),
[complete events](../development/exploratory-single-v1-pilot-failure.jsonl),
and [original profile](../../configs/exploratory-single-judge-v1.json).
Generated counts and timings appear in the development execution report.
This failure concerns the output contract, not evidence about learning or the
usefulness of the reward. Invalid assessments are not converted to zero reward.

## Repair and frozen identity

Use `single-indexed-v1` under a new `exploratory-single-v2-` run prefix. Each
correct response still receives one accepted assessment from one local frozen
judge, with the existing bounded contract/transport retries. No specialist,
repair model, synthesis model or semantic reranking is introduced.

Provide the complete candidate and conventional reference as ordered maps of
passage IDs to original text. Split at physical lines and further cut long lines
at 320 characters. This is a pragmatic citation granularity, not a claim that
each passage is a mathematical atomic proposition. Concatenating the map values
reconstructs the original source exactly, including whitespace and line endings.
The character limit prevents a single citation from implicitly selecting an
arbitrarily long explanation; no text is truncated or omitted.

The judge selects candidate IDs for criterion, addition and use evidence, and
a reference ID for reference comparison. The per-request JSON schema constrains
IDs to the correct source and excludes blank passages. Code resolves IDs to
their original text, then applies the unchanged exact-excerpt checks and scoring
gates. Unknown, blank or cross-source IDs fail explicitly. Selecting a real
passage does not establish relevance, correctness or entailment; those remain
potentially unreliable judge opinions.

Keep rubric v7's substantive instructions and score anchors verbatim, replacing
only its output-contract paragraph with the
[indexed contract](../../src/grothendieck_rlvr/prompts/indexed-evidence-v1.txt).
Keep quotations in the quoted variant and omit them in the rubric-only variant.
Preserve the six weights, modest connection credit, validity gate and
`R=C*(1+0.5*T)`. Models, quantizations, runtime, visible/reasoning token budgets,
task manifests and training settings do not change. Complete context preflight
still rejects oversized requests; it never silently shortens a solution.

The prompt, complete materialization implementation and citation contract enter
the new identity. Do not reuse old assessments, overwrite historical profiles,
or reclassify an old exploratory run as a qualified run. Cache materialized
assessments and retain raw ID outputs in the complete request/response logs.

## Execution and interpretation

Publish this amendment, tests, code and regenerated documents before new
inference. Restart the development save/resume pilot from the selected base;
the failed attempt has no checkpoint to resume. Archive each completed pilot
invocation before resumption overwrites its summary. Use only the new protocol's
intervals for its runtime scenarios. Discard pilot updates, publish the pilot,
then execute the already specified baselines, matched training and evaluations.

This remains an experiment with unqualified judges. It does not rerun or weaken
calibration, open an audit, alter a calibration label, or claim the repaired
instrument meets an accuracy threshold. Report any further execution failure
separately. Larger-judge comparisons remain future amended studies.

## Basis and limits

[RULERS](https://arxiv.org/html/2601.08654v1) motivates mechanically traceable
evidence and explicitly discusses the brittleness of deterministic extraction.
Its essay/summarization results do not validate mathematical judging here.
[Anthropic's citation documentation](https://platform.claude.com/docs/en/build-with-claude/citations#how-citations-work)
describes source-location references and extraction of original cited text.
We adopt that general representation idea with local JSON schemas and Python;
we do not use its service, models, SDK, native citation API or source code.
No third-party implementation is copied. This repair addresses copying failures,
not the false mathematical objections observed during calibration.
