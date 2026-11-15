# Decomposed judge implementation before inference

The [amendment](../amendments/2026-11-15-decomposed-judges.md) addresses the
reference-comparison and semantic-attribution failures retained in the
[previous trial](qwen-v7-reference-scope-learnings.md). It registers a two-call
instrument and a specialist fallback, with unchanged acceptance thresholds and
the user's modest-credit rule.

The implementation separates typed findings, deterministic aggregation, transport,
and caching. Tests first failed on the absent stage module and absent pipeline
interface, then passed after implementation. A synthetic context-test fixture
initially miscalculated its passing boundary; the test expectation was corrected,
without changing the context check. The existing framing test required the old
rubric's literal weight notation and was updated to check the active wording.
Historical v7 service-contract tests explicitly select the preserved legacy path.
These are implementation checks, not mathematical performance evidence.

The full test result is [machine-readable](../verification-decomposed-judge.xml).
After final injection-handling/reporting additions, relevant focused tests passed
in [a separate record](../verification-decomposed-final.xml). Ruff, JavaScript
tests/syntax checks and Git whitespace checks passed. The regenerated paper was
rendered and every page visually inspected. The dashboard HTTP endpoint exposes
the selected protocol and stage progress; browser-based visual validation remains
unavailable and is not claimed.

The [integrity artifact](../development/judge-decomposed-protocol-integrity.json)
records both protocols' identities, ordered schemas, prompt hashes, budgets and
aggregation implementation hashes. Development/audit case hashes and reference
hash match the prior protocol. The [capacity artifact](../development/judge-decomposed-context.json)
records non-inference checks using the served Qwen template and tokenizer.
Synthetic inputs fit, but do not establish capacity for every real candidate,
retry or Gemma template. Every actual stage checks its exact input before inference.

The code and amendment were merged in
[PR 36](https://github.com/BurnyCoder/grothendieck-reinforcement-learning-with-llm-as-a-judge-reward-in-grpo-rlvr/pull/36),
uploaded to [Hugging Face](https://huggingface.co/datasets/BurnyCoder/grothendieck-rlvr/commit/ea1b2297d10d0b19b75b504f630e1d8cce3f6591),
and successfully deployed to Pages before the first mathematical request.
Publication receipts are retained in `reports/publication.json`.
Development calibration then started under the published two-call identity.
Its subsequent outcomes belong in a separate empirical report; no qualification
or comparative policy improvement follows from these software checks.

A later reporting-only clarification labels novelty before validity/eligibility
gates as "pre-gate novelty": legacy instruments supplied a model score, whereas
the decomposed instruments derive a level from stage findings. The stored values
and acceptance decisions are unchanged. Existing reporting regression tests
passed in [their saved record](../verification-decomposed-reporting.xml).
