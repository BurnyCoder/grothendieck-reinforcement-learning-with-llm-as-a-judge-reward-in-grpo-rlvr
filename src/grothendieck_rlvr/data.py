"""Reasoning Gym manifests with semantic deduplication and independent references.

Generator API: https://github.com/open-thought/reasoning-gym
Only trusted generator expressions enter symbolic canonicalization.
"""
import importlib.metadata
import math
import os
import random
from collections import Counter
from fractions import Fraction
from pathlib import Path

from .io import PROJECT, atomic_json, digest, read_json
from .schema import Task

TRAIN_FAMILIES = ("gcd", "lcm", "polynomial_multiplication", "dice")
UNSEEN_FAMILIES = ("prime_factorization", "polynomial_equations")


def parameters(family: str, hard=False) -> dict:
    """The preregistered difficulty schedule, independent of policy performance."""
    if family in ("gcd", "lcm"):
        return {"min_numbers": 4 if hard else 2, "max_numbers": 5 if hard else 3,
                "min_value": (1001 if family == "gcd" else 101) if hard else 2,
                "max_value": (10000 if family == "gcd" else 300) if hard
                else (1000 if family == "gcd" else 100)}
    if family == "dice":
        return {"num_dice": 5 if hard else 3, "max_dice_size": 24 if hard else 20}
    if family == "prime_factorization":
        return {"min_value": 100, "max_value": 10000}
    params = {"min_terms": 3 if hard else 2, "max_terms": 4 if hard else 3,
              "min_degree": 0, "max_degree": 3 if hard else 2,
              "min_value": 1, "max_value": 12 if hard else 8,
              "min_polynomials": 3 if hard else 2, "max_polynomials": 3 if hard else 2,
              "variables": ("x",)}
    if family == "polynomial_equations":
        return {"min_terms": 2, "max_terms": 4, "min_degree": 1,
                "max_degree": 3, "min_value": 1, "max_value": 10}
    return params


def canonical_key(task: Task) -> str:
    """Collapse wording/permutation/variable-name differences in mathematical instances."""
    from .verifier_worker import expression
    import sympy as sp
    m = task.metadata
    if task.family in ("gcd", "lcm"):
        content = sorted(m["numbers"])
    elif task.family == "dice":
        content = [sorted(int(s[2:]) for s in m["puzzle"]["dice_str"].split(", ")),
                   m["puzzle"]["target"]]
    elif task.family == "prime_factorization":
        content = m["number"]
    else:
        poly = expression(m["polynomial_expr"])
        symbols = sorted(poly.free_symbols, key=str)
        if not symbols or poly == 0:
            raise ValueError("Degenerate polynomial instance")
        poly = poly.subs({symbol: sp.Symbol("x") for symbol in symbols})
        content = str(sp.Poly(poly, sp.Symbol("x")).monic().as_expr()
                      if task.family == "polynomial_equations" else sp.expand(poly))
    return digest([task.family, content])


def reference_check(task: Task) -> None:
    """Recompute the generator reference without using its permissive reward function."""
    import sympy as sp
    from .verifier_worker import expression
    m, family = task.metadata, task.family
    if family in ("gcd", "lcm"):
        expected = getattr(math, family)(*m["numbers"])
        valid = expected == int(task.answer)
    elif family == "prime_factorization":
        factors = [int(x) for x in task.answer.split("×")]
        valid = math.prod(factors) == m["number"] and all(sp.isprime(x) for x in factors)
    elif family == "dice":
        counts = Counter({0: 1})
        dice = [int(s[2:]) for s in m["puzzle"]["dice_str"].split(", ")]
        for sides in dice:
            updated = Counter()
            for total, count in counts.items():
                for face in range(1, sides + 1):
                    updated[total + face] += count
            counts = updated
        expected = Fraction(sum(c for n, c in counts.items() if n >= m["puzzle"]["target"]), math.prod(dice))
        valid = expected == Fraction(task.answer)
    elif family == "polynomial_multiplication":
        valid = sp.expand(expression(task.answer) - expression(m["polynomial_expr"])) == 0
    else:
        poly = expression(m["polynomial_expr"])
        if len(poly.free_symbols) != 1:
            raise ValueError("Degenerate polynomial equation")
        # Real-root isolation catches omitted roots instead of trusting is_real filtering.
        expected = sorted(set(round(float(r.evalf()), 4) for r in sp.real_roots(poly)))
        actual = sorted(float(x) for x in task.answer.split(",") if x.strip())
        valid = expected == actual
    if not valid:
        raise ValueError("Generator reference disagrees with independent arithmetic")


