#!/usr/bin/env bash
# Runtime setup follows uv and Unsloth's documented Python/GRPO installation route.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")/.."
export GROTH_ROOT="${GROTH_ROOT:-/mnt/d/AI/grothendieck-rlvr}"
export UV_CACHE_DIR="$GROTH_ROOT/uv-cache-linux"
export UV_LINK_MODE=copy
export HF_HOME="$GROTH_ROOT/huggingface"
mkdir -p "$GROTH_ROOT"
test -f .env || cp .env.example .env
uv sync --locked --python 3.12 --extra train
