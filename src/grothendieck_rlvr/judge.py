"""Frozen local llama.cpp judgment with constrained JSON and content-addressed caching.

Server API: https://github.com/ggml-org/llama.cpp/tree/master/tools/server
SQLite durability: https://docs.python.org/3/library/sqlite3.html
"""
import json
import sqlite3
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx

from .io import PROJECT, EventLog, digest, read_json, root
from .prompts import judge_system
from .schema import Assessment, Task


class JudgeFailure(RuntimeError):
    """A transport/schema/evidence error invalidates a rollout instead of reducing reward."""


def local_url(url: str) -> str:
    """All inference is loopback-only; redirects remain disabled in httpx."""
    parsed = urlparse(url)
    if parsed.scheme != "http" or parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
        raise ValueError("Only local loopback HTTP model endpoints are permitted")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("No credentials, query or fragment may appear in a local model URL")
    return url.rstrip("/")


def assessment_schema() -> dict:
    """Constrain the dictionary to exactly the declared rubric keys for llama.cpp."""
    schema = Assessment.model_json_schema()
    schema["properties"]["criteria"] = {
        "type": "object", "properties": {k: {"$ref": "#/$defs/Criterion"} for k in Assessment.weights},
        "required": list(Assessment.weights), "additionalProperties": False,
    }
    return schema


class LocalChat:
    """Minimal streaming client; full prompts, chunks and responses are timestamped."""
    def __init__(self, url: str, model: str, log: EventLog, timeout=900):
        self.url, self.model, self.log, self.timeout = local_url(url), model, log, timeout

    def generate(self, messages: list[dict], max_tokens=1024, schema=None, seed=42) -> str:
        """Preserve raw streamed text; malformed responses are handled by the caller."""
        request = {"model": self.model, "messages": messages, "temperature": 0,
                   "max_tokens": max_tokens, "seed": seed, "stream": True,
                   "chat_template_kwargs": {"enable_thinking": False}}
        if schema:
            request["response_format"] = {"type": "json_schema", "json_schema": {
                "name": "assessment", "strict": True, "schema": schema}}
        self.log.emit("model_request", model=self.model, request=request)
        pieces = []
        start = time.monotonic()
        with httpx.Client(timeout=self.timeout, trust_env=False) as client:
            with client.stream("POST", self.url + "/v1/chat/completions", json=request) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line.startswith("data: ") or line == "data: [DONE]":
                        continue
                    chunk = json.loads(line[6:])
                    for choice in chunk.get("choices", []):
                        delta = choice.get("delta", {})
                        if delta:
                            self.log.emit("model_chunk", model=self.model, delta=delta)
                        pieces.append(delta.get("content") or "")
        text = "".join(pieces)
        self.log.emit("model_response", model=self.model, response=text, seconds=time.monotonic()-start)
        if not text:
            raise JudgeFailure("Local server returned no visible content")
        return text


class Judge:
    """Cached exact-model assessments, with bounded retries and no silent defaults."""
    def __init__(self, url: str, role="training_judge", variant="quoted", log=None, cache: Path | None=None):
        self.spec = read_json(PROJECT / "configs/models.lock.json")[role]
        self.config = read_json(PROJECT / "configs/study.json")
        self.system = judge_system(variant)
        self.role, self.variant = role, variant
        self.log = log or EventLog(root() / "logs" / f"{role}-{variant}.jsonl")
        self.client = LocalChat(url, role, self.log, self.config["judge_timeout_seconds"])
        cache = cache or root() / "judge-cache.sqlite"
        cache.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(cache)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("CREATE TABLE IF NOT EXISTS assessments (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self.identity = digest({"model": self.spec, "system": self.system,
                                "schema": assessment_schema(), "max_tokens": self.config["judge_max_tokens"],
                                "temperature": 0, "seed": 42, "thinking": False})

    def assess(self, task: Task, response: str) -> Assessment:
        """The correctness gate is externally established before this method is called."""
        key = digest([self.identity, task.model_dump(), response])
        cached = self.db.execute("SELECT value FROM assessments WHERE key=?", (key,)).fetchone()
        if cached:
            assessment = Assessment.model_validate_json(cached[0])
            assessment.validate_evidence(response)
            self.log.emit("judge_cache_hit", key=key, task_id=task.id)
            return assessment
        payload = json.dumps({"problem": task.problem, "reference_answer": task.answer,
                              "external_final_answer_verdict": "correct", "candidate_response": response},
                             ensure_ascii=False)
        messages = [{"role": "system", "content": self.system}, {"role": "user", "content": payload}]
        for attempt in range(3):
            try:
                output = self.client.generate(messages, self.config["judge_max_tokens"], assessment_schema())
                assessment = Assessment.model_validate_json(output)
                assessment.validate_evidence(response)
                self.db.execute("INSERT OR REPLACE INTO assessments VALUES (?, ?)",
                                (key, assessment.model_dump_json()))
                self.db.commit()
                self.log.emit("judge_assessment", key=key, task_id=task.id,
                              assessment=assessment.model_dump(), theory=assessment.quality)
                return assessment
            except (httpx.HTTPError, ValueError, JudgeFailure) as exc:
                self.log.emit("judge_failure", attempt=attempt + 1, task_id=task.id, error=str(exc))
                if attempt == 2:
                    raise JudgeFailure(f"Judge failed after three attempts: {exc}") from exc
        raise AssertionError("Unreachable retry state")

    def checkpoint(self, destination: Path) -> None:
        """SQLite online backup gives a consistent cache snapshot alongside trainer state."""
        with sqlite3.connect(destination) as snapshot:
            self.db.backup(snapshot)
