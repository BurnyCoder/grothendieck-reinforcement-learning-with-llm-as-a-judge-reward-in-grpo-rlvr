"""Versioned judge interpretation and identical ordinary policy prompts across arms."""
from pathlib import Path

from .schema import Task

DIRECTORY = Path(__file__).with_name("prompts")


def judge_system(variant="quoted") -> str:
    """The ablation changes only the historical framing, retaining the whole rubric."""
    rubric = (DIRECTORY / "rubric-v1.txt").read_text(encoding="utf-8")
    if variant == "rubric":
        return rubric
    if variant != "quoted":
        raise ValueError(f"Unknown judge prompt variant {variant}")
    return (DIRECTORY / "rising-sea-v1.txt").read_text(encoding="utf-8") + "\n\n" + rubric


def policy_messages(task: Task, rising=False, notes=None, request_notes=False) -> list[dict]:
    """Only the problem enters the model; references and target answers are withheld."""
    instruction = "Solve the mathematical problem and explain your reasoning clearly."
    if rising:
        instruction += (" Develop a useful, justified general framework, show how the problem follows "
                        "from it, and demonstrate a reusable consequence where appropriate.")
    if request_notes:
        instruction += (" Include reusable mathematical notes within exactly one <notes>...</notes> "
                        "section. State assumptions and justify any general claims.")
    instruction += (" End with exactly one <final>...</final> section containing only the requested "
                    "answer, with nothing after it. Use * for multiplication and ** for powers.")
    problem = task.problem
    if notes is not None:
        problem += "\n\nOptional mathematical notes (check their validity yourself):\n" + notes
    return [{"role": "system", "content": instruction}, {"role": "user", "content": problem}]
