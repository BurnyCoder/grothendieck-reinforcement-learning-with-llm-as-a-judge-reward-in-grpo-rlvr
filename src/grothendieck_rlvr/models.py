"""Pinned local model artifacts and loopback llama.cpp serving; no remote inference."""
import hashlib
import importlib.metadata
import os
import platform
import subprocess
from pathlib import Path

from .io import PROJECT, atomic_json, read_json, root


def model_directory(role: str) -> Path:
    """Keep each frozen experiment's downloads separate from postponed model artifacts."""
    spec = read_json(PROJECT / "configs/models.lock.json")[role]
    base = root() / "models"
    directory = base / spec.get("artifact_subdir", role)
    if not directory.resolve().is_relative_to(base.resolve()):
        raise ValueError("Configured model directory escapes the project artifact store")
    return directory


def require_cuda_policy(model) -> None:
    """Reject CPU/disk placement for the experiment requiring all policy weights on GPU.

    https://pytorch.org/docs/stable/tensor_attributes.html#torch.device
    """
    devices = {parameter.device.type for parameter in model.parameters()}
    if devices != {"cuda"}:
        raise RuntimeError(f"Policy requires all parameter tensors on CUDA; observed {sorted(devices)}")


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
        directory = model_directory(name)
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
        directory = model_directory(role)
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


def judge_runtime(role: str) -> dict:
    """Freeze numerically relevant serving settings alongside the prompt and weights."""
    runtime = read_json(PROJECT / "configs/judge-runtime.json")[role]
    if runtime.get("require_full_gpu") and (runtime["backend"] == "cpu" or
                                           runtime["gpu_layers"] != 999 or runtime["fit"] != "off"):
        raise ValueError("The registered full GPU judge cannot reduce layers or silently fit to CPU")
    if runtime["backend"] == "cpu" and runtime["gpu_layers"] != 0:
        raise ValueError("CPU runtime cannot request GPU layers")
    return runtime


def judge_environment(runtime: dict) -> dict:
    """Bind registered OpenMP controls before libgomp initializes; preserve other environment.

    https://gcc.gnu.org/onlinedocs/libgomp/GOMP_005fSPINCOUNT.html
    Null explicitly restores the library default instead of inheriting a shell override.
    """
    environment = os.environ.copy()
    for name, value in runtime.get("environment", {}).items():
        if value is None:
            environment.pop(name, None)
        else:
            environment[name] = value
    return environment


def serve(role="training_judge", gpu_layers=None):
    """A foreground server is easy to supervise and stop; aliases identify the role."""
    if role not in ("training_judge", "evaluation_judge"):
        raise ValueError("Only the frozen judge models use GGUF serving")
    runtime = judge_runtime(role)
    if gpu_layers is not None and gpu_layers != runtime["gpu_layers"]:
        raise ValueError("Offload differs from registered judge-runtime.json; amend and recalibrate first")
    spec = read_json(PROJECT / "configs/models.lock.json")[role]
    default = root() / "tools" / ("llama.cpp/build/bin/llama-server" if runtime["backend"] == "cpu"
                                   else "llama-b12359-cuda12/bin/llama-server")
    variable = "LLAMA_SERVER_CPU" if runtime["backend"] == "cpu" else "LLAMA_SERVER_CUDA"
    executable = Path(os.environ.get(variable, default))
    model = model_directory(role) / spec["file"]
    if not executable.exists() or not model.exists():
        raise FileNotFoundError("Build the pinned llama-server and download the frozen judge first")
    version = subprocess.run([str(executable), "--version"], capture_output=True, text=True, check=True)
    revision = read_json(PROJECT / "configs/models.lock.json")["llama_cpp"]["revision"]
    if revision[:7] not in version.stdout + version.stderr:
        raise RuntimeError("llama-server source revision differs from the lock")
    if runtime["backend"] != "cpu":
        devices = subprocess.run([str(executable), "--list-devices"], capture_output=True, text=True, check=True)
        if "CUDA0:" not in devices.stdout + devices.stderr:
            raise RuntimeError("Registered CUDA backend unavailable; refusing silent CPU fallback")
    port = 8081 if role == "training_judge" else 8082
    context = read_json(PROJECT / "configs/study.json")["judge_context_length"]
    args = [str(executable), "-m", str(model), "--alias", role, "--host", "127.0.0.1",
            "--port", str(port), "--ctx-size", str(context), "--parallel", "1",
            "--threads", str(runtime["threads"]), "--n-gpu-layers", str(runtime["gpu_layers"]),
            "--batch-size", str(runtime["batch_size"]), "--ubatch-size", str(runtime["ubatch_size"]),
            "--flash-attn", runtime["flash_attention"], "--cache-type-k", runtime["cache_type_k"],
            "--cache-type-v", runtime["cache_type_v"], "--fit", runtime["fit"], "--jinja"]
    if runtime.get("require_full_gpu"):
        # Explicit device/layers with fitting disabled fail on OOM instead of spilling layers.
        # https://github.com/ggml-org/llama.cpp/blob/b1b770d90d94cad9e9ea5b993bdbc383a522fb28/tools/server/README.md
        args += ["--device", "CUDA0"]
    # The receipt makes accidental use of a stale, differently configured server explicit.
    atomic_json(root() / "services" / f"{role}.json", {"model": spec, "runtime": runtime,
                "context_length": context, "command": args,
                "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest()})
    subprocess.run(args, check=True, env=judge_environment(runtime))
