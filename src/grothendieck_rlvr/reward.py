"""One correctness-gated scalar for TRL, plus separately logged components."""
import random

from .io import EventLog
from .schema import Assessment, Task
from .verify import verify_answer


def composite(correct: bool, assessment: Assessment | None) -> float:
    """Wrong answers cannot recover reward through stylistic or theory scores."""
    return float(correct) * (1 + .5 * (assessment.quality if assessment else 0))


def permute_correct(values: list[float], correct: list[bool], seed: int) -> list[float]:
    """Randomly permute the eligible bonuses; individual assignments can remain fixed."""
    indices = [i for i, passed in enumerate(correct) if passed]
    shuffled = [values[i] for i in indices]
    random.Random(seed).shuffle(shuffled)
    result = [0.0] * len(values)
    for i, value in zip(indices, shuffled, strict=True):
        result[i] = value
    return result


def completion_text(completion) -> str:
    """TRL supports plain strings and conversational assistant message lists."""
    if isinstance(completion, str):
        return completion
    return "".join(message.get("content", "") for message in completion)


class CompositeReward:
    """TRL custom reward API: https://huggingface.co/docs/trl/grpo_trainer.

    Each task record is a dataset column repeated alongside its completion.
    This callable returns only the already-aggregated scalar reward.
    """
    __name__ = "correctness_gated_theory"

    def __init__(self, judge, log: EventLog, arm="theory", seed=42):
        self.judge, self.log, self.arm, self.seed = judge, log, arm, seed
        self.calls = 0

    def __call__(self, completions, task_record, prompts=None, **kwargs) -> list[float]:
        """Verify first, judge only correct outputs, and propagate service failures."""
        texts = [completion_text(c) for c in completions]
        tasks = [Task.model_validate(t) for t in task_record]
        if len(texts) != len(tasks):
            raise ValueError("TRL task/completion alignment mismatch")
        # Archive the whole sampled batch before any external check can fail. These
        # records are observations only; a failed check must not create a reward.
        for index, (task, text) in enumerate(zip(tasks, texts, strict=True)):
            self.log.emit("policy_completion", task_id=task.id, completion_index=index,
                          prompt=prompts[index] if prompts else task.problem, response=text,
                          reward_call=self.calls)
        verdicts = [verify_answer(t, text) for t, text in zip(tasks, texts, strict=True)]
        assessments = [self.judge.assess(t, text) if v.correct and self.arm != "correctness" else None
                       for t, text, v in zip(tasks, texts, verdicts, strict=True)]
        quality = [a.quality if a else 0.0 for a in assessments]
        novelty = [a.novelty if a else 0.0 for a in assessments]
        assigned = permute_correct(quality, [v.correct for v in verdicts], self.seed + self.calls) \
            if self.arm == "shuffled" else quality
        rewards = [float(v.correct) * (1 + .5*t) for v, t in zip(verdicts, assigned, strict=True)]
        for index, (task, text, verdict, assessment) in enumerate(zip(tasks, texts, verdicts, assessments, strict=True)):
            self.log.emit("rollout", task_id=task.id, family=task.family, prompt=prompts[index] if prompts else task.problem,
                          response=text, verification=verdict.model_dump(),
                          assessment=assessment.model_dump() if assessment else None,
                          novelty_credit=assessment.novelty_credit if assessment else None,
                          theory=quality[index], novelty=novelty[index],
                          assigned_theory=assigned[index], reward=rewards[index],
                          response_characters=len(text), reward_call=self.calls)
        self.log.emit("reward_batch", reward_call=self.calls, accuracy=sum(v.correct for v in verdicts)/len(verdicts),
                      theory=sum(quality)/len(quality), novelty=sum(novelty)/len(novelty),
                      zero_variance=len(set(rewards)) == 1,
                      permutation_eligible=sum(v.correct for v in verdicts) >= 2)
        self.calls += 1
        return rewards
