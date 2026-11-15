"""Transparent runtime scenarios from development artifacts, never confidence intervals."""
from collections import Counter

from .io import PROJECT, digest, read_json


def training_budget(feasibility: list[dict], config: dict) -> dict:
    """Do not infer evaluation cost or future reward density from two optimizer intervals."""
    kinds = {"grpo_first_saved_boundary", "grpo_resumed_completion"}
    intervals = [record["step_metrics"]["step_time"] for record in feasibility if record.get("kind") in kinds]
    judged_arms = len(config["training_seeds"]) + 2  # Proposed seeds, permutation control, rubric ablation.
    # Single-GPU GRPO repeats each prompt num_generations times; shuffle_dataset is False.
    # https://huggingface.co/docs/trl/grpo_trainer#trl.GRPOConfig
    completions = config["max_steps"] * config["per_device_train_batch_size"] * config["gradient_accumulation_steps"]
    prompt_occurrences, remainder = divmod(completions, config["num_generations"])
    if remainder:
        raise ValueError("Generation budget must contain complete prompt groups")
    tasks = read_json(PROJECT / "data/train.json")
    prefix = tasks[:min(prompt_occurrences, len(tasks))]
    return {
        "observed_step_seconds": intervals, "judged_training_arms": judged_arms,
        "selected_updates": config["max_steps"],
        "planned_exposure": {"completions": completions, "prompt_occurrences": prompt_occurrences,
                             "distinct_prompts": len(prefix), "manifest_prompts": len(tasks),
                             "distinct_by_family": dict(sorted(Counter(t["family"] for t in prefix).items())),
                             "manifest_hash": digest(tasks),
                             "assumption": "One GPU, sequential pre-shuffled manifest, one GRPO iteration, completed fixed budget. Actual exposure must be checked against rollout logs."},
        "assumption": "Each future step repeats one observed development interval. These are scenarios, not confidence bounds.",
        "limitations": "Two intervals, including first-use overhead, used the v3 non-thinking judge. Neither the later reasoning-enabled judge nor the decomposed protocols are timed by these scenarios. Refresh development throughput before comparative training; future lengths, accuracy and theory density may differ. Excludes correctness-only runs, calibration, evaluation, transfer, loading and publication.",
        "options": [{"updates": updates,
                     "one_judged_arm_hours": [updates * t / 3600 for t in (min(intervals), max(intervals))],
                     "all_judged_arms_hours": [updates * t * judged_arms / 3600 for t in (min(intervals), max(intervals))]}
                    for updates in (32, 64, 128, 256)] if intervals else [],
    }


def budget_markdown(budget: dict) -> str:
    """Regenerate the planning table from saved timings alongside the scientific reports."""
    lines = ["# Development training-budget scenarios", budget["assumption"], budget["limitations"],
             f"Selected matched budget: **{budget['selected_updates']} optimizer updates per training arm**.",
             "| Updates | One judge-scored arm (hours) | All judge-scored arms (hours) |",
             "|---:|---:|---:|"]
    for row in budget["options"]:
        one, all_arms = row["one_judged_arm_hours"], row["all_judged_arms_hours"]
        lines.append(f"| {row['updates']} | {one[0]:.2f}–{one[1]:.2f} | {all_arms[0]:.2f}–{all_arms[1]:.2f} |")
    lines.extend(["", "Sources: `reports/development/feasibility-grpo-first-boundary.json` and "
                  "`reports/development/feasibility-grpo-resumed-complete.json`. "
                  "The reduction is preregistered in [the budget amendment](amendments/2026-11-15-training-budget.md). "
                  "This is not a guarantee that the full study fits in one week."])
    exposure = budget["planned_exposure"]
    lines.extend(["", "## Planned data exposure", "", exposure["assumption"], "",
                  f"The configured budget schedules {exposure['completions']} completions across "
                  f"{exposure['prompt_occurrences']} prompt occurrences, covering "
                  f"{exposure['distinct_prompts']} distinct prompts from the "
                  f"{exposure['manifest_prompts']}-prompt training manifest. All arms use this same order. "
                  "These are configuration-derived counts, not completed training results.", "",
                  "| Training family | Distinct prompts scheduled |", "|---|---:|"])
    lines.extend(f"| {family} | {count} |" for family, count in exposure["distinct_by_family"].items())
    lines.extend(["", "Source: `data/train.json` and `configs/study.json`. Reducing optimizer updates "
                  "also reduces task exposure; it does not merely shorten optimization on the full manifest."])
    return "\n\n".join(lines[:4]) + "\n\n" + "\n".join(lines[4:]) + "\n"
