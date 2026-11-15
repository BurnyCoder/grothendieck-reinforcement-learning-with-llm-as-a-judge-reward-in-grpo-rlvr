#!/usr/bin/env bash
# Official binaries use the same source commit as the CPU build; verify both archives.
# Release: https://github.com/ggml-org/llama.cpp/releases/tag/b12359
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/environment.sh
destination="${GROTH_ROOT:-/mnt/d/AI/grothendieck-rlvr}/tools/llama-b12359-cuda12"
mkdir -p "$destination/bin"
base=https://github.com/ggml-org/llama.cpp/releases/download/b12359
curl -fL --retry 3 -C - -o "$destination/llama.tar.gz" "$base/llama-b12359-bin-ubuntu-cuda-12.8-x64.tar.gz"
curl -fL --retry 3 -C - -o "$destination/cudart.tar.gz" "$base/cudart-llama-b12359-bin-ubuntu-cuda-12.8-x64.tar.gz"
"${UV_PROJECT_ENVIRONMENT:-.venv}/bin/python" - "$destination" <<'PY'
import hashlib
import json
import sys
from pathlib import Path
lock = json.loads(Path("configs/llama-binaries.lock.json").read_text())
for asset, filename in zip(lock["assets"], ("llama.tar.gz", "cudart.tar.gz"), strict=True):
    with (Path(sys.argv[1]) / filename).open("rb") as handle:
        actual = hashlib.file_digest(handle, "sha256").hexdigest()
    if actual != asset["sha256"]:
        raise SystemExit(f"Archive checksum mismatch: {filename}")
PY
tar -xzf "$destination/llama.tar.gz" --strip-components=1 -C "$destination/bin"
tar -xzf "$destination/cudart.tar.gz" --strip-components=1 -C "$destination/bin"
"$destination/bin/llama-server" --version
