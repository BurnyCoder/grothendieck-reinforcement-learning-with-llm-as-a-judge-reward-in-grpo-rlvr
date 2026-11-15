"""Pinned local model artifacts and loopback llama.cpp serving; no remote inference."""
import hashlib
import importlib.metadata
import os
import platform
import subprocess
from pathlib import Path

from .io import PROJECT, atomic_json, read_json, root


def download(role="all") -> dict:
    """Download only pinned official/quantized Qwen and Gemma artifacts through the Hub API."""
    from huggingface_hub import hf_hub_download, snapshot_download
    lock = read_json(PROJECT / "configs/models.lock.json")
    roles = ["policy", "training_judge", "evaluation_judge"] if role == "all" else [role]
    results = {}
    for name in roles:
        if name not in ("policy", "training_judge", "evaluation_judge"):
            raise ValueError("Fallback requires a documented policy-selection amendment")
        spec = lock[name]
        directory = root() / "models" / name
        if "file" in spec:
            hf_hub_download(spec["repo"], spec["file"], revision=spec["revision"], local_dir=directory)
        else:
            snapshot_download(spec["repo"], revision=spec["revision"], local_dir=directory)
        results[name] = str(directory)
    return results


def artifact_hashes() -> dict:
    """Publish content hashes after downloads; no tensor is loaded or model executed."""
    hashes = {}
    for role in ("policy", "training_judge", "evaluation_judge"):
        directory = root() / "models" / role
        files = [p for p in directory.rglob("*") if p.is_file() and ".cache" not in p.parts]
        if not any(p.suffix in (".gguf", ".safetensors") for p in files):
            raise FileNotFoundError(f"Weights not downloaded for {role}")
        for path in files:
            sha = hashlib.sha256()
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(8*1024*1024), b""):
                    sha.update(chunk)
            hashes[str(path.relative_to(root() / "models"))] = {"sha256": sha.hexdigest(), "bytes": path.stat().st_size}
    atomic_json(PROJECT / "configs/artifacts.lock.json", hashes)
    return {"files_hashed": len(hashes)}


def doctor() -> dict:
    """Read runtime versions and hardware without running inference."""
    packages = {}
    for name in ("unsloth", "unsloth-zoo", "torch", "transformers", "trl", "reasoning-gym", "math-verify"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,memory.free,driver_version",
                          "--format=csv,noheader"], capture_output=True, text=True, check=True).stdout.strip()
    result = {"python": platform.python_version(), "platform": platform.platform(), "gpu": gpu,
              "packages": packages, "artifact_root": str(root())}
    atomic_json(PROJECT / "reports/environment.json", result)
    return result


def serve(role="training_judge", gpu_layers=0):
    """A foreground server is easy to supervise and stop; aliases identify the role."""
    if role not in ("training_judge", "evaluation_judge"):
        raise ValueError("Only the frozen judge models use GGUF serving")
    if role == "training_judge" and gpu_layers:
        raise ValueError("The registered training judge must remain on CPU")
    spec = read_json(PROJECT / "configs/models.lock.json")[role]
    executable = Path(os.environ.get("LLAMA_SERVER", root() / "tools/llama.cpp/build/bin/llama-server"))
    model = root() / "models" / role / spec["file"]
    if not executable.exists() or not model.exists():
        raise FileNotFoundError("Build the pinned llama-server and download the frozen judge first")
    port = 8081 if role == "training_judge" else 8082
    args = [str(executable), "-m", str(model), "--alias", role, "--host", "127.0.0.1",
            "--port", str(port), "--ctx-size", "8192", "--parallel", "1", "--threads", "8",
            "--n-gpu-layers", str(gpu_layers), "--jinja"]
    atomic_json(root() / "services" / f"{role}.json", {"model": spec, "command": args})
    subprocess.run(args, check=True)
