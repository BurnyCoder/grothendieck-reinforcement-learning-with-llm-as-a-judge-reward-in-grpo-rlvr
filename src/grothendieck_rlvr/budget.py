"""Transparent runtime scenarios from development artifacts, never confidence intervals."""


def training_budget(feasibility: list[dict], config: dict) -> dict:
    """Do not infer evaluation cost or future reward density from two optimizer intervals."""
    kinds = {"grpo_first_saved_boundary", "grpo_resumed_completion"}
    intervals = [record["step_metrics"]["step_time"] for record in feasibility if record.get("kind") in kinds]
    judged_arms = len(config["training_seeds"]) + 2  # Proposed seeds, permutation control, rubric ablation.
    return {
        "observed_step_seconds": intervals, "judged_training_arms": judged_arms,
        "selected_updates": config["max_steps"],
        "assumption": "Each future step repeats one observed development interval. These are scenarios, not confidence bounds.",
        "limitations": "Two intervals, including first-use overhead; v3 judge protocol. Future lengths, accuracy, theory and v4 latency may differ. Excludes correctness-only runs, calibration, evaluation, transfer, loading and publication.",
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
    return "\n\n".join(lines[:4]) + "\n\n" + "\n".join(lines[4:]) + "\n"