def assert_disjoint(tasks: list[Task]) -> None:
    """Detect overlap globally; stricter than merely checking task identifiers."""
    seen = {}
    for task in tasks:
        key = canonical_key(task)
        if key in seen:
            raise ValueError(f"Canonical overlap: {seen[key]} and {task.id}")
        seen[key] = task.id


def prepare(destination: Path | None = None) -> dict:
    """Generate and lock all manifests without any model inference or model-based filtering."""
    import reasoning_gym
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("Launch with PYTHONHASHSEED=0 for Reasoning Gym monomial reproducibility")
    destination = destination or PROJECT / "data"
    if (destination / "manifest.lock.json").exists():
        return validate_manifests(destination)
    cfg = read_json(PROJECT / "configs/study.json")
    all_tasks, seen, rejected = [], set(), []
    version = importlib.metadata.version("reasoning-gym")
    split_number = 0

    def generate(split, families, count, hard=False, sources=None):
        nonlocal split_number
        split_number += 1
        tasks = []
        for family_number, family in enumerate(families):
            seed = cfg["data_seed"] + split_number * 10000000 + family_number * 100000
            params = parameters(family, hard)
            dataset = reasoning_gym.create_dataset(family, seed=seed, size=90000, **params)
            wanted = count // len(families)
            accepted = 0
            for index in range(90000):
                entry = dataset[index]
                question = entry["question"]
                if family == "polynomial_equations":
                    question = question.split("In solving equations")[0].strip() + (
                        " Give all real roots as comma-separated decimals rounded to nearest four decimal "
                        "places, or an empty answer if there are no real roots.")
                record = Task(id="pending", problem=question, answer=entry["answer"],
                              family=family, split=split, metadata=entry["metadata"],
                              provenance={"generator": "reasoning-gym", "version": version,
                                          "seed": seed, "index": index, "parameters": params,
                                          "original_question": entry["question"], "pythonhashseed": "0"})
                try:
                    key = canonical_key(record)
                    reference_check(record)
                except ValueError as exc:
                    rejected.append({"split": split, "family": family, "seed": seed,
                                     "index": index, "reason": str(exc)})
                    continue
                if key in seen:
                    continue
                seen.add(key)
                record.id = f"{split}-{key[:20]}"
                if sources:
                    family_sources = [s for s in sources if s.family == family]
                    record.source_id = family_sources[accepted // cfg["transfer_targets_per_source"]].id
                tasks.append(record)
                accepted += 1
                if accepted == wanted:
                    break
            if accepted != wanted:
                raise RuntimeError(f"Cannot fill {split}/{family} without duplicates")
        random.Random(cfg["data_seed"]).shuffle(tasks)
        all_tasks.extend(tasks)
        atomic_json(destination / f"{split}.json", [t.model_dump() for t in tasks])
        return tasks

    generate("train", TRAIN_FAMILIES, cfg["train_size"])
    generate("dev", TRAIN_FAMILIES, cfg["dev_size"])
    generate("test_fresh", TRAIN_FAMILIES, cfg["test_fresh_size"])
    generate("test_hard", TRAIN_FAMILIES, cfg["test_hard_size"], hard=True)
    generate("test_unseen", UNSEEN_FAMILIES, cfg["test_unseen_size"])
    sources = generate("transfer_source", TRAIN_FAMILIES, cfg["transfer_sources"])
    generate("transfer_target", TRAIN_FAMILIES,
             cfg["transfer_sources"] * cfg["transfer_targets_per_source"], sources=sources)
    assert_disjoint(all_tasks)
    atomic_json(destination / "rejections.json", rejected)
    lock = {"config_hash": digest(cfg), "generator_version": version,
            "files": {p.name: digest(read_json(p)) for p in destination.glob("*.json")},
            "counts": dict(Counter(t.split for t in all_tasks))}
    atomic_json(destination / "manifest.lock.json", lock)
    return lock


def validate_manifests(directory: Path | None = None) -> dict:
    """Refuse changed dataset artifacts after the lock has been published."""
    directory = directory or PROJECT / "data"
    lock = read_json(directory / "manifest.lock.json")
    for name, expected in lock["files"].items():
        if digest(read_json(directory / name)) != expected:
            raise ValueError(f"Manifest changed after locking: {name}")
    return lock


def load_tasks(split: str, directory: Path | None = None) -> list[Task]:
    """Read only a named locked split; test references never enter training prompts."""
    directory = directory or PROJECT / "data"
    validate_manifests(directory)
    return [Task.model_validate(t) for t in read_json(directory / f"{split}.json")]
