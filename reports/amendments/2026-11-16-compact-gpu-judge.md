# Bounded assessment fields and persistent streaming logs

Date: 2026-11-16, Europe/Berlin. Register this repair before inference under the
new identity. It responds to development execution failures, not held-out scores.

## Observation and scope

The initial small-GPU pilot exhausted its existing retries because the judge
repeated text until the output budget ended inside a JSON string. No assessment
was accepted and no optimizer boundary was saved. Preserve the
[raw events](../development/exploratory-small-gpu-v1-pilot-failure.jsonl),
[derived failure record](../development/feasibility-small-gpu-v1-truncation.json)
and [original profile](../../configs/history/exploratory-small-gpu-v1/).
The generated [failure report](../experiments/exploratory-small-gpu-v1-failure.md)
contains counts, timings and memory observations. This is an execution failure,
not evidence of learning or failed mathematical calibration.

The full-length backward probe and CUDA parameter check passed. The server
reported full layer offload; mapped input weights and host I/O buffers are not
claimed absent. Unsloth's existing gradient-checkpointing implementation may stage
intermediates in host memory; policy parameters and model computation remain on
CUDA. No CPU model-layer fallback or GPU OOM was observed in this attempt.

## Output contract

Use `single-compact-v1`, implemented by `compact_evidence.py`, under
`exploratory-small-gpu-v2`. Keep the original indexed evidence catalogs and exact
materialization. Impose the following output constraints in both the prompt and
server JSON schema: criterion rationales at most 240 characters; evidence lists
at most three IDs; at most eight problem descriptions, each at most 160 characters.
Validate bounds again in code. Do not truncate input, repair invalid JSON, shorten
returned opinions after generation or turn failures into zero rewards.

The [pinned llama.cpp grammar documentation](https://github.com/ggml-org/llama.cpp/blob/b1b770d90d94cad9e9ea5b993bdbc383a522fb28/grammars/README.md)
supports `maxLength` and `maxItems`. Inspect converted grammar offline before a
model run. These constraints prevent unrestricted repetition in a single field;
they do not guarantee semantic accuracy or completion within a token budget.
They can constrain explanatory detail, so the changed instrument has its own
cache, calibration and run identity rather than inheriting qualification.
The [offline converter check](../development/feasibility-compact-schema.json),
[input schema](../development/compact-wire-schema.json),
[converted grammar](../development/compact-wire-schema.gbnf) and
[helper source](../development/compact-schema-check.cpp) preserve that verification
without loading model weights.

Retain every scoring criterion, weight, anchor, validity gate, modest valid
connection credit, quotation, and the externally verified correctness gate.
Keep the existing request/context/reasoning budgets and bounded retries. An
essential unsupported claim or contradiction still removes the theory bonus.
No new calibration run or locked audit is opened; the user-authorized
uncalibrated exploratory interpretation and original 80%/90% gates remain intact.

## Logging and measurement

The client records every streamed chunk on the Windows-backed data drive. A
[synthetic disk diagnostic](../development/feasibility-logging-open-probe.json)
compared repeated append/open/close with one append handle and a flush per event.
It ran concurrently with the pilot, omits stdout, and is not an end-to-end model
speedup estimate. Use persistent append handles with immediate complete-record
flushes; preserve timestamps, complete stdout, all prompts/chunks/responses, and
propagated I/O failures. Serialization reopens handles rather than transporting
live descriptors. Record the logging protocol in the new experiment profile.

## Execution and falsification

Publish tested implementation, amendment, failure evidence and regenerated
documentation before restarting the pilot. The same frozen models, GPU placement,
LoRA settings, completion length, update budget, splits and analysis remain fixed.
The previous model/backward check remains applicable; repeat GRPO from the
unmodified base with the judge resident, save boundary one and resume to boundary
two. Archive both invocations and discard updates. Persistent contract errors,
CPU model fallback, OOM or incomplete recovery block comparative training until
another explicit repair. Do not keep rerolling the same failed protocol.

After successful recovery, publish feasibility and measured runtime, then resume
ordinary/prompted baselines and the registered training/evaluation sequence.
The larger-model, agentic-RL, Lean and quantitative-reward roadmap remains
postponed. No output-length reward penalty is introduced: these bounds constrain
the judge's report format, not policy rewards for explanation length.
