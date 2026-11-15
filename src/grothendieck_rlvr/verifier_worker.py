"""Resource-limited exact arithmetic worker; AST is interpreted, never executed.

Python AST: https://docs.python.org/3/library/ast.html
Resource bounds: https://docs.python.org/3/library/resource.html
SymPy objects are constructed directly; Math-Verify receives objects, not code.
"""
import ast
import json
import re
import sys
from fractions import Fraction


class InvalidExpression(ValueError):
    """Candidate falls outside the explicitly supported mathematical grammar."""


def expression(text: str, scalar=False):
    """Interpret bounded rational polynomials with single-letter variables safely."""
    # Scalar tasks need only exact standard-library fractions, avoiding symbolic-parser startup.
    # https://docs.python.org/3/library/fractions.html
    if not scalar:
        import sympy as sp
    text = text.strip().replace("^", "**").replace("×", "*")
    if not text or len(text) > 1024 or not re.fullmatch(r"[0-9a-z+*/().\s-]+", text):
        raise InvalidExpression("Use numbers, single-letter variables and arithmetic operators")
    try:
        tree = ast.parse(text, mode="eval")
    except (SyntaxError, RecursionError) as exc:
        raise InvalidExpression("Malformed arithmetic") from exc
    if sum(1 for _ in ast.walk(tree)) > 256:
        raise InvalidExpression("Too many arithmetic nodes")

    def visit(node, depth=0):
        if depth > 24:
            raise InvalidExpression("Arithmetic nesting exceeds limit")
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            # Preserve the written decimal: AST float values have already been rounded.
            literal = ast.get_source_segment(text, node)
            if not re.fullmatch(r"(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?", literal):
                raise InvalidExpression("Require decimal numerical literals")
            if "e" in literal and abs(int(literal.split("e")[1])) > 1000:
                raise InvalidExpression("Scientific exponent exceeds limit")
            value = Fraction(literal)
            if abs(value) > 10**12:
                raise InvalidExpression("Numeric magnitude exceeds limit")
            return value if scalar else sp.Rational(value.numerator, value.denominator)
        if isinstance(node, ast.Name) and re.fullmatch("[a-z]", node.id):
            if scalar:
                raise InvalidExpression("Require numerical arithmetic without variables")
            return sp.Symbol(node.id)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand, depth + 1)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp):
            left = visit(node.left, depth + 1)
            if isinstance(node.op, ast.Pow):
                if not isinstance(node.right, ast.Constant) or type(node.right.value) is not int:
                    raise InvalidExpression("Exponent must be a literal integer")
                if not 0 <= node.right.value <= 12:
                    raise InvalidExpression("Exponent outside 0..12")
                return left ** node.right.value
            right = visit(node.right, depth + 1)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div) and (scalar or right.is_number) and right != 0:
                return left / right
        raise InvalidExpression("Unsupported expression node")

    result = visit(tree.body)
    if not scalar and result.has(sp.zoo, sp.oo, -sp.oo, sp.nan):
        raise InvalidExpression("Nonfinite value")
    return result


def check(family: str, answer: str, gold: str, metadata: dict) -> bool:
    """Task-specific complete-answer checks; gold is trusted, candidate grammar is bounded."""
    if family == "polynomial_equations":
        def roots(text):
            if not text.strip():
                return []
            if not re.fullmatch(r"[0-9.,+\s-]+", text) or len(text.split(",")) > 12:
                raise InvalidExpression("Require a complete comma-separated decimal root list")
            try:
                return sorted(Fraction(x.strip()) for x in text.split(","))
            except (ValueError, ZeroDivisionError) as exc:
                raise InvalidExpression("Invalid decimal root") from exc
        predicted, expected = roots(answer), roots(gold)
        return len(predicted) == len(expected) and all(
            abs(a-b) <= Fraction(1, 20000) for a, b in zip(predicted, expected, strict=True))
    if family == "prime_factorization":
        import sympy as sp
        factors = answer.replace("×", "*").replace("^", "**").replace(" ", "")
        if not re.fullmatch(r"\d+(?:\*\*\d+)?(?:\*\d+(?:\*\*\d+)?)*", factors):
            raise InvalidExpression("Require prime factors separated by * or ×")
        product = 1
        for base, exponent in re.findall(r"(\d+)(?:\*\*(\d+))?(?:\*|$)", factors):
            base, exponent = int(base), int(exponent or 1)
            if base > 10**12 or not 1 <= exponent <= 12:
                raise InvalidExpression("Factor magnitude exceeds limit")
            if not sp.isprime(base):
                return False
            product *= base**exponent
        return product == int(expression(gold, scalar=True))
    if family in ("gcd", "lcm", "dice", "largest_island", "simple_geometry", "matrix_rank", "modular_inverse"):
        expected, predicted = expression(gold, scalar=True), expression(answer, scalar=True)
        return predicted == expected and (family == "dice" or predicted.denominator == 1)
    if family == "polynomial_multiplication":
        import sympy as sp
        from math_verify import verify
        expected, predicted = expression(gold), expression(answer)
        allowed = set(metadata.get("variables", [str(s) for s in expected.free_symbols]))
        if not {str(s) for s in predicted.free_symbols} <= allowed:
            raise InvalidExpression("Unexpected polynomial variable")
        return bool(verify([sp.expand(expected)], [sp.expand(predicted)], timeout_seconds=5))
    raise RuntimeError(f"Unsupported task family {family}")


def main():
    """Install limits before importing symbolic libraries and serialize a typed outcome."""
    if sys.platform == "linux":
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
        resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    payload = json.load(sys.stdin)
    try:
        status = "correct" if check(**payload) else "incorrect"
        result = {"status": status}
    except InvalidExpression as exc:
        result = {"status": "invalid_format", "detail": str(exc)}
    except Exception as exc:
        result = {"error": f"{type(exc).__name__}: {exc}"}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
