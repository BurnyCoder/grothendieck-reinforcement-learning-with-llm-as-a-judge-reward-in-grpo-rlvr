"""Reproduce the 2026-11-26 CPU analysis from immutable generation receipts."""
import ast
import hashlib
import math
import re
import tomllib
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from importlib.metadata import version
from pathlib import Path

from .analysis import paired_bootstrap
from .data import load_tasks
from .experiments import EXPLORATORY_PREFIX
from .io import PROJECT, atomic_json, digest, read_json, read_jsonl, root
from .prompts import policy_messages
from .verify import VerifierFailure, verify_answer

AUDIT = PROJECT / "results/scientific-audit"
SPLITS = ("test_fresh", "test_hard", "test_unseen")
ARMS = ("ordinary", "prompted")


def file_hash(path):
    """Hash the downloaded bytes without decoding JSON or normalizing newlines."""
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def form_failure(family, answer, gold):
    """Apply the published form sensitivity only after the mathematical verifier passes."""
    if family == "dice":
        match = re.fullmatch(r"([+-]?\d+)(?:\s*/\s*(\+?\d+))?", answer)
        if not match:
            return "fraction_form"
        numerator, denominator = int(match[1]), int(match[2] or 1)
        if denominator <= 0 or math.gcd(numerator, denominator) != 1:
            return "fraction_form"
    elif family == "polynomial_multiplication":
        tree = ast.parse(answer.replace("^", "**").replace("×", "*"), mode="eval")
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mult, ast.Pow, ast.Div)):
                for part in ast.walk(node):
                    if (isinstance(part, ast.BinOp) and isinstance(part.op, (ast.Add, ast.Sub))
                            and any(isinstance(v, ast.Name) for v in ast.walk(part))):
                        return "polynomial_form"
    elif family == "polynomial_equations":
        def decimals(value):
            return sorted(Fraction(x.strip()) for x in value.split(",")) if value.strip() else []
        if decimals(answer) != decimals(gold):
            return "rounded_roots"
    return None


def frozen_inputs(archives, arm, tasks):
    """Authenticate all three artifacts, then check every ID and the actual complete prompt."""
    name = EXPLORATORY_PREFIX + arm
    receipt = read_json(PROJECT / "reports/generation" / (name + ".json"))
    directory = archives / name
    for filename, field in (("generations.jsonl", "generations_sha256"), ("events.jsonl", "events_sha256"),
                            ("generation-config.json", "generation_config_sha256")):
        if file_hash(directory / filename) != receipt[field]:
            raise ValueError(f"{name}: hash mismatch for {filename}")
    cfg = read_json(directory / "generation-config.json")
    rising = arm == "prompted"
    prompts = {key: policy_messages(task, rising=rising) for key, task in tasks.items()}
    if (cfg["run_id"] != name or cfg["rising"] != rising or cfg["adapter"] is not None
            or cfg["split"] != "test" or cfg["seed"] != 42 or cfg["inference"]["do_sample"]
            or cfg["inference"]["model"] != read_json(PROJECT / "configs/models.lock.json")["policy"]
            or cfg["tasks"] != digest([task.model_dump() for task in tasks.values()])
            or cfg["prompts"] != digest(prompts)):
        raise ValueError(f"{name}: baseline configuration differs from the frozen design")
    records = read_jsonl(directory / "generations.jsonl")
    if len(records) != len(tasks) or {r["task_id"] for r in records} != set(tasks):
        raise ValueError(f"{name}: expected every locked task exactly once")
    for row in records:
        key = row["task_id"]
        if (row["prompt"], row["family"], row["split"]) != (prompts[key], tasks[key].family, tasks[key].split):
            raise ValueError(f"{name}: input metadata differs for {key}")
    return records, receipt, cfg["inference"]


def score_one(task, row):
    """Keep mathematical errors, invalid answer format and infrastructure failures distinct."""
    record = {"task_id": task.id, "split": task.split, "family": task.family,
              "generation_digest": digest(row)}
    try:
        verdict = verify_answer(task, row["response"])
    except VerifierFailure as exc:
        return {**record, "status": "infrastructure", "detail": str(exc), "correct": None, "strict": None}
    reason = form_failure(task.family, verdict.answer, task.answer) if verdict.correct else None
    return {**record, **verdict.model_dump(), "correct": verdict.correct,
            "form_failure": reason, "strict": verdict.correct and reason is None}


