#!/usr/bin/env bash
# Load config before Python starts so PYTHONHASHSEED also affects interpreter hashing.
set -euo pipefail
cd "$(dirname "$0")/.."
if test -f .env; then
  set -a
  source .env
  set +a
fi
export PYTHONHASHSEED=0
exec .venv/bin/python -m grothendieck_rlvr.cli "$@"
