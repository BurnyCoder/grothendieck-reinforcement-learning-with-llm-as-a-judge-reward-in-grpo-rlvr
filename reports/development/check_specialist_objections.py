"""Reproduce narrow post-hoc mathematical checks; never rescore a judge output.

Run with the project's locked environment and PYTHONPATH=src. Expressions below
are authored diagnostic code, not parsed or executed from model responses.
SymPy polynomial remainder and expansion:
https://docs.sympy.org/latest/modules/polys/reference.html#sympy.polys.polytools.rem
https://docs.sympy.org/latest/modules/core.html#sympy.core.function.expand
"""
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import sympy as sp

from grothendieck_rlvr.io import atomic_json
from grothendieck_rlvr.novelty_cases import novelty_example


def check():
    """Test the disputed substitutions and identities, not whole explanations."""
    instances = []
    for index, operation in ((0, math.gcd), (1, math.lcm)):
        task = novelty_example(index, "dev")[0]
        a, b = map(int, re.findall(r"\d+", task.problem))
        scale = a // 2
        instances.append({"task_id": task.id, "problem": task.problem, "scale": scale,
                          "matches_2n_3n": a == 2 * scale and b == 3 * scale,
                          "computed_answer": operation(a, b),
                          "matches_reference_answer": operation(a, b) == int(task.answer)})
    x, n, e, a, b, c, d = sp.symbols("x n e a b c d")
    identities = {
        "norm_product_modulo_e_squared_minus_one": sp.rem(
            (x + n * e) * (x - n * e) - (x**2 - n**2), e**2 - 1, e),
        "product_of_evaluations": sp.expand((x + n) * (x - n) - (x**2 - n**2)),
        "norm_composition": sp.expand(
            (a**2 - b**2) * (c**2 - d**2) - ((a * c + b * d)**2 - (a * d + b * c)**2)),
    }
    assert all(row["matches_2n_3n"] and row["matches_reference_answer"] for row in instances)
    assert all(residual == 0 for residual in identities.values())
    result = {"time": datetime.now(timezone.utc).isoformat(),
              "kind": "posthoc_specialist_objection_math_check", "inference_performed": False,
              "scores_modified": False, "instances": instances,
              "symbolic_residuals": {name: str(value) for name, value in identities.items()},
              "scope": "Exact checks of elementary substitutions and polynomial identities under commutative arithmetic. Not a certificate of every claim in either the candidate or the judge output; not a calibration relabeling."}
    atomic_json(Path(__file__).with_name("specialist-objection-math-check.json"), result)
    return result


if __name__ == "__main__":
    print(check())
