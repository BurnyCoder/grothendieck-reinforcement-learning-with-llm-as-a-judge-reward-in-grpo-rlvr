"""Locked secondary family-generalization tasks, never used for training or selection.

Reuse Apache-2.0 Reasoning Gym for grids and polygons; use SymPy for rank/inverses.
Sources: https://github.com/open-thought/reasoning-gym/tree/main/reasoning_gym
https://docs.sympy.org/latest/modules/matrices/matrices.html
https://docs.sympy.org/latest/modules/core.html#sympy.core.intfunc.mod_inverse
Independent reference checks use union-find, angle sums, minors and enumeration.
"""
import importlib.metadata
import itertools
import math
import random
from pathlib import Path

from .io import PROJECT, atomic_json, digest, read_json
from .schema import Task

OOD_FAMILIES = ("largest_island", "simple_geometry", "matrix_rank", "modular_inverse")
PARAMETERS = {
    "largest_island": {"min_rows": 5, "max_rows": 8, "min_cols": 5, "max_cols": 8,
                       "min_num_islands": 2, "max_num_islands": 6,
                       "min_island_size": 2, "max_island_size": 12},
    "simple_geometry": {"min_sides": 3, "max_sides": 6, "min_angle": 30, "max_angle": 160},
    "matrix_rank": {"min_size": 2, "max_size": 4, "entry_bound": 5},
    "modular_inverse": {"min_modulus": 31, "max_modulus": 300},
}


def canonical(task: Task) -> str:
    """Collapse grid symmetries, polygon order and matrix row/column permutations."""
    m = task.metadata
    if task.family == "largest_island":
        grid = tuple(tuple(row) for row in m["grid"])
        variants = []
        for _ in range(4):
            variants.extend((grid, tuple(reversed(grid))))
            grid = tuple(zip(*grid[::-1]))
        content = min(variants)
    elif task.family == "simple_geometry":
        content = [m["n_sides"], sorted(m["known_angles"])]
    elif task.family == "matrix_rank":
        matrix = m["matrix"]
        content = min(tuple(sorted(tuple(row[c] for c in order) for row in matrix))
                      for order in itertools.permutations(range(len(matrix[0]))))
    elif task.family == "modular_inverse":
        content = [m["a"] % m["modulus"], m["modulus"]]
    else:
        raise ValueError("Unknown OOD family")
    return digest([task.family, content])


