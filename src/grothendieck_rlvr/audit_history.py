"""Reconstruct instrument and execution findings from saved events and tensor bytes on CPU."""
import csv
import math
import struct
from collections import Counter, defaultdict
from datetime import datetime
from fractions import Fraction
from statistics import mean
from zoneinfo import ZoneInfo
import json

import numpy as np

from .io import PROJECT, read_json, read_jsonl
from .saved_correctness import file_hash

DEV = PROJECT / "reports/development"
WEIGHTS = {"structural_understanding": 20, "justified_generality": 20, "problem_as_consequence": 15,
           "reuse_and_connections": 15, "conceptual_economy": 10, "constructive_novelty": 20}


def rubric_values(a):
    """Reconstruct the dated six-item rubric; v4 predates the declared-reference gate."""
    if not a or a["theory_validity"] != "supported":
        return 0., 0.
    scores = {k: v["score"] for k, v in a["criteria"].items()}
    if comp := a.get("novelty_comparison"):
        cap = 4 if comp["use_evidence"] else 1
        if comp["relation"] != "beyond_reference" or not comp["addition_evidence"]:
            cap = 0
        scores["constructive_novelty"] = min(cap, scores["constructive_novelty"])
    return sum(WEIGHTS[k]*scores[k] for k in WEIGHTS)/400, scores["constructive_novelty"]/4


def calibration_history():
    """Rebuild strict pair judgements, ties and the best attainable final rate from raw opinions."""
    results = []
    for file in sorted(DEV.glob("calibration-*.json")):
        published = read_json(file)
        raw = file.with_name(file.stem.removeprefix("calibration-") + ".jsonl")
        events = read_jsonl(raw)
        pairs = defaultdict(list)
        for e in events:
            if e["kind"] == "judge_assessment":
                t, n = rubric_values(e["assessment"])
                if not (math.isclose(t, e["theory"], abs_tol=1e-12) and n == e["novelty"]):
                    raise ValueError(f"{raw.name}: component scores disagree with the logged assessment")
                pairs[e["task_id"]].append((t, n))
        observed, wins, ties, suppression = [], 0, 0, len(published["suppression"])
        for pair in published["ordering"]:
            (pt, pn), (bt, bn) = pairs.pop(pair["id"])
            control = bn > 0 if pair.get("expected_control_novelty") == "modest" else bn == 0
            passed = pt > bt and (pair["stratum"] != "novelty" or (pn > bn and control))
            if passed != pair["passed"] or not all(math.isclose(x, pair[k], abs_tol=1e-12)
                    for x, k in zip((pt, pn, bt, bn), ("preferred", "preferred_novelty", "dispreferred", "dispreferred_novelty"))):
                raise ValueError(f"{file.name}: archived pair differs from component reanalysis")
            observed.append({"id": pair["id"], "quality": [pt, bt], "novelty": [pn, bn], "passed": passed})
            wins += passed
            ties += pt == bt
        if pairs or suppression or any(x["stratum"] != "novelty" for x in published["ordering"]):
            raise ValueError(f"{file.name}: unexpected case population; inspect before pooling")
        total = 8 if "v4" in file.name else 12
        upper = Fraction(wins + total - len(observed), total)
        if upper >= Fraction(4, 5) or published["passed"] or float(upper) != published["strata"]["novelty"]["preference_upper_bound"]:
            raise ValueError(f"{file.name}: futility decision differs")
        results.append({"log": raw.name, "judge": published["identity"]["judge"], "pairs": observed,
                        "passes": wins, "observed": len(observed), "quality_ties": ties, "scheduled": total,
                        "attainable_rate": float(upper), "suppression_observed": suppression, "suppression_rate": None,
                        "requests": sum(e["kind"] == "model_request" for e in events),
                        "responses": sum(e["kind"] == "model_response" for e in events)})
    return results


