"""Verify the registered inputs of statistical comparisons using only archived artifacts."""
from pathlib import Path
import re

from .data import load_tasks
from .io import PROJECT, digest, read_json, read_jsonl
from .prompts import policy_messages


def locked_tasks(secondary):
    """Return the manifest used for an analysis, including the registered stratum of each ID."""
    if secondary:
        from .ood import load_ood
        return load_ood()
    return [t for split in ("test_fresh", "test_hard", "test_unseen") for t in load_tasks(split)]


def qualified_evidence(directory, maps, judge_id, cfg, tasks):
    """A complete file count alone cannot identify a qualified judge or the trained checkpoint."""
    from .calibration import build_cases, calibration_summary, require_calibration
    from .saved_correctness import file_hash
    if directory is None:
        return "Qualification and final checkpoints lack archive provenance"
    try:
        if cfg != read_json(PROJECT/"configs/study.json"):
            return "Analysis configuration differs from the locked study"
        require_calibration()
        for split in ("dev", "audit"):
            cases = build_cases(split)
            for role, variant in (("training_judge", "quoted"), ("training_judge", "rubric"), ("evaluation_judge", "quoted")):
                record = read_json(directory / "calibration" / f"{role}-{variant}-{split}.json")
                if (record["role"], record["variant"], record["split"]) != (role, variant, split):
                    return "Calibration suite label differs from the archived identity"
                for case_key, rows_key in (("pairs", "ordering"), ("false_cases", "suppression")):
                    expected = {c["task"]["id"]: c for c in cases[case_key]}
                    rows = record[rows_key]
                    if len(rows) != len(expected) or {r["id"] for r in rows} != set(expected):
                        return "Calibration suite has missing, duplicated or substituted cases"
                    for row in rows:
                        case = expected[row["id"]]
                        if row["stratum"] != case["stratum"]:
                            return "Calibration stratum differs from the registered case"
                        if rows_key == "ordering":
                            credit = row["dispreferred_novelty"]
                            control = credit > 0 if case.get("control_novelty") == "modest" else credit == 0
                            passed = row["preferred"] > row["dispreferred"] and (case["stratum"] != "novelty"
                                     or (row["preferred_novelty"] > credit and control))
                        else:
                            passed = row["theory"] == 0
                        if row["passed"] is not passed:
                            return "Calibration verdict disagrees with observed scores"
                gates = calibration_summary(cases, record["ordering"], record["suppression"])
                if not gates["passed"] or any(record[k] != v for k,v in gates.items()):
                    return "Recorded judge qualification differs from recomputed complete gates"
        def qualified_judge(role):
            return read_json(directory / "calibration" / f"{role}-quoted-audit.json")["identity"]["judge"]
        if judge_id != qualified_judge("evaluation_judge"):
            return "Evaluation rows use a different judge from the qualified audit"
        training_judge = qualified_judge("training_judge")
        selected = read_json(PROJECT / "configs/policy-selection.json")["policy"]
        qualified_models = read_json(PROJECT / "configs/history/exploratory-single-v2/models.lock.json")
        current_models = read_json(PROJECT / "configs/models.lock.json")
        if any(current_models[r]["revision"] != qualified_models[r]["revision"]
               for r in ("policy", "training_judge", "evaluation_judge")):
            return "Selected models differ from the registered qualification study"
        manifest = read_json(PROJECT / "data/manifest.lock.json")
        prompts = {t.id: policy_messages(t) for t in tasks}
        task_hash = digest([t.model_dump() for t in tasks])
        for (arm, seed), observations in maps.items():
            name = f"{arm}-seed{seed}"
            run, ev = directory / "runs" / name, directory / "evaluations" / name
            identity, summary = read_json(run / "run.json"), read_json(run / "summary.json")
            step = cfg["max_steps"]
            ckpt = run / f"checkpoint-{step}"
            state = read_json(ckpt / "groth-state.json")
            if (identity["arm"] != arm or identity["seed"] != seed or identity["config"] != cfg
                    or identity["model"] != selected or identity["manifest"] != digest(manifest)
                    or identity["judge"] != (training_judge if arm == "theory" else None)
                    or identity.get("experiment") or summary.get("experiment") != "qualified-study"
                    or summary["run_id"] != name or summary["step"] != step or summary["pilot"]
                    or not summary["completed"] or not state["complete"] or state["global_step"] != step
                    or state["identity_hash"] != digest(identity)):
                return f"{name}: final qualified training boundary is unverified"
            gen, status = read_json(ev / "generation-config.json"), read_json(ev / "status.json")
            if (gen["run_id"] != name or not gen["adapter"] or gen.get("experiment") or gen["rising"]
                    or gen["split"] != "test" or gen["tasks"] != task_hash or gen["prompts"] != digest(prompts)
                    or gen["inference"]["model"] != selected or gen["inference"]["do_sample"]
                    or not status["complete"] or status["judge_identity"] != judge_id
                    or status["expected"] != len(tasks) or status["scored"] != len(tasks)):
                return f"{name}: evaluation identity or coverage differs"
            for file in ("adapter_model.safetensors", "adapter_config.json"):
                if gen["inference"]["files"][file] != file_hash(ckpt / file):
                    return f"{name}: generation differs from the final checkpoint"
            raw = read_jsonl(ev / "generations.jsonl")
            if len(raw) != len(tasks) or {r["task_id"] for r in raw} != set(observations):
                return f"{name}: raw generations do not cover the manifest"
            for row in raw:
                scored = observations[row["task_id"]]
                if (scored.get("experiment") != "qualified-study" or row["prompt"] != prompts[row["task_id"]]
                        or row["response"] != scored["response"] or scored["prompt"] != row["prompt"]):
                    return f"{name}: scored response differs from generation"
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        return f"Missing or incompatible qualification evidence: {exc}"
    return None


