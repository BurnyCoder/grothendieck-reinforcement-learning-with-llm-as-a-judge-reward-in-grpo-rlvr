"""Frozen local llama.cpp judgment with constrained JSON and content-addressed caching.

Server API: https://github.com/ggml-org/llama.cpp/tree/master/tools/server
SQLite durability: https://docs.python.org/3/library/sqlite3.html
"""
import asyncio
import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx

from .io import PROJECT, EventLog, atomic_json, digest, read_json, root
from . import models
from .prompts import judge_system
from .schema import Assessment, Criterion, NoveltyComparison, Task
from .judge_stages import aggregate, stage_specs, validate_stage


RETRY_PROTOCOL = {"version": "validation-feedback-v1", "max_attempts": 3,
                  "error_character_limit": 2000, "feedback_history": "latest_invalid_assessment_only"}
TRANSPORT_PROTOCOL = "stream-total-deadline-v1"
ASSESSMENT_PROTOCOL = "tiered-novelty-eligibility-v2"


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
    def __init__(self, url: str, model: str, log: EventLog, timeout=900, runtime=None,
                 model_spec=None, context_length=None, reasoning_budget_tokens=0, check_context=False):
        if type(reasoning_budget_tokens) is not int or reasoning_budget_tokens < 0:
            raise ValueError("Reasoning budget must be a nonnegative integer; zero disables thinking")
        self.url, self.model, self.log, self.timeout = local_url(url), model, log, timeout
        self.runtime = runtime
        self.model_spec, self.context_length = model_spec, context_length
        self.reasoning_budget_tokens = reasoning_budget_tokens
        self.check_context = check_context

    def validate_context(self, request: dict) -> None:
        """Use the served template/tokenizer; reserve the complete generation budget.

        These endpoints do not run inference. The pinned API is documented at
        https://github.com/ggml-org/llama.cpp/tree/master/tools/server#api-endpoints.
        """
        with httpx.Client(timeout=min(self.timeout, 30), trust_env=False) as client:
            formatted = client.post(self.url + "/apply-template", json=request)
            formatted.raise_for_status()
            prompt = formatted.json()["prompt"]
            tokenized = client.post(self.url + "/tokenize", json={
                "content": prompt, "add_special": True, "parse_special": True})
            tokenized.raise_for_status()
            tokens = len(tokenized.json()["tokens"])
        required = tokens + request["max_tokens"]
        self.log.emit("judge_context_check", model=self.model, prompt_tokens=tokens,
                      completion_budget=request["max_tokens"], context_length=self.context_length)
        if not self.context_length or required > self.context_length:
            raise JudgeFailure(f"Judge context requires {required} tokens; limit is {self.context_length}; no truncation")

    def reasoning_options(self) -> dict:
        """Use the pinned server's native budget and separate thought-channel parser.

        https://github.com/ggml-org/llama.cpp/blob/b1b770d90d94cad9e9ea5b993bdbc383a522fb28/tools/server/server-common.cpp
        reads reasoning_budget_tokens and obtains the model's end tags from its template.
        With thinking disabled, retain the original request and identity byte-for-byte.
        """
        return ({"reasoning_budget_tokens": self.reasoning_budget_tokens, "reasoning_format": "deepseek"}
                if self.reasoning_budget_tokens else {})

    def generate(self, messages: list[dict], max_tokens=1024, schema=None, seed=42) -> str:
        """Preserve raw streamed text; malformed responses are handled by the caller."""
        if self.runtime is not None:
            receipt = root() / "services" / f"{self.model}.json"
            actual = read_json(receipt) if receipt.exists() else {}
            expected = {"runtime": self.runtime, "model": self.model_spec, "context_length": self.context_length}
            if any(actual.get(k) != v for k, v in expected.items() if v is not None):
                raise JudgeFailure("Server runtime differs from judge identity; restart with the registered CLI")
        request = {"model": self.model, "messages": messages, "temperature": 0,
                   "max_tokens": max_tokens + self.reasoning_budget_tokens, "seed": seed, "stream": True,
                   "chat_template_kwargs": {"enable_thinking": bool(self.reasoning_budget_tokens)},
                   **self.reasoning_options()}
        if schema:
            request["response_format"] = {"type": "json_schema", "json_schema": {
                "name": "assessment", "strict": True, "schema": schema}}
        if self.check_context:
            self.validate_context(request)
        self.log.emit("model_request", model=self.model, request=request)
        start = time.monotonic()
        try:
            text = asyncio.run(self._stream(request))
        except TimeoutError as exc:
            self.log.emit("model_timeout", model=self.model, seconds=time.monotonic()-start,
                          deadline_seconds=self.timeout)
            raise JudgeFailure(f"Local server exceeded total request deadline ({self.timeout}s)") from exc
        self.log.emit("model_response", model=self.model, response=text, seconds=time.monotonic()-start)
        if not text:
            raise JudgeFailure("Local server returned no visible content")
        return text

    async def _stream(self, request: dict) -> str:
        """Cancel and close slow streams, even when each chunk beats HTTPX's read timeout.

        https://www.python-httpx.org/advanced/timeouts/ describes per-chunk limits.
        https://docs.python.org/3.12/library/asyncio-task.html#asyncio.timeout
        supplies the enclosing wall-clock deadline, including connection and prefill.
        """
        pieces = []
        async with asyncio.timeout(self.timeout):
            async with httpx.AsyncClient(timeout=self.timeout, trust_env=False) as client:
                async with client.stream("POST", self.url + "/v1/chat/completions", json=request) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.startswith("data: ") or line == "data: [DONE]":
                            continue
                        chunk = json.loads(line[6:])
                        for choice in chunk.get("choices", []):
                            delta = choice.get("delta", {})
                            if delta:
                                self.log.emit("model_chunk", model=self.model, delta=delta)
                            pieces.append(delta.get("content") or "")
        return "".join(pieces)


