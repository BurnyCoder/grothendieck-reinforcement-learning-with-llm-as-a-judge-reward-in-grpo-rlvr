"""Independent arithmetic checks on trusted, locked generator records. No model text is executed."""
import itertools
import math
import re
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path

import sympy as sp

from .io import PROJECT, digest, read_json


def dice_tail(sides, threshold):
    """Count bounded positive compositions using inclusion-exclusion, independently of the generator's DP."""
    below = 0
    for k in range(len(sides) + 1):
        for selection in itertools.combinations(sides, k):
            top = threshold - 1 - sum(selection)
            if top >= len(sides):
                below += (-1)**k * math.comb(top, len(sides))
    return 1 - Fraction(below, math.prod(sides))


def flood_size(grid):
    """Measure the largest four-connected land component by a direct flood fill."""
    land = {(i, j) for i, row in enumerate(grid) for j, v in enumerate(row) if v}
    largest = 0
    while land:
        todo, size = [land.pop()], 0
        while todo:
            i, j = todo.pop()
            size += 1
            for other in ((i-1, j), (i+1, j), (i, j-1), (i, j+1)):
                if other in land:
                    land.remove(other)
                    todo.append(other)
        largest = max(largest, size)
    return largest


def reference_and_key(row):
    """Return correctness of the gold and a canonical within-family key from independent arithmetic."""
    f, m, gold = row["family"], row["metadata"], row["answer"]
    if f in ("gcd", "lcm"):
        key = tuple(sorted(m["numbers"]))
        factors = [sp.factorint(n) for n in key]
        choose = min if f == "gcd" else max
        n = math.prod(p**choose(a.get(p, 0) for a in factors) for p in set().union(*factors))
        return int(gold) == n, key
    if f == "dice":
        sides = tuple(sorted(map(int, re.findall(r"1d(\d+)", m["puzzle"]["dice_str"]))))
        target = m["puzzle"]["target"]
        return Fraction(gold) == dice_tail(sides, target), (sides, target)
    if f == "prime_factorization":
        factors = Counter(int(i.strip()) for i in gold.split("×"))
        return factors == sp.factorint(m["number"]), m["number"]
    if f.startswith("polynomial_"):
        # Only the version-locked generator's expressions enter SymPy here.
        symbols = {v: sp.Symbol(v) for v in m.get("variables", [m.get("variable", "x")])}
        poly = sp.Poly(sp.sympify(m["polynomial_expr"], locals=symbols), *symbols.values())
        if f == "polynomial_multiplication":
            other = sp.Poly(sp.sympify(gold, locals=symbols), *symbols.values())
            bound = max(poly.degree(), other.degree())
            return all(poly.eval(i) == other.eval(i) for i in range(bound+1)), tuple(poly.all_coeffs())
        # Isolate all distinct real roots over Q, then round exact rational interval endpoints.
        roots = []
        for (lo, hi), _ in poly.intervals(eps=sp.Rational(1, 10**14)):
            a, b = round(Fraction(int(lo.p), int(lo.q)), 4), round(Fraction(int(hi.p), int(hi.q)), 4)
            if a != b:
                raise ValueError(f"Unresolved rounding at {row['id']}")
            roots.append(a)
        actual = sorted(Fraction(x.strip()) for x in gold.split(",") if x.strip())
        return sorted(set(roots)) == actual, tuple(poly.monic().all_coeffs())
    if f == "matrix_rank":
        matrix = m["matrix"]
        key = min(tuple(sorted(tuple(r[j] for j in perm) for r in matrix))
                  for perm in itertools.permutations(range(len(matrix[0]))))
        return len(sp.Matrix(matrix).rref()[1]) == int(gold), key
    if f == "modular_inverse":
        a, mod = m["a"], m["modulus"]
        return int(gold) == pow(a, -1, mod), (a % mod, mod)
    if f == "simple_geometry":
        angles = tuple(sorted(map(Fraction, m["known_angles"])))
        return 0 < int(gold) < 180 and sum(angles) + int(gold) == 180*(m["n_sides"]-2), (m["n_sides"], angles)
    if f == "largest_island":
        grid = tuple(map(tuple, m["grid"]))
        variants = []
        for _ in range(4):
            variants.extend((grid, grid[::-1]))
            grid = tuple(zip(*grid[::-1]))
        return flood_size(grid) == int(gold), min(variants)
    raise ValueError(f"Unknown family {f}")


def audit_manifests():
    """Examine all locked records, gold answers, semantic keys and transfer assignments."""
    directory = PROJECT / "data"
    lock, ood = read_json(directory / "manifest.lock.json"), read_json(directory / "ood.lock.json")
    for name, signature in lock["files"].items():
        if digest(read_json(directory / name)) != signature:
            raise ValueError(f"Changed original data: {name}")
    if digest(read_json(directory / "test_ood.json")) != ood["manifest_hash"]:
        raise ValueError("Changed OOD data")
    seen, seen_ids, failures, overlaps, counts, transfer = {}, set(), [], [], {}, {}
    for split in (*lock["counts"], "test_ood"):
        rows = read_json(directory / (split + ".json"))
        counts[split] = dict(sorted(Counter(r["family"] for r in rows).items()))
        for r in rows:
            verified, content = reference_and_key(r)
            key = (r["family"], content)
            if not verified or r["split"] != split or r["id"] in seen_ids:
                failures.append(r["id"])
            if key in seen:
                overlaps.append([seen[key], r["id"]])
            seen[key] = r["id"]
            seen_ids.add(r["id"])
        if split.startswith("transfer_"):
            transfer[split] = rows
    sources = {r["id"]: r["family"] for r in transfer["transfer_source"]}
    links = Counter(r["source_id"] for r in transfer["transfer_target"])
    valid_links = (set(sources) == set(links) and all(n == 4 for n in links.values())
                   and all(sources.get(r["source_id"]) == r["family"] for r in transfer["transfer_target"]))
    return {"by_split_family": counts, "records": len(seen_ids), "reference_or_metadata_errors": failures,
            "semantic_duplicates": overlaps, "matched_transfer": valid_links,
            "transfer_sources": len(sources), "transfer_targets": sum(links.values())}


def replay_generators():
    """Regenerate into an empty directory so manifest validation cannot short-circuit generation."""
    from .data import prepare
    from .ood import prepare_ood
    original = PROJECT/"data"
    with tempfile.TemporaryDirectory(prefix="grothendieck-audit-manifests-") as directory:
        target = Path(directory)
        regenerated, secondary = prepare(target), prepare_ood(target)
        locked = read_json(original/"manifest.lock.json")
        files = {f: {"locked": h, "replayed": regenerated["files"].get(f)} for f,h in locked["files"].items()}
        files["test_ood.json"] = {"locked": read_json(original/"ood.lock.json")["manifest_hash"],
                                  "replayed": secondary["manifest_hash"]}
        return {"files": files, "all_records_match": all(x["locked"] == x["replayed"] for x in files.values()),
                "original_config_hash": locked["config_hash"], "current_config_hash": regenerated["config_hash"],
                "ood_lock_matches": secondary == read_json(original/"ood.lock.json")}
