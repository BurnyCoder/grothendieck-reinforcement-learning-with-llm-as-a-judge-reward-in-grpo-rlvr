# Deferred larger-model configuration

These are byte-preserving copies of the active configuration at Git revision
`e83d41a1502ce41176749c8a37e5cfa597662da8`, before the user requested a smaller
Qwen3.5 GPU experiment on 2026-11-16. That revision contains the matching code,
dependency lock and documentation. Use that revision and its original artifact
paths to resume the deferred experiment; do not combine these configs with new
model identities or restore pilot adapters as comparative initialization.

The original `models/policy`, `models/training_judge`, `models/evaluation_judge`,
run directories, cache entries and saved responses remain on the project artifact
drive. [The postponement record](../../../reports/development/exploratory-single-v2-postponed.json)
records the stop requested by the user. This is a scheduling change, not a negative
finding about training effectiveness or an out-of-memory failure.
