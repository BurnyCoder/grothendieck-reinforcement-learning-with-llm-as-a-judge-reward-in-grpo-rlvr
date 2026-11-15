"""The diagnostic launcher must preserve successful and timed-out synthetic runs."""
import subprocess

import pytest

from grothendieck_rlvr import benchmark
from grothendieck_rlvr.io import read_json, read_jsonl


@pytest.mark.parametrize("timeout", [False, True])
@pytest.mark.parametrize("sweep", ["threads", "offload"])
def test_benchmark_records_completion_or_timeout(tmp_path, monkeypatch, timeout, sweep):
    """Exercise launch/logging end to end with a fake binary, never a real model."""
    monkeypatch.setenv("GROTH_ROOT", str(tmp_path))
    executable = tmp_path / "tools/llama-b12359-cuda12/bin/llama-bench"
    executable.parent.mkdir(parents=True)
    executable.write_bytes(b"fixture binary")
    def unavailable(*args, **kwargs):
        raise ConnectionRefusedError
    monkeypatch.setattr(benchmark.socket, "create_connection", unavailable)
    revision = read_json(benchmark.PROJECT / "configs/models.lock.json")["llama_cpp"]["revision"]
    def run(command, **kwargs):
        if "--version" in command:
            return subprocess.CompletedProcess(command, 0, stdout=revision, stderr="")
        if sweep == "offload":
            assert command[command.index("-ngl") + 1] == "24,32,40"
            assert command[command.index("-d") + 1] == "8176"
            assert command[command.index("-t") + 1] == "8"
        if timeout:
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])
        kwargs["stdout"].write(b'{"n_threads":1,"avg_ts":1.0}\n')
        return subprocess.CompletedProcess(command, 0)
    monkeypatch.setattr(benchmark.subprocess, "run", run)
    result = benchmark.benchmark_judge(sweep=sweep)
    assert result["timed_out"] is timeout
    assert result["timings"] == ([] if timeout else [{"n_threads": 1, "avg_ts": 1.0}])
    folder = next((tmp_path / "benchmarks").iterdir())
    assert read_json(folder / "result.json") == result
    assert [r["kind"] for r in read_jsonl(folder / "events.jsonl")] == ["benchmark_started", "benchmark_finished"]
