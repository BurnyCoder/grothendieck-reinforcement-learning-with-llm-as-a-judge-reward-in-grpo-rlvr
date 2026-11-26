"""Prespecified paired analyses; resampling units are problems or transfer sources."""
import numpy as np

from .analysis_evidence import locked_tasks, qualified_evidence


def paired_bootstrap(differences, strata, samples=10000, seed=20261115, hierarchical=False):
    """Keep matched seeds together within each problem; optionally resample seed pairs too."""
    values = np.asarray(differences, dtype=float)
    if values.ndim == 1:
        values = values[:, None]
    if not len(values) or len(values) != len(strata) or not np.isfinite(values).all():
        raise ValueError("Require finite paired observations with one stratum per problem")
    rng = np.random.default_rng(seed)
    draws = np.zeros(samples)
    labels = np.asarray(strata)
    seed_indices = rng.integers(values.shape[1], size=(samples, values.shape[1])) if hierarchical else None
    for label in sorted(set(strata)):
        group = values[labels == label]
        indices = rng.integers(len(group), size=(samples, len(group)))
        sampled = group[indices]
        if hierarchical:
            sampled = np.take_along_axis(sampled, seed_indices[:, None, :], axis=2)
        draws += sampled.mean(axis=(1, 2)) * len(group) / len(values)
    low, high = np.quantile(draws, [.025, .975])
    per_seed = values.mean(axis=0)
    return {"difference": float(values.mean()), "ci95": [float(low), float(high)],
            "per_seed_differences": per_seed.tolist(),
            "between_seed_sd": float(per_seed.std(ddof=1)) if len(per_seed) > 1 else None,
            "problems": len(values), "seeds": values.shape[1],
            "bootstrap_samples": samples, "hierarchical": hierarchical}


def summarize(rows: list[dict]) -> dict:
    """All reported scalar evaluation values derive from saved per-problem records."""
    if not rows:
        return {"n": 0, "accuracy": None, "metric": None, "theory_given_correct": None}
    correct = [r for r in rows if r["correct"]]
    return {"n": len(rows), "accuracy": sum(r["correct"] for r in rows)/len(rows),
            "metric": sum(r["metric"] for r in rows)/len(rows),
            "correctness_weighted_novelty": sum(float(r["correct"])*r["novelty"] for r in rows)/len(rows)
            if all("novelty" in r for r in rows) else None,
            "theory_given_correct": sum(r["theory"] for r in correct)/len(correct) if correct else None,
            "mean_response_tokens": sum(r["response_tokens"] for r in rows)/len(rows),
            "valid_format_rate": sum(r["verification"]["status"] != "invalid_format" for r in rows)/len(rows)}


def h1_decision(theory, accuracy):
    """Evaluate the registered inequalities; failure to show noninferiority alone is inconclusive."""
    # The discrete rubric and fixed sample resolve far less than twelve decimals.
    # Remove binary representation noise before applying the three strict/inclusive boundaries.
    tlo, thi = (round(float(x), 12) for x in theory["ci95"])
    alo, ahi = (round(float(x), 12) for x in accuracy["ci95"])
    if ahi < -.03:
        return "accuracy_inferior"
    if thi < .05:
        return "useful_gain_ruled_out"
    if round(float(theory["difference"]), 12) >= .05 and tlo > 0 and alo > -.03:
        return "criteria_met"
    return "inconclusive"


