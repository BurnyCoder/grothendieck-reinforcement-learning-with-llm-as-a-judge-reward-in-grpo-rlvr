# Bounded native reasoning for development judging

Date: 2026-11-15. Development-informed amendment, published before inference
under the changed settings. No locked judge audit or comparative run has begun.

## Evidence motivating the change

Gemma's completed development attempt reached the fixed futility condition;
its [negative result and interpretation](../experiments/gemma-v4-learnings.md)
remain unchanged. Qwen's subsequent v4 attempt passed the observed novelty
contrasts but assigned `theory_validity: none` to conventional explanations that
explicitly state a general polynomial identity and a parameterized probability
law. It described these as offering no general framework. The polynomial
explanation also demonstrates another application and identifies commutativity
as a boundary. These judgments conflate conventionality with absence of theory,
contrary to the rubric. They are qualitative counterexamples, not a population
false-negative estimate.

The Qwen development run was interrupted after this diagnosis. Its
[full streamed events](../development/qwen-v4-interrupted.jsonl),
[progress](../development/qwen-v4-interrupted.progress.json),
[identity lock](../development/qwen-v4-interrupted.lock.json), and
[interruption traceback](../development/qwen-v4-interrupted.traceback.txt)
are retained. Its observed preference passes do not constitute a completed
calibration. It is neither relabeled as a threshold failure nor pooled with the
next attempt. Counts and accepted scores are generated in the development report.

## Hypothesis and fixed intervention

A bounded native reasoning phase may help the judges apply the distinction
between supported conventional theory and additional conceptual novelty.
This is a development hypothesis; success is not established. The
[inference review](../judge-inference-review.md) records supportive and contrary
evidence from other judging settings and its limits.

Enable native thinking for both frozen judges, with **512 reasoning tokens** and
**2,048 total generated tokens** per request. The existing 1,536-token assessment
allowance is augmented by the reasoning budget. The server may end reasoning
earlier; the total limit is a ceiling, not a fixed output length. Keep greedy
decoding, seed 42, the 8,192-token context, total 900-second deadline, runtime,
models, quantizations, v4 system prompt, references, schema and reward unchanged.
This is a test of a bounded inference configuration, not an isolated estimate of
the causal effect of reasoning length or a replication of a paper's sampling.

Use llama.cpp's `reasoning_budget_tokens` and `reasoning_format: deepseek` with
`enable_thinking: true`. The pinned
[server source](https://github.com/ggml-org/llama.cpp/blob/b1b770d90d94cad9e9ea5b993bdbc383a522fb28/tools/server/server-common.cpp)
passes the budget to the sampler and derives thought delimiters from the model
template. Both the thought channel and visible response remain fully logged;
only the visible JSON is parsed as an assessment. The inference settings enter
the cache/calibration identity. No old assessment can satisfy the changed gate.

The budget is a conservative engineering choice to limit added latency on this
machine. It is not an empirically optimal value. Enabling thinking, increasing
the total completion ceiling, or forced closure can change outputs and introduce
truncation or schema failures. Preserve these failures and stop after the
existing bounded retries; never fabricate a score or enlarge the budget during
an attempt. If the server does not honor the requested thought-channel contract,
treat that as an implementation failure rather than a mathematical verdict.

## Selection and stopping

Run the Qwen quoted development suite first. If it completes and passes, run
Gemma quoted and Qwen rubric-only development suites sequentially. Any failure
blocks long training and requires its own report before a further amendment.
Keep all calibration cases, labels, strata and acceptance thresholds fixed,
including the debatable polynomial-control novelty classification. Keep the
existing development futility rule; do not stop early as successful. Do not run
locked audits until every required development configuration passes. The locked
audits remain untouched and must subsequently pass in full.

Compare the new observations descriptively with preserved development evidence.
Do not use partial adaptive development attempts as a significance test. A pass
would validate only these constructed contract tests, not general mathematical
reliability, historical originality, or policy improvement. The comparative
initialization, training prompts, budget, locked evaluation problems and primary
analysis remain fixed. Distant mathematical bridges remain eligible for reward;
mere unfamiliarity does not substitute for valid, useful mathematical work.
The historical training-time scenarios used non-thinking v3 judgments. Refresh
development throughput before comparative training; the new reasoning overhead
is not included in those scenarios. Any subsequent matched-budget change requires
a further pre-comparison amendment, never an arm-specific adjustment after results.
