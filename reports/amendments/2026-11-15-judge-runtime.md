# Development runtime provenance

Date: 2026-11-15. Development judging has begun; policy-generated evaluation and
training results do not yet exist. This amendment changes execution provenance,
not the mathematical rubric, reward, acceptance thresholds or locked tasks.

The first CPU Gemma invocation produced a structured assessment, then became
too slow to continue the current request productively. The incomplete invocation
was stopped; its complete response, partial streamed output and original lock
are retained. This is not a completed calibration or a passed gate. Host and WSL
memory checks did not show substantial swapping, so the slowdown is not being
classified as an out-of-memory failure. Concurrent file operations and startup
were present. Their causal contribution has not been isolated.

The original design permits evaluation GPU offload after policy generation.
The evaluation runtime now uses official CUDA binaries at the same pinned
llama.cpp commit, with initial partial offload and unchanged F16 KV storage.
The training judge remains on CPU. Exact settings live in
[`configs/judge-runtime.json`](../../configs/judge-runtime.json), and binary
archive checksums in
[`configs/llama-binaries.lock.json`](../../configs/llama-binaries.lock.json).
Successful loading and calibration are still required; these settings are not
a claim of feasibility. The maximum-length policy probe is run with Gemma stopped.

Backend, offload count, attention mode, cache types and batching are now included
in the judge identity. Runtime receipts prevent accidental reuse of an older
server launch; changed identities cannot reuse cached assessments or audit passes.
An explicit development restart archives previous locks/results. Locked audits
cannot be reset through that option. Any further runtime adjustment will be
recorded before the corresponding calibration, with prior evidence preserved.

The first assessment gave a small novelty score to a conventional divisibility
argument. This is a development observation worth checking against the dedicated
novelty contrasts, not evidence of reliable novelty measurement or systematic
failure. The rubric remains unchanged while this runtime issue is addressed.

Sources: [pinned llama.cpp release and binaries](https://github.com/ggml-org/llama.cpp/releases/tag/b12359),
[server settings](https://github.com/ggml-org/llama.cpp/tree/b1b770d90d94cad9e9ea5b993bdbc383a522fb28/tools/server),
and [WSL filesystem guidance](https://learn.microsoft.com/en-us/windows/wsl/filesystems).