def tensor_comparison(first, second):
    """Read F32 checkpoint buffers without constructing a model. Serialization metadata is excluded."""
    with first.open("rb") as a, second.open("rb") as b:
        headers = [json.loads(f.read(struct.unpack("<Q", f.read(8))[0])) for f in (a, b)]
        buffers = [f.read() for f in (a,b)]
        names = set(headers[0]) - {"__metadata__"}
        if names != set(headers[1]) - {"__metadata__"}:
            raise ValueError("Adapter tensor names changed")
        changed, peak = 0, 0.
        for name in sorted(names):
            values = []
            if headers[0][name]["shape"] != headers[1][name]["shape"]:
                raise ValueError("Mismatched adapter shapes")
            for buffer, h in zip(buffers, headers):
                info = h[name]
                if info["dtype"] != "F32":
                    raise ValueError("Unexpected archived adapter dtype")
                lo, hi = info["data_offsets"]
                values.append(np.frombuffer(buffer, dtype="<f4", count=(hi-lo)//4, offset=lo))
            delta = float(np.max(np.abs(values[0]-values[1])))
            changed += delta > 0
            peak = max(peak, delta)
    return {"adapter_tensors": len(names), "changed_tensors": changed, "maximum_parameter_change": peak}


def execution_history(storage):
    """Reconstruct every archived pilot boundary and the interrupted comparative and diagnostic runs."""
    pilots = []
    for name in ("pilot-theory-seed42", "exploratory-single-v2-pilot-theory-seed42",
                 "exploratory-small-gpu-v2-pilot-theory-seed42"):
        directory = storage / "runs" / name
        events = read_jsonl(directory / "events.jsonl")
        batches = defaultdict(list)
        for e in events:
            if e["kind"] == "rollout":
                t, n = rubric_values(e["assessment"])
                c = e["verification"]["status"] == "correct"
                if not math.isclose(e["reward"], c*(1+.5*t), abs_tol=1e-12):
                    raise ValueError(f"{name}: reward mismatch")
                batches[e["reward_call"]].append((c, c*t, c*n, e["reward"]))
        steps = [e for e in events if e["kind"] == "training_metrics" and "step_time" in e["metrics"]]
        stats = [{**dict(zip(("accuracy", "metric", "novelty", "reward"), map(mean, zip(*rows)))),
                  "rollouts": len(rows), "step": e["step"], "step_seconds": e["metrics"]["step_time"],
                  "learning_rate": e["metrics"]["learning_rate"]} for rows, e in zip(batches.values(), steps, strict=True)]
        a, b = [directory / f"checkpoint-{i}/adapter_model.safetensors" for i in (1, 2)]
        diff = tensor_comparison(a, b)
        receipt = next(read_json(p) for p in DEV.glob("feasibility*.json")
                       if (r := read_json(p)).get("run_id") == name and r.get("step") == 2 and "changed_tensors" in r)
        if any(receipt[k] != v for k, v in diff.items()):
            raise ValueError(f"{name}: adapter comparison differs from receipt")
        pilots.append({"run": name, "steps": stats, **diff, "checkpoint_sha256": [file_hash(a), file_hash(b)],
                       "resumed": any(e["kind"] == "training_started" and e.get("resumed_from") for e in events)})
    trajectories = {}
    for name in ("exploratory-small-gpu-v2-theory-seed42",
                 "exploratory-small-gpu-v2-pilot-cache-release-v1-theory-seed42"):
        directory = storage / "runs" / name
        events = read_jsonl(directory / "events.jsonl")
        updates = [{k: e[k] for k in ("time", "step", "peak_gpu_allocated_bytes", "peak_gpu_reserved_bytes",
                                       "current_gpu_reserved_bytes") if k in e} | {"seconds": e["metrics"]["step_time"]}
                   for e in events if e["kind"] == "training_metrics" and "step_time" in e["metrics"]]
        if not updates:
            raise FileNotFoundError(f"No recorded updates for {name}")
        trajectories[name] = {"updates": updates, "required": read_json(directory / "run.json")["config"]["max_steps"],
                              "last_step": updates[-1]["step"], "checkpoints": [e["step"] for e in events if e["kind"] == "checkpoint"],
                              "resumes": sum(e["kind"] == "training_started" and bool(e.get("resumed_from")) for e in events)}
    receipt = read_json(DEV / "feasibility-small-gpu-v2-device-memory.json")
    samples = []
    with (PROJECT / receipt["source"]).open() as f:
        for entry in csv.DictReader(f):
            dt = datetime.strptime(entry["timestamp"], "%Y/%m/%d %H:%M:%S.%f").replace(tzinfo=ZoneInfo("Europe/Berlin"))
            samples.append((dt, int(entry[" memory.used [MiB]"].split()[0])))
    windows = []
    for span in receipt["invocations"]:
        values = [v for dt, v in samples if datetime.fromisoformat(span["start"]) <= dt <= datetime.fromisoformat(span["end"])]
        if (len(values), max(values)) != (span["samples"], span["peak_mib"]):
            raise ValueError("Device sampling window disagrees with raw CSV")
        windows.append({"samples": len(values), "peak_mib": max(values)})
    return {"pilots": pilots, "trajectories": trajectories, "device_windows": windows}


def transcript_counts():
    """Count events per preserved excerpt; also report unique requests/responses across overlapping excerpts."""
    from .io import digest
    per_file, unique = {}, defaultdict(set)
    for path in sorted(DEV.glob("*.jsonl")):
        counts = Counter()
        for e in read_jsonl(path):
            counts[e["kind"]] += 1
            if e["kind"] in ("model_request", "model_response", "judge_assessment"):
                unique[e["kind"]].add(digest(e))
        per_file[path.name] = dict(sorted(counts.items()))
    return {"files": per_file, "distinct_events": {k: len(v) for k, v in unique.items()}}


def generation_history(archives):
    """Reconcile every saved full response and prompt with its timestamped request-response event pair."""
    from .saved_correctness import ARMS, EXPLORATORY_PREFIX
    result = {}
    for arm in ARMS:
        name = EXPLORATORY_PREFIX+arm
        path = archives/name
        receipt = read_json(PROJECT/"reports/generation"/(name+".json"))
        raw = read_jsonl(path/"generations.jsonl")
        counts, times, pending = Counter(), [], None
        with (path/"events.jsonl").open(encoding="utf-8") as f:
            for line in f:
                e = json.loads(line)
                counts[e["kind"]] += 1
                if e["kind"] == "policy_request":
                    pending = e["messages"]
                if e["kind"] == "policy_response":
                    row = raw[len(times)]
                    if pending != row["prompt"] or any(e[k] != row[k] for k in ("response","response_tokens","seconds")):
                        raise ValueError(f"{name}: stored answer differs from event stream")
                    times.append(e["time"])
                    pending = None
        seconds = sum(r["seconds"] for r in raw)
        saved = [r["time"] for r in raw]
        if (counts != receipt["event_counts"] or [saved[0],saved[-1]] != [receipt["first_response_at"],receipt["last_response_at"]]
                or not math.isclose(seconds, receipt["generation_seconds_sum"], abs_tol=1e-8)
                or len(times) != len(raw) or len(raw) != receipt["saved"]
                or any(t > s for t,s in zip(times,saved))):
            raise ValueError(f"{name}: generation chronology or duration differs from receipt")
        result[arm] = {"events": dict(counts), "saved": len(raw), "first_response_event": times[0],
                       "last_response_event": times[-1], "first_saved": saved[0], "last_saved": saved[-1],
                       "seconds_sum": seconds, "seconds_mean": seconds/len(raw),
                       "unmatched_requests": counts["policy_request"]-len(times)}
    return result


def mathematical_objections():
    """Tie each case derivation to the actual evaluated text and every recorded specialist objection."""
    import sympy as sp
    from .io import digest
    from .novelty_cases import novelty_example
    trials = {}
    for name in ("qwen-v8-specialists-dev", "qwen-v8-specialists-rubric-dev"):
        cases, stage_findings, side = [], {}, Counter()
        for event in read_jsonl(DEV / (name+".jsonl")):
            if event["kind"] == "model_request":
                payload = json.loads(event["request"]["messages"][-1]["content"])
            elif event["kind"] == "judge_stage_assessment":
                stage_findings[event["key"]] = event
            elif event["kind"] == "judge_assessment":
                key = event["task_id"]
                task, bridge, conventional, _ = novelty_example(int(key.rsplit("-", 1)[1]), "dev")
                text = (bridge, conventional)[side[key]]
                if payload["candidate_response"] != text or payload["problem"] != task.problem:
                    raise ValueError(f"{name}/{key}: candidate text differs")
                issues = [{"stage": stage_findings[k]["stage"], **issue} for k in event["stage_keys"].values()
                          for issue in stage_findings[k]["finding"].get("issues", [])]
                cases.append({"id": key, "side": ("developed", "control")[side[key]], "family": task.family,
                              "candidate_digest": digest(text), "problem": task.problem, "answer": task.answer,
                              "validity": event["assessment"]["theory_validity"], "issues": issues})
                side[key] += 1
        trials[name] = cases
    a,b,c,d = sp.symbols("a b c d")
    # Multiplication in the basis (1,e) has this matrix, whose determinant is the norm.
    left, right = sp.Matrix([[a,b],[b,a]]), sp.Matrix([[c,d],[d,c]])
    residual = sp.expand((left*right).det() - (a*a-b*b)*(c*c-d*d))
    # A complete directed relation on a finite set maps every nonempty subset to the full set.
    universe = frozenset((0,1))
    def neighbors(x):
        return universe if x else frozenset()
    u, v = frozenset((0,)), frozenset((1,))
    return {"trials": trials, "norm_composition_residual": str(residual),
            "literature_case6": {"linear_on_singletons": neighbors(u ^ v) == (neighbors(u) ^ neighbors(v)),
                                 "full_set_fixed": neighbors(universe) == universe,
                                 "singleton_image_size": len(neighbors(u))}}