def counts(rows):
    """Every descriptive proportion has an explicit common denominator."""
    statuses = Counter(r["status"] for r in rows)
    complete = not statuses["infrastructure"]
    return {"n": len(rows), "correct": statuses["correct"], "invalid_format": statuses["invalid_format"],
            "incorrect": statuses["incorrect"], "infrastructure": statuses["infrastructure"],
            "accuracy": statuses["correct"]/len(rows) if complete else None,
            "strict_correct": sum(r["strict"] is True for r in rows) if complete else None,
            "form_failures": dict(Counter(r["form_failure"] for r in rows if r.get("form_failure")))}


def baseline_summary(by_arm, cfg):
    """Pair by locked problem before resampling, as in the dated scoring protocol."""
    summary = {"protocol": "2026-11-26-cpu-baseline-audit", "arms": {}, "paired": {}}
    maps = {}
    for arm, rows in by_arm.items():
        maps[arm] = {r["task_id"]: r for r in rows}
        summary["arms"][arm] = {**counts(rows), **{
            field: {k: counts([r for r in rows if r[field] == k]) for k in sorted({r[field] for r in rows})}
            for field in ("split", "family")}}
    if set(maps["ordinary"]) != set(maps["prompted"]):
        raise ValueError("Unmatched frozen baselines")
    if any(v["infrastructure"] for v in summary["arms"].values()):
        summary["status"] = "incomplete"
        return summary
    ids = sorted(maps["ordinary"])
    for field in ("correct", "strict"):
        pairs = [(maps["ordinary"][i][field], maps["prompted"][i][field]) for i in ids]
        diff = [int(p)-int(o) for o, p in pairs]
        estimate = paired_bootstrap(diff, [maps["ordinary"][i]["split"] for i in ids],
                                    cfg["bootstrap_samples"], cfg["data_seed"])
        summary["paired"][field] = {"both": pairs.count((True, True)), "neither": pairs.count((False, False)),
                                    "ordinary_only": pairs.count((True, False)), "prompted_only": pairs.count((False, True)),
                                    **{k: estimate[k] for k in ("difference", "ci95", "problems", "bootstrap_samples")}}
    summary["status"] = "complete"
    return summary


def score_saved_correctness(archives=None, output=None, workers=2):
    """Score only authenticated text on CPU. No judge, trainer, tokenizer or policy is constructed."""
    if workers < 1:
        raise ValueError("workers must be positive")
    # Check the locked arithmetic and resampling stack before opening the held-out responses.
    required = {"sympy", "math-verify", "numpy", "reasoning-gym"}
    packages = tomllib.loads((PROJECT / "uv.lock").read_text())["package"]
    for package in packages:
        if package["name"] in required and version(package["name"]) != package["version"]:
            raise RuntimeError(f"CPU audit requires the locked {package['name']} {package['version']}")
    archives = Path(archives) if archives else root() / "evaluations"
    output = Path(output) if output else AUDIT
    tasks = {t.id: t for split in SPLITS for t in load_tasks(split)}
    inputs = {arm: frozen_inputs(archives, arm, tasks) for arm in ARMS}
    if inputs["ordinary"][2] != inputs["prompted"][2]:
        raise ValueError("Baseline inference identities differ")
    by_arm = {}
    for arm, (records, receipt, _) in inputs.items():
        print(f"CPU verifier: {arm}, {len(records)} archived answers", flush=True)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(lambda row: score_one(tasks[row["task_id"]], row), records))
        by_arm[arm] = sorted(rows, key=lambda row: row["task_id"])
        atomic_json(output / (arm + ".json"), {"generations_sha256": receipt["generations_sha256"],
                                                "records": by_arm[arm]})
    summary = baseline_summary(by_arm, read_json(PROJECT / "configs/study.json"))
    atomic_json(output / "baseline-summary.json", summary)
    return {"status": summary["status"], "paired": summary["paired"]}
