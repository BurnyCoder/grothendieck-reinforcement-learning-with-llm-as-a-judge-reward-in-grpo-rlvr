"""Streaming deadlines must bound a whole request, including a slow but active stream."""
import asyncio
import json
import time

import httpx
import pytest

from grothendieck_rlvr.io import EventLog, read_jsonl
from grothendieck_rlvr.judge import JudgeFailure, LocalChat


@pytest.mark.parametrize("drip", [True, False])
def test_total_deadline_closes_stream_and_preserves_partial_log(tmp_path, monkeypatch, drip):
    """Regular chunks must not reset the deadline; stalled reads must also cancel."""
    class SlowStream(httpx.AsyncByteStream):
        closed = False

        async def __aiter__(self):
            while True:
                await asyncio.sleep(.01 if drip else 10)
                yield b'data: {"choices":[{"delta":{"content":"partial"}}]}\n\n'

        async def aclose(self):
            self.closed = True

    stream = SlowStream()
    transport = httpx.MockTransport(lambda request: httpx.Response(200, stream=stream))
    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs))
    path = tmp_path / "events.jsonl"
    client = LocalChat("http://127.0.0.1:8082", "fixture", EventLog(path), timeout=.08)
    started = time.monotonic()
    with pytest.raises(JudgeFailure, match="total request deadline"):
        client.generate([])
    assert time.monotonic() - started < 2
    assert stream.closed
    events = read_jsonl(path)
    assert events[-1]["kind"] == "model_timeout"
    assert not any(e["kind"] == "model_response" for e in events)
    assert bool([e for e in events if e["kind"] == "model_chunk"]) == drip


def test_completed_stream_keeps_request_and_response_contract(tmp_path, monkeypatch):
    """An ordinary complete response preserves structured requests and exact text."""
    requests = []
    def respond(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, text='data: {"choices":[{"delta":{"content":"done"}}]}\n\ndata: [DONE]\n\n')
    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(
        transport=httpx.MockTransport(respond), **kwargs))
    path = tmp_path / "events.jsonl"
    client = LocalChat("http://127.0.0.1:8082", "fixture", EventLog(path), timeout=2)
    assert client.generate([{"role": "user", "content": "fixture"}], schema={"type": "object"}) == "done"
    assert requests[0]["response_format"]["json_schema"]["strict"] is True
    assert read_jsonl(path)[-1]["response"] == "done"
