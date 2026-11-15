# Development environment storage

Date: 2026-11-15. The first Qwen policy probe reached BF16 weight loading after
slow cold imports through the Windows-mounted virtual environment. Process
profiles showed filesystem waits during Torch/Transformers/xFormers imports.
The original console log and startup profile are retained in project artifacts.
This observation does not establish a clean causal timing comparison: concurrent
I/O and first-use bytecode compilation were present.

The CLI and setup scripts now honor uv's `UV_PROJECT_ENVIRONMENT` option. A
project-specific native WSL environment can use the exact existing lockfile and
the current source checkout. The default workspace `.venv` remains supported;
the original environment is preserved during validation. Models, large caches,
logs and checkpoints remain in the project's data-drive directory. No model,
prompt, reward, task split or training hyperparameter changes in this amendment.

The initial probe reports that xFormers cannot load and selects PyTorch attention.
This is recorded as an execution setting, not yet treated as a memory failure.
First measure the available supported path. Any dependency or kernel change
needed later must be locked and recorded before comparative experiments.

Sources: [Microsoft WSL filesystem recommendations](https://learn.microsoft.com/en-us/windows/wsl/filesystems)
and [uv project environment configuration](https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path).
