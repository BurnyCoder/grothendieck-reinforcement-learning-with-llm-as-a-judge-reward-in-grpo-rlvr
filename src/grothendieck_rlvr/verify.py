"""Final-answer extraction and bounded, isolated symbolic verification.

Math-Verify: https://github.com/huggingface/Math-Verify (gold-first verification).
No generated text reaches eval/exec or SymPy's expression-string parser.
"""
import json
import os
import re
import subprocess
import sys

from .schema import Task, Verification


class VerifierFailure(RuntimeError):
    """Infrastructure must not be converted into a zero correctness reward."""


def run_worker(payload: dict) -> dict:
    """Use a fresh process so wall-time and Linux resource limits are enforceable."""
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    completed = subprocess.run([sys.executable, "-m", "grothendieck_rlvr.verifier_worker"],
                               input=json.dumps(payload), capture_output=True, text=True,
                               timeout=15, env=env, check=True)
    return json.loads(completed.stdout)


def verify_answer(task: Task, response: str) -> Verification:
    """Score only one terminal delimited answer, retrying infrastructure once."""
    matches = re.findall(r"<final>(.*?)</final>", response, flags=re.S)
    if (len(matches) != 1 or response.count("<final>") != 1 or response.count("</final>") != 1
            or not response.rstrip().endswith("</final>")):
        return Verification(status="invalid_format", detail="Require exactly one terminal <final> answer")
    answer = matches[0].strip()
    if len(answer) > 1024:
        return Verification(status="invalid_format", detail="Answer exceeds parser size limit")
    payload = {"family": task.family, "answer": answer, "gold": task.answer, "metadata": task.metadata}
    for attempt in range(2):
        try:
            result = run_worker(payload)
            if result.get("error"):
                raise VerifierFailure(result["error"])
            return Verification(answer=answer, **result)
        except (subprocess.SubprocessError, TimeoutError, OSError, ValueError, VerifierFailure) as exc:
            if attempt:
                raise VerifierFailure(f"Verification failed twice for {task.id}: {exc}") from exc
    raise AssertionError("Unreachable retry state")