class Judge:
    """Cached exact-model assessments, with bounded retries and no silent defaults."""
    def __init__(self, url: str, role="training_judge", variant="quoted", log=None, cache: Path | None=None,
                 protocol=None):
        self.spec = read_json(PROJECT / "configs/models.lock.json")[role]
        self.config = read_json(PROJECT / "configs/study.json")
        self.anchors = read_json(PROJECT / "configs/novelty-anchors.json")
        self.protocol = protocol or self.config.get("judge_protocol", "legacy")
        single = self.protocol in ("legacy", "single-v1")
        self.stages = [] if single else stage_specs(self.protocol, variant)
        self.system = judge_system(variant, version="v7" if single else "v8")
        self.role, self.variant = role, variant
        self.log = log or EventLog(root() / "logs" / f"{role}-{variant}.jsonl")
        runtime = models.judge_runtime(role)
        reasoning_budget = self.config.get("judge_reasoning_budget_tokens", {}).get(role, 0)
        self.client = LocalChat(url, role, self.log, self.config["judge_timeout_seconds"], runtime,
                                self.spec, self.config["judge_context_length"], reasoning_budget,
                                check_context=self.protocol == "single-v1")
        cache = cache or root() / "judge-cache.sqlite"
        cache.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(cache)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("CREATE TABLE IF NOT EXISTS assessments (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS judgment_stages (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS judgment_pipelines (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self.identity = digest({"model": self.spec,
                                "runtime": read_json(PROJECT / "configs/models.lock.json")["llama_cpp"],
                                "serving_settings": runtime,
                                "binary_release": read_json(PROJECT / "configs/llama-binaries.lock.json")
                                    if runtime["backend"] != "cpu" else None,
                                "novelty_anchors": self.anchors,
                                "rubric_weights": Assessment.weights,
                                "context_length": self.config["judge_context_length"], "system": self.system,
                                "schema": assessment_schema(),
                                "max_tokens": self.config["judge_max_tokens"] + reasoning_budget,
                                "criterion_field_order": list(Criterion.model_fields),
                                "assessment_field_order": list(Assessment.model_fields),
                                "comparison_field_order": list(NoveltyComparison.model_fields),
                                "assessment_protocol": ASSESSMENT_PROTOCOL,
                                "retry_protocol": RETRY_PROTOCOL,
                                "transport_protocol": TRANSPORT_PROTOCOL,
                                "request_deadline_seconds": self.config["judge_timeout_seconds"],
                                "temperature": 0, "seed": 42, "thinking": bool(reasoning_budget),
                                **self.client.reasoning_options()})
        if self.stages:
            self.identity = digest({"base": self.identity, "protocol": self.protocol,
                                    "stages": [s.manifest() for s in self.stages],
                                    "context_check": "served-template-tokenizer-reserve-full-generation-v1"})
        elif self.protocol == "single-v1":
            # Keep historical legacy scores intact; preflight behavior has its own identity.
            self.identity = digest({"base": self.identity, "protocol": self.protocol,
                                    "context_check": "served-template-tokenizer-reserve-full-generation-v1"})

    def assess(self, task: Task, response: str) -> Assessment:
        """The correctness gate is externally established before this method is called."""
        key = digest([self.identity, task.model_dump(), response])
        cached = self.db.execute("SELECT value FROM assessments WHERE key=?", (key,)).fetchone()
        if cached:
            assessment = Assessment.model_validate_json(cached[0])
            assessment.validate_evidence(response)
            assessment.validate_reference(self.anchors[task.family])
            self.log.emit("judge_cache_hit", key=key, task_id=task.id,
                          assessment=assessment.model_dump(), theory=assessment.quality,
                          novelty=assessment.novelty, novelty_credit=assessment.novelty_credit)
            if self.stages:
                self._stage_progress(task.id, None, "completed_from_cache")
            return assessment
        payload = {"problem": task.problem, "reference_answer": task.answer,
                   "conventional_reference": self.anchors[task.family],
                   "external_final_answer_verdict": "correct", "candidate_response": response}
        if self.stages:
            assessment, stage_keys = self._assess_pipeline(task, response, payload)
            self.db.execute("INSERT OR REPLACE INTO assessments VALUES (?, ?)",
                            (key, assessment.model_dump_json()))
            self.db.execute("INSERT OR REPLACE INTO judgment_pipelines VALUES (?, ?)",
                            (key, json.dumps({"protocol": self.protocol, "stage_keys": stage_keys})))
            self.db.commit()
            self.log.emit("judge_assessment", key=key, task_id=task.id, protocol=self.protocol,
                          stage_keys=stage_keys, assessment=assessment.model_dump(), theory=assessment.quality,
                          novelty=assessment.novelty, novelty_credit=assessment.novelty_credit)
            self._stage_progress(task.id, None, "completed")
            return assessment
        for attempt in range(RETRY_PROTOCOL["max_attempts"]):
            messages = [{"role": "system", "content": self.system},
                        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}]
            output = None
            try:
                output = self.client.generate(messages, self.config["judge_max_tokens"], assessment_schema())
                assessment = Assessment.model_validate_json(output)
                assessment.validate_evidence(response)
                assessment.validate_reference(self.anchors[task.family])
                self.db.execute("INSERT OR REPLACE INTO assessments VALUES (?, ?)",
                                (key, assessment.model_dump_json()))
                self.db.commit()
                self.log.emit("judge_assessment", key=key, task_id=task.id,
                              assessment=assessment.model_dump(), theory=assessment.quality,
                              novelty=assessment.novelty, novelty_credit=assessment.novelty_credit)
                return assessment
            except (httpx.HTTPError, ValueError, JudgeFailure) as exc:
                self.log.emit("judge_failure", attempt=attempt + 1, task_id=task.id, error=str(exc))
                if attempt + 1 == RETRY_PROTOCOL["max_attempts"]:
                    raise JudgeFailure(f"Judge failed after three attempts: {exc}") from exc
                if output is not None:
                    # Keep the task immutable and replace feedback instead of growing a transcript.
                    # The preceding assessment is untrusted; only exact candidate spans may pass.
                    payload["validation_feedback"] = {
                        "error": str(exc)[:RETRY_PROTOCOL["error_character_limit"]],
                        "previous_assessment": output,
                    }
        raise AssertionError("Unreachable retry state")

    def _generate_stage(self, spec, messages):
        """Each isolated conversation uses the same frozen endpoint with its own budget."""
        client = LocalChat(self.client.url, self.role, self.log, self.client.timeout,
                           self.client.runtime, self.spec, self.client.context_length,
                           spec.reasoning_tokens, check_context=True)
        return client.generate(messages, spec.max_tokens, spec.schema())

    def _stage_progress(self, task_id, stage, status, **extra):
        """A compact last-event record supports the dashboard without claiming liveness."""
        atomic_json(self.log.path.with_suffix(".judge-progress.json"), {
            "time": datetime.now(timezone.utc).isoformat(), "role": self.role, "variant": self.variant,
            "judge_identity": self.identity, "protocol": self.protocol,
            "task_id": task_id, "stage": stage, "status": status, **extra})

    def _assess_pipeline(self, task, response, original_payload):
        """Persist validated stages before advancing; retries cannot contaminate siblings."""
        findings, stage_keys = {}, {}
        for spec in self.stages:
            payload = dict(original_payload)
            if spec.dependencies:
                payload["proposed_additions"] = findings["reference"].model_dump()
            stage_key = digest([self.identity, spec.name, task.model_dump(), payload])
            stage_keys[spec.name] = stage_key
            cached = self.db.execute("SELECT value FROM judgment_stages WHERE key=?", (stage_key,)).fetchone()
            if cached:
                finding = spec.record.model_validate_json(cached[0])
                validate_stage(finding, response, self.anchors[task.family])
                findings[spec.name] = finding
                self.log.emit("judge_stage_cache_hit", key=stage_key, task_id=task.id,
                              protocol=self.protocol, stage=spec.name, finding=finding.model_dump())
                self._stage_progress(task.id, spec.name, "cached")
                continue
            for attempt in range(RETRY_PROTOCOL["max_attempts"]):
                messages = [{"role": "system", "content": spec.system},
                            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}]
                output = None
                started = time.monotonic()
                try:
                    self.log.emit("judge_stage_started", key=stage_key, task_id=task.id,
                                  protocol=self.protocol, stage=spec.name, attempt=attempt + 1)
                    self._stage_progress(task.id, spec.name, "started", attempt=attempt + 1)
                    output = self._generate_stage(spec, messages)
                    finding = spec.record.model_validate_json(output)
                    validate_stage(finding, response, self.anchors[task.family])
                    self.db.execute("INSERT INTO judgment_stages VALUES (?, ?)",
                                    (stage_key, finding.model_dump_json()))
                    self.db.commit()
                    findings[spec.name] = finding
                    self.log.emit("judge_stage_assessment", key=stage_key, task_id=task.id,
                                  protocol=self.protocol, stage=spec.name, finding=finding.model_dump(),
                                  seconds=time.monotonic() - started)
                    self._stage_progress(task.id, spec.name, "accepted", seconds=time.monotonic() - started)
                    break
                except (httpx.HTTPError, ValueError, KeyError, JudgeFailure) as exc:
                    self.log.emit("judge_failure", stage=spec.name, attempt=attempt + 1,
                                  task_id=task.id, error=str(exc))
                    self._stage_progress(task.id, spec.name,
                                         "failed" if attempt + 1 == RETRY_PROTOCOL["max_attempts"] else "retrying",
                                         attempt=attempt + 1, error=str(exc))
                    if attempt + 1 == RETRY_PROTOCOL["max_attempts"]:
                        raise JudgeFailure(f"Judge stage {spec.name} failed after three attempts: {exc}") from exc
                    if output is not None:
                        payload["validation_feedback"] = {
                            "error": str(exc)[:RETRY_PROTOCOL["error_character_limit"]],
                            "previous_assessment": output}
        assessment = aggregate(findings)
        assessment.validate_evidence(response)
        assessment.validate_reference(self.anchors[task.family])
        return assessment, stage_keys

    def checkpoint(self, destination: Path) -> None:
        """SQLite online backup gives a consistent cache snapshot alongside trainer state."""
        with sqlite3.connect(destination) as snapshot:
            self.db.backup(snapshot)
