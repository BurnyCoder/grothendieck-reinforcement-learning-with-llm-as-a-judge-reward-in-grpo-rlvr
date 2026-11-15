# Development amendment: judge synchronization and request deadlines

Date: 2026-11-15. Comparative training and locked audits have not started.

The resumed Gemma v4 development calibration initially completed structured
judgments, then slowed severely within a later request. Preserve its entire
interrupted stream, completed judgments and progress under
`reports/development/gemma-cuda24-v4-resumed*`. The native
[stack sample](../development/gemma-v4-slow-stack.txt) shows inference workers
inside libgomp barriers. The corresponding register sample is preserved too.
This implicates synchronization as a useful diagnostic target; it does not
establish the root cause. Short synthetic thread/offload benchmarks did not
predict sustained server behavior.

Change only the evaluation server's OpenMP waiting policy to
`OMP_WAIT_POLICY=PASSIVE`, `GOMP_SPINCOUNT=0`. Keep its model, quantization,
thread count, GPU offload, context and prompt fixed. GNU
[libgomp documents these controls](https://gcc.gnu.org/onlinedocs/libgomp/GOMP_005fSPINCOUNT.html)
as selecting passive rather than busy waiting. Related upstream
[OpenMP observations](https://github.com/ggml-org/llama.cpp/issues/31516)
motivate measurement but concern different hardware and do not establish a fix
here. The training server retains library defaults. Explicit configuration
overrides inherited wait settings, and the setting becomes part of judge identity.

The existing HTTPX timeout limits waiting for each chunk, so a continuously
dripping response can run indefinitely. Use an enclosing
[asyncio deadline](https://docs.python.org/3.12/library/asyncio-task.html#asyncio.timeout)
and cancel/close the stream after the configured total request budget. See
[HTTPX's timeout definitions](https://www.python-httpx.org/advanced/timeouts/).
Log partial chunks and the timeout, then apply the existing bounded retry policy.
A timeout never produces a judgment or reward. Bind this transport protocol
and its budget into cache and calibration identity.

Publish this amendment and regression tests before new inference. Restart
development calibration under the new identity; do not pool old and new
assessments. Retain the same cases, reference anchors, rubric and thresholds.
In particular, retain the disagreement over the conventional polynomial
control's commutator boundary statement. Its validity does not settle whether
it deserves novelty credit; changing that case after seeing the score would
change the constructed test. No such change is made.

Use the full development workload as the sustained serving check. A completed
suite without transport failure is operational evidence only. Failure to
complete within the request budgets, invalid outputs after retries, or failure
of the fixed calibration thresholds blocks the locked audit and long training.
Do not select a runtime on locked test performance or count development
preference ordering as independent mathematical improvement.
