# Pre-judgment verifier clarification

Date: 2026-11-15. No judge assessment or policy output exists yet. The first
development-calibration invocation stopped during reference verification:
the worker exceeded its wall-clock bound twice while large dependencies were
being installed across Windows/WSL filesystems. The failure is retained in the
timestamped phase-failure log. It is infrastructure evidence, not a failed
mathematical answer or failed judge calibration.

The verifier unnecessarily imported the symbolic/LaTeX stack even for scalar
arithmetic. Scalar tasks now use the standard library's exact `Fraction`
arithmetic through the same bounded AST interpreter. Math-Verify is loaded only
for polynomial comparison; primality checking still uses SymPy. Worker CPU,
memory, wall-time, grammar-size and retry limits are unchanged. Scalar answers
must be numerical arithmetic without variables, even if variables could cancel.
No generated program is executed.

A regression also exposed premature rounding of decimal literals through
Python's AST float values. Reading the literal source segment and constructing
an exact rational fixes that error for both scalar and polynomial arithmetic.
Scientific-notation exponents are bounded in magnitude to prevent enormous
denominators. This is a verifier correctness repair, applied identically to all
arms before any policy-generated results, not a changed theory reward.

Sources: [Python AST source segments](https://docs.python.org/3/library/ast.html#ast.get_source_segment),
[exact fractions](https://docs.python.org/3/library/fractions.html),
[Math-Verify](https://github.com/huggingface/Math-Verify), and
[Microsoft's cross-filesystem performance guidance](https://learn.microsoft.com/en-us/windows/wsl/filesystems).
Further model-backed integration remains pending; passing unit tests does not
guarantee runtime performance under every concurrent workload.
