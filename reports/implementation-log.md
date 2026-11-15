# Implementation observations

## 2026-11-15: dependency resolution and provenance

Initial unconstrained resolution selected an old Unsloth release while maximizing
newer Torch/TRL/Transformers. This was caught by inspecting `uv.lock` before
installation completed or any model ran. The old package does not establish
Qwen3.5 support. The installer was interrupted; the project now requires the
current released Unsloth and honors its published compatibility ceilings.
Evidence: [Unsloth release metadata](https://pypi.org/pypi/unsloth/2026.11.4/json)
and [official package specification](https://github.com/unslothai/unsloth/blob/main/pyproject.toml).
The final exact environment is recorded in `uv.lock`; latest compatible means
compatible with this training implementation, not independently maximizing each
package version. This is an implementation issue, not a model feasibility result.

The llama.cpp release API's `target_commitish` differed from the commit actually
referenced by the release tag. The model/runtime lock records the checked-out
tag commit, verified by the built executable. The local CPU server compiled
successfully. No inference measurement is implied by a successful build.

Generator-source observations and corrected rounding instructions are documented
in the state-of-the-art review. No policy outputs informed these decisions.