def registered_transfer(directory: Path, cfg, analyse):
    """Validate frozen source-run conditions and every source-target mapping before estimating H2."""
    rows = read_jsonl(directory / "scores.jsonl")
    if not rows:
        return {**analyse([], cfg["bootstrap_samples"], cfg["transfer_sources"]), "status": "pending"}
    if not (directory / "config.json").is_file():
        return {"status": "incomplete", "summaries": {}, "reason": "Missing frozen transfer configuration"}
    config = read_json(directory / "config.json")
    sources, targets = load_tasks("transfer_source"), load_tasks("transfer_target")
    names = config.get("source_runs", [])
    conditions = {"no_notes"} | {n + ":" + kind for n in names for kind in ("notes", "unrelated")}
    target_map = {t.id: (t.source_id, t.family) for t in targets}
    keys = {(r["condition"], r["task_id"]) for r in rows}
    full = {(c, t) for c in conditions for t in target_map}
    source_configs = config.get("source_configs", {})
    from .evaluation import inference_identity
    ordered = sorted(sources, key=lambda t: (t.family, t.id))
    deranged = {s.id: ordered[(i + len(ordered)//4) % len(ordered)].id for i,s in enumerate(ordered)}
    valid = (bool(names) and len(set(names)) == len(names) and set(names) == set(source_configs)
             and config.get("inference") == inference_identity() and config.get("note_token_limit") == 1024
             and config.get("tasks") == digest([t.model_dump() for t in sources + targets])
             and config.get("prompts") == digest([[policy_messages(t), policy_messages(t, notes="")] for t in targets])
             and len(keys) == len(rows) and keys == full
             and all(target_map.get(r["task_id"]) == (r["source_id"], r["family"])
                     and type(r["correct"]) is bool and r["correct"] == (r["verification"]["status"] == "correct")
                     for r in rows))
    if not valid:
        return {"status": "incomplete", "summaries": {}, "reason": "Unmatched frozen conditions or source-target IDs"}
    for r in rows:
        if r["condition"] == "no_notes":
            valid = r.get("notes") is None and r.get("unrelated_source_id") is None and r.get("notes_tokens") == 0
        else:
            valid = (isinstance(r.get("notes"), str) and r.get("unrelated_source_id") == deranged[r["source_id"]]
                     and 0 <= r.get("notes_tokens", -1) <= config["note_token_limit"])
        if not valid:
            return {"status": "incomplete", "summaries": {}, "reason": "Missing or mismatched note condition"}
    from .evaluation import extract_notes
    storage = directory.parent if directory.name == "transfer" else directory.parent.parent
    note_sets = {}
    for name in names:
        source = source_configs[name]
        if (source.get("split") != "transfer_source" or source.get("run_id") != name
                or source.get("tasks") != digest([t.model_dump() for t in sources])
                or source.get("inference", {}).get("model") != config.get("inference", {}).get("model")):
            return {"status": "incomplete", "summaries": {}, "reason": "Source-note provenance differs"}
        note_dir = storage/"evaluations"/name
        raw = read_jsonl(note_dir/"generations.jsonl")
        prompts = {t.id: policy_messages(t, rising=source["rising"], request_notes=True) for t in sources}
        if (not (note_dir/"generation-config.json").is_file() or read_json(note_dir/"generation-config.json") != source
                or source.get("experiment") != config.get("experiment") or source["prompts"] != digest(prompts)
                or len(raw) != len(sources) or {r["task_id"] for r in raw} != set(prompts)
                or any(r["prompt"] != prompts[r["task_id"]] for r in raw)):
            return {"status": "incomplete", "summaries": {}, "reason": "Source generations do not match frozen notes"}
        note_sets[name] = {r["task_id"]: extract_notes(r["response"]) for r in raw}
    if config.get("notes") != digest(note_sets):
        return {"status": "incomplete", "summaries": {}, "reason": "Source-note digest differs"}
    # The design also requires note producers from both baseline prompts and matched trained policies.
    baseline_prompts = {v["rising"] for v in source_configs.values() if v["adapter"] is None}
    trained = {"theory": set(), "correctness": set()}
    for spec in source_configs.values():
        if spec.get("adapter"):
            from .saved_correctness import file_hash
            boundary = Path(spec["adapter"])
            match = re.search(r"(?:^|-)(theory|correctness)-seed(\d+)$", boundary.parent.name)
            run = storage/"runs"/boundary.parent.name
            ckpt = run/f"checkpoint-{cfg['max_steps']}"
            if (not match or boundary.name not in ("adapter", ckpt.name) or not (run/"summary.json").is_file()
                    or not (ckpt/"groth-state.json").is_file()):
                return {"status": "incomplete", "summaries": {}, "reason": "Missing final note-producer checkpoint"}
            end, state = read_json(run/"summary.json"), read_json(ckpt/"groth-state.json")
            if (end["completed"] and not end["pilot"] and end["step"] == state["global_step"] == cfg["max_steps"]
                    and state["complete"] and all((ckpt/f).is_file() and spec["inference"]["files"].get(f) == file_hash(ckpt/f)
                                                  for f in ("adapter_model.safetensors", "adapter_config.json"))):
                trained[match[1]].add(int(match[2]))
            else:
                return {"status": "incomplete", "summaries": {}, "reason": "Note producer differs from final checkpoint"}
    by_key = {(r["condition"], r["task_id"]): r for r in rows}
    shortfalls = sum(by_key[n+":notes", t]["notes_tokens"] != by_key[n+":unrelated", t]["notes_tokens"]
                     for n in names for t in target_map)
    if (baseline_prompts != {True, False} or not trained["theory"] or trained["theory"] != trained["correctness"]
            or not trained["theory"] <= set(cfg["training_seeds"]) or shortfalls):
        return {"status": "incomplete", "summaries": {}, "unequal_note_length_pairs": shortfalls,
                "reason": "Missing matched final note producers, baseline prompts or token lengths"}
    result = analyse(rows, cfg["bootstrap_samples"], cfg["transfer_sources"])
    result.update(status="exploratory", unequal_note_length_pairs=0)
    return result
