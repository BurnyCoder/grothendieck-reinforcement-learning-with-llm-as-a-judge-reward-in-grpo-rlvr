"""Bounded development-only inference diagnostics using upstream llama-bench.

https://github.com/ggml-org/llama.cpp/tree/b1b770d90d94cad9e9ea5b993bdbc383a522fb28/tools/llama-bench
These synthetic token timings never enter mathematical evaluation results.
"""
import hashlib
import socket
import subprocess
from datetime import datetime, timezone

from .io import PROJECT, EventLog, atomic_json, read_json, read_jsonl, root
from .models import judge_environment, model_directory


def benchmark_judge(sweep="threads") -> dict:
    """Vary one registered runtime factor; preserve partial output and bounded failures."""
    if sweep not in ("threads", "offload"):
        raise ValueError("Unknown registered benchmark sweep")
    for port in (8081, 8082):
        try:
            connection = socket.create_connection(("127.0.0.1", port), timeout=1)
        except ConnectionRefusedError:
            continue
        connection.close()
        raise RuntimeError("Stop local judges and policy generation before benchmarking")
    runtime = read_json(PROJECT / "configs/judge-runtime.json")["evaluation_judge"]
    model = read_json(PROJECT / "configs/models.lock.json")["evaluation_judge"]
    if runtime["backend"] != "cuda12.8":
        raise ValueError("This registered diagnostic targets the CUDA evaluation runtime")
    directory = root() / "benchmarks" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    directory.mkdir(parents=True)
    executable = root() / "tools/llama-b12359-cuda12/bin/llama-bench"
    revision = read_json(PROJECT / "configs/models.lock.json")["llama_cpp"]["revision"]
    version = subprocess.run([str(executable), "--version"], capture_output=True, text=True, check=True)
    if revision[:7] not in version.stdout + version.stderr:
        raise RuntimeError("Benchmark binary differs from the pinned source revision")
    with executable.open("rb") as handle:
        executable_hash = hashlib.file_digest(handle, "sha256").hexdigest()
    threads = [1, 4, 8] if sweep == "threads" else [8]
    gpu_layers = [runtime["gpu_layers"]] if sweep == "threads" else [24, 32, 40]
    depth = 2048 if sweep == "threads" else 8176
    command = ["stdbuf", "-oL", "-eL", str(executable), "-m", str(model_directory("evaluation_judge") / model["file"]),
               "-p", "0", "-n", "16", "-d", str(depth), "-r", "2",
               "-t", ",".join(map(str, threads)), "-ngl", ",".join(map(str, gpu_layers)),
               "-o", "jsonl", "--progress"]
    for flag, key in (("-b", "batch_size"), ("-ub", "ubatch_size"),
                      ("-fa", "flash_attention"), ("-ctk", "cache_type_k"), ("-ctv", "cache_type_v")):
        command += [flag, str(runtime[key])]
    log = EventLog(directory / "events.jsonl")
    environment = judge_environment(runtime)
    config = {"kind": "synthetic_judge_runtime_benchmark", "sweep": sweep, "model": model, "runtime": runtime,
              "source_revision": revision, "executable_sha256": executable_hash,
              "command": command, "timeout_seconds": 900, "threads": threads,
              "gpu_layers": gpu_layers, "depth": depth,
              "environment": {k: environment.get(k) for k in ("OMP_NUM_THREADS", "OMP_WAIT_POLICY", "GOMP_SPINCOUNT")}}
    atomic_json(directory / "config.json", config)
    log.emit("benchmark_started", configuration=config)
    with (directory / "timings.jsonl").open("wb") as output, (directory / "stderr.log").open("wb") as errors:
        try:
            completed = subprocess.run(command, stdout=output, stderr=errors, timeout=900, check=False,
                                       env=environment)
            status = {"exit_code": completed.returncode, "timed_out": False}
        except subprocess.TimeoutExpired:
            status = {"exit_code": None, "timed_out": True}
    result = {**config, **status, "timings": read_jsonl(directory / "timings.jsonl"), "artifact": str(directory)}
    atomic_json(directory / "result.json", result)
    log.emit("benchmark_finished", **status, artifact=str(directory))
    return result