def reference(task: Task) -> int:
    """Independent checks of trusted generated references, not candidate code execution."""
    m = task.metadata
    if task.family == "largest_island":
        grid = m["grid"]
        parent = {(r, c): (r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value}
        def find(cell):
            while parent[cell] != cell:
                parent[cell] = parent[parent[cell]]
                cell = parent[cell]
            return cell
        for r, c in parent:
            for neighbor in ((r-1, c), (r, c-1)):
                if neighbor in parent:
                    parent[find((r, c))] = find(neighbor)
        from collections import Counter
        return max(Counter(find(cell) for cell in parent).values(), default=0)
    if task.family == "simple_geometry":
        angle = 180 * (m["n_sides"] - 2) - sum(m["known_angles"])
        if not 0 < angle < 180:
            raise ValueError("Generated missing angle is incompatible with a convex polygon")
        return int(angle)
    if task.family == "modular_inverse":
        return next(b for b in range(1, m["modulus"]) if (m["a"] * b) % m["modulus"] == 1)
    if task.family == "matrix_rank":
        from sympy import Matrix
        matrix = Matrix(m["matrix"])
        # Rank is the greatest order of a nonzero minor; the generator uses elimination.
        for k in range(min(matrix.shape), 0, -1):
            for rows in itertools.combinations(range(matrix.rows), k):
                for cols in itertools.combinations(range(matrix.cols), k):
                    if matrix.extract(rows, cols).det() != 0:
                        return k
        return 0
    raise ValueError("Unknown OOD family")


def custom_entry(family: str, seed: int, index: int) -> dict:
    """Small bounded SymPy-backed tasks cover linear algebra and modular arithmetic."""
    from sympy import Matrix, mod_inverse
    rng = random.Random(seed + index)
    params = PARAMETERS[family]
    if family == "modular_inverse":
        modulus = rng.randint(params["min_modulus"], params["max_modulus"])
        a = rng.choice([a for a in range(2, modulus) if math.gcd(a, modulus) == 1])
        return {"question": f"Find the integer b with 0 <= b < {modulus} such that {a}*b = 1 modulo {modulus}.",
                "answer": str(mod_inverse(a, modulus)), "metadata": {"a": a, "modulus": modulus}}
    rows, cols = (rng.randint(params["min_size"], params["max_size"]) for _ in range(2))
    factor_size = rng.randint(1, min(rows, cols))
    bound = params["entry_bound"]
    left = Matrix(rows, factor_size, lambda i, j: rng.randint(-bound, bound))
    right = Matrix(factor_size, cols, lambda i, j: rng.randint(-bound, bound))
    matrix = left * right
    values = [[int(value) for value in row] for row in matrix.tolist()]
    return {"question": f"Find the rank over the rational numbers of the matrix with rows {values}.",
            "answer": str(matrix.rank()), "metadata": {"matrix": values}}


def prepare_ood(destination: Path | None = None) -> dict:
    """Add a separately locked manifest without rewriting any original registered split."""
    import reasoning_gym
    destination = destination or PROJECT / "data"
    cfg = read_json(PROJECT / "configs/study.json")
    version = importlib.metadata.version("reasoning-gym")
    identity = {"seed": cfg["ood_seed"], "per_family": cfg["test_ood_per_family"],
                "parameters": PARAMETERS, "reasoning_gym": version,
                "sympy": importlib.metadata.version("sympy"), "generator_version": 1}
    lock_path, manifest = destination / "ood.lock.json", destination / "test_ood.json"
    if lock_path.exists():
        lock = read_json(lock_path)
        if lock["identity"] != identity or digest(read_json(manifest)) != lock["manifest_hash"]:
            raise ValueError("Locked OOD configuration or manifest changed")
        return lock
    records, rejected, seen = [], [], set()
    for family_number, family in enumerate(OOD_FAMILIES):
        seed = cfg["ood_seed"] + 1000000000 + family_number * 100000
        dataset = reasoning_gym.create_dataset(family, seed=seed, size=90000, **PARAMETERS[family]) \
            if family in ("largest_island", "simple_geometry") else None
        accepted = 0
        for index in range(90000):
            entry = dataset[index] if dataset is not None else custom_entry(family, seed, index)
            problem = entry["question"]
            if family == "simple_geometry":
                # RG's answer-only instruction conflicts with explanation generation; preserve provenance.
                problem = problem.split("Return only the angle")[0].strip() + " Give the final angle in degrees without units."
            task = Task(id="pending", problem=problem, answer=entry["answer"], family=family,
                        split="test_ood", metadata=entry["metadata"],
                        provenance={"generator": "reasoning-gym" if dataset is not None else "sympy-project-v1",
                                    "version": version if dataset is not None else identity["sympy"],
                                    "seed": seed, "index": index, "parameters": PARAMETERS[family],
                                    "original_question": entry["question"]})
            try:
                expected = reference(task)
            except ValueError as exc:
                rejected.append({"family": family, "index": index, "reason": str(exc)})
                continue
            if str(expected) != task.answer:
                raise ValueError("OOD generator reference disagrees with independent check")
            key = canonical(task)
            if key in seen:
                continue
            seen.add(key)
            task.id = f"test_ood-{key[:20]}"
            records.append(task.model_dump())
            accepted += 1
            if accepted == cfg["test_ood_per_family"]:
                break
        if accepted != cfg["test_ood_per_family"]:
            raise RuntimeError(f"Unable to fill OOD family {family}")
    random.Random(cfg["ood_seed"]).shuffle(records)
    lock = {"identity": identity, "manifest_hash": digest(records), "count": len(records), "rejections": rejected}
    atomic_json(manifest, records)
    atomic_json(lock_path, lock)
    return lock


def load_ood() -> list[Task]:
    """Validate the independently locked secondary manifest before any evaluation."""
    prepare_ood()
    return [Task.model_validate(row) for row in read_json(PROJECT / "data/test_ood.json")]
