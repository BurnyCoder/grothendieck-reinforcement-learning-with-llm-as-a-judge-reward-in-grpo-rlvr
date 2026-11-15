"""Context checks use the served template and fail before inference, including retries."""
import json

import httpx
import pytest

from grothendieck_rlvr.io import EventLog
from grothendieck_rlvr.judge import JudgeFailure, LocalChat


@pytest.mark.parametrize("context,passes", [(3048, True), (2048, False)])
def test_reserved_budget_cannot_silently_truncate_candidate(tmp_path, monkeypatch, context, passes):
    seen = []
    def respond(request):
        seen.append((request.url.path, json.loads(request.content)))
        if request.url.path == "/apply-template":
            return httpx.Response(200, json={"prompt": "formatted fixture"})
        if request.url.path == "/tokenize":
            return httpx.Response(200, json={"tokens": list(range(1000))})
        pytest.fail("Preflight must not perform inference")
    original = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kw: original(transport=httpx.MockTransport(respond), **kw))
    client = LocalChat("http://127.0.0.1:8081", "fixture", EventLog(tmp_path / "events.jsonl"),
                       context_length=context, check_context=True)
    request = {"messages": [{"role": "user", "content": "entire candidate"}], "max_tokens": 2048}
    if passes:
        client.validate_context(request)
    else:
        with pytest.raises(JudgeFailure, match="no truncation"):
            client.validate_context(request)
    assert seen[0][1]["messages"] == request["messages"]
    assert seen[1][1] == {"content": "formatted fixture", "add_special": True, "parse_special": True}
