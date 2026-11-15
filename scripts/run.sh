#!/usr/bin/env bash
# Load config before Python starts so PYTHONHASHSEED also affects interpreter hashing.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/environment.sh
export PYTHONHASHSEED=0
export PYTHONUNBUFFERED=1
exec "${UV_PROJECT_ENVIRONMENT:-.venv}/bin/python" -m grothendieck_rlvr.cli "$@"