def primary_comparison(evaluations: dict, cfg: dict, suffix="", secondary=False, exploratory=False, archive=None) -> dict:
    """Do not turn a first-seed or partial result into a confirmatory success claim."""
    seeds = [s for s in cfg["training_seeds"]
             if f"theory-seed{s}{suffix}" in evaluations and f"correctness-seed{s}{suffix}" in evaluations]
    if not seeds:
        return {"status": "pending", "reason": "No matched trained arms have been evaluated"}
    maps = {}
    for seed in seeds:
        for arm in ("theory", "correctness"):
            rows = evaluations[f"{arm}-seed{seed}{suffix}"]
            if len({r["task_id"] for r in rows}) != len(rows):
                raise ValueError("Duplicate problem in evaluation")
            maps[arm, seed] = {r["task_id"]: r for r in rows}
    id_sets = [set(m) for m in maps.values()]
    if not all(ids == id_sets[0] for ids in id_sets):
        return {"status": "incomplete", "reason": "Matched runs have different evaluated problem IDs"}
    identifiers = sorted(id_sets[0])
    tasks = locked_tasks(secondary)
    expected_ids = {t.id: (t.split, t.family) for t in tasks}
    if any({i: (r["split"], r["family"]) for i, r in m.items()} != expected_ids for m in maps.values()):
        return {"status": "incomplete", "reason": "Evaluated IDs, splits or families differ from the locked manifest"}
    strata = [maps["theory", seeds[0]][i]["family" if secondary else "split"] for i in identifiers]
    judgments = {r["judge_identity"] for m in maps.values() for r in m.values()}
    if len(judgments) != 1:
        raise ValueError("Primary comparison requires identical frozen independent judge settings")
    for group in maps.values():
        for row in group.values():
            if (type(row["correct"]) is not bool or not 0 <= row["metric"] <= 1
                    or row["metric"] != row["correct"] * row["theory"]
                    or row["correct"] != (row["verification"]["status"] == "correct")):
                raise ValueError("Inconsistent archived correctness or C times theory")
    results = {}
    metrics = ["metric", "correct"]
    if all("novelty" in r for m in maps.values() for r in m.values()):
        metrics.append("novelty")
    for metric in metrics:
        difference = [[float(maps["theory", s][i][metric])-float(maps["correctness", s][i][metric])
                       for s in seeds] for i in identifiers]
        results[metric] = paired_bootstrap(difference, strata, cfg["bootstrap_samples"], cfg["data_seed"])
        results[metric + "_hierarchical"] = paired_bootstrap(
            difference, strata, cfg["bootstrap_samples"], cfg["data_seed"], hierarchical=True)
    expected = {"test_fresh": cfg["test_fresh_size"], "test_hard": cfg["test_hard_size"],
                "test_unseen": cfg["test_unseen_size"]}
    if secondary:
        from .ood import OOD_FAMILIES
        expected = {"test_ood": cfg["test_ood_per_family"] * len(OOD_FAMILIES)}
    observed = [maps["theory", seeds[0]][i]["split"] for i in identifiers]
    complete = seeds == cfg["training_seeds"] and len(observed) == sum(expected.values()) \
        and all(observed.count(k) == n for k, n in expected.items())
    status = ("secondary" if secondary else "confirmatory") if complete else "exploratory"
    decision = None
    if complete and not secondary and not exploratory:
        reason = qualified_evidence(archive, maps, next(iter(judgments)), cfg, tasks)
        if reason:
            return {"status": "unqualified", "reason": reason, "criteria_met": None, **results}
        decision = h1_decision(results["metric"], results["correct"])
    return {"status": "exploratory_uncalibrated" if exploratory else status, "seeds": seeds,
            "decision": decision, "criteria_met": decision == "criteria_met" if decision else None, **results}


def transfer_analysis(rows: list[dict], samples=10000, expected_sources=100) -> dict:
    """Aggregate the four targets per source before paired resampling of source IDs."""
    conditions = sorted({r["condition"] for r in rows})
    summaries = {}
    groups = {}
    for condition in conditions:
        subset = [r for r in rows if r["condition"] == condition]
        summaries[condition] = {"n": len(subset), "accuracy": sum(r["correct"] for r in subset)/len(subset)}
        groups[condition] = {}
        for row in subset:
            groups[condition].setdefault(row["source_id"], []).append(row)
    def compare(left, right):
        """Keep every target paired and every four-target source clustered in all contrasts."""
        current, baseline = groups.get(left, {}), groups.get(right, {})
        if len(current) != expected_sources or set(current) != set(baseline) or any(
                len(v) != 4 for group in (current, baseline) for v in group.values()):
            return {"status": "incomplete"}
        ids = sorted(current)
        differences, strata = [], []
        for source in ids:
            a, b = current[source], baseline[source]
            if len({r["task_id"] for r in a}) != 4 or {r["task_id"] for r in a} != {r["task_id"] for r in b}:
                raise ValueError("Transfer conditions must contain matching probes")
            differences.append(np.mean([r["correct"] for r in a])-np.mean([r["correct"] for r in b]))
            strata.append(a[0]["family"])
        return paired_bootstrap(differences, strata, samples=samples)

    notes = [c for c in conditions if c.endswith(":notes")]
    return {"summaries": summaries,
            "versus_no_notes": {c: compare(c, "no_notes") for c in conditions if c != "no_notes"},
            "versus_unrelated": {c.removesuffix(":notes"): compare(c, c.removesuffix(":notes") + ":unrelated")
                                 for c in notes},
            "between_note_sources": {f"{left} minus {right}": compare(left, right)
                                     for i, left in enumerate(notes) for right in notes[:i]},
            "interpretation": "exploratory; source-clustered, unadjusted paired intervals"}
