# Evaluation GPU offload diagnostic

Date: 2026-11-15, before the offload sweep. The first completed v4 development
novelty contrast favors the justified lattice construction over its conventional
counterpart, but judgments remain slow. This is partial development evidence,
not a calibration pass. No locked audit or comparative result exists.

The earlier thread sweep retained the fastest observed thread count. The next
runtime question is whether moving more evaluation-judge layers onto the GPU
reduces CPU decoding cost while the policy is unloaded. The GGUF metadata records
a model with 48 transformer blocks. Numerical output may change with offload;
any selected setting requires a new identity and fresh development calibration
before the untouched locked audit. The training judge stays on CPU.

Run the pinned upstream [llama-bench](https://github.com/ggml-org/llama.cpp/tree/b1b770d90d94cad9e9ea5b993bdbc383a522fb28/tools/llama-bench)
with GPU layer counts **24, 32, 40**, eight CPU threads and two repetitions each.
Use a synthetic prefix of **8176** tokens followed by **16** timed decoding
steps, allocating the registered **8192**-token context. Keep the model,
quantization, CUDA binary, batch/microbatch sizes and F16 KV types fixed. Stop
policy and judge processes first. Retain standard output, errors, command,
environment settings and partial results. Cap the complete sweep at **900 seconds**.
Out-of-memory or timeout outcomes are feasibility failures, never model scores.

Prefer the fastest successfully completed setting, then confirm that the
registered server loads at the full context and completes structured development
judgments. If that confirmation fails, retain the failure and use the next
successful candidate; do not silently reduce context or change quantization.
The sweep is a runtime diagnostic, not an optimization against mathematical
test answers. It does not establish a stable end-to-end throughput guarantee.

Command: `bash scripts/run.sh benchmark-judge --sweep offload`.
Publish the chosen serving configuration and evidence before recalibration.
Retain the previous partial judgments and their runtime identity.
