"""Native thought tokens are bounded, identity-bound, and never parsed as scores."""
import json

import httpx
import pytest

from grothendieck_rlvr import judge as module
from grothendieck_rlvr.io import EventLog, read_jsonl


@pytest.mark.parametrize("budget", [0, 512])
def test_reasoning_request_and_visible_assessment_are_separate(tmp_path, monkeypatch, budget):
    """The existing JSON budget remains available after a bounded thought channel."""
    requests = []
    def respond(request):
        requests.append(json.loads(request.content))
        deltas = [{"reasoning_content": "A fixture thought, not a score."}, {"content": '{"fixture":true}'}]
        body = "".join('data: ' + json.dumps({"choices": [{"delta": delta}]}) + '\n\n'
                       for delta in deltas) + 'data: [DONE]\n\n'
        return httpx.Response(200, text=body)
    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: original(
        transport=httpx.MockTransport(respond), **kwargs))
    path = tmp_path / "events.jsonl"
    client = module.LocalChat("http://127.0.0.1:8082", "fixture", EventLog(path),
                              reasoning_budget_tokens=budget)
    assert client.generate([], max_tokens=1536, schema={"type": "object"}) == '{"fixture":true}'
    request = requests[0]
    assert request["max_tokens"] == 1536 + budget
    assert request["chat_template_kwargs"] == {"enable_thinking": bool(budget)}
    assert request["response_format"]["json_schema"]["strict"] is True
    if budget:
        assert request["reasoning_budget_tokens"] == budget
        assert request["reasoning_format"] == "deepseek"
    else:
        assert "reasoning_budget_tokens" not in request and "reasoning_format" not in request
    events = read_jsonl(path)
    assert events[1]["delta"]["reasoning_content"] == "A fixture thought, not a score."
    assert events[-1]["response"] == '{"fixture":true}'


def test_role_specific_reasoning_changes_only_affected_identity(tmp_path, monkeypatch):
    """A Gemma development intervention must not reuse old Gemma opinions or alter Qwen's run."""
    original_read = module.read_json
    budgets = {"training_judge": 0, "evaluation_judge": 0}
    def read(path):
        data = original_read(path)
        if path.name == "study.json":
            data["judge_reasoning_budget_tokens"] = budgets.copy()
        return data
    monkeypatch.setattr(module, "read_json", read)
    def judge(role):
        return module.Judge("http://127.0.0.1:8082", role=role,
                            log=EventLog(tmp_path / "events.jsonl"), cache=tmp_path / "cache.sqlite")
    before = {role: judge(role).identity for role in budgets}
    budgets["evaluation_judge"] = 512
    enabled_identity = judge("evaluation_judge").identity
    assert enabled_identity != before["evaluation_judge"]
    assert judge("training_judge").identity == before["training_judge"]
    budgets["evaluation_judge"] = 256
    assert judge("evaluation_judge").identity not in (before["evaluation_judge"], enabled_identity)


@pytest.mark.parametrize("budget", [-1, True, 1.5])
def test_unbounded_or_invalid_reasoning_configuration_fails_before_request(tmp_path, budget):
    with pytest.raises(ValueError, match="nonnegative integer"):
        module.LocalChat("http://127.0.0.1:8082", "fixture", EventLog(tmp_path / "events.jsonl"),
                         reasoning_budget_tokens=budget)
